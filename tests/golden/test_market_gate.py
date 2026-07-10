from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path

import pytest
import yaml
from indiciumforge_core.artifacts.comparator import compare_semantic_market_gate, load_meta
from indiciumforge_workflow.market_gate.runner import run_market_gate

ROOT = Path(__file__).resolve().parents[2]
GOLDEN_ROOT = ROOT / "tests" / "golden" / "market_gate"
MANIFEST = ROOT / "GOLDEN_MANIFEST.yaml"


def _scenarios() -> list[dict]:
    payload = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    return payload["scenarios"]


def _scenario_trade_date(scenario: dict) -> date:
    raw = scenario["trade_date"]
    if isinstance(raw, date):
        return raw
    return date.fromisoformat(str(raw))


@pytest.mark.parametrize("scenario", _scenarios(), ids=lambda item: item["id"])
def test_market_gate_golden_scenarios(scenario: dict, tmp_path: Path) -> None:
    scenario_id = scenario["id"]
    if scenario.get("status") == "pending_export":
        pytest.skip("golden scenario pending export")
    scenario_dir = GOLDEN_ROOT / scenario_id
    if scenario.get("expects") == "FileNotFoundError":
        inputs = scenario_dir / "inputs"
        for rel in inputs.rglob("*"):
            if rel.is_file():
                target = tmp_path / rel.relative_to(inputs)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(rel, target)
        with pytest.raises(FileNotFoundError):
            run_market_gate(
                trade_date=_scenario_trade_date(scenario),
                artifact_root=tmp_path,
            )
        return

    inputs = scenario_dir / "inputs"
    for rel in inputs.rglob("*"):
        if rel.is_file():
            target = tmp_path / rel.relative_to(inputs)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(rel, target)

    trade_date = date.fromisoformat(
        str(load_meta(scenario_dir / "expected" / "meta.json")["trade_date"])
    )
    result = run_market_gate(trade_date=trade_date, artifact_root=tmp_path)
    expected_dir = scenario_dir / "expected" / "market_gate"
    compare_semantic_market_gate(result.stage_dir, expected_dir)

    if scenario_id == "catalyst_ignored":
        strict = json.loads(
            (result.stage_dir / "market_gate_summary.json").read_text(encoding="utf-8-sig")
        )
        baseline = json.loads(
            (
                GOLDEN_ROOT
                / "strict_pass_mixed"
                / "expected"
                / "market_gate"
                / "market_gate_summary.json"
            ).read_text(encoding="utf-8-sig")
        )
        assert strict["strict_count"] == baseline["strict_count"]

from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path

import pytest
import yaml
from indiciumforge_core.artifacts.comparator import GATE_ARTIFACTS
from indiciumforge_core.artifacts.manifest import (
    DAILY_REVIEW_REQUIRED_FILES,
    list_daily_review_stages,
    list_market_gate_stages,
    validate_daily_review_stage,
    validate_market_gate_stage,
)
from indiciumforge_workflow.market_awareness.runner import run_daily_review_skeleton

ROOT = Path(__file__).resolve().parents[2]
GOLDEN_ROOT = ROOT / "tests" / "golden" / "market_gate"
MANIFEST = ROOT / "GOLDEN_MANIFEST.yaml"
DEMO_FIXTURE = ROOT / "tests" / "fixtures" / "market_awareness" / "theme_sectors_demo.yaml"


def _scenarios() -> list[dict]:
    payload = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    return payload["scenarios"]


@pytest.mark.parametrize("scenario", _scenarios(), ids=lambda item: item["id"])
def test_golden_expected_dirs_pass_structural_audit(scenario: dict) -> None:
    if scenario.get("status") == "pending_export":
        pytest.skip("golden scenario pending export")
    if scenario.get("expects") == "FileNotFoundError":
        pytest.skip("scenario has no expected market_gate artifacts")

    stage_dir = GOLDEN_ROOT / scenario["id"] / "expected" / "market_gate"
    if not stage_dir.is_dir():
        pytest.skip("scenario has no expected market_gate directory")
    meta_path = GOLDEN_ROOT / scenario["id"] / "expected" / "meta.json"
    expected_trade_date = str(scenario["trade_date"])

    result = validate_market_gate_stage(
        stage_dir,
        expected_trade_date=expected_trade_date,
        meta_path=meta_path,
    )

    assert result.ok, result.violations


def test_missing_file_reports_violation(tmp_path: Path) -> None:
    source = GOLDEN_ROOT / "strict_pass_mixed" / "expected" / "market_gate"
    target = tmp_path / "market_gate"
    shutil.copytree(source, target)
    (target / "market_gate_summary.json").unlink()

    result = validate_market_gate_stage(target, expected_trade_date="2026-06-23")

    assert not result.ok
    assert any(v.code == "missing_file" for v in result.violations)


def test_schema_mismatch_reports_violation(tmp_path: Path) -> None:
    source = GOLDEN_ROOT / "strict_pass_mixed" / "expected" / "market_gate"
    target = tmp_path / "market_gate"
    shutil.copytree(source, target)

    summary_path = target / "market_gate_summary.json"
    payload = json.loads(summary_path.read_text(encoding="utf-8-sig"))
    payload["schema"] = "broken.schema.v0"
    summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8-sig")

    result = validate_market_gate_stage(target, expected_trade_date="2026-06-23")

    assert not result.ok
    assert any(v.code == "schema_mismatch" for v in result.violations)


def test_trade_date_mismatch_reports_violation(tmp_path: Path) -> None:
    source = GOLDEN_ROOT / "strict_pass_mixed" / "expected" / "market_gate"
    target = tmp_path / "market_gate"
    shutil.copytree(source, target)

    result = validate_market_gate_stage(target, expected_trade_date="2026-06-24")

    assert not result.ok
    assert any(v.code == "trade_date_mismatch" for v in result.violations)


def test_list_market_gate_stages_discovers_golden_layout(tmp_path: Path) -> None:
    source = GOLDEN_ROOT / "strict_pass_mixed" / "expected" / "market_gate"
    stage_dir = tmp_path / "workflows" / "20260623" / "market_gate"
    shutil.copytree(source, stage_dir)

    refs = list_market_gate_stages(tmp_path)

    assert len(refs) == 1
    assert refs[0].trade_date == "2026-06-23"
    assert refs[0].core_artifact_count == len(GATE_ARTIFACTS)


def test_validate_daily_review_stage_passes_after_skeleton_run(tmp_path: Path) -> None:
    run_daily_review_skeleton(
        trade_date=date(2026, 6, 23),
        artifact_root=tmp_path,
        fixture_path=DEMO_FIXTURE,
    )
    stage_dir = tmp_path / "market_awareness" / "20260623" / "daily_review"

    result = validate_daily_review_stage(stage_dir, expected_trade_date="2026-06-23")

    assert result.ok, result.violations


def test_daily_review_missing_file_reports_violation(tmp_path: Path) -> None:
    run_daily_review_skeleton(
        trade_date=date(2026, 6, 23),
        artifact_root=tmp_path,
        fixture_path=DEMO_FIXTURE,
    )
    stage_dir = tmp_path / "market_awareness" / "20260623" / "daily_review"
    (stage_dir / "market_daily_review_state.json").unlink()

    result = validate_daily_review_stage(stage_dir, expected_trade_date="2026-06-23")

    assert not result.ok
    assert any(v.code == "missing_file" for v in result.violations)


def test_daily_review_schema_mismatch_reports_violation(tmp_path: Path) -> None:
    run_daily_review_skeleton(
        trade_date=date(2026, 6, 23),
        artifact_root=tmp_path,
        fixture_path=DEMO_FIXTURE,
    )
    stage_dir = tmp_path / "market_awareness" / "20260623" / "daily_review"
    state_path = stage_dir / "market_daily_review_state.json"
    payload = json.loads(state_path.read_text(encoding="utf-8-sig"))
    payload["schema"] = "broken.schema.v0"
    state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8-sig")

    result = validate_daily_review_stage(stage_dir, expected_trade_date="2026-06-23")

    assert not result.ok
    assert any(v.code == "schema_mismatch" for v in result.violations)


def test_daily_review_csv_column_mismatch_reports_violation(tmp_path: Path) -> None:
    run_daily_review_skeleton(
        trade_date=date(2026, 6, 23),
        artifact_root=tmp_path,
        fixture_path=DEMO_FIXTURE,
    )
    stage_dir = tmp_path / "market_awareness" / "20260623" / "daily_review"
    ranking_path = stage_dir / "theme_state_ranking.csv"
    ranking_path.write_text("wrong,columns\n", encoding="utf-8-sig")

    result = validate_daily_review_stage(stage_dir, expected_trade_date="2026-06-23")

    assert not result.ok
    assert any(v.code == "csv_column_mismatch" for v in result.violations)


def test_list_daily_review_stages_discovers_layout(tmp_path: Path) -> None:
    run_daily_review_skeleton(
        trade_date=date(2026, 6, 23),
        artifact_root=tmp_path,
        fixture_path=DEMO_FIXTURE,
    )

    refs = list_daily_review_stages(tmp_path)

    assert len(refs) == 1
    assert refs[0].trade_date == "2026-06-23"
    assert refs[0].core_artifact_count == len(DAILY_REVIEW_REQUIRED_FILES)

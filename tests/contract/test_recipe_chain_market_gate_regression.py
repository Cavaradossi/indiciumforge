from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from lucerna_workflow.workflow_chain.runner import (
    WorkflowChainRecipeConfig,
    run_workflow_chain_recipe,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures"
RECIPE_PATH = FIXTURE_ROOT / "workflow" / "recipe_ashare_daily_v1.yaml"
EXTENSION_PACK = FIXTURE_ROOT / "recipe_extension_pack_demo.yaml"
DAILY_REVIEW_FIXTURE = FIXTURE_ROOT / "market_awareness" / "theme_sectors_demo.yaml"
BASELINE_SUMMARY = (
    ROOT
    / "tests"
    / "golden"
    / "market_gate"
    / "strict_pass_mixed"
    / "expected"
    / "market_gate"
    / "market_gate_summary.json"
)
TRADE_DATE = date(2026, 6, 23)


def test_recipe_chain_market_gate_strict_count_matches_baseline(tmp_path: Path) -> None:
    result = run_workflow_chain_recipe(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        config=WorkflowChainRecipeConfig(
            recipe_path=RECIPE_PATH,
            recipe_extension_pack=EXTENSION_PACK,
            daily_review_fixture=DAILY_REVIEW_FIXTURE,
        ),
    )

    baseline = json.loads(BASELINE_SUMMARY.read_text(encoding="utf-8-sig"))
    summary = json.loads(
        (result.market_gate_stage_dir / "market_gate_summary.json").read_text(encoding="utf-8-sig")
    )
    assert summary["strict_count"] == baseline["strict_count"]

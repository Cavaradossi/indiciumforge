from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from indiciumforge_core.artifacts.manifest import (
    validate_daily_review_stage,
    validate_market_gate_stage,
)
from indiciumforge_workflow.workflow_chain.runner import (
    WORKFLOW_CHAIN_SUMMARY_SCHEMA_V4,
    WorkflowChainRecipeConfig,
    run_workflow_chain_recipe,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures"
RECIPE_PATH = FIXTURE_ROOT / "workflow" / "recipe_ashare_daily_v1.yaml"
EXTENSION_PACK = FIXTURE_ROOT / "recipe_extension_pack_demo.yaml"
DAILY_REVIEW_FIXTURE = FIXTURE_ROOT / "market_awareness" / "theme_sectors_demo.yaml"
TRADE_DATE = date(2026, 6, 24)


def test_fake_ashare_recipe_chain_produces_auditable_artifacts(tmp_path: Path) -> None:
    result = run_workflow_chain_recipe(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        config=WorkflowChainRecipeConfig(
            recipe_path=RECIPE_PATH,
            recipe_extension_pack=EXTENSION_PACK,
            daily_review_fixture=DAILY_REVIEW_FIXTURE,
        ),
    )

    assert result.chain_ok
    assert result.recipe_id == "indiciumforge.recipe.ashare_daily_research.v1"
    assert result.extension_pack_id == "demo-recipe-extension-pack"
    assert (result.post_close_stage_dir / "candidate_pool_raw.json").is_file()
    assert (result.post_close_stage_dir / "buy_point_review_internal.csv").is_file()
    assert (result.post_close_stage_dir / "post_close_review_state.json").is_file()
    assert (result.preopen_stage_dir / "buy_point_review_internal.csv").is_file()
    assert (result.preopen_stage_dir / "preopen_review_state.json").is_file()

    daily_manifest = validate_daily_review_stage(
        result.daily_review_stage_dir,
        expected_trade_date=TRADE_DATE.isoformat(),
    )
    gate_manifest = validate_market_gate_stage(
        result.market_gate_stage_dir,
        expected_trade_date=TRADE_DATE.isoformat(),
    )
    assert daily_manifest.ok
    assert gate_manifest.ok

    summary = json.loads(result.summary_path.read_text(encoding="utf-8-sig"))
    assert summary["schema"] == WORKFLOW_CHAIN_SUMMARY_SCHEMA_V4
    assert summary["provenance"]["mode"] == "workflow_chain_recipe"

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from indiciumforge_core.recipes.models import RECIPE_RUN_SUMMARY_SCHEMA
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


def test_recipe_run_summary_and_chain_summary_v4(tmp_path: Path) -> None:
    result = run_workflow_chain_recipe(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        config=WorkflowChainRecipeConfig(
            recipe_path=RECIPE_PATH,
            recipe_extension_pack=EXTENSION_PACK,
            daily_review_fixture=DAILY_REVIEW_FIXTURE,
        ),
    )

    assert result.recipe_run_summary_path is not None
    recipe_summary = json.loads(result.recipe_run_summary_path.read_text(encoding="utf-8-sig"))
    assert recipe_summary["schema"] == RECIPE_RUN_SUMMARY_SCHEMA
    assert recipe_summary["recipe_id"] == "indiciumforge.recipe.ashare_daily_research.v1"
    assert "fake_ashare_recipe" in recipe_summary["extension_ids"]

    chain_summary = json.loads(result.summary_path.read_text(encoding="utf-8-sig"))
    assert chain_summary["schema"] == WORKFLOW_CHAIN_SUMMARY_SCHEMA_V4
    recipe_id = "indiciumforge.recipe.ashare_daily_research.v1"
    assert chain_summary["workflow_session"]["recipe_id"] == recipe_id
    assert chain_summary["provenance"]["extension_pack"]["pack_id"] == "demo-recipe-extension-pack"
    assert "discovery_post_close" in {
        stage["stage_id"] for stage in chain_summary["stages"].values()
    }

from __future__ import annotations

from pathlib import Path

import pytest
from lucerna_core.workflow.handoff import HandoffArtifactKind
from lucerna_core.workflow.model import (
    AssetDomain,
    RecipeStageKind,
    SessionModel,
)
from lucerna_core.workflow.recipe_schema import (
    RecipeSchemaError,
    load_workflow_recipe,
    parse_workflow_recipe_payload,
)

ROOT = Path(__file__).resolve().parents[2]
RECIPE_PATH = ROOT / "tests" / "fixtures" / "workflow" / "recipe_ashare_daily_v1.yaml"

IG_FOLDER_TO_STAGE_ID = {
    "daily_review": "awareness_daily_review",
    "factor_scan": "evidence_factor_scan",
    "post_close": "discovery_post_close",
    "preopen": "handoff_preopen",
    "midday": "refresh_midday_quotes",
    "market_gate": "gate_market_theme",
}


def test_load_ashare_recipe_fixture() -> None:
    recipe = load_workflow_recipe(RECIPE_PATH)

    assert recipe.recipe_id == "lucerna.recipe.ashare_daily_research.v1"
    assert recipe.asset_domain == AssetDomain.CHINA_A_SHARE
    assert recipe.session_model == SessionModel.CALENDAR_DAY_CYCLE
    assert len(recipe.stages) == 6


def test_ashare_recipe_maps_ig_folders() -> None:
    recipe = load_workflow_recipe(RECIPE_PATH)
    by_folder = {
        stage.ig_folder_name: stage.stage_id
        for stage in recipe.stages
        if stage.ig_folder_name
    }

    assert by_folder == IG_FOLDER_TO_STAGE_ID


def test_ashare_recipe_stage_kinds() -> None:
    recipe = load_workflow_recipe(RECIPE_PATH)
    by_id = {stage.stage_id: stage for stage in recipe.stages}

    assert by_id["discovery_post_close"].kind == RecipeStageKind.DISCOVERY
    assert by_id["handoff_preopen"].kind == RecipeStageKind.HANDOFF
    assert by_id["gate_market_theme"].kind == RecipeStageKind.GATE
    assert by_id["evidence_factor_scan"].optional is True


def test_ashare_recipe_handoff_artifacts() -> None:
    recipe = load_workflow_recipe(RECIPE_PATH)
    post_close = next(s for s in recipe.stages if s.stage_id == "discovery_post_close")

    assert HandoffArtifactKind.CANDIDATE_POOL_RAW in post_close.handoff_artifacts


def test_parse_workflow_recipe_rejects_invalid_schema() -> None:
    with pytest.raises(RecipeSchemaError, match="schema"):
        parse_workflow_recipe_payload({"schema": "broken", "recipe_id": "x", "version": "1"})


def test_parse_workflow_recipe_rejects_empty_stages() -> None:
    payload = {
        "schema": "lucerna.workflow_recipe.v1",
        "recipe_id": "test",
        "asset_domain": "china_a_share",
        "session_model": "calendar_day_cycle",
        "version": "1.0.0",
        "stages": [],
    }

    with pytest.raises(RecipeSchemaError, match="stages"):
        parse_workflow_recipe_payload(payload)

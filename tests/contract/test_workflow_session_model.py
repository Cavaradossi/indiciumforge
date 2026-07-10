from __future__ import annotations

from datetime import date

from indiciumforge_core.workflow.model import (
    AssetDomain,
    RecipeStageKind,
    SessionModel,
    WorkflowCheckpoint,
    WorkflowSessionMetadata,
    ashare_cycle_id,
)
from indiciumforge_core.workflow.recipe_schema import recipe_to_payload


def test_ashare_cycle_id_uses_trade_date_iso() -> None:
    assert ashare_cycle_id(date(2026, 6, 23)) == "2026-06-23"


def test_workflow_session_metadata_payload() -> None:
    meta = WorkflowSessionMetadata(
        recipe_id="indiciumforge.recipe.ashare_daily_research.v1",
        asset_domain=AssetDomain.CHINA_A_SHARE,
        session_model=SessionModel.CALENDAR_DAY_CYCLE,
        cycle_id="2026-06-23",
    )

    payload = meta.to_payload()

    assert payload["recipe_id"] == "indiciumforge.recipe.ashare_daily_research.v1"
    assert payload["asset_domain"] == "china_a_share"
    assert payload["session_model"] == "calendar_day_cycle"
    assert payload["cycle_id"] == "2026-06-23"


def test_workflow_checkpoint_frozen_fields() -> None:
    checkpoint = WorkflowCheckpoint(
        checkpoint_id="cp-001",
        recipe_id="indiciumforge.recipe.ashare_daily_research.v1",
        recipe_stage_id="discovery_post_close",
        asset_domain=AssetDomain.CHINA_A_SHARE,
        cycle_id="2026-06-23",
        as_of="2026-06-23",
        handoff_from=("awareness_daily_review",),
    )

    assert checkpoint.recipe_stage_id == "discovery_post_close"
    assert checkpoint.handoff_from == ("awareness_daily_review",)


def test_recipe_to_payload_includes_stage_kinds() -> None:
    from pathlib import Path

    from indiciumforge_core.workflow.recipe_schema import load_workflow_recipe

    root = Path(__file__).resolve().parents[2]
    recipe_path = root / "tests" / "fixtures" / "workflow" / "recipe_ashare_daily_v1.yaml"
    recipe = load_workflow_recipe(recipe_path)
    payload = recipe_to_payload(recipe)

    kinds = {stage["kind"] for stage in payload["stages"]}
    assert RecipeStageKind.DISCOVERY.value in kinds
    assert RecipeStageKind.HANDOFF.value in kinds
    assert RecipeStageKind.GATE.value in kinds

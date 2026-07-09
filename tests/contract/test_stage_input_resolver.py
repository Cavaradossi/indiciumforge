from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from lucerna_core.recipes.models import RecipeStageContext
from lucerna_core.recipes.resolver import StageInputResolver
from lucerna_core.workflow.handoff import HandoffArtifactKind
from lucerna_core.workflow.model import (
    AssetDomain,
    RecipeStageKind,
    RecipeStageSpec,
    SessionModel,
    WorkflowRecipe,
    WorkflowSessionMetadata,
)

TRADE_DATE = date(2026, 6, 23)


def _recipe() -> WorkflowRecipe:
    return WorkflowRecipe(
        recipe_id="lucerna.recipe.ashare_daily_research.v1",
        asset_domain=AssetDomain.CHINA_A_SHARE,
        session_model=SessionModel.CALENDAR_DAY_CYCLE,
        version="1.0.0",
        stages=(
            RecipeStageSpec(
                stage_id="discovery_post_close",
                kind=RecipeStageKind.DISCOVERY,
                ig_folder_name="post_close",
                handoff_artifacts=(
                    HandoffArtifactKind.CANDIDATE_POOL_RAW,
                    HandoffArtifactKind.BUY_POINT_REVIEW_INTERNAL,
                ),
            ),
            RecipeStageSpec(
                stage_id="handoff_preopen",
                kind=RecipeStageKind.HANDOFF,
                ig_folder_name="preopen",
                handoff_artifacts=(HandoffArtifactKind.BUY_POINT_REVIEW_INTERNAL,),
            ),
        ),
    )


def test_stage_input_resolver_maps_post_close_handoff(tmp_path: Path) -> None:
    resolver = StageInputResolver()
    post_close_dir = tmp_path / "workflows" / "20260623" / "post_close"
    post_close_dir.mkdir(parents=True)
    pool_path = post_close_dir / "candidate_pool_raw.json"
    pool_path.write_text("{}", encoding="utf-8")

    recipe = _recipe()
    preopen_stage = recipe.stages[1]
    session = WorkflowSessionMetadata(
        recipe_id=recipe.recipe_id,
        asset_domain=recipe.asset_domain,
        session_model=recipe.session_model,
        cycle_id=TRADE_DATE.isoformat(),
    )
    context = RecipeStageContext(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        recipe=recipe,
        stage=preopen_stage,
        session=session,
    )
    inputs = resolver.resolve_inputs(context)

    key = f"discovery_post_close:{HandoffArtifactKind.CANDIDATE_POOL_RAW.value}"
    assert inputs[key] == pool_path


def test_stage_input_resolver_require_input_raises(tmp_path: Path) -> None:
    resolver = StageInputResolver()
    with pytest.raises(FileNotFoundError, match="missing handoff input"):
        resolver.require_input(
            {},
            stage_id="discovery_post_close",
            kind=HandoffArtifactKind.CANDIDATE_POOL_RAW,
        )

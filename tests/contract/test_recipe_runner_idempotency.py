from __future__ import annotations

from datetime import date
from pathlib import Path

from indiciumforge_core.recipes.models import StageRunResult
from indiciumforge_core.recipes.runner import RecipeRunner
from indiciumforge_core.storage import SQLiteMetadataStore
from indiciumforge_core.workflow.model import (
    AssetDomain,
    RecipeStageKind,
    RecipeStageSpec,
    SessionModel,
    WorkflowRecipe,
)


def _handler(context) -> StageRunResult:
    # Deterministic: identical inputs always yield identical output state, which
    # is exactly what the idempotency seam relies on.
    return StageRunResult(
        stage_id=context.stage.stage_id,
        stage_dir=Path("."),
        artifacts=("marker.json",),
        warnings=(),
        audit_ok=True,
    )


def _recipe() -> WorkflowRecipe:
    return WorkflowRecipe(
        recipe_id="test.idempotent.v1",
        asset_domain=AssetDomain.CHINA_A_SHARE,
        session_model=SessionModel.CALENDAR_DAY_CYCLE,
        version="1",
        stages=(
            RecipeStageSpec(
                stage_id="s1",
                kind=RecipeStageKind.EVIDENCE,
                ig_folder_name="daily_review",
            ),
            RecipeStageSpec(
                stage_id="s2",
                kind=RecipeStageKind.EVIDENCE,
                ig_folder_name="factor_scan",
            ),
        ),
        cycle_fn_id="ashare",
    )


def test_first_run_executes_all_stages(tmp_path: Path) -> None:
    store = SQLiteMetadataStore(tmp_path / "meta.db")
    runner = RecipeRunner(stage_handlers={"s1": _handler, "s2": _handler})
    recipe = _recipe()
    trade_date = date(2026, 6, 23)

    result = runner.run(
        trade_date=trade_date,
        artifact_root=tmp_path,
        recipe=recipe,
        metadata_store=store,
    )

    assert len(result.stage_results) == 2
    # No skip warnings on the first execution.
    assert not any("skipped (idempotent hit)" in w for w in result.warnings)
    # Stage records were persisted for both stages.
    for stage_id in ("s1", "s2"):
        rec = store.find_stage_by_input_hash(
            recipe_id=recipe.recipe_id,
            stage_id=stage_id,
            trade_date=trade_date.isoformat(),
            input_descriptor_hash=__descriptor(recipe, stage_id, trade_date),
        )
        assert rec is not None, f"missing stage record for {stage_id}"


def test_second_identical_run_skips_stages(tmp_path: Path) -> None:
    store = SQLiteMetadataStore(tmp_path / "meta.db")
    runner = RecipeRunner(stage_handlers={"s1": _handler, "s2": _handler})
    recipe = _recipe()
    trade_date = date(2026, 6, 23)

    runner.run(
        trade_date=trade_date,
        artifact_root=tmp_path,
        recipe=recipe,
        metadata_store=store,
    )
    result = runner.run(
        trade_date=trade_date,
        artifact_root=tmp_path,
        recipe=recipe,
        metadata_store=store,
    )

    # Every stage must be skipped via the idempotency seam.
    skip_warnings = [w for w in result.warnings if "skipped (idempotent hit)" in w]
    assert len(skip_warnings) == 2

    # The re-used results are equivalent to a fresh execution.
    assert [r.stage_id for r in result.stage_results] == ["s1", "s2"]
    assert result.stage_results[0].artifacts == ("marker.json",)
    assert result.stage_results[0].audit_ok is True


def __descriptor(recipe: WorkflowRecipe, stage_id: str, trade_date: date) -> str:
    from indiciumforge_core.run_id import input_descriptor_hash

    return input_descriptor_hash(
        recipe_id=recipe.recipe_id,
        stage_id=stage_id,
        trade_date=trade_date,
        inputs={},
        options={},
    )

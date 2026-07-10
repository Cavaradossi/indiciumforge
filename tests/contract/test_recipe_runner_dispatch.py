from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from indiciumforge_core.recipes.models import StageRunResult
from indiciumforge_core.recipes.pack import load_recipe_extension_pack
from indiciumforge_core.recipes.runner import RecipeRunError, RecipeRunner
from indiciumforge_core.workflow.recipe_schema import load_workflow_recipe

ROOT = Path(__file__).resolve().parents[2]
RECIPE_PATH = ROOT / "tests" / "fixtures" / "workflow" / "recipe_ashare_daily_v1.yaml"
EXTENSION_PACK = ROOT / "tests" / "fixtures" / "recipe_extension_pack_demo.yaml"
DAILY_REVIEW_FIXTURE = ROOT / "tests" / "fixtures" / "market_awareness" / "theme_sectors_demo.yaml"
TRADE_DATE = date(2026, 6, 23)


def _minimal_handlers() -> dict[str, object]:
    def noop(context) -> StageRunResult:  # noqa: ANN001
        return StageRunResult(
            stage_id=context.stage.stage_id,
            stage_dir=Path("."),
            warnings=("noop",),
            audit_ok=True,
        )

    return {
        "awareness_daily_review": noop,
        "evidence_factor_scan": noop,
        "gate_market_theme": noop,
    }


def test_recipe_runner_dispatches_extension_stages(tmp_path: Path) -> None:
    pack = load_recipe_extension_pack(pack_config=EXTENSION_PACK)
    runner = RecipeRunner(
        extensions=pack.extensions,
        stage_handlers=_minimal_handlers(),
    )
    recipe = load_workflow_recipe(RECIPE_PATH)
    result = runner.run(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        recipe=recipe,
        options={"daily_review_fixture": DAILY_REVIEW_FIXTURE},
    )

    stage_ids = {item.stage_id for item in result.stage_results}
    assert "discovery_post_close" in stage_ids
    assert "handoff_preopen" in stage_ids
    assert result.extension_id == "fake_ashare_recipe"


def test_recipe_runner_skips_optional_refresh_stage(tmp_path: Path) -> None:
    pack = load_recipe_extension_pack(pack_config=EXTENSION_PACK)
    runner = RecipeRunner(
        extensions=pack.extensions,
        stage_handlers=_minimal_handlers(),
    )
    recipe = load_workflow_recipe(RECIPE_PATH)
    result = runner.run(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        recipe=recipe,
        options={"daily_review_fixture": DAILY_REVIEW_FIXTURE},
    )

    refresh = next(
        item for item in result.stage_results if item.stage_id == "refresh_midday_quotes"
    )
    assert refresh.empty_result_reason == "optional_stage_skipped"


def test_recipe_runner_requires_handler_for_required_stage(tmp_path: Path) -> None:
    pack = load_recipe_extension_pack(pack_config=EXTENSION_PACK)
    runner = RecipeRunner(extensions=pack.extensions, stage_handlers={})
    recipe = load_workflow_recipe(RECIPE_PATH)

    with pytest.raises(RecipeRunError, match="awareness_daily_review"):
        runner.run(
            trade_date=TRADE_DATE,
            artifact_root=tmp_path,
            recipe=recipe,
        )

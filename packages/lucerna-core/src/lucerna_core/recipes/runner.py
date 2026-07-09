from __future__ import annotations

import json
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

from lucerna_core.artifacts.paths import workflow_root
from lucerna_core.recipes.models import (
    RECIPE_RUN_SUMMARY_SCHEMA,
    RECIPE_STAGE_STATE_SCHEMA,
    RecipeRunResult,
    RecipeStageContext,
    StageRunResult,
)
from lucerna_core.recipes.ports import PrivateRecipeExtensionPort
from lucerna_core.recipes.resolver import StageInputResolver
from lucerna_core.workflow.model import (
    WorkflowRecipe,
    WorkflowSessionMetadata,
    ashare_cycle_id,
)

StageHandler = Callable[[RecipeStageContext], StageRunResult]


class RecipeRunError(ValueError):
    """Raised when a recipe stage cannot be executed."""


class RecipeRunner:
    """Dispatch recipe stages to private extensions or registered open-core handlers."""

    def __init__(
        self,
        *,
        extensions: tuple[PrivateRecipeExtensionPort, ...] = (),
        stage_handlers: dict[str, StageHandler] | None = None,
        resolver: StageInputResolver | None = None,
    ) -> None:
        self._extensions = extensions
        self._stage_handlers = stage_handlers or {}
        self._resolver = resolver or StageInputResolver()

    def find_extension(
        self,
        recipe_id: str,
        stage_id: str,
    ) -> PrivateRecipeExtensionPort | None:
        for extension in self._extensions:
            if extension.supports_stage(recipe_id, stage_id):
                return extension
        return None

    def run(
        self,
        *,
        trade_date: date,
        artifact_root: Path,
        recipe: WorkflowRecipe,
        options: dict[str, Any] | None = None,
    ) -> RecipeRunResult:
        options = options or {}
        warnings: list[str] = []
        stage_results: list[StageRunResult] = []
        extension_ids: set[str] = set()

        session = WorkflowSessionMetadata(
            recipe_id=recipe.recipe_id,
            asset_domain=recipe.asset_domain,
            session_model=recipe.session_model,
            cycle_id=ashare_cycle_id(trade_date),
        )

        for stage in recipe.stages:
            stage_dir = self._resolver.stage_dir(artifact_root, trade_date, stage)
            inputs = self._resolver.resolve_inputs(
                RecipeStageContext(
                    trade_date=trade_date,
                    artifact_root=artifact_root,
                    recipe=recipe,
                    stage=stage,
                    session=session,
                    options=options,
                )
            )
            context = RecipeStageContext(
                trade_date=trade_date,
                artifact_root=artifact_root,
                recipe=recipe,
                stage=stage,
                session=session,
                inputs=inputs,
                options=options,
            )

            extension = self.find_extension(recipe.recipe_id, stage.stage_id)
            if extension is not None:
                result = extension.execute_stage(context)
                extension_ids.add(extension.extension_id)
            elif stage.stage_id in self._stage_handlers:
                result = self._stage_handlers[stage.stage_id](context)
            elif stage.optional:
                result = StageRunResult(
                    stage_id=stage.stage_id,
                    stage_dir=stage_dir,
                    warnings=(f"skipped optional stage {stage.stage_id}",),
                    empty_result_reason="optional_stage_skipped",
                )
            else:
                raise RecipeRunError(
                    f"no handler or extension for required stage {stage.stage_id!r}"
                )

            stage_results.append(result)
            warnings.extend(result.warnings)
            self._write_stage_state(stage_dir, result)

        summary_path = workflow_root(artifact_root, trade_date) / "recipe_run_summary.json"
        self._write_run_summary(
            summary_path,
            trade_date=trade_date,
            recipe=recipe,
            session=session,
            stage_results=tuple(stage_results),
            extension_ids=tuple(sorted(extension_ids)),
            options=options,
            warnings=warnings,
        )

        chain_ok = all(result.audit_ok is not False for result in stage_results)

        return RecipeRunResult(
            trade_date=trade_date,
            recipe_id=recipe.recipe_id,
            extension_id=next(iter(extension_ids), None),
            stage_results=tuple(stage_results),
            summary_path=summary_path,
            warnings=tuple(warnings),
            chain_ok=chain_ok,
        )

    def _write_stage_state(self, stage_dir: Path, result: StageRunResult) -> None:
        stage_dir.mkdir(parents=True, exist_ok=True)
        path = stage_dir / "recipe_stage_state.json"
        path.write_text(
            json.dumps(result.to_payload(), ensure_ascii=False, indent=2),
            encoding="utf-8-sig",
        )

    def _write_run_summary(
        self,
        path: Path,
        *,
        trade_date: date,
        recipe: WorkflowRecipe,
        session: WorkflowSessionMetadata,
        stage_results: tuple[StageRunResult, ...],
        extension_ids: tuple[str, ...],
        options: dict[str, Any],
        warnings: list[str],
    ) -> None:
        payload: dict[str, Any] = {
            "schema": RECIPE_RUN_SUMMARY_SCHEMA,
            "trade_date": trade_date.isoformat(),
            "recipe_id": recipe.recipe_id,
            "recipe_version": recipe.version,
            "workflow_session": session.to_payload(),
            "extension_ids": list(extension_ids),
            "stages": {
                result.stage_id: {
                    "schema": RECIPE_STAGE_STATE_SCHEMA,
                    "stage_dir": str(result.stage_dir),
                    "artifacts": list(result.artifacts),
                    "audit_ok": result.audit_ok,
                    "empty_result_reason": result.empty_result_reason,
                    "warnings": list(result.warnings),
                }
                for result in stage_results
            },
            "provenance": {
                "mode": "recipe_runner",
                "options": {
                    key: str(value)
                    for key, value in options.items()
                    if isinstance(value, (str, Path))
                },
            },
            "warnings": warnings,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8-sig")

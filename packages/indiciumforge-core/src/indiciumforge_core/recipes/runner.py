from __future__ import annotations

import json
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

from indiciumforge_core.artifacts.paths import workflow_root
from indiciumforge_core.clock import utc_now_iso
from indiciumforge_core.recipes.models import (
    RECIPE_RUN_SUMMARY_SCHEMA,
    RECIPE_STAGE_STATE_SCHEMA,
    RecipeRunResult,
    RecipeStageContext,
    StageRunResult,
)
from indiciumforge_core.recipes.ports import PrivateRecipeExtensionPort
from indiciumforge_core.recipes.resolver import StageInputResolver
from indiciumforge_core.run_id import (
    DEFAULT_RUN_ID,
    content_hash,
    input_descriptor_hash,
    mint_run_id,
)
from indiciumforge_core.ports.storage import MetadataStore, RunRecord, StageRecord
from indiciumforge_core.workflow.model import (
    WorkflowRecipe,
    WorkflowSessionMetadata,
    resolve_cycle_id_fn,
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
        metadata_store: MetadataStore | None = None,
    ) -> RecipeRunResult:
        options = options or {}
        warnings: list[str] = []
        stage_results: list[StageRunResult] = []
        extension_ids: set[str] = set()

        # W3: mint a stable run identity. A caller-supplied run_id wins; an
        # "isolate_run" option mints a fresh one; otherwise the legacy default
        # (flat, shared) namespace is used so behavior is unchanged.
        run_id = options.get("run_id") or (
            mint_run_id() if options.get("isolate_run") else DEFAULT_RUN_ID
        )

        session = WorkflowSessionMetadata(
            recipe_id=recipe.recipe_id,
            asset_domain=recipe.asset_domain,
            session_model=recipe.session_model,
            cycle_id=resolve_cycle_id_fn(recipe.cycle_fn_id)(trade_date),
        )

        if metadata_store is not None:
            metadata_store.record_run(
                RunRecord(
                    run_id=run_id,
                    recipe_id=recipe.recipe_id,
                    asset_domain=str(recipe.asset_domain),
                    session_model=str(session.session_model),
                    cycle_id=session.cycle_id,
                    trade_date=trade_date.isoformat(),
                    started_at=utc_now_iso(),
                    status="ok",
                    meta={"options": {k: str(v) for k, v in options.items()}},
                )
            )

        for stage in recipe.stages:
            stage_dir = self._resolver.stage_dir(
                artifact_root, trade_date, stage, run_id=run_id
            )
            inputs = self._resolver.resolve_inputs(
                RecipeStageContext(
                    trade_date=trade_date,
                    artifact_root=artifact_root,
                    recipe=recipe,
                    stage=stage,
                    session=session,
                    options=options,
                    run_id=run_id,
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
                run_id=run_id,
            )

            result = self._maybe_skip_or_dispatch(
                stage=stage,
                stage_dir=stage_dir,
                context=context,
                options=options,
                metadata_store=metadata_store,
                warnings=warnings,
                extension_ids=extension_ids,
            )

            stage_results.append(result)
            warnings.extend(result.warnings)
            self._write_stage_state(stage_dir, result)

            if metadata_store is not None:
                metadata_store.record_stage(
                    StageRecord(
                        stage_id=stage.stage_id,
                        run_id=run_id,
                        recipe_id=recipe.recipe_id,
                        trade_date=trade_date.isoformat(),
                        status="ok",
                        input_descriptor_hash=self._descriptor(
                            recipe, stage, trade_date, inputs, options
                        ),
                        output_content_hash=content_hash(result.to_payload()),
                        provider_id=result.extra.get("provider_id"),
                        warnings=result.warnings,
                        extra={},
                    )
                )

        summary_path = workflow_root(artifact_root, trade_date, run_id) / "recipe_run_summary.json"
        self._write_run_summary(
            summary_path,
            run_id=run_id,
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

    def _descriptor(
        self,
        recipe: WorkflowRecipe,
        stage: Any,
        trade_date: date,
        inputs: dict[str, Path],
        options: dict[str, Any],
    ) -> str:
        return input_descriptor_hash(
            recipe_id=recipe.recipe_id,
            stage_id=stage.stage_id,
            trade_date=trade_date,
            inputs=inputs,
            options=options,
        )

    def _maybe_skip_or_dispatch(
        self,
        *,
        stage: Any,
        stage_dir: Path,
        context: RecipeStageContext,
        options: dict[str, Any],
        metadata_store: MetadataStore | None,
        warnings: list[str],
        extension_ids: set[str],
    ) -> StageRunResult:
        # W3 idempotency: if a prior stage with identical inputs already ran
        # and its on-disk output is still intact, reuse the prior result
        # instead of re-executing (skip = no side effects, deterministic).
        if metadata_store is not None:
            descriptor = self._descriptor(
                context.recipe, stage, context.trade_date, context.inputs, options
            )
            prior = metadata_store.find_stage_by_input_hash(
                recipe_id=context.recipe.recipe_id,
                stage_id=stage.stage_id,
                trade_date=context.trade_date.isoformat(),
                input_descriptor_hash=descriptor,
            )
            if prior is not None and self._output_intact(stage_dir, prior.output_content_hash):
                state_path = stage_dir / "recipe_stage_state.json"
                try:
                    prior_payload = json.loads(
                        state_path.read_text(encoding="utf-8-sig")
                    )
                    warnings.append(
                        f"stage {stage.stage_id}: skipped (idempotent hit)"
                    )
                    return StageRunResult.from_payload(prior_payload)
                except (FileNotFoundError, json.JSONDecodeError):
                    pass  # fall through to (re)execution

        return self._dispatch(stage, stage_dir, context, warnings, extension_ids)

    @staticmethod
    def _output_intact(stage_dir: Path, prior_output_hash: str) -> bool:
        state_path = stage_dir / "recipe_stage_state.json"
        if not state_path.is_file():
            return False
        try:
            payload = json.loads(state_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            return False
        return content_hash(payload) == prior_output_hash

    def _dispatch(
        self,
        stage: Any,
        stage_dir: Path,
        context: RecipeStageContext,
        warnings: list[str],
        extension_ids: set[str],
    ) -> StageRunResult:
        extension = self.find_extension(context.recipe.recipe_id, stage.stage_id)
        if extension is not None:
            result = extension.execute_stage(context)
            extension_ids.add(extension.extension_id)
            result = self._attach_provider(result, extension.extension_id)
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
        return result

    @staticmethod
    def _attach_provider(result: StageRunResult, provider_id: str) -> StageRunResult:
        # Record which extension produced the stage so StageRecord.provider_id
        # is meaningful for idempotency / lineage.
        extra = dict(result.extra)
        extra["provider_id"] = provider_id
        return StageRunResult(
            stage_id=result.stage_id,
            stage_dir=result.stage_dir,
            artifacts=result.artifacts,
            warnings=result.warnings,
            empty_result_reason=result.empty_result_reason,
            audit_ok=result.audit_ok,
            extra=extra,
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
        run_id: str,
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
            "run_id": run_id,
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

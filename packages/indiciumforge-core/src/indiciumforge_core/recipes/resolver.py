from __future__ import annotations

from datetime import date
from pathlib import Path

from indiciumforge_core.artifacts.paths import (
    daily_review_dir,
    factor_scan_dir,
    market_gate_stage_dir,
    post_close_review_dir,
    preopen_review_dir,
    workflow_root,
)
from indiciumforge_core.recipes.models import RecipeStageContext
from indiciumforge_core.workflow.handoff import HANDOFF_ARTIFACT_FILE_HINTS, HandoffArtifactKind
from indiciumforge_core.workflow.model import RecipeStageKind, RecipeStageSpec


class StageInputResolver:
    """Resolve handoff artifact paths for a recipe stage."""

    def stage_dir(
        self,
        artifact_root: Path,
        trade_date: date,
        stage: RecipeStageSpec,
        run_id: str = "default",
    ) -> Path:
        folder = stage.ig_folder_name or stage.stage_id
        if folder == "daily_review":
            return daily_review_dir(artifact_root, trade_date, run_id)
        if folder == "factor_scan":
            return factor_scan_dir(artifact_root, trade_date, run_id)
        if folder == "market_gate":
            return market_gate_stage_dir(artifact_root, trade_date, run_id)
        if folder == "post_close":
            return post_close_review_dir(artifact_root, trade_date, run_id)
        if folder == "preopen":
            return preopen_review_dir(artifact_root, trade_date, run_id)
        return workflow_root(artifact_root, trade_date, run_id) / folder

    def resolve_handoff_path(
        self,
        artifact_root: Path,
        trade_date: date,
        *,
        ig_folder: str,
        kind: HandoffArtifactKind,
        run_id: str = "default",
    ) -> Path:
        if kind == HandoffArtifactKind.THEME_STATE_RANKING:
            return (
                daily_review_dir(artifact_root, trade_date, run_id)
                / HANDOFF_ARTIFACT_FILE_HINTS[kind]
            )
        stage = RecipeStageSpec(
            stage_id=ig_folder,
            kind=RecipeStageKind.EVIDENCE,
            ig_folder_name=ig_folder,
        )
        base = self.stage_dir(artifact_root, trade_date, stage, run_id)
        hint = HANDOFF_ARTIFACT_FILE_HINTS[kind]
        if "{date}" in hint:
            hint = hint.replace("{date}", trade_date.isoformat())
        return base / hint

    def resolve_inputs(self, context: RecipeStageContext) -> dict[str, Path]:
        inputs: dict[str, Path] = {}
        recipe = context.recipe
        for prior in recipe.stages:
            if prior.stage_id == context.stage.stage_id:
                break
            if not prior.handoff_artifacts or not prior.ig_folder_name:
                continue
            folder = prior.ig_folder_name
            for kind in prior.handoff_artifacts:
                path = self.resolve_handoff_path(
                    context.artifact_root,
                    context.trade_date,
                    ig_folder=folder,
                    kind=kind,
                    run_id=context.run_id,
                )
                inputs[f"{prior.stage_id}:{kind.value}"] = path
        return inputs

    def require_input(
        self,
        inputs: dict[str, Path],
        *,
        stage_id: str,
        kind: HandoffArtifactKind,
    ) -> Path:
        key = f"{stage_id}:{kind.value}"
        path = inputs.get(key)
        if path is None or not path.is_file():
            raise FileNotFoundError(f"missing handoff input {key}: {path}")
        return path

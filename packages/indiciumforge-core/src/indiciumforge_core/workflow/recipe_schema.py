from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from indiciumforge_core.schema_compat import accepts_schema
from indiciumforge_core.workflow.handoff import HandoffArtifactKind
from indiciumforge_core.workflow.model import (
    WORKFLOW_RECIPE_SCHEMA,
    AssetDomain,
    RecipeStageKind,
    RecipeStageSpec,
    SessionModel,
    WorkflowRecipe,
)


class RecipeSchemaError(ValueError):
    """Raised when a workflow recipe document is invalid."""


def _parse_handoff_artifacts(values: Any) -> tuple[HandoffArtifactKind, ...]:
    if not isinstance(values, list):
        raise RecipeSchemaError("handoff_artifacts must be a list")
    parsed: list[HandoffArtifactKind] = []
    for item in values:
        try:
            parsed.append(HandoffArtifactKind(str(item)))
        except ValueError as exc:
            raise RecipeSchemaError(f"unknown handoff artifact kind: {item}") from exc
    return tuple(parsed)


def _parse_stage(entry: dict[str, Any]) -> RecipeStageSpec:
    stage_id = entry.get("stage_id")
    if not stage_id:
        raise RecipeSchemaError("recipe stage requires stage_id")
    kind_raw = entry.get("kind")
    if not kind_raw:
        raise RecipeSchemaError(f"recipe stage {stage_id!r} requires kind")
    try:
        kind = RecipeStageKind(str(kind_raw))
    except ValueError as exc:
        raise RecipeSchemaError(f"unknown recipe stage kind: {kind_raw}") from exc
    ig_folder = entry.get("ig_folder_name")
    handoffs = _parse_handoff_artifacts(entry.get("handoff_artifacts", []))
    optional = bool(entry.get("optional", False))
    return RecipeStageSpec(
        stage_id=str(stage_id),
        kind=kind,
        ig_folder_name=str(ig_folder) if ig_folder else None,
        handoff_artifacts=handoffs,
        optional=optional,
    )


def parse_workflow_recipe_payload(payload: dict[str, Any]) -> WorkflowRecipe:
    schema = payload.get("schema")
    if not accepts_schema(schema, WORKFLOW_RECIPE_SCHEMA, context="workflow recipe"):
        raise RecipeSchemaError(
            f"expected schema {WORKFLOW_RECIPE_SCHEMA!r}, got {schema!r}"
        )
    recipe_id = payload.get("recipe_id")
    if not recipe_id:
        raise RecipeSchemaError("recipe requires recipe_id")
    version = payload.get("version")
    if not version:
        raise RecipeSchemaError("recipe requires version")
    try:
        asset_domain = AssetDomain(str(payload.get("asset_domain")))
    except ValueError as exc:
        raise RecipeSchemaError(
            f"unknown asset_domain: {payload.get('asset_domain')!r}"
        ) from exc
    try:
        session_model = SessionModel(str(payload.get("session_model")))
    except ValueError as exc:
        raise RecipeSchemaError(
            f"unknown session_model: {payload.get('session_model')!r}"
        ) from exc
    raw_stages = payload.get("stages")
    if not isinstance(raw_stages, list) or not raw_stages:
        raise RecipeSchemaError("recipe requires non-empty stages list")
    stages = tuple(_parse_stage(entry) for entry in raw_stages if isinstance(entry, dict))
    if not stages:
        raise RecipeSchemaError("recipe stages must be mappings")
    return WorkflowRecipe(
        recipe_id=str(recipe_id),
        asset_domain=asset_domain,
        session_model=session_model,
        version=str(version),
        stages=stages,
        cycle_fn_id=str(payload.get("cycle_fn_id", "ashare")),
    )


def load_workflow_recipe(path: Path) -> WorkflowRecipe:
    if not path.is_file():
        raise RecipeSchemaError(f"recipe file not found: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RecipeSchemaError("recipe root must be a mapping")
    return parse_workflow_recipe_payload(payload)


def recipe_to_payload(recipe: WorkflowRecipe) -> dict[str, Any]:
    return {
        "schema": recipe.schema,
        "recipe_id": recipe.recipe_id,
        "asset_domain": recipe.asset_domain.value,
        "session_model": recipe.session_model.value,
        "version": recipe.version,
        "cycle_fn_id": recipe.cycle_fn_id,
        "stages": [
            {
                "stage_id": stage.stage_id,
                "kind": stage.kind.value,
                "ig_folder_name": stage.ig_folder_name,
                "handoff_artifacts": [item.value for item in stage.handoff_artifacts],
                "optional": stage.optional,
            }
            for stage in recipe.stages
        ],
    }

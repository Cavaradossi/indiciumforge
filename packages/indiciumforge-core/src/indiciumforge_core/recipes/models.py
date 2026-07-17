from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from indiciumforge_core.workflow.model import (
    RecipeStageSpec,
    WorkflowRecipe,
    WorkflowSessionMetadata,
)

RECIPE_RUN_SUMMARY_SCHEMA = "indiciumforge.recipe_run_summary.v1"
RECIPE_STAGE_STATE_SCHEMA = "indiciumforge.recipe_stage_state.v1"


@dataclass(frozen=True)
class RecipeStageContext:
    trade_date: date
    artifact_root: Path
    recipe: WorkflowRecipe
    stage: RecipeStageSpec
    session: WorkflowSessionMetadata
    inputs: dict[str, Path] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)
    run_id: str = "default"


@dataclass(frozen=True)
class StageRunResult:
    stage_id: str
    stage_dir: Path
    artifacts: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    empty_result_reason: str | None = None
    audit_ok: bool | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema": RECIPE_STAGE_STATE_SCHEMA,
            "stage_id": self.stage_id,
            "stage_dir": str(self.stage_dir),
            "artifacts": list(self.artifacts),
            "warnings": list(self.warnings),
        }
        if self.empty_result_reason is not None:
            payload["empty_result_reason"] = self.empty_result_reason
        if self.audit_ok is not None:
            payload["audit_ok"] = self.audit_ok
        if self.extra:
            payload["extra"] = self.extra
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "StageRunResult":
        return cls(
            stage_id=payload["stage_id"],
            stage_dir=Path(payload["stage_dir"]),
            artifacts=tuple(payload.get("artifacts", [])),
            warnings=tuple(payload.get("warnings", [])),
            empty_result_reason=payload.get("empty_result_reason"),
            audit_ok=payload.get("audit_ok"),
            extra=payload.get("extra", {}),
        )


@dataclass(frozen=True)
class RecipeRunResult:
    trade_date: date
    recipe_id: str
    extension_id: str | None
    stage_results: tuple[StageRunResult, ...]
    summary_path: Path
    warnings: tuple[str, ...] = ()
    chain_ok: bool = False

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any, Protocol

from lucerna_core.workflow.handoff import HandoffArtifactKind


class AssetDomain(str, Enum):
    CHINA_A_SHARE = "china_a_share"
    HK_EQUITY = "hk_equity"
    US_EQUITY = "us_equity"
    CRYPTO_SPOT = "crypto_spot"
    CRYPTO_PERP = "crypto_perp"
    RATES_FUTURES = "rates_futures"


class SessionModel(str, Enum):
    CALENDAR_DAY_CYCLE = "calendar_day_cycle"
    EXCHANGE_SESSION_HANDOFF = "exchange_session_handoff"
    ROLLING_24X7 = "rolling_24x7"


class RecipeStageKind(str, Enum):
    EVIDENCE = "evidence"
    DISCOVERY = "discovery"
    HANDOFF = "handoff"
    REFRESH = "refresh"
    GATE = "gate"
    RISK_REVIEW = "risk_review"


WORKFLOW_RECIPE_SCHEMA = "lucerna.workflow_recipe.v1"
WORKFLOW_CHECKPOINT_SCHEMA = "lucerna.workflow_checkpoint.v1"
EVIDENCE_STAGE_REF_SCHEMA = "lucerna.evidence_stage_ref.v1"

DEFAULT_ASHARE_RECIPE_ID = "lucerna.recipe.ashare_daily_research.v1"


@dataclass(frozen=True)
class RecipeStageSpec:
    stage_id: str
    kind: RecipeStageKind
    ig_folder_name: str | None = None
    handoff_artifacts: tuple[HandoffArtifactKind, ...] = ()
    optional: bool = False


@dataclass(frozen=True)
class WorkflowRecipe:
    recipe_id: str
    asset_domain: AssetDomain
    session_model: SessionModel
    version: str
    stages: tuple[RecipeStageSpec, ...]
    schema: str = WORKFLOW_RECIPE_SCHEMA


@dataclass(frozen=True)
class WorkflowCheckpoint:
    checkpoint_id: str
    recipe_id: str
    recipe_stage_id: str
    asset_domain: AssetDomain
    cycle_id: str
    as_of: str
    handoff_from: tuple[str, ...] = ()
    schema: str = WORKFLOW_CHECKPOINT_SCHEMA


@dataclass(frozen=True)
class EvidenceStageRef:
    recipe_stage_id: str
    stage_dir: str
    schema_ids: tuple[str, ...] = ()
    schema: str = EVIDENCE_STAGE_REF_SCHEMA


@dataclass(frozen=True)
class WorkflowSessionMetadata:
    recipe_id: str
    asset_domain: AssetDomain
    session_model: SessionModel
    cycle_id: str

    def to_payload(self) -> dict[str, str]:
        return {
            "recipe_id": self.recipe_id,
            "asset_domain": self.asset_domain.value,
            "session_model": self.session_model.value,
            "cycle_id": self.cycle_id,
        }


def ashare_cycle_id(trade_date: date) -> str:
    """A-share recipe uses trade_date ISO string as cycle_id for IG folder compatibility."""
    return trade_date.isoformat()


class MarketCalendarPort(Protocol):
    """Contract-only port for v0.9+; v0.8 defines the interface shape only."""

    def resolve_cycle_id(self, asset_domain: AssetDomain, as_of: date) -> str: ...

    def next_checkpoint_window(
        self,
        asset_domain: AssetDomain,
        recipe_stage_id: str,
        as_of: date,
    ) -> dict[str, Any]: ...

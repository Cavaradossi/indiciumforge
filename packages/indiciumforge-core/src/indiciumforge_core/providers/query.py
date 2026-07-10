from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from indiciumforge_core.domain.models import AssetID
from indiciumforge_core.providers.capabilities import DataKind
from indiciumforge_core.workflow.model import (
    AssetDomain,
    SessionModel,
    WorkflowCheckpoint,
    WorkflowSessionMetadata,
)


@dataclass(frozen=True)
class DataQuery:
    asset: AssetID
    asset_domain: AssetDomain
    data_kind: DataKind
    as_of: date | None = None
    start: date | None = None
    end: date | None = None
    session_model: SessionModel | None = None
    checkpoint_id: str | None = None
    cycle_id: str | None = None
    recipe_id: str | None = None
    calendar_id: str | None = None
    venue: str | None = None
    frequency: str | None = None
    adjustment_policy: str | None = None

    @classmethod
    def from_session(
        cls,
        *,
        asset: AssetID,
        data_kind: DataKind,
        session: WorkflowSessionMetadata,
        as_of: date | None = None,
        start: date | None = None,
        end: date | None = None,
        checkpoint_id: str | None = None,
        venue: str | None = None,
        frequency: str | None = None,
        adjustment_policy: str | None = None,
    ) -> DataQuery:
        return cls(
            asset=asset,
            asset_domain=session.asset_domain,
            data_kind=data_kind,
            as_of=as_of,
            start=start,
            end=end,
            session_model=session.session_model,
            checkpoint_id=checkpoint_id,
            cycle_id=session.cycle_id,
            recipe_id=session.recipe_id,
            venue=venue,
            frequency=frequency,
            adjustment_policy=adjustment_policy,
        )

    @classmethod
    def from_checkpoint(
        cls,
        *,
        asset: AssetID,
        data_kind: DataKind,
        checkpoint: WorkflowCheckpoint,
        session_model: SessionModel | None = None,
        start: date | None = None,
        end: date | None = None,
        venue: str | None = None,
        frequency: str | None = None,
        adjustment_policy: str | None = None,
    ) -> DataQuery:
        as_of = date.fromisoformat(checkpoint.as_of)
        return cls(
            asset=asset,
            asset_domain=checkpoint.asset_domain,
            data_kind=data_kind,
            as_of=as_of,
            start=start,
            end=end,
            session_model=session_model,
            checkpoint_id=checkpoint.checkpoint_id,
            cycle_id=checkpoint.cycle_id,
            recipe_id=checkpoint.recipe_id,
            venue=venue,
            frequency=frequency,
            adjustment_policy=adjustment_policy,
        )

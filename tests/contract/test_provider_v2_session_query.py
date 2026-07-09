from __future__ import annotations

from datetime import date

from lucerna_core.domain.models import AssetID, AssetType, Exchange
from lucerna_core.providers.capabilities import DataKind
from lucerna_core.providers.query import DataQuery
from lucerna_core.workflow.model import (
    AssetDomain,
    SessionModel,
    WorkflowCheckpoint,
    WorkflowSessionMetadata,
)

ASSET = AssetID("600000", Exchange.SSE, AssetType.STOCK)


def test_data_query_from_session_populates_session_fields() -> None:
    session = WorkflowSessionMetadata(
        recipe_id="lucerna.recipe.ashare_daily_research.v1",
        asset_domain=AssetDomain.CHINA_A_SHARE,
        session_model=SessionModel.CALENDAR_DAY_CYCLE,
        cycle_id="2026-04-30",
    )
    query = DataQuery.from_session(
        asset=ASSET,
        data_kind=DataKind.OHLCV,
        session=session,
        as_of=date(2026, 4, 30),
        checkpoint_id="cp-post-close",
    )

    assert query.recipe_id == session.recipe_id
    assert query.cycle_id == "2026-04-30"
    assert query.checkpoint_id == "cp-post-close"
    assert query.session_model == SessionModel.CALENDAR_DAY_CYCLE


def test_data_query_from_checkpoint_populates_fields() -> None:
    checkpoint = WorkflowCheckpoint(
        checkpoint_id="cp-preopen",
        recipe_id="lucerna.recipe.ashare_daily_research.v1",
        recipe_stage_id="preopen",
        asset_domain=AssetDomain.CHINA_A_SHARE,
        cycle_id="2026-04-30",
        as_of="2026-04-30",
    )
    query = DataQuery.from_checkpoint(
        asset=ASSET,
        data_kind=DataKind.OHLCV,
        checkpoint=checkpoint,
        session_model=SessionModel.EXCHANGE_SESSION_HANDOFF,
    )

    assert query.checkpoint_id == "cp-preopen"
    assert query.cycle_id == "2026-04-30"
    assert query.as_of == date(2026, 4, 30)
    assert query.session_model == SessionModel.EXCHANGE_SESSION_HANDOFF


def test_provenance_payload_round_trip_session_fields() -> None:
    from lucerna_core.providers.capabilities import ProviderAuthorityLevel
    from lucerna_core.providers.result import ProviderProvenance, utc_now_iso

    provenance = ProviderProvenance(
        provider_id="local_fixture",
        authority_level=ProviderAuthorityLevel.FIXTURE,
        data_kind=DataKind.OHLCV,
        asset_domain=AssetDomain.CHINA_A_SHARE,
        captured_at=utc_now_iso(),
        as_of=date(2026, 4, 30),
        session_model=SessionModel.CALENDAR_DAY_CYCLE,
        checkpoint_id="cp-1",
        cycle_id="2026-04-30",
    )
    payload = provenance.to_payload()

    assert payload["session_model"] == "calendar_day_cycle"
    assert payload["checkpoint_id"] == "cp-1"
    assert payload["cycle_id"] == "2026-04-30"
    assert "D:" not in str(payload)
    forbidden = "." + "indiciumgrid"
    assert forbidden not in str(payload)

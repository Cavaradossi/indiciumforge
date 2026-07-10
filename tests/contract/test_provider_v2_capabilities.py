from __future__ import annotations

from datetime import date
from pathlib import Path

from indiciumforge_core.domain.models import AssetID, AssetType, Exchange
from indiciumforge_core.providers.capabilities import DataKind
from indiciumforge_core.providers.local_fixture_v2 import LocalFixtureProviderV2
from indiciumforge_core.providers.query import DataQuery
from indiciumforge_core.providers.result import ProviderFailureStatus
from indiciumforge_core.workflow.model import AssetDomain

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "ohlcv"
ASSET = AssetID("600000", Exchange.SSE, AssetType.STOCK)


def _query(**overrides: object) -> DataQuery:
    base = DataQuery(
        asset=ASSET,
        asset_domain=AssetDomain.CHINA_A_SHARE,
        data_kind=DataKind.OHLCV,
    )
    return DataQuery(
        asset=overrides.get("asset", base.asset),  # type: ignore[arg-type]
        asset_domain=overrides.get("asset_domain", base.asset_domain),  # type: ignore[arg-type]
        data_kind=overrides.get("data_kind", base.data_kind),  # type: ignore[arg-type]
        as_of=overrides.get("as_of", base.as_of),  # type: ignore[arg-type]
        start=overrides.get("start", base.start),  # type: ignore[arg-type]
        end=overrides.get("end", base.end),  # type: ignore[arg-type]
        session_model=overrides.get("session_model", base.session_model),  # type: ignore[arg-type]
        checkpoint_id=overrides.get("checkpoint_id", base.checkpoint_id),  # type: ignore[arg-type]
        cycle_id=overrides.get("cycle_id", base.cycle_id),  # type: ignore[arg-type]
        recipe_id=overrides.get("recipe_id", base.recipe_id),  # type: ignore[arg-type]
        calendar_id=overrides.get("calendar_id", base.calendar_id),  # type: ignore[arg-type]
        venue=overrides.get("venue", base.venue),  # type: ignore[arg-type]
        frequency=overrides.get("frequency", base.frequency),  # type: ignore[arg-type]
        adjustment_policy=overrides.get("adjustment_policy", base.adjustment_policy),  # type: ignore[arg-type]
    )


def test_local_fixture_v2_supports_ohlcv_china_a_share() -> None:
    provider = LocalFixtureProviderV2(FIXTURE_ROOT)

    assert provider.supports_query(_query()) is True


def test_local_fixture_v2_rejects_quote_snapshot() -> None:
    provider = LocalFixtureProviderV2(FIXTURE_ROOT)

    assert provider.supports_query(_query(data_kind=DataKind.QUOTE_SNAPSHOT)) is False


def test_local_fixture_v2_rejects_crypto_perp_funding() -> None:
    provider = LocalFixtureProviderV2(FIXTURE_ROOT)

    assert (
        provider.supports_query(
            _query(
                asset_domain=AssetDomain.CRYPTO_PERP,
                data_kind=DataKind.FUNDING_RATE,
            )
        )
        is False
    )


def test_local_fixture_v2_fetch_returns_provenance() -> None:
    provider = LocalFixtureProviderV2(FIXTURE_ROOT)

    result = provider.fetch(_query())

    assert result.provenance.provider_id == "local_fixture"
    assert result.provenance.failure_status == ProviderFailureStatus.OK
    assert result.provenance.as_of == date(2026, 4, 30)
    assert len(result.frame) == 3


def test_local_fixture_v2_missing_capability_for_wrong_kind() -> None:
    provider = LocalFixtureProviderV2(FIXTURE_ROOT)

    result = provider.fetch(_query(data_kind=DataKind.QUOTE_SNAPSHOT))

    assert result.frame.empty
    assert result.provenance.failure_status == ProviderFailureStatus.MISSING_CAPABILITY

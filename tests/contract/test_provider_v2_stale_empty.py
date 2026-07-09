from __future__ import annotations

from datetime import date

from lucerna_core.domain.models import AssetID, AssetType, Exchange
from lucerna_core.providers.capabilities import DataKind
from lucerna_core.providers.query import DataQuery
from lucerna_core.providers.registry_v2 import ProviderRegistryV2
from lucerna_core.providers.result import ProviderFailureStatus
from lucerna_core.workflow.model import AssetDomain
from provider_stubs_v2 import EmptyV2Provider, StaleV2Provider

ASSET = AssetID("600000", Exchange.SSE, AssetType.STOCK)
QUERY = DataQuery(
    asset=ASSET,
    asset_domain=AssetDomain.CHINA_A_SHARE,
    data_kind=DataKind.OHLCV,
    as_of=date(2026, 4, 30),
)


def test_registry_returns_empty_failure_status_when_all_providers_empty() -> None:
    registry = ProviderRegistryV2([EmptyV2Provider()])

    result = registry.fetch(QUERY)

    assert result.frame.empty
    assert result.provenance.failure_status == ProviderFailureStatus.EMPTY
    assert result.provenance.provider_id == "none"


def test_stale_provider_skipped_with_warning_trace() -> None:
    registry = ProviderRegistryV2([StaleV2Provider()])

    result = registry.fetch(QUERY)

    assert result.frame.empty
    assert result.provenance.failure_status == ProviderFailureStatus.EMPTY
    assert any("stale" in warning for warning in result.provenance.warnings)

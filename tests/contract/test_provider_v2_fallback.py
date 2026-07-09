from __future__ import annotations

from datetime import date
from pathlib import Path

from lucerna_core.domain.models import AssetID, AssetType, Exchange
from lucerna_core.providers.capabilities import DataKind, ProviderAuthorityLevel
from lucerna_core.providers.local_fixture_v2 import LocalFixtureProviderV2
from lucerna_core.providers.query import DataQuery
from lucerna_core.providers.registry_v2 import ProviderRegistryV2
from lucerna_core.workflow.model import AssetDomain
from provider_stubs_v2 import FailingV2Provider, SuccessV2Provider

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "ohlcv"
ASSET = AssetID("600000", Exchange.SSE, AssetType.STOCK)
QUERY = DataQuery(
    asset=ASSET,
    asset_domain=AssetDomain.CHINA_A_SHARE,
    data_kind=DataKind.OHLCV,
    as_of=date(2026, 4, 30),
)


def test_registry_prefers_first_successful_provider() -> None:
    registry = ProviderRegistryV2([SuccessV2Provider(), LocalFixtureProviderV2(FIXTURE_ROOT)])

    result = registry.fetch(QUERY)

    assert result.provenance.provider_id == "success_v2"
    assert len(result.frame) == 1


def test_registry_falls_back_with_warnings_and_authority_tag() -> None:
    registry = ProviderRegistryV2([FailingV2Provider(), LocalFixtureProviderV2(FIXTURE_ROOT)])

    result = registry.fetch(QUERY)

    assert result.provenance.provider_id == "local_fixture"
    assert result.provenance.authority_level == ProviderAuthorityLevel.FIXTURE
    assert len(result.frame) == 3
    assert any("simulated timeout" in warning for warning in result.provenance.warnings)
    assert result.attempted_providers == ("failing_v2", "local_fixture")

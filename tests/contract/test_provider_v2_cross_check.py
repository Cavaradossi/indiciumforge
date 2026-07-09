from __future__ import annotations

from datetime import date

from lucerna_core.domain.models import AssetID, AssetType, Exchange
from lucerna_core.providers.capabilities import DataKind
from lucerna_core.providers.query import DataQuery
from lucerna_core.providers.registry_v2 import ProviderRegistryV2
from lucerna_core.workflow.model import AssetDomain
from provider_stubs_v2 import MismatchCrossCheckProvider, SuccessV2Provider

ASSET = AssetID("600000", Exchange.SSE, AssetType.STOCK)
QUERY = DataQuery(
    asset=ASSET,
    asset_domain=AssetDomain.CHINA_A_SHARE,
    data_kind=DataKind.OHLCV,
    as_of=date(2026, 4, 30),
)


def test_cross_check_warns_without_replacing_primary_frame() -> None:
    registry = ProviderRegistryV2([SuccessV2Provider(), MismatchCrossCheckProvider()])

    result = registry.fetch(QUERY, cross_check_providers=("cross_check_mismatch",))

    assert result.provenance.provider_id == "success_v2"
    assert float(result.frame.iloc[0]["close"]) == 1.0
    assert any("frame mismatch" in warning for warning in result.provenance.warnings)

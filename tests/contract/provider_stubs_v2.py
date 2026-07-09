from __future__ import annotations

from datetime import date

import pandas as pd
from lucerna_core.domain.models import AssetID, MissingData
from lucerna_core.providers.capabilities import (
    DataKind,
    LatencyProfile,
    ProviderAuthorityLevel,
    ProviderCapability,
)
from lucerna_core.providers.query import DataQuery
from lucerna_core.providers.result import (
    ProviderFailureStatus,
    ProviderProvenance,
    ProviderResult,
    utc_now_iso,
)
from lucerna_core.workflow.model import AssetDomain


def _base_query(asset: AssetID) -> DataQuery:
    return DataQuery(
        asset=asset,
        asset_domain=AssetDomain.CHINA_A_SHARE,
        data_kind=DataKind.OHLCV,
    )


class FailingV2Provider:
    provider_id = "failing_v2"
    authority_level = ProviderAuthorityLevel.PRIMARY
    capabilities = (
        ProviderCapability(
            asset_domain=AssetDomain.CHINA_A_SHARE,
            data_kind=DataKind.OHLCV,
            latency_profile=LatencyProfile.HISTORICAL,
        ),
    )

    def supports_query(self, query: DataQuery) -> bool:
        return True

    def fetch(self, query: DataQuery) -> ProviderResult:
        raise MissingData("simulated timeout")


class SuccessV2Provider:
    provider_id = "success_v2"
    authority_level = ProviderAuthorityLevel.PRIMARY
    capabilities = (
        ProviderCapability(
            asset_domain=AssetDomain.CHINA_A_SHARE,
            data_kind=DataKind.OHLCV,
            latency_profile=LatencyProfile.HISTORICAL,
        ),
    )

    def supports_query(self, query: DataQuery) -> bool:
        return True

    def fetch(self, query: DataQuery) -> ProviderResult:
        frame = pd.DataFrame(
            [
                {
                    "date": date(2026, 4, 30),
                    "open": 1.0,
                    "high": 1.1,
                    "low": 0.9,
                    "close": 1.0,
                    "volume": 1,
                }
            ]
        )
        return ProviderResult(
            frame=frame,
            provenance=ProviderProvenance(
                provider_id=self.provider_id,
                authority_level=self.authority_level,
                data_kind=query.data_kind,
                asset_domain=query.asset_domain,
                captured_at=utc_now_iso(),
                as_of=date(2026, 4, 30),
            ),
        )


class EmptyV2Provider:
    provider_id = "empty_v2"
    authority_level = ProviderAuthorityLevel.PRIMARY
    capabilities = SuccessV2Provider.capabilities

    def supports_query(self, query: DataQuery) -> bool:
        return True

    def fetch(self, query: DataQuery) -> ProviderResult:
        return ProviderResult(
            frame=pd.DataFrame(),
            provenance=ProviderProvenance(
                provider_id=self.provider_id,
                authority_level=self.authority_level,
                data_kind=query.data_kind,
                asset_domain=query.asset_domain,
                captured_at=utc_now_iso(),
                failure_status=ProviderFailureStatus.EMPTY,
            ),
        )


class StaleV2Provider:
    provider_id = "stale_v2"
    authority_level = ProviderAuthorityLevel.PRIMARY
    capabilities = SuccessV2Provider.capabilities

    def supports_query(self, query: DataQuery) -> bool:
        return True

    def fetch(self, query: DataQuery) -> ProviderResult:
        return ProviderResult(
            frame=pd.DataFrame(),
            provenance=ProviderProvenance(
                provider_id=self.provider_id,
                authority_level=self.authority_level,
                data_kind=query.data_kind,
                asset_domain=query.asset_domain,
                captured_at=utc_now_iso(),
                failure_status=ProviderFailureStatus.STALE,
                warnings=("data older than requested as_of",),
            ),
        )


class MismatchCrossCheckProvider:
    provider_id = "cross_check_mismatch"
    authority_level = ProviderAuthorityLevel.CROSS_CHECK
    capabilities = SuccessV2Provider.capabilities

    def supports_query(self, query: DataQuery) -> bool:
        return True

    def fetch(self, query: DataQuery) -> ProviderResult:
        frame = pd.DataFrame(
            [
                {
                    "date": date(2026, 4, 30),
                    "open": 9.0,
                    "high": 9.1,
                    "low": 8.9,
                    "close": 9.0,
                    "volume": 9,
                }
            ]
        )
        return ProviderResult(
            frame=frame,
            provenance=ProviderProvenance(
                provider_id=self.provider_id,
                authority_level=self.authority_level,
                data_kind=query.data_kind,
                asset_domain=query.asset_domain,
                captured_at=utc_now_iso(),
                as_of=date(2026, 4, 30),
            ),
        )

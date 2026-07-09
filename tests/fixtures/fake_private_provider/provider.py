from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
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


class FakePrivateOhlcvProvider:
    """Synthetic private adapter for contract tests only."""

    provider_id = "fake_private_ohlcv"
    authority_level = ProviderAuthorityLevel.EXPERIMENTAL
    capabilities = (
        ProviderCapability(
            asset_domain=AssetDomain.CHINA_A_SHARE,
            data_kind=DataKind.OHLCV,
            latency_profile=LatencyProfile.HISTORICAL,
            venues=("SSE",),
        ),
    )

    def __init__(self, fixture_root: Path | None = None) -> None:
        self._fixture_root = fixture_root

    def supports_query(self, query: DataQuery) -> bool:
        if query.data_kind != DataKind.OHLCV:
            return False
        if query.asset_domain != AssetDomain.CHINA_A_SHARE:
            return False
        return query.asset.code == "DEMO001"

    def fetch(self, query: DataQuery) -> ProviderResult:
        if not self.supports_query(query):
            return ProviderResult(
                frame=pd.DataFrame(),
                provenance=self._provenance(
                    query,
                    failure_status=ProviderFailureStatus.MISSING_CAPABILITY,
                ),
            )

        frame = pd.DataFrame(
            [
                {
                    "date": date(2026, 4, 30),
                    "open": 2.0,
                    "high": 2.2,
                    "low": 1.9,
                    "close": 2.1,
                    "volume": 100,
                }
            ]
        )
        return ProviderResult(
            frame=frame,
            provenance=self._provenance(query, as_of=date(2026, 4, 30)),
        )

    def _provenance(
        self,
        query: DataQuery,
        *,
        as_of: date | None = None,
        failure_status: ProviderFailureStatus = ProviderFailureStatus.OK,
    ) -> ProviderProvenance:
        return ProviderProvenance(
            provider_id=self.provider_id,
            authority_level=self.authority_level,
            data_kind=query.data_kind,
            asset_domain=query.asset_domain,
            captured_at=utc_now_iso(),
            as_of=as_of or query.as_of,
            failure_status=failure_status,
            session_model=query.session_model,
            checkpoint_id=query.checkpoint_id,
            cycle_id=query.cycle_id,
            cache_policy="private_fixture",
            quota_policy="unlimited_test",
        )

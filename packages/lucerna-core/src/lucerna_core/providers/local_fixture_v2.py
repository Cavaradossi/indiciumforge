from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from lucerna_core.artifacts.local_store import LocalArtifactStore
from lucerna_core.domain.models import MissingData
from lucerna_core.ports.contracts import ArtifactStorePort
from lucerna_core.providers.capabilities import (
    DataKind,
    LatencyProfile,
    ProviderAuthorityLevel,
    ProviderCapability,
)
from lucerna_core.providers.local_fixture import LocalFixtureProvider, fixture_path_for
from lucerna_core.providers.query import DataQuery
from lucerna_core.providers.result import (
    ProviderFailureStatus,
    ProviderProvenance,
    ProviderResult,
    utc_now_iso,
)
from lucerna_core.workflow.model import AssetDomain


class LocalFixtureProviderV2:
    provider_id = "local_fixture"
    authority_level = ProviderAuthorityLevel.FIXTURE
    capabilities = (
        ProviderCapability(
            asset_domain=AssetDomain.CHINA_A_SHARE,
            data_kind=DataKind.OHLCV,
            latency_profile=LatencyProfile.HISTORICAL,
            venues=("SSE", "SZSE"),
        ),
    )

    def __init__(
        self,
        fixture_root: Path,
        store: ArtifactStorePort | None = None,
    ) -> None:
        self._fixture_root = fixture_root
        self._store = store or LocalArtifactStore()
        self._v1 = LocalFixtureProvider(fixture_root, store=self._store)

    def supports_query(self, query: DataQuery) -> bool:
        if query.data_kind != DataKind.OHLCV:
            return False
        if query.asset_domain != AssetDomain.CHINA_A_SHARE:
            return False
        return fixture_path_for(query.asset, self._fixture_root).is_file()

    def fetch(self, query: DataQuery) -> ProviderResult:
        if not self.supports_query(query):
            return ProviderResult(
                frame=pd.DataFrame(),
                provenance=self._provenance(
                    query,
                    failure_status=ProviderFailureStatus.MISSING_CAPABILITY,
                    warnings=("unsupported query for local_fixture",),
                ),
            )

        path = fixture_path_for(query.asset, self._fixture_root)
        if not path.is_file():
            raise MissingData(f"missing fixture for {query.asset.uid}")

        try:
            frame, _ = self._v1.fetch_ohlcv(query.asset, query.start, query.end)
        except MissingData:
            raise
        except Exception as exc:
            return ProviderResult(
                frame=pd.DataFrame(),
                provenance=self._provenance(
                    query,
                    failure_status=ProviderFailureStatus.PROVIDER_ERROR,
                    warnings=(str(exc),),
                ),
            )

        if frame.empty:
            return ProviderResult(
                frame=frame,
                provenance=self._provenance(
                    query,
                    failure_status=ProviderFailureStatus.EMPTY,
                    warnings=("empty frame after date filter",),
                ),
            )

        as_of = frame["date"].iloc[-1]
        if not isinstance(as_of, date):
            as_of = pd.to_datetime(as_of).date()

        return ProviderResult(
            frame=frame.reset_index(drop=True),
            provenance=self._provenance(query, as_of=as_of),
        )

    def _provenance(
        self,
        query: DataQuery,
        *,
        as_of: date | None = None,
        failure_status: ProviderFailureStatus = ProviderFailureStatus.OK,
        warnings: tuple[str, ...] = (),
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
            cache_policy="read_through_fixture",
            warnings=warnings,
        )

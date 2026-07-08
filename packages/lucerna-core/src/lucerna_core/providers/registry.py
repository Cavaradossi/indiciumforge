from __future__ import annotations

from datetime import date

import pandas as pd

from lucerna_core.domain.models import AssetID, MissingData, Provenance
from lucerna_core.ports.contracts import DataProviderPort, FetchResult


class ProviderRegistry:
    def __init__(self, providers: list[DataProviderPort]) -> None:
        self._providers = providers

    def fetch_ohlcv(
        self,
        asset: AssetID,
        start: date | None = None,
        end: date | None = None,
    ) -> FetchResult:
        warnings: list[str] = []
        for provider in self._providers:
            try:
                frame, provenance = provider.fetch_ohlcv(asset, start, end)
            except MissingData as exc:
                warnings.append(str(exc))
                continue
            if frame.empty:
                warnings.append(f"{provider.name}: empty data")
                continue
            return frame, Provenance(
                provider=provenance.provider,
                tier=provenance.tier,
                as_of=provenance.as_of,
                warnings=tuple(warnings),
            )
        return pd.DataFrame(), Provenance(provider="none", tier="none", warnings=tuple(warnings))

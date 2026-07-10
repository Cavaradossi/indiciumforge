from __future__ import annotations

from datetime import date

import pandas as pd
from indiciumforge_core.domain.models import AssetID, MissingData, Provenance
from indiciumforge_core.ports.contracts import FetchResult


class EmptyProvider:
    name = "empty"
    tier = "free"

    def supports(self, asset: AssetID) -> bool:
        return True

    def fetch_ohlcv(
        self,
        asset: AssetID,
        start: date | None = None,
        end: date | None = None,
    ) -> FetchResult:
        return pd.DataFrame(), Provenance(provider=self.name, tier=self.tier)


class FailingProvider:
    name = "failing"
    tier = "paid"

    def supports(self, asset: AssetID) -> bool:
        return True

    def fetch_ohlcv(
        self,
        asset: AssetID,
        start: date | None = None,
        end: date | None = None,
    ) -> FetchResult:
        raise MissingData("simulated timeout")


class SuccessProvider:
    name = "success"
    tier = "local"

    def supports(self, asset: AssetID) -> bool:
        return True

    def fetch_ohlcv(
        self,
        asset: AssetID,
        start: date | None = None,
        end: date | None = None,
    ) -> FetchResult:
        return (
            pd.DataFrame(
                [
                    {
                        "date": "2026-04-30",
                        "open": 1.0,
                        "high": 1.1,
                        "low": 0.9,
                        "close": 1.0,
                        "volume": 1,
                    }
                ]
            ),
            Provenance(provider=self.name, tier=self.tier, as_of=date(2026, 4, 30)),
        )

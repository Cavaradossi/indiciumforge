from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Protocol

import pandas as pd

from indiciumforge_core.domain.models import AssetID, Provenance

OHLCV_COLUMNS: tuple[str, ...] = ("date", "open", "high", "low", "close", "volume")
FetchResult = tuple[pd.DataFrame, Provenance]


class ArtifactStorePort(Protocol):
    def read_csv(self, path: Path, **kwargs: object) -> pd.DataFrame: ...

    def write_csv(self, path: Path, frame: pd.DataFrame) -> None: ...


class DataProviderPort(Protocol):
    name: str
    tier: str

    def supports(self, asset: AssetID) -> bool: ...

    def fetch_ohlcv(
        self,
        asset: AssetID,
        start: date | None = None,
        end: date | None = None,
    ) -> FetchResult: ...

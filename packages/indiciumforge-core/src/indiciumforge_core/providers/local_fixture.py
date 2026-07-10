from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from indiciumforge_core.artifacts.local_store import LocalArtifactStore
from indiciumforge_core.domain.models import AssetID, MissingData, Provenance
from indiciumforge_core.ports.contracts import OHLCV_COLUMNS, ArtifactStorePort, FetchResult


def fixture_path_for(asset: AssetID, fixture_root: Path) -> Path:
    filename = f"{asset.exchange.value}_{asset.asset_type.value}_{asset.code}.csv"
    return fixture_root / filename


class LocalFixtureProvider:
    name = "local_fixture"
    tier = "fixture"

    def __init__(
        self,
        fixture_root: Path,
        store: ArtifactStorePort | None = None,
    ) -> None:
        self._fixture_root = fixture_root
        self._store = store or LocalArtifactStore()

    def supports(self, asset: AssetID) -> bool:
        return fixture_path_for(asset, self._fixture_root).is_file()

    def fetch_ohlcv(
        self,
        asset: AssetID,
        start: date | None = None,
        end: date | None = None,
    ) -> FetchResult:
        path = fixture_path_for(asset, self._fixture_root)
        if not path.is_file():
            raise MissingData(f"missing fixture: {path}")

        frame = self._store.read_csv(path, encoding="utf-8-sig")
        missing_columns = [column for column in OHLCV_COLUMNS if column not in frame.columns]
        if missing_columns:
            raise MissingData(f"fixture missing columns: {', '.join(missing_columns)}")

        frame = frame.loc[:, list(OHLCV_COLUMNS)].copy()
        frame["date"] = pd.to_datetime(frame["date"]).dt.date

        if start is not None:
            frame = frame[frame["date"] >= start]
        if end is not None:
            frame = frame[frame["date"] <= end]
        if frame.empty:
            return pd.DataFrame(columns=list(OHLCV_COLUMNS)), Provenance(
                provider=self.name,
                tier=self.tier,
            )

        as_of = frame["date"].iloc[-1]
        if not isinstance(as_of, date):
            as_of = pd.to_datetime(as_of).date()

        return frame.reset_index(drop=True), Provenance(
            provider=self.name,
            tier=self.tier,
            as_of=as_of,
        )

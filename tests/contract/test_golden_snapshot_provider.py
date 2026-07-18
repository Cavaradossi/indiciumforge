"""Tests for the GoldenSnapshotProvider (W4a) — uses a tmp parquet panel."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
from indiciumforge_core.domain.models import AssetID, AssetType, Exchange
from indiciumforge_core.providers.capabilities import DataKind, ProviderAuthorityLevel
from indiciumforge_core.providers.golden_snapshot import GoldenSnapshotProvider
from indiciumforge_core.providers.query import DataQuery
from indiciumforge_core.providers.result import ProviderFailureStatus
from indiciumforge_core.workflow.model import AssetDomain

_UID = "sse:stock:600000"


def _build_panel(tmp_path: Path) -> Path:
    rows = []
    d = date(2024, 1, 2)
    for i in range(10):
        rows.append((_UID, d, 10.0 + i, 10.5 + i, 9.8 + i, 10.2 + i, 100000 + i * 1000))
        from datetime import timedelta
        d = d + timedelta(days=1 if d.weekday() < 4 else 3)  # skip weekends roughly
    panel = pd.DataFrame(
        rows,
        columns=["asset_uid", "date", "open", "high", "low", "close", "volume"],
    )
    path = tmp_path / "panel.parquet"
    panel.to_parquet(path, index=False)
    return path


def _query(*, start: date | None = None, end: date | None = None, as_of: date | None = None,
           code: str = "600000") -> DataQuery:
    asset = AssetID(code=code, exchange=Exchange.from_code("sse"), asset_type=AssetType.STOCK)
    return DataQuery(asset=asset, asset_domain=AssetDomain.CHINA_A_SHARE,
                     data_kind=DataKind.OHLCV, start=start, end=end, as_of=as_of)


def test_identity_and_available_uids(tmp_path: Path) -> None:
    p = GoldenSnapshotProvider(_build_panel(tmp_path))
    assert p.provider_id == "golden_ashare"
    assert p.authority_level == ProviderAuthorityLevel.FIXTURE
    assert _UID in p.available_uids


def test_fetch_returns_rows(tmp_path: Path) -> None:
    p = GoldenSnapshotProvider(_build_panel(tmp_path))
    result = p.fetch(_query())
    assert result.provenance.failure_status == ProviderFailureStatus.OK
    assert not result.frame.empty
    assert list(result.frame.columns) == ["date", "open", "high", "low", "close", "volume"]
    assert result.provenance.cache_hit is True


def test_as_of_point_in_time_slicing(tmp_path: Path) -> None:
    p = GoldenSnapshotProvider(_build_panel(tmp_path))
    # Full range vs as_of cutoff — as_of must exclude strictly-future rows.
    full = p.fetch(_query())
    cutoff = full.frame["date"].iloc[3]
    sliced = p.fetch(_query(as_of=cutoff))
    assert len(sliced.frame) <= len(full.frame)
    assert (sliced.frame["date"] <= cutoff).all()


def test_missing_asset_returns_missing_capability(tmp_path: Path) -> None:
    p = GoldenSnapshotProvider(_build_panel(tmp_path))
    result = p.fetch(_query(code="999999"))
    assert result.provenance.failure_status == ProviderFailureStatus.MISSING_CAPABILITY
    assert result.frame.empty


def test_empty_range_returns_empty(tmp_path: Path) -> None:
    p = GoldenSnapshotProvider(_build_panel(tmp_path))
    result = p.fetch(_query(start=date(2099, 1, 1), end=date(2099, 6, 1)))
    assert result.provenance.failure_status == ProviderFailureStatus.EMPTY

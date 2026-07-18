from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
from indiciumforge_core.domain.models import AssetID, AssetType, Exchange
from indiciumforge_core.ports.storage import asset_uid_from_asset_id
from indiciumforge_core.providers.capabilities import DataKind, ProviderAuthorityLevel
from indiciumforge_core.providers.result import ProviderProvenance
from indiciumforge_core.storage import ParquetDuckDBMarketDataStore
from indiciumforge_core.workflow.model import AssetDomain

ASSET = AssetID("600000", Exchange.SSE, AssetType.STOCK)
UID = asset_uid_from_asset_id(ASSET)


def _prov(as_of: date | None, captured_at: str) -> ProviderProvenance:
    return ProviderProvenance(
        provider_id="fake",
        authority_level=ProviderAuthorityLevel.PRIMARY,
        data_kind=DataKind.OHLCV,
        asset_domain=AssetDomain.CHINA_A_SHARE,
        captured_at=captured_at,
        as_of=as_of,
    )


def _frame(dates: list[date], close: float) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "date": d,
                "open": close,
                "high": close,
                "low": close,
                "close": close,
                "volume": 10,
            }
            for d in dates
        ]
    )


def _dates(frame: pd.DataFrame) -> list[date]:
    return [pd.to_datetime(d).date() for d in frame["date"].tolist()]


# ---------------------------------------------------------------------------
# Basic write / read round-trip (no as_of -> latest snapshot returned).
# ---------------------------------------------------------------------------
def test_write_then_fetch_round_trip(tmp_path: Path) -> None:
    store = ParquetDuckDBMarketDataStore(tmp_path / "ohlcv")
    df = _frame([date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3)], 100.0)
    store.write_ohlcv(UID, df, provenance=_prov(date(2026, 1, 3), "2026-01-03T23:00:00+00:00"))

    out, prov = store.fetch_ohlcv(UID)
    assert not out.empty
    assert list(out.columns) == ["date", "open", "high", "low", "close", "volume"]
    assert _dates(out) == [date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3)]
    assert out["close"].tolist() == [100.0, 100.0, 100.0]
    assert prov is not None
    assert prov.as_of == date(2026, 1, 3)


def test_empty_write_is_noop(tmp_path: Path) -> None:
    store = ParquetDuckDBMarketDataStore(tmp_path / "ohlcv")
    store.write_ohlcv(
        UID, pd.DataFrame(), provenance=_prov(date(2026, 1, 3), "2026-01-03T23:00:00+00:00")
    )
    out, _ = store.fetch_ohlcv(UID)
    assert out.empty


# ---------------------------------------------------------------------------
# Point-in-time look-ahead guard (W2 risk ①): a snapshot whose own as-of
# (the last trade date it represents) lies AFTER the query as_of must be
# excluded — otherwise future data leaks into a past evaluation.
# ---------------------------------------------------------------------------
def test_point_in_time_excludes_future_provenance_as_of(tmp_path: Path) -> None:
    store = ParquetDuckDBMarketDataStore(tmp_path / "ohlcv")
    # A snapshot that actually represents data through 2026-01-10.
    df = _frame([date(2026, 1, 8), date(2026, 1, 9), date(2026, 1, 10)], 100.0)
    store.write_ohlcv(
        UID, df, provenance=_prov(date(2026, 1, 10), "2026-01-10T23:00:00+00:00")
    )

    # Evaluating as_of 2026-01-05: the snapshot's as-of (2026-01-10) is in the
    # future, so it must NOT be returned (no look-ahead).
    out, _ = store.fetch_ohlcv(UID, as_of=date(2026, 1, 5))
    assert out.empty


def test_point_in_time_allows_in_scope_provenance_as_of(tmp_path: Path) -> None:
    store = ParquetDuckDBMarketDataStore(tmp_path / "ohlcv")
    df = _frame([date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3)], 100.0)
    store.write_ohlcv(
        UID, df, provenance=_prov(date(2026, 1, 3), "2026-01-03T23:00:00+00:00")
    )

    out, _ = store.fetch_ohlcv(UID, as_of=date(2026, 1, 3))
    assert not out.empty
    assert _dates(out) == [date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3)]


# ---------------------------------------------------------------------------
# De-duplication: overlapping writes for the same dates keep the LATEST
# captured snapshot (ROW_NUMBER OVER ... ORDER BY captured_at DESC).
# ---------------------------------------------------------------------------
def test_overlapping_writes_dedup_to_latest_snapshot(tmp_path: Path) -> None:
    store = ParquetDuckDBMarketDataStore(tmp_path / "ohlcv")
    base = [date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3)]
    # First snapshot (close=100), captured 2026-01-03.
    store.write_ohlcv(
        UID, _frame(base, 100.0), provenance=_prov(date(2026, 1, 3), "2026-01-03T23:00:00+00:00")
    )
    # Revised snapshot (close=999), captured later 2026-02-01.
    store.write_ohlcv(
        UID, _frame(base, 999.0), provenance=_prov(date(2026, 1, 3), "2026-02-01T23:00:00+00:00")
    )

    out, _ = store.fetch_ohlcv(UID, as_of=date(2026, 2, 1))
    assert out["close"].tolist() == [999.0, 999.0, 999.0]


# ---------------------------------------------------------------------------
# Date-range filtering and the remaining port methods.
# ---------------------------------------------------------------------------
def test_fetch_ohlcv_date_range(tmp_path: Path) -> None:
    store = ParquetDuckDBMarketDataStore(tmp_path / "ohlcv")
    store.write_ohlcv(
        UID,
        _frame([date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3), date(2026, 1, 4)], 100.0),
        provenance=_prov(date(2026, 1, 4), "2026-01-04T23:00:00+00:00"),
    )
    out, _ = store.fetch_ohlcv(UID, start=date(2026, 1, 2), end=date(2026, 1, 3))
    assert _dates(out) == [date(2026, 1, 2), date(2026, 1, 3)]


def test_fetch_ohlcv_batch(tmp_path: Path) -> None:
    store = ParquetDuckDBMarketDataStore(tmp_path / "ohlcv")
    store.write_ohlcv(
        UID, _frame([date(2026, 1, 1), date(2026, 1, 2)], 100.0),
        provenance=_prov(date(2026, 1, 2), "2026-01-02T23:00:00+00:00"),
    )
    result = store.fetch_ohlcv_batch([UID], as_of=date(2026, 1, 2))
    assert set(result.keys()) == {UID}
    assert not result[UID][0].empty


def test_fetch_panel_long_format(tmp_path: Path) -> None:
    store = ParquetDuckDBMarketDataStore(tmp_path / "ohlcv")
    store.write_ohlcv(
        UID, _frame([date(2026, 1, 1), date(2026, 1, 2)], 100.0),
        provenance=_prov(date(2026, 1, 2), "2026-01-02T23:00:00+00:00"),
    )
    panel = store.fetch_panel(
        [UID], start=date(2026, 1, 1), end=date(2026, 1, 2), as_of=date(2026, 1, 2)
    )
    assert "asset_uid" in panel.columns
    assert (panel["asset_uid"] == UID).all()
    assert len(panel) == 2


def test_has_coverage(tmp_path: Path) -> None:
    store = ParquetDuckDBMarketDataStore(tmp_path / "ohlcv")
    assert store.has_coverage(UID, start=date(2026, 1, 1), end=date(2026, 1, 3)) is False
    store.write_ohlcv(
        UID, _frame([date(2026, 1, 1), date(2026, 1, 2)], 100.0),
        provenance=_prov(date(2026, 1, 2), "2026-01-02T23:00:00+00:00"),
    )
    assert store.has_coverage(UID, start=date(2026, 1, 1), end=date(2026, 1, 2)) is True
    # Out-of-range window reports no coverage.
    assert store.has_coverage(UID, start=date(2026, 2, 1), end=date(2026, 2, 2)) is False


def test_partition_layout_is_hive_style(tmp_path: Path) -> None:
    # `root` is the cache base dir; the store creates `ohlcv/` beneath it.
    store = ParquetDuckDBMarketDataStore(tmp_path)
    store.write_ohlcv(
        UID,
        _frame([date(2026, 1, 1), date(2027, 1, 1)], 100.0),
        provenance=_prov(date(2027, 1, 1), "2027-01-01T23:00:00+00:00"),
    )
    asset_dir = tmp_path / "ohlcv" / "sse" / "stock" / "600000"
    # Two distinct years -> two Hive partition folders.
    year_dirs = sorted(p.name for p in asset_dir.iterdir() if p.is_dir())
    assert year_dirs == ["year=2026", "year=2027"]
    assert list((asset_dir / "year=2026").glob("*.parquet"))

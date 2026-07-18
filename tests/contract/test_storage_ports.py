from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
from indiciumforge_core.domain.models import AssetID, AssetType, Exchange
from indiciumforge_core.ports.storage import (
    asset_uid_from_asset_id,
)
from indiciumforge_core.providers.caching import CachingDataProvider
from indiciumforge_core.providers.capabilities import (
    DataKind,
    LatencyProfile,
    ProviderAuthorityLevel,
    ProviderCapability,
)
from indiciumforge_core.providers.query import DataQuery
from indiciumforge_core.providers.result import ProviderProvenance, ProviderResult
from indiciumforge_core.storage import ParquetDuckDBMarketDataStore, SQLiteMetadataStore
from indiciumforge_core.workflow.model import AssetDomain


# ---------------------------------------------------------------------------
# Structural conformance — the new implementations satisfy the storage ports.
# ---------------------------------------------------------------------------
def test_sqlite_metadata_store_implements_metadata_store() -> None:
    assert isinstance(SQLiteMetadataStore, object)
    # The port is a Protocol; structural conformance is exercised by the real
    # method tests below. Here we assert the public surface is present.
    required = {
        "record_run",
        "get_run",
        "list_runs",
        "record_stage",
        "find_stage_by_input_hash",
        "record_factor_metadata",
        "record_parity_report",
    }
    assert required <= set(dir(SQLiteMetadataStore))


def test_parquet_store_implements_market_data_store() -> None:
    required = {
        "write_ohlcv",
        "fetch_ohlcv",
        "fetch_ohlcv_batch",
        "fetch_panel",
        "has_coverage",
    }
    assert required <= set(dir(ParquetDuckDBMarketDataStore))


def test_caching_provider_is_a_v2_provider() -> None:
    # Not runtime_checkable, so assert the structural surface on an instance
    # (provider_id/authority_level/capabilities are set in __init__).
    store = ParquetDuckDBMarketDataStore(Path("/tmp/_w2_v2_probe") / "ohlcv")
    cache = CachingDataProvider(_FakeV2Source(), store)
    required = {"provider_id", "authority_level", "capabilities", "supports_query", "fetch"}
    assert required <= set(dir(cache))


# ---------------------------------------------------------------------------
# Caching round-trip: first fetch misses (source invoked), second hits cache.
# ---------------------------------------------------------------------------
class _FakeV2Source:
    provider_id = "fake_source"
    authority_level = ProviderAuthorityLevel.PRIMARY
    capabilities = (
        ProviderCapability(
            asset_domain=AssetDomain.CHINA_A_SHARE,
            data_kind=DataKind.OHLCV,
            latency_profile=LatencyProfile.HISTORICAL,
        ),
    )

    def __init__(self) -> None:
        self.calls = 0

    def supports_query(self, query: DataQuery) -> bool:
        return True

    def fetch(self, query: DataQuery) -> ProviderResult:
        self.calls += 1
        frame = pd.DataFrame(
            [
                {
                    "date": date(2026, 1, 2),
                    "open": 10.0,
                    "high": 11.0,
                    "low": 9.0,
                    "close": 10.5,
                    "volume": 100,
                }
            ]
        )
        provenance = ProviderProvenance(
            provider_id="fake_source",
            authority_level=ProviderAuthorityLevel.PRIMARY,
            data_kind=DataKind.OHLCV,
            asset_domain=AssetDomain.CHINA_A_SHARE,
            captured_at="2026-01-03T00:00:00+00:00",
            as_of=date(2026, 1, 2),
        )
        return ProviderResult(frame, provenance)


def test_caching_provider_round_trip(tmp_path: Path) -> None:
    store = ParquetDuckDBMarketDataStore(tmp_path / "ohlcv")
    source = _FakeV2Source()
    cache = CachingDataProvider(source, store)

    asset = AssetID("600000", Exchange.SSE, AssetType.STOCK)
    query = DataQuery(
        asset=asset,
        asset_domain=AssetDomain.CHINA_A_SHARE,
        data_kind=DataKind.OHLCV,
        as_of=date(2026, 1, 2),
        start=date(2026, 1, 2),
        end=date(2026, 1, 2),
    )

    first = cache.fetch(query)
    assert source.calls == 1
    assert first.provenance.cache_hit is False
    assert first.frame["close"].iloc[0] == 10.5

    second = cache.fetch(query)
    # Source must NOT be re-invoked — the cache served the hit.
    assert source.calls == 1
    assert second.provenance.cache_hit is True
    assert second.frame["close"].iloc[0] == 10.5
    # as_of preserved across the cache boundary (point-in-time intact).
    assert second.provenance.as_of == date(2026, 1, 2)


def test_caching_provider_does_not_cache_empty(tmp_path: Path) -> None:
    store = ParquetDuckDBMarketDataStore(tmp_path / "ohlcv")
    source = _FakeV2Source()

    # Monkeypatch the source to return an empty frame.
    def _empty_fetch(query: DataQuery) -> ProviderResult:
        source.calls += 1
        return ProviderResult(
            pd.DataFrame(),
            ProviderProvenance(
                provider_id="fake_source",
                authority_level=ProviderAuthorityLevel.PRIMARY,
                data_kind=DataKind.OHLCV,
                asset_domain=AssetDomain.CHINA_A_SHARE,
                captured_at="2026-01-03T00:00:00+00:00",
                as_of=date(2026, 1, 2),
            ),
        )

    source.fetch = _empty_fetch  # type: ignore[assignment]
    cache = CachingDataProvider(source, store)
    asset = AssetID("600000", Exchange.SSE, AssetType.STOCK)
    query = DataQuery(
        asset=asset,
        asset_domain=AssetDomain.CHINA_A_SHARE,
        data_kind=DataKind.OHLCV,
        as_of=date(2026, 1, 2),
    )

    cache.fetch(query)
    cache.fetch(query)
    # Empty results must not be cached, so the source is hit every time.
    assert source.calls == 2


def test_asset_uid_helper_normalizes_merged_identity() -> None:
    asset = AssetID("000001", Exchange.SZSE, AssetType.STOCK)
    assert asset_uid_from_asset_id(asset) == "szse:stock:000001"

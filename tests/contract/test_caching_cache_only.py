"""Tests for the CachingDataProvider cache_only invariant (W4a)."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from indiciumforge_core.domain.models import AssetID, AssetType, Exchange
from indiciumforge_core.providers.caching import CachingDataProvider
from indiciumforge_core.providers.capabilities import DataKind, ProviderAuthorityLevel
from indiciumforge_core.providers.query import DataQuery
from indiciumforge_core.providers.result import (
    ProviderFailureStatus,
    ProviderProvenance,
    ProviderResult,
)
from indiciumforge_core.workflow.model import AssetDomain


class _FakeStore:
    """Minimal MarketDataStore stand-in returning a fixed cached frame."""

    def __init__(self, cached: pd.DataFrame | None = None) -> None:
        self._cached = cached if cached is not None else pd.DataFrame()
        self.writes = 0

    def fetch_ohlcv(self, asset_uid, *, start=None, end=None, as_of=None):
        return self._cached, None

    def write_ohlcv(self, asset_uid, frame, *, provenance=None) -> None:
        self.writes += 1


class _RecordingSource:
    """DataProviderPortV2 stand-in that counts fetch calls."""

    provider_id = "recording"
    authority_level = ProviderAuthorityLevel.PRIMARY
    capabilities = ()

    def __init__(self) -> None:
        self.fetch_calls = 0

    def supports_query(self, query: DataQuery) -> bool:
        return True

    def fetch(self, query: DataQuery) -> ProviderResult:
        self.fetch_calls += 1
        frame = pd.DataFrame({"date": [date(2024, 1, 2)], "open": [10.0], "high": [10.5],
                              "low": [9.8], "close": [10.2], "volume": [100000]})
        return ProviderResult(
            frame=frame,
            provenance=ProviderProvenance(
                provider_id="recording",
                authority_level=ProviderAuthorityLevel.PRIMARY,
                data_kind=DataKind.OHLCV,
                asset_domain=AssetDomain.CHINA_A_SHARE,
                captured_at="2024-01-02T00:00:00+00:00",
                as_of=date(2024, 1, 2),
            ),
        )


def _query() -> DataQuery:
    asset = AssetID(code="600000", exchange=Exchange.from_code("sse"), asset_type=AssetType.STOCK)
    return DataQuery(asset=asset, asset_domain=AssetDomain.CHINA_A_SHARE,
                     data_kind=DataKind.OHLCV, start=date(2024, 1, 1), end=date(2024, 6, 1))


def test_cache_only_miss_does_not_call_source() -> None:
    store = _FakeStore(cached=pd.DataFrame())  # cache miss
    source = _RecordingSource()
    cache = CachingDataProvider(source, store, cache_only=True)

    result = cache.fetch(_query())
    assert source.fetch_calls == 0  # source never touched
    assert result.provenance.failure_status == ProviderFailureStatus.EMPTY
    assert any("cache_only" in w for w in result.provenance.warnings)
    assert store.writes == 0


def test_cache_only_hit_returns_cached() -> None:
    cached = pd.DataFrame({"date": [date(2024, 1, 2)], "open": [10.0], "high": [10.5],
                           "low": [9.8], "close": [10.2], "volume": [100000]})
    store = _FakeStore(cached=cached)
    source = _RecordingSource()
    cache = CachingDataProvider(source, store, cache_only=True)

    result = cache.fetch(_query())
    assert source.fetch_calls == 0
    assert not result.frame.empty
    assert result.provenance.cache_hit is True


def test_default_delegates_to_source_on_miss() -> None:
    store = _FakeStore(cached=pd.DataFrame())  # miss
    source = _RecordingSource()
    cache = CachingDataProvider(source, store)  # cache_only defaults to False

    result = cache.fetch(_query())
    assert source.fetch_calls == 1  # source was called
    assert not result.frame.empty
    assert store.writes == 1  # healthy result persisted

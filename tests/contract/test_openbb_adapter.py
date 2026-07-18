"""Tests for the OpenBBDataProvider adapter (W5) — no network required.

The ``openbb`` package is injected as a fake module so the OBBject coercion,
column normalization, provenance, and error-handling logic are exercised
deterministically. The offline public demo never touches this provider (it
reads a committed sample panel), so these tests are the only OpenBB adapter
coverage and must remain network-free.
"""

from __future__ import annotations

import sys
import types
from datetime import date

import pandas as pd
import pytest
from indiciumforge_core.domain.models import AssetID, AssetType, Exchange
from indiciumforge_core.providers.capabilities import DataKind, ProviderAuthorityLevel
from indiciumforge_core.providers.openbb import OpenBBDataProvider
from indiciumforge_core.providers.query import DataQuery
from indiciumforge_core.providers.result import ProviderFailureStatus
from indiciumforge_core.workflow.model import AssetDomain


def _query(
    code: str = "AAPL",
    *,
    start: date = date(2024, 1, 1),
    end: date = date(2024, 6, 1),
) -> DataQuery:
    asset = OpenBBDataProvider.asset_from_ticker(code)
    return DataQuery(
        asset=asset,
        asset_domain=AssetDomain.US_EQUITY,
        data_kind=DataKind.OHLCV,
        start=start,
        end=end,
    )


class _FakeOBBject:
    """Mimics OpenBB's OBBject: exposes ``.to_dataframe()``."""

    def __init__(self, frame: pd.DataFrame) -> None:
        self._frame = frame

    def to_dataframe(self) -> pd.DataFrame:
        return self._frame


def _install_fake_openbb(
    monkeypatch: pytest.MonkeyPatch,
    *,
    result: object,
    raises: Exception | None = None,
) -> None:
    """Inject a fake ``openbb`` module exposing ``obb.equity.price.historical``."""

    def historical(**kwargs):  # noqa: ANN202
        if raises is not None:
            raise raises
        return result

    price = types.SimpleNamespace(historical=historical)
    equity = types.SimpleNamespace(price=price)
    obb = types.SimpleNamespace(equity=equity)
    mod = types.ModuleType("openbb")
    mod.obb = obb  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "openbb", mod)


def _sample_indexed_frame() -> pd.DataFrame:
    """OpenBB-style frame: DatetimeIndex named 'date', lowercase OHLCV columns."""
    idx = pd.to_datetime(["2024-01-02", "2024-01-03"])
    idx.name = "date"
    return pd.DataFrame(
        {
            "open": [185.0, 186.0],
            "high": [187.0, 188.5],
            "low": [184.0, 185.5],
            "close": [186.5, 188.0],
            "volume": [50_000_000, 48_000_000],
        },
        index=idx,
    )


def test_provider_identity() -> None:
    p = OpenBBDataProvider()
    assert p.provider_id == "openbb"
    assert p.authority_level == ProviderAuthorityLevel.PRIMARY
    assert p.capabilities[0].data_kind == DataKind.OHLCV
    assert p.capabilities[0].asset_domain == AssetDomain.US_EQUITY
    assert "xnas" in p.capabilities[0].venues


def test_supports_query_gating() -> None:
    p = OpenBBDataProvider()
    assert p.supports_query(_query("AAPL")) is True
    assert p.supports_query(_query("BRK.B")) is True  # dot class suffix allowed
    # A-share numeric code rejected (wrong domain + non-alpha).
    bad = DataQuery(
        asset=AssetID(
            code="600000", exchange=Exchange.from_code("sse"), asset_type=AssetType.STOCK
        ),
        asset_domain=AssetDomain.CHINA_A_SHARE,
        data_kind=DataKind.OHLCV,
    )
    assert p.supports_query(bad) is False


def test_normalize_from_obbject(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_openbb(monkeypatch, result=_FakeOBBject(_sample_indexed_frame()))
    p = OpenBBDataProvider()
    result = p.fetch(_query())
    assert result.provenance.failure_status == ProviderFailureStatus.OK
    assert list(result.frame.columns) == ["date", "open", "high", "low", "close", "volume"]
    assert len(result.frame) == 2
    assert isinstance(result.frame["date"].iloc[0], date)
    assert result.provenance.provider_id == "openbb"
    assert result.provenance.cache_hit is False
    assert result.provenance.as_of == date(2024, 1, 3)


def test_normalize_from_plain_dataframe(monkeypatch: pytest.MonkeyPatch) -> None:
    # A plain DataFrame (with a 'date' column) is accepted directly.
    frame = _sample_indexed_frame().reset_index()
    _install_fake_openbb(monkeypatch, result=frame)
    p = OpenBBDataProvider()
    result = p.fetch(_query())
    assert result.provenance.failure_status == ProviderFailureStatus.OK
    assert len(result.frame) == 2


def test_empty_range_returns_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_openbb(monkeypatch, result=pd.DataFrame())
    p = OpenBBDataProvider()
    result = p.fetch(_query())
    assert result.provenance.failure_status == ProviderFailureStatus.EMPTY
    assert result.frame.empty


def test_exception_returns_provider_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_openbb(
        monkeypatch, result=None, raises=RuntimeError("vendor rate limit")
    )
    p = OpenBBDataProvider()
    result = p.fetch(_query())
    assert result.provenance.failure_status == ProviderFailureStatus.PROVIDER_ERROR
    assert any("vendor rate limit" in w for w in result.provenance.warnings)
    assert result.frame.empty


def test_unsupported_query_returns_missing_capability() -> None:
    p = OpenBBDataProvider()
    bad = DataQuery(
        asset=AssetID(
            code="600000", exchange=Exchange.from_code("sse"), asset_type=AssetType.STOCK
        ),
        asset_domain=AssetDomain.CHINA_A_SHARE,
        data_kind=DataKind.OHLCV,
    )
    result = p.fetch(bad)
    assert result.provenance.failure_status == ProviderFailureStatus.MISSING_CAPABILITY


def test_missing_extra_raises_helpful_import_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Ensure a real/absent openbb import surfaces the install hint through fetch().
    monkeypatch.setitem(sys.modules, "openbb", None)
    p = OpenBBDataProvider()
    result = p.fetch(_query())
    assert result.provenance.failure_status == ProviderFailureStatus.PROVIDER_ERROR
    assert any("indiciumforge-core[openbb]" in w for w in result.provenance.warnings)


def test_asset_from_ticker() -> None:
    asset = OpenBBDataProvider.asset_from_ticker("nvda")
    assert asset.uid == "xnas:stock:NVDA"
    assert asset.currency == "USD"
    # Explicit NYSE exchange.
    nyse = OpenBBDataProvider.asset_from_ticker("BAC", exchange="xnys")
    assert nyse.uid == "xnys:stock:BAC"

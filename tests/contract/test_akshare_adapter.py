"""Tests for the AkshareDataProvider adapter (W4a) — no network required.

akshare is injected as a fake module so the normalization / provenance /
error-handling logic is exercised deterministically.
"""

from __future__ import annotations

import sys
import types
from datetime import date

import pandas as pd
import pytest
from indiciumforge_core.domain.models import AssetID, AssetType, Exchange
from indiciumforge_core.providers.akshare import AkshareDataProvider, _exchange_for_code
from indiciumforge_core.providers.capabilities import DataKind, ProviderAuthorityLevel
from indiciumforge_core.providers.query import DataQuery
from indiciumforge_core.providers.result import ProviderFailureStatus
from indiciumforge_core.workflow.model import AssetDomain


def _query(
    code: str = "600000",
    *,
    start: date = date(2024, 1, 1),
    end: date = date(2024, 6, 1),
) -> DataQuery:
    asset = AssetID(
        code=code,
        exchange=_exchange_for_code(code),
        asset_type=AssetType.STOCK,
        currency="CNY",
    )
    return DataQuery(
        asset=asset,
        asset_domain=AssetDomain.CHINA_A_SHARE,
        data_kind=DataKind.OHLCV,
        start=start,
        end=end,
    )


def _fake_akshare_module(
    frame: pd.DataFrame | None = None,
    *,
    raises: Exception | None = None,
) -> types.ModuleType:
    mod = types.ModuleType("akshare")

    def stock_zh_a_hist(**kwargs):  # noqa: ANN202
        if raises is not None:
            raise raises
        return frame

    mod.stock_zh_a_hist = stock_zh_a_hist  # type: ignore[attr-defined]
    return mod


def _sample_raw_frame() -> pd.DataFrame:
    return pd.DataFrame({
        "日期": ["2024-01-02", "2024-01-03"],
        "开盘": [10.0, 10.5],
        "收盘": [10.2, 10.3],
        "最高": [10.5, 10.6],
        "最低": [9.9, 10.1],
        "成交量": [100000, 120000],
        "成交额": [1020000.0, 1236000.0],
        "振幅": [5.88, 4.81],
        "涨跌幅": [2.0, 0.98],
        "涨跌额": [0.2, 0.1],
        "换手率": [0.5, 0.6],
    })


def test_provider_identity() -> None:
    p = AkshareDataProvider()
    assert p.provider_id == "akshare"
    assert p.authority_level == ProviderAuthorityLevel.PRIMARY
    assert p.capabilities[0].data_kind == DataKind.OHLCV
    assert p.capabilities[0].asset_domain == AssetDomain.CHINA_A_SHARE


def test_supports_query_gating() -> None:
    p = AkshareDataProvider()
    assert p.supports_query(_query("600000")) is True
    # Non-digit code rejected.
    bad = DataQuery(
        asset=AssetID(code="AAPL", exchange=Exchange.from_code("xnas"),
                      asset_type=AssetType.STOCK),
        asset_domain=AssetDomain.US_EQUITY,
        data_kind=DataKind.OHLCV,
    )
    assert p.supports_query(bad) is False


def test_normalize_maps_chinese_columns(monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _fake_akshare_module(_sample_raw_frame())
    monkeypatch.setitem(sys.modules, "akshare", mod)
    p = AkshareDataProvider()
    result = p.fetch(_query())
    assert result.provenance.failure_status == ProviderFailureStatus.OK
    assert list(result.frame.columns) == ["date", "open", "high", "low", "close", "volume"]
    assert len(result.frame) == 2
    assert isinstance(result.frame["date"].iloc[0], date)
    assert result.provenance.provider_id == "akshare"
    assert result.provenance.cache_hit is False


def test_empty_range_returns_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _fake_akshare_module(pd.DataFrame())
    monkeypatch.setitem(sys.modules, "akshare", mod)
    p = AkshareDataProvider()
    result = p.fetch(_query())
    assert result.provenance.failure_status == ProviderFailureStatus.EMPTY
    assert result.frame.empty


def test_exception_returns_provider_error(monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _fake_akshare_module(raises=RuntimeError("network timeout"))
    monkeypatch.setitem(sys.modules, "akshare", mod)
    p = AkshareDataProvider()
    result = p.fetch(_query())
    assert result.provenance.failure_status == ProviderFailureStatus.PROVIDER_ERROR
    assert any("network timeout" in w for w in result.provenance.warnings)
    assert result.frame.empty


def test_unsupported_query_returns_missing_capability() -> None:
    p = AkshareDataProvider()
    bad = DataQuery(
        asset=AssetID(code="AAPL", exchange=Exchange.from_code("xnas"),
                      asset_type=AssetType.STOCK),
        asset_domain=AssetDomain.US_EQUITY,
        data_kind=DataKind.OHLCV,
    )
    result = p.fetch(bad)
    assert result.provenance.failure_status == ProviderFailureStatus.MISSING_CAPABILITY


def test_exchange_for_code_mapping() -> None:
    assert _exchange_for_code("600000").code == "sse"
    assert _exchange_for_code("000001").code == "szse"
    assert _exchange_for_code("300750").code == "szse"
    assert _exchange_for_code("830799").code == "bse_cn"


def test_asset_from_code() -> None:
    p = AkshareDataProvider()
    asset = p.asset_from_code("600519")
    assert asset.uid == "sse:stock:600519"
    assert asset.currency == "CNY"

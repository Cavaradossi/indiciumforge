from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from indiciumforge_core.domain.models import AssetID, AssetType, Exchange, MissingData
from indiciumforge_core.providers.local_fixture import LocalFixtureProvider
from indiciumforge_core.providers.registry import ProviderRegistry
from provider_stubs import FailingProvider, SuccessProvider

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "ohlcv"
ASSET = AssetID("600000", Exchange.SSE, AssetType.STOCK)


def test_fixture_provider_supports_existing_fixture() -> None:
    provider = LocalFixtureProvider(FIXTURE_ROOT)

    assert provider.supports(ASSET) is True
    assert provider.supports(AssetID("999999", Exchange.SSE, AssetType.STOCK)) is False


def test_fixture_provider_fetch_ohlcv_full_series() -> None:
    provider = LocalFixtureProvider(FIXTURE_ROOT)

    frame, provenance = provider.fetch_ohlcv(ASSET)

    assert provenance.provider == "local_fixture"
    assert provenance.tier == "fixture"
    assert provenance.as_of == date(2026, 4, 30)
    assert len(frame) == 3
    assert list(frame.columns) == ["date", "open", "high", "low", "close", "volume"]


def test_fixture_provider_fetch_ohlcv_date_range() -> None:
    provider = LocalFixtureProvider(FIXTURE_ROOT)

    frame, provenance = provider.fetch_ohlcv(
        ASSET,
        start=date(2026, 4, 29),
        end=date(2026, 4, 30),
    )

    assert len(frame) == 2
    assert provenance.as_of == date(2026, 4, 30)


def test_fixture_provider_missing_fixture_raises_missing_data(tmp_path: Path) -> None:
    provider = LocalFixtureProvider(tmp_path)

    with pytest.raises(MissingData, match="missing fixture"):
        provider.fetch_ohlcv(ASSET)


def test_registry_prefers_earlier_provider_over_fixture() -> None:
    registry = ProviderRegistry([SuccessProvider(), LocalFixtureProvider(FIXTURE_ROOT)])

    frame, provenance = registry.fetch_ohlcv(ASSET)

    assert provenance.provider == "success"
    assert len(frame) == 1


def test_registry_falls_back_to_fixture_provider() -> None:
    registry = ProviderRegistry([FailingProvider(), LocalFixtureProvider(FIXTURE_ROOT)])

    frame, provenance = registry.fetch_ohlcv(ASSET)

    assert provenance.provider == "local_fixture"
    assert len(frame) == 3
    assert any("simulated timeout" in warning for warning in provenance.warnings)

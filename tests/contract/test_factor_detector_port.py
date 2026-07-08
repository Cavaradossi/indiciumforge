from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
from lucerna_core.domain.models import AssetID, AssetType, Exchange
from lucerna_core.factors.demo import DemoQuietAccumulationDetector, DemoVolumeBreakoutDetector
from lucerna_core.providers.local_fixture import LocalFixtureProvider

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "ohlcv"
AS_OF = date(2026, 5, 6)
DEMO001 = AssetID("DEMO001", Exchange.SSE, AssetType.STOCK)
DEMO002 = AssetID("DEMO002", Exchange.SSE, AssetType.STOCK)


def _load_fixture(asset: AssetID) -> pd.DataFrame:
    provider = LocalFixtureProvider(FIXTURE_ROOT)
    frame, _ = provider.fetch_ohlcv(asset)
    return frame


def test_demo_volume_breakout_matches_synthetic_fixture() -> None:
    detector = DemoVolumeBreakoutDetector()
    frame = _load_fixture(DEMO001)

    signal = detector.detect(DEMO001, frame, AS_OF)

    assert signal is not None
    assert signal.matched is True
    assert signal.factor == "demo_volume_breakout"
    assert signal.score is not None
    assert signal.score > 2.0


def test_demo_volume_breakout_misses_on_insufficient_bars() -> None:
    detector = DemoVolumeBreakoutDetector()
    frame = _load_fixture(DEMO001).head(3)

    signal = detector.detect(DEMO001, frame, AS_OF)

    assert signal is not None
    assert signal.matched is False


def test_demo_quiet_accumulation_matches_synthetic_fixture() -> None:
    detector = DemoQuietAccumulationDetector()
    frame = _load_fixture(DEMO002)
    as_of = date(2026, 5, 10)

    signal = detector.detect(DEMO002, frame, as_of)

    assert signal is not None
    assert signal.matched is True
    assert signal.factor == "demo_quiet_accumulation"


def test_demo_detectors_support_all_assets() -> None:
    assert DemoVolumeBreakoutDetector().supports(DEMO001) is True
    assert DemoQuietAccumulationDetector().supports(DEMO002) is True

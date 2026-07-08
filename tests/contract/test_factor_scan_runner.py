from __future__ import annotations

from datetime import date
from pathlib import Path

from lucerna_core.domain.models import AssetID, AssetType, Exchange
from lucerna_core.factors.demo import DemoQuietAccumulationDetector, DemoVolumeBreakoutDetector
from lucerna_core.factors.registry import FactorDetectorRegistry
from lucerna_core.factors.scan import FactorScanRunner
from lucerna_core.providers.local_fixture import LocalFixtureProvider
from lucerna_core.providers.registry import ProviderRegistry
from provider_stubs import FailingProvider

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "ohlcv"
AS_OF = date(2026, 5, 10)
DEMO001 = AssetID("DEMO001", Exchange.SSE, AssetType.STOCK)
DEMO002 = AssetID("DEMO002", Exchange.SSE, AssetType.STOCK)


def test_scan_runner_runs_demo_detectors_on_multiple_assets() -> None:
    provider_registry = ProviderRegistry([LocalFixtureProvider(FIXTURE_ROOT)])
    detector_registry = FactorDetectorRegistry(
        [DemoVolumeBreakoutDetector(), DemoQuietAccumulationDetector()]
    )
    runner = FactorScanRunner(provider_registry, detector_registry)

    result = runner.scan([DEMO001, DEMO002], AS_OF)

    assert len(result.signals) == 4
    keyed = {(signal.asset.code, signal.factor): signal for signal in result.signals}
    assert keyed[("DEMO001", "demo_volume_breakout")].matched is True
    assert keyed[("DEMO002", "demo_quiet_accumulation")].matched is True
    assert result.detector_runs == ("demo_volume_breakout", "demo_quiet_accumulation")


def test_scan_runner_preserves_provider_warnings() -> None:
    provider_registry = ProviderRegistry([FailingProvider(), LocalFixtureProvider(FIXTURE_ROOT)])
    detector_registry = FactorDetectorRegistry([DemoVolumeBreakoutDetector()])
    runner = FactorScanRunner(provider_registry, detector_registry)

    result = runner.scan([DEMO001], AS_OF)

    assert any("simulated timeout" in warning for warning in result.warnings)
    assert len(result.signals) == 1

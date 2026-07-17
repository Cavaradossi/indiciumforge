from __future__ import annotations

from datetime import date
from pathlib import Path

from indiciumforge_core.domain.models import AssetID, AssetType, Exchange
from indiciumforge_core.factors.demo import (
    DemoQuietAccumulationDetector,
    DemoVolumeBreakoutDetector,
)
from indiciumforge_core.factors.registry import FactorDetectorRegistry
from indiciumforge_core.factors.scan import FactorScanRunner
from indiciumforge_core.providers.local_fixture import LocalFixtureProvider
from indiciumforge_core.providers.registry import ProviderRegistry
from provider_stubs import FailingProvider

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "ohlcv"
AS_OF = date(2026, 5, 10)
DEMO001 = AssetID("DEMO001", Exchange.SSE, AssetType.STOCK)
DEMO002 = AssetID("DEMO002", Exchange.SSE, AssetType.STOCK)
DEMO999 = AssetID("DEMO999", Exchange.SSE, AssetType.STOCK)  # no fixture -> empty


def _runner(providers) -> FactorScanRunner:
    detector_registry = FactorDetectorRegistry(
        [DemoVolumeBreakoutDetector(), DemoQuietAccumulationDetector()]
    )
    return FactorScanRunner(providers, detector_registry)


def test_parallel_matches_serial() -> None:
    providers = ProviderRegistry([LocalFixtureProvider(FIXTURE_ROOT)])
    runner = _runner(providers)
    assets = [DEMO001, DEMO002]

    serial = runner.scan(assets, AS_OF)
    parallel = runner.scan(assets, AS_OF, max_workers=2)

    assert serial == parallel
    assert len(serial.signals) == 4


def test_parallel_matches_serial_with_provider_warnings() -> None:
    # FailingProvider first -> every asset carries a "simulated timeout" warning,
    # exercising the warning-merge path under parallelism.
    providers = ProviderRegistry(
        [FailingProvider(), LocalFixtureProvider(FIXTURE_ROOT)]
    )
    runner = _runner(providers)
    assets = [DEMO001, DEMO002]

    serial = runner.scan(assets, AS_OF)
    parallel = runner.scan(assets, AS_OF, max_workers=2)

    assert serial == parallel
    assert any("simulated timeout" in w for w in serial.warnings)


def test_parallel_matches_serial_with_empty_asset() -> None:
    # DEMO999 has no fixture -> empty frame. Mixed order (data, empty, data)
    # proves per-asset warning interleaving matches the serial path.
    providers = ProviderRegistry(
        [FailingProvider(), LocalFixtureProvider(FIXTURE_ROOT)]
    )
    runner = _runner(providers)
    assets = [DEMO001, DEMO999, DEMO002]

    serial = runner.scan(assets, AS_OF)
    parallel = runner.scan(assets, AS_OF, max_workers=2)

    assert serial == parallel
    assert any("DEMO999: empty ohlcv" in w for w in serial.warnings)


def test_max_workers_one_falls_back_to_serial() -> None:
    providers = ProviderRegistry([LocalFixtureProvider(FIXTURE_ROOT)])
    runner = _runner(providers)
    assets = [DEMO001, DEMO002]

    serial = runner.scan(assets, AS_OF)
    single = runner.scan(assets, AS_OF, max_workers=1)

    assert serial == single

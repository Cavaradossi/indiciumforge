from __future__ import annotations

from datetime import date

import pandas as pd
import pytest
from factor_stubs import EmptyDetector, FailingDetector, SuccessDetector
from indiciumforge_core.domain.models import AssetID, AssetType, Exchange
from indiciumforge_core.factors.demo import DemoVolumeBreakoutDetector
from indiciumforge_core.factors.registry import DuplicateDetectorError, FactorDetectorRegistry

AS_OF = date(2026, 5, 6)
ASSET = AssetID("DEMO001", Exchange.SSE, AssetType.STOCK)
FRAME = pd.DataFrame(
    [
        {"date": "2026-05-01", "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1},
    ]
)


def test_registry_registers_and_lists_detectors() -> None:
    registry = FactorDetectorRegistry([DemoVolumeBreakoutDetector(), EmptyDetector()])

    assert registry.list_detectors() == ("demo_volume_breakout", "empty_detector")


def test_registry_rejects_duplicate_names() -> None:
    registry = FactorDetectorRegistry([DemoVolumeBreakoutDetector()])

    with pytest.raises(DuplicateDetectorError, match="already registered"):
        registry.register(DemoVolumeBreakoutDetector())


def test_registry_runs_selected_detectors() -> None:
    registry = FactorDetectorRegistry(
        [SuccessDetector(), EmptyDetector(), DemoVolumeBreakoutDetector()]
    )

    result = registry.run(ASSET, FRAME, AS_OF, detectors=["success_detector", "empty_detector"])

    assert len(result.signals) == 1
    assert result.signals[0].factor == "success_detector"
    assert result.detector_runs == ("success_detector", "empty_detector")


def test_registry_aggregates_detector_failures_as_warnings() -> None:
    registry = FactorDetectorRegistry([FailingDetector(), SuccessDetector()])

    result = registry.run(ASSET, FRAME, AS_OF)

    assert len(result.signals) == 1
    assert any("simulated detector failure" in warning for warning in result.warnings)

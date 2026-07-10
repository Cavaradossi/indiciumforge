from __future__ import annotations

from datetime import date

import pandas as pd

from indiciumforge_core.domain.models import AssetID
from indiciumforge_core.factors.models import FactorScanResult, FactorSignal
from indiciumforge_core.factors.ports import FactorDetectorPort


class DuplicateDetectorError(ValueError):
    """Raised when registering a detector with an existing name."""


class FactorDetectorRegistry:
    def __init__(self, detectors: list[FactorDetectorPort] | None = None) -> None:
        self._detectors: dict[str, FactorDetectorPort] = {}
        for detector in detectors or []:
            self.register(detector)

    def register(self, detector: FactorDetectorPort) -> None:
        if detector.name in self._detectors:
            raise DuplicateDetectorError(f"detector already registered: {detector.name}")
        self._detectors[detector.name] = detector

    def list_detectors(self) -> tuple[str, ...]:
        return tuple(self._detectors.keys())

    def run(
        self,
        asset: AssetID,
        ohlcv: pd.DataFrame,
        as_of: date,
        detectors: list[str] | None = None,
    ) -> FactorScanResult:
        selected = self._select_detectors(detectors)
        signals: list[FactorSignal] = []
        warnings: list[str] = []
        detector_runs: list[str] = []

        for name, detector in selected:
            detector_runs.append(name)
            if not detector.supports(asset):
                continue
            try:
                signal = detector.detect(asset, ohlcv, as_of)
            except Exception as exc:  # noqa: BLE001 - aggregate warnings without crashing scan
                warnings.append(f"{name}: {exc}")
                continue
            if signal is not None:
                signals.append(signal)

        return FactorScanResult(
            as_of=as_of,
            signals=tuple(signals),
            warnings=tuple(warnings),
            detector_runs=tuple(detector_runs),
        )

    def _select_detectors(
        self,
        detectors: list[str] | None,
    ) -> list[tuple[str, FactorDetectorPort]]:
        if detectors is None:
            return list(self._detectors.items())

        selected: list[tuple[str, FactorDetectorPort]] = []
        for name in detectors:
            detector = self._detectors.get(name)
            if detector is None:
                continue
            selected.append((name, detector))
        return selected

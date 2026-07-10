from __future__ import annotations

from datetime import date

from indiciumforge_core.domain.models import AssetID
from indiciumforge_core.factors.models import FactorScanResult, FactorSignal
from indiciumforge_core.factors.registry import FactorDetectorRegistry
from indiciumforge_core.providers.registry import ProviderRegistry


class FactorScanRunner:
    def __init__(
        self,
        provider_registry: ProviderRegistry,
        detector_registry: FactorDetectorRegistry,
    ) -> None:
        self._providers = provider_registry
        self._detectors = detector_registry

    def scan(
        self,
        assets: list[AssetID],
        as_of: date,
        detectors: list[str] | None = None,
        start: date | None = None,
        end: date | None = None,
    ) -> FactorScanResult:
        signals: list[FactorSignal] = []
        warnings: list[str] = []
        detector_runs: list[str] = []

        for asset in assets:
            frame, provenance = self._providers.fetch_ohlcv(asset, start=start, end=end)
            warnings.extend(provenance.warnings)
            if frame.empty:
                warnings.append(f"{asset.uid}: empty ohlcv")
                continue

            effective_as_of = provenance.as_of or as_of
            result = self._detectors.run(
                asset,
                frame,
                effective_as_of,
                detectors=detectors,
            )
            signals.extend(result.signals)
            warnings.extend(result.warnings)
            for name in result.detector_runs:
                if name not in detector_runs:
                    detector_runs.append(name)

        return FactorScanResult(
            as_of=as_of,
            signals=tuple(signals),
            warnings=tuple(warnings),
            detector_runs=tuple(detector_runs),
        )

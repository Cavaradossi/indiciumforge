from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

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
        *,
        max_workers: int | None = None,
    ) -> FactorScanResult:
        """Scan ``assets`` for factor signals.

        ``max_workers`` is opt-in parallelism (W3). When ``None``/``<=1``/single
        asset, runs serially (legacy behavior). Otherwise the CPU-bound detector
        step is fanned out across a process pool while OHLCV fetching stays on
        the main process — providers are deliberately kept out of the pickle
        boundary (they may hold non-picklable handles/sessions). Results are
        merged in deterministic asset order so serial and parallel runs are
        bit-for-bit identical for the same inputs.
        """
        if max_workers is None or max_workers <= 1 or len(assets) <= 1:
            return self._scan_serial(assets, as_of, detectors, start, end)

        # Fetch on the main process (provider I/O / sessions stay here).
        fetched: dict[str, pd.DataFrame] = {}
        provider_warnings: dict[str, list[str]] = {}
        effective_as_of: dict[str, date] = {}
        for asset in assets:
            frame, provenance = self._providers.fetch_ohlcv(asset, start=start, end=end)
            provider_warnings[asset.uid] = list(provenance.warnings)
            if frame.empty:
                continue
            fetched[asset.uid] = frame
            # Mirror the serial path: prefer the provenance's own as_of.
            effective_as_of[asset.uid] = provenance.as_of or as_of

        args = [
            (
                asset,
                fetched[asset.uid],
                provider_warnings[asset.uid],
                effective_as_of[asset.uid],
                detectors,
                self._detectors,
            )
            for asset in assets
            if asset.uid in fetched
        ]

        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # executor.map is ordered; key results by uid so the merge below
            # can walk assets in input order regardless of worker scheduling.
            results = {
                arg[0].uid: res
                for arg, res in zip(args, executor.map(_detect_asset, args))
            }

        signals: list[FactorSignal] = []
        warnings: list[str] = []
        detector_runs: list[str] = []
        # Merge in asset input order so the output is byte-for-byte identical
        # to the serial path: per asset -> provider warnings, then either the
        # empty marker or the detector warnings. This is what guarantees
        # `scan(..., max_workers=N) == scan(...)` for the same inputs
        # (including the mixed empty/non-empty asset case).
        for asset in assets:
            uid = asset.uid
            warnings.extend(provider_warnings[uid])
            if uid not in fetched:
                warnings.append(f"{uid}: empty ohlcv")
                continue
            result = results[uid]
            warnings.extend(result.warnings)
            signals.extend(result.signals)
            for name in result.detector_runs:
                if name not in detector_runs:
                    detector_runs.append(name)

        return FactorScanResult(
            as_of=as_of,
            signals=tuple(signals),
            warnings=tuple(warnings),
            detector_runs=tuple(detector_runs),
        )

    def _scan_serial(
        self,
        assets: list[AssetID],
        as_of: date,
        detectors: list[str] | None,
        start: date | None,
        end: date | None,
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


def _detect_asset(args: tuple[Any, ...]) -> FactorScanResult:
    """Module-level worker (picklable by reference) for the process pool."""
    _asset, frame, _pwarn, as_of, detectors, registry = args
    return registry.run(_asset, frame, as_of, detectors=detectors)

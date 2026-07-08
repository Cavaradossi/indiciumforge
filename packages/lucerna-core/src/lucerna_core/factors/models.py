from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from lucerna_core.domain.models import AssetID


@dataclass(frozen=True)
class FactorSignal:
    asset: AssetID
    factor: str
    as_of: date
    matched: bool
    score: float | None = None
    metrics: dict[str, float | int | str] = field(default_factory=dict)


@dataclass(frozen=True)
class FactorScanResult:
    as_of: date
    signals: tuple[FactorSignal, ...]
    warnings: tuple[str, ...] = ()
    detector_runs: tuple[str, ...] = ()

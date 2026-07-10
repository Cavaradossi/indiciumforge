from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class ThemeSectorMetrics:
    theme_name: str
    sample_count: int
    median_1d: float
    median_3d: float
    up_rate: float
    relative_1d: float = 0.0
    ge5_ratio: float = 0.0
    le_minus5_ratio: float = 0.0
    limit_up_count: int = 0
    limit_down_count: int = 0


@dataclass(frozen=True)
class ThemeStateRow:
    theme_name: str
    status: str
    daily_state: str
    mid_state: str
    risk_state: str
    divergence_state: str


@dataclass(frozen=True)
class DailyReviewResult:
    trade_date: date
    rows: tuple[ThemeStateRow, ...]
    warnings: tuple[str, ...] = ()
    fixture_path: Path | None = None
    theme_state_ranking_path: Path | None = None
    state_path: Path | None = None

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml

from lucerna_workflow.market_awareness.models import ThemeSectorMetrics


class ThemeFixtureLoadError(ValueError):
    """Raised when a theme sector fixture cannot be parsed."""


def load_theme_sector_fixture(path: Path) -> tuple[date, list[ThemeSectorMetrics]]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ThemeFixtureLoadError("fixture root must be a mapping")

    trade_date_raw = payload.get("trade_date")
    if not trade_date_raw:
        raise ThemeFixtureLoadError("fixture requires trade_date")
    trade_date = date.fromisoformat(str(trade_date_raw))

    themes = payload.get("themes")
    if not isinstance(themes, list) or not themes:
        raise ThemeFixtureLoadError("fixture requires non-empty themes list")

    metrics: list[ThemeSectorMetrics] = []
    for index, entry in enumerate(themes):
        if not isinstance(entry, dict):
            raise ThemeFixtureLoadError(f"theme entry {index} must be a mapping")
        metrics.append(_parse_theme_entry(entry, index))
    return trade_date, metrics


def _parse_theme_entry(entry: dict[str, Any], index: int) -> ThemeSectorMetrics:
    theme_name = entry.get("theme_name")
    if not theme_name:
        raise ThemeFixtureLoadError(f"theme entry {index} missing theme_name")
    required = ("sample_count", "median_1d", "median_3d", "up_rate")
    for field in required:
        if field not in entry:
            raise ThemeFixtureLoadError(f"theme entry {index} missing {field}")
    return ThemeSectorMetrics(
        theme_name=str(theme_name),
        sample_count=int(entry["sample_count"]),
        median_1d=float(entry["median_1d"]),
        median_3d=float(entry["median_3d"]),
        up_rate=float(entry["up_rate"]),
        relative_1d=float(entry.get("relative_1d", 0.0)),
        ge5_ratio=float(entry.get("ge5_ratio", 0.0)),
        le_minus5_ratio=float(entry.get("le_minus5_ratio", 0.0)),
        limit_up_count=int(entry.get("limit_up_count", 0)),
        limit_down_count=int(entry.get("limit_down_count", 0)),
    )

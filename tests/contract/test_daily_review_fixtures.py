from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from indiciumforge_workflow.market_awareness.fixtures import (
    ThemeFixtureLoadError,
    load_theme_sector_fixture,
)

ROOT = Path(__file__).resolve().parents[2]
DEMO_FIXTURE = ROOT / "tests" / "fixtures" / "market_awareness" / "theme_sectors_demo.yaml"


def test_load_theme_sector_fixture_reads_demo_file() -> None:
    trade_date, metrics = load_theme_sector_fixture(DEMO_FIXTURE)

    assert trade_date == date(2026, 6, 23)
    assert len(metrics) == 3
    assert metrics[0].sample_count == 40


def test_load_theme_sector_fixture_rejects_missing_themes(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("trade_date: 2026-06-23\n", encoding="utf-8")

    with pytest.raises(ThemeFixtureLoadError, match="themes"):
        load_theme_sector_fixture(path)

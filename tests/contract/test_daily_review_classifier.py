from __future__ import annotations

from pathlib import Path

from lucerna_core.labels.market_gate import MARKET_DAILY
from lucerna_workflow.market_awareness.classifier import classify_theme_state
from lucerna_workflow.market_awareness.fixtures import load_theme_sector_fixture
from lucerna_workflow.market_awareness.models import ThemeSectorMetrics

ROOT = Path(__file__).resolve().parents[2]
DEMO_FIXTURE = ROOT / "tests" / "fixtures" / "market_awareness" / "theme_sectors_demo.yaml"


def test_classify_daily_strong_theme() -> None:
    metrics = ThemeSectorMetrics(
        theme_name="strong",
        sample_count=40,
        median_1d=0.02,
        median_3d=0.04,
        up_rate=0.75,
        relative_1d=0.018,
        ge5_ratio=0.08,
        limit_up_count=3,
    )

    row = classify_theme_state(metrics)

    assert row.status == MARKET_DAILY["daily_strong"]
    assert row.daily_state == MARKET_DAILY["daily_strong"]


def test_classify_hard_weak_theme() -> None:
    metrics = ThemeSectorMetrics(
        theme_name="weak",
        sample_count=40,
        median_1d=-0.03,
        median_3d=-0.01,
        up_rate=0.25,
        le_minus5_ratio=0.15,
        limit_down_count=3,
    )

    row = classify_theme_state(metrics)

    assert row.status == MARKET_DAILY["hard_weak"]
    assert row.risk_state == MARKET_DAILY["hard_weak"]


def test_classify_turn_weak_theme() -> None:
    metrics = ThemeSectorMetrics(
        theme_name="turn",
        sample_count=40,
        median_1d=-0.005,
        median_3d=0.05,
        up_rate=0.40,
        le_minus5_ratio=0.10,
    )

    row = classify_theme_state(metrics)

    assert row.status == MARKET_DAILY["mid_strong_daily_weak"]
    assert row.mid_state == MARKET_DAILY["mid_strong"]


def test_demo_fixture_produces_golden_compatible_labels() -> None:
    _, metrics = load_theme_sector_fixture(DEMO_FIXTURE)
    rows = [classify_theme_state(item) for item in metrics]

    by_name = {row.theme_name: row for row in rows}
    assert "\u5f3a\u65b9\u5411" in by_name
    assert by_name["\u5f3a\u65b9\u5411"].status == MARKET_DAILY["daily_strong"]
    assert by_name["\u786c\u5f31\u65b9\u5411"].status == MARKET_DAILY["hard_weak"]
    assert by_name["\u8f6c\u5f31\u65b9\u5411"].status == MARKET_DAILY["mid_strong_daily_weak"]

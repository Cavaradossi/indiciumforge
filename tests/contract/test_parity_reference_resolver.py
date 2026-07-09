from __future__ import annotations

from datetime import date
from pathlib import Path

from lucerna_core.parity.reference import ReferenceArtifactProvider

ROOT = Path(__file__).resolve().parents[2]
REFERENCE_ROOT = ROOT / "tests" / "fixtures" / "parity_reference_demo" / "reference"
TRADE_DATE = date(2026, 6, 23)


def test_reference_provider_resolves_ig_shaped_paths() -> None:
    provider = ReferenceArtifactProvider(REFERENCE_ROOT)

    assert provider.daily_review_dir(TRADE_DATE).is_dir()
    assert (provider.daily_review_dir(TRADE_DATE) / "theme_state_ranking.csv").is_file()
    assert provider.post_close_dir(TRADE_DATE).is_dir()
    assert provider.preopen_dir(TRADE_DATE).is_dir()
    assert provider.market_gate_dir(TRADE_DATE).is_dir()
    assert (provider.market_gate_dir(TRADE_DATE) / "market_gate_summary.json").is_file()

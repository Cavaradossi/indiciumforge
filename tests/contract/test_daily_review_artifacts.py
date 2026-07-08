from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from lucerna_core.labels.market_gate import MARKET_DAILY, MARKET_ZH
from lucerna_workflow.market_awareness.artifacts import (
    THEME_STATE_RANKING_COLUMNS,
    theme_state_rows_to_frame,
    write_daily_review_state,
    write_theme_state_ranking,
)
from lucerna_workflow.market_awareness.models import ThemeStateRow

STRONG = "\u5f3a\u65b9\u5411"


def test_theme_state_rows_to_frame_has_gate_columns() -> None:
    row = ThemeStateRow(
        theme_name=STRONG,
        status=MARKET_DAILY["daily_strong"],
        daily_state=MARKET_DAILY["daily_strong"],
        mid_state=MARKET_ZH["neutral_theme"],
        risk_state=MARKET_DAILY["normal_risk"],
        divergence_state=MARKET_DAILY["normal_divergence"],
    )

    frame = theme_state_rows_to_frame([row])

    assert list(frame.columns) == list(THEME_STATE_RANKING_COLUMNS)
    assert frame.iloc[0][MARKET_ZH["theme_name"]] == STRONG


def test_write_daily_review_state_uses_lucerna_schema(tmp_path: Path) -> None:
    ranking = tmp_path / "theme_state_ranking.csv"
    ranking.write_text("x", encoding="utf-8")
    state_path = tmp_path / "market_daily_review_state.json"

    write_daily_review_state(
        state_path,
        trade_date=date(2026, 6, 23),
        theme_state_ranking_path=ranking,
        fixture_name="theme_sectors_demo.yaml",
    )

    payload = json.loads(state_path.read_text(encoding="utf-8-sig"))
    assert payload["schema"] == "lucerna.market_daily_review_state.v1"
    assert payload["provenance"]["source"] == "synthetic_fixture"


def test_write_theme_state_ranking_creates_csv(tmp_path: Path) -> None:
    row = ThemeStateRow(
        theme_name=STRONG,
        status=MARKET_DAILY["daily_strong"],
        daily_state=MARKET_DAILY["daily_strong"],
        mid_state=MARKET_ZH["neutral_theme"],
        risk_state=MARKET_DAILY["normal_risk"],
        divergence_state=MARKET_DAILY["normal_divergence"],
    )
    path = tmp_path / "theme_state_ranking.csv"

    write_theme_state_ranking(path, [row])

    assert path.is_file()
    assert STRONG in path.read_text(encoding="utf-8-sig")

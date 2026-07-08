from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
from lucerna_core.labels.market_gate import MARKET_DAILY, MARKET_ZH
from lucerna_core.market.theme_rules import THEME_STATE_RULE_VERSION, THEME_STATE_RULES

from lucerna_workflow.market_awareness.models import ThemeStateRow

THEME_STATE_RANKING_COLUMNS: tuple[str, ...] = (
    MARKET_ZH["theme_name"],
    MARKET_DAILY["status"],
    MARKET_DAILY["daily_state"],
    MARKET_DAILY["mid_state"],
    MARKET_DAILY["risk_state"],
    MARKET_DAILY["divergence_state"],
)


def theme_state_rows_to_frame(rows: list[ThemeStateRow]) -> pd.DataFrame:
    records = [
        {
            MARKET_ZH["theme_name"]: row.theme_name,
            MARKET_DAILY["status"]: row.status,
            MARKET_DAILY["daily_state"]: row.daily_state,
            MARKET_DAILY["mid_state"]: row.mid_state,
            MARKET_DAILY["risk_state"]: row.risk_state,
            MARKET_DAILY["divergence_state"]: row.divergence_state,
        }
        for row in rows
    ]
    if not records:
        return pd.DataFrame(columns=list(THEME_STATE_RANKING_COLUMNS))
    return pd.DataFrame(records)


def write_theme_state_ranking(path: Path, rows: list[ThemeStateRow]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = theme_state_rows_to_frame(rows)
    frame.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def write_daily_review_state(
    path: Path,
    *,
    trade_date: date,
    theme_state_ranking_path: Path,
    fixture_name: str,
    warnings: list[str] | None = None,
) -> Path:
    payload: dict[str, Any] = {
        "schema": "lucerna.market_daily_review_state.v1",
        "trade_date": trade_date.isoformat(),
        "theme_state_rule_version": THEME_STATE_RULE_VERSION,
        "theme_state_rules": dict(THEME_STATE_RULES),
        "paths": {"theme_state_ranking": str(theme_state_ranking_path)},
        "warnings": warnings or [],
        "provenance": {
            "source": "synthetic_fixture",
            "fixture": fixture_name,
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    return path

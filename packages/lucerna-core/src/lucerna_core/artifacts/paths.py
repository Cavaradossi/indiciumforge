from __future__ import annotations

from datetime import date
from pathlib import Path


def workflow_root(artifact_root: Path, trade_date: date) -> Path:
    return artifact_root / "workflows" / trade_date.strftime("%Y%m%d")


def market_gate_stage_dir(artifact_root: Path, trade_date: date) -> Path:
    return workflow_root(artifact_root, trade_date) / "market_gate"


def theme_state_ranking_path(artifact_root: Path, trade_date: date) -> Path:
    day = trade_date.strftime("%Y%m%d")
    return artifact_root / "market_awareness" / day / "daily_review" / "theme_state_ranking.csv"

from __future__ import annotations

from datetime import date
from pathlib import Path


def workflow_root(artifact_root: Path, trade_date: date) -> Path:
    return artifact_root / "workflows" / trade_date.strftime("%Y%m%d")


def market_gate_stage_dir(artifact_root: Path, trade_date: date) -> Path:
    return workflow_root(artifact_root, trade_date) / "market_gate"


def theme_state_ranking_path(artifact_root: Path, trade_date: date) -> Path:
    return daily_review_dir(artifact_root, trade_date) / "theme_state_ranking.csv"


def daily_review_dir(artifact_root: Path, trade_date: date) -> Path:
    day = trade_date.strftime("%Y%m%d")
    return artifact_root / "market_awareness" / day / "daily_review"


def synthetic_e2e_summary_path(artifact_root: Path, trade_date: date) -> Path:
    return workflow_root(artifact_root, trade_date) / "synthetic_e2e_summary.json"


def post_close_review_dir(artifact_root: Path, trade_date: date) -> Path:
    return workflow_root(artifact_root, trade_date) / "post_close"


def preopen_review_dir(artifact_root: Path, trade_date: date) -> Path:
    return workflow_root(artifact_root, trade_date) / "preopen"


def workflow_chain_summary_path(artifact_root: Path, trade_date: date) -> Path:
    return workflow_root(artifact_root, trade_date) / "workflow_chain_summary.json"

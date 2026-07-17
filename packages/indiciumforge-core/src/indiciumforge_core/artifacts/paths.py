from __future__ import annotations

from datetime import date
from pathlib import Path

from indiciumforge_core.run_id import is_isolated


def workflow_root(artifact_root: Path, trade_date: date, run_id: str = "default") -> Path:
    base = artifact_root / "workflows" / trade_date.strftime("%Y%m%d")
    if is_isolated(run_id):
        base = base / "runs" / run_id
    return base


def market_gate_stage_dir(
    artifact_root: Path, trade_date: date, run_id: str = "default"
) -> Path:
    return workflow_root(artifact_root, trade_date, run_id) / "market_gate"


def theme_state_ranking_path(
    artifact_root: Path, trade_date: date, run_id: str = "default"
) -> Path:
    return daily_review_dir(artifact_root, trade_date, run_id) / "theme_state_ranking.csv"


def daily_review_dir(
    artifact_root: Path, trade_date: date, run_id: str = "default"
) -> Path:
    day = trade_date.strftime("%Y%m%d")
    base = artifact_root / "market_awareness" / day
    if is_isolated(run_id):
        base = base / "runs" / run_id
    return base / "daily_review"


def synthetic_e2e_summary_path(
    artifact_root: Path, trade_date: date, run_id: str = "default"
) -> Path:
    return workflow_root(artifact_root, trade_date, run_id) / "synthetic_e2e_summary.json"


def post_close_review_dir(
    artifact_root: Path, trade_date: date, run_id: str = "default"
) -> Path:
    return workflow_root(artifact_root, trade_date, run_id) / "post_close"


def preopen_review_dir(
    artifact_root: Path, trade_date: date, run_id: str = "default"
) -> Path:
    return workflow_root(artifact_root, trade_date, run_id) / "preopen"


def workflow_chain_summary_path(
    artifact_root: Path, trade_date: date, run_id: str = "default"
) -> Path:
    return workflow_root(artifact_root, trade_date, run_id) / "workflow_chain_summary.json"


def factor_scan_dir(
    artifact_root: Path, trade_date: date, run_id: str = "default"
) -> Path:
    return workflow_root(artifact_root, trade_date, run_id) / "factor_scan"

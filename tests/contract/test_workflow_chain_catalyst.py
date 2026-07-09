from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path

from lucerna_workflow.workflow_chain.runner import run_workflow_chain_skeleton

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures"
DAILY_REVIEW_FIXTURE = FIXTURE_ROOT / "market_awareness" / "theme_sectors_demo.yaml"
POST_CLOSE_FIXTURE = FIXTURE_ROOT / "workflow" / "post_close_buy_point_review_demo.csv"
PREOPEN_FIXTURE = FIXTURE_ROOT / "workflow" / "preopen_buy_point_review_demo.csv"
CATALYST_INPUTS = ROOT / "tests" / "golden" / "market_gate" / "catalyst_ignored" / "inputs"
BASELINE_SUMMARY = (
    ROOT
    / "tests"
    / "golden"
    / "market_gate"
    / "strict_pass_mixed"
    / "expected"
    / "market_gate"
    / "market_gate_summary.json"
)
TRADE_DATE = date(2026, 6, 23)


def test_workflow_chain_catalyst_does_not_change_strict_count(tmp_path: Path) -> None:
    catalyst_dir = tmp_path / "research"
    catalyst_dir.mkdir(parents=True)
    shutil.copy2(
        CATALYST_INPUTS / "research" / "catalyst_review.json",
        catalyst_dir / "catalyst_review.json",
    )

    result = run_workflow_chain_skeleton(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        daily_review_fixture=DAILY_REVIEW_FIXTURE,
        post_close_review_fixture=POST_CLOSE_FIXTURE,
        preopen_review_fixture=PREOPEN_FIXTURE,
    )

    assert result.chain_ok
    baseline = json.loads(BASELINE_SUMMARY.read_text(encoding="utf-8-sig"))
    summary = json.loads(
        (result.market_gate_stage_dir / "market_gate_summary.json").read_text(encoding="utf-8-sig")
    )
    assert summary["strict_count"] == baseline["strict_count"]

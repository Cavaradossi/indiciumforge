from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from lucerna_workflow.workflow_chain.runner import (
    WORKFLOW_CHAIN_SUMMARY_SCHEMA,
    run_workflow_chain_skeleton,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures"
DAILY_REVIEW_FIXTURE = FIXTURE_ROOT / "market_awareness" / "theme_sectors_demo.yaml"
POST_CLOSE_FIXTURE = FIXTURE_ROOT / "workflow" / "post_close_buy_point_review_demo.csv"
PREOPEN_FIXTURE = FIXTURE_ROOT / "workflow" / "preopen_buy_point_review_empty_strict_demo.csv"
TRADE_DATE = date(2026, 6, 24)


def test_workflow_chain_summary_v3_includes_session_metadata(tmp_path: Path) -> None:
    result = run_workflow_chain_skeleton(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        daily_review_fixture=DAILY_REVIEW_FIXTURE,
        post_close_review_fixture=POST_CLOSE_FIXTURE,
        preopen_review_fixture=PREOPEN_FIXTURE,
    )

    payload = json.loads(result.summary_path.read_text(encoding="utf-8-sig"))

    assert payload["schema"] == WORKFLOW_CHAIN_SUMMARY_SCHEMA
    assert payload["schema"] == "lucerna.workflow_chain_summary.v3"
    assert payload["chain_ok"] is True
    assert payload["strict_count"] == 0

    session = payload["workflow_session"]
    assert session["recipe_id"] == "lucerna.recipe.ashare_daily_research.v1"
    assert session["asset_domain"] == "china_a_share"
    assert session["session_model"] == "calendar_day_cycle"
    assert session["cycle_id"] == "2026-06-24"

    assert "daily_review" in payload["stages"]
    assert "post_close" in payload["stages"]
    assert "preopen" in payload["stages"]
    assert "market_gate" in payload["stages"]

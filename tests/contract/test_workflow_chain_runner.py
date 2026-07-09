from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from lucerna_workflow.workflow_chain.runner import (
    WORKFLOW_CHAIN_SUMMARY_SCHEMA,
    run_workflow_chain_skeleton,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures"
DAILY_REVIEW_FIXTURE = FIXTURE_ROOT / "market_awareness" / "theme_sectors_demo.yaml"
POST_CLOSE_FIXTURE = FIXTURE_ROOT / "workflow" / "post_close_buy_point_review_demo.csv"
PREOPEN_FIXTURE = FIXTURE_ROOT / "workflow" / "preopen_buy_point_review_demo.csv"
PREOPEN_EMPTY_STRICT_FIXTURE = (
    FIXTURE_ROOT / "workflow" / "preopen_buy_point_review_empty_strict_demo.csv"
)
TRADE_DATE = date(2026, 6, 23)
EMPTY_STRICT_DATE = date(2026, 6, 24)


def test_run_workflow_chain_skeleton_happy_path(tmp_path: Path) -> None:
    result = run_workflow_chain_skeleton(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        daily_review_fixture=DAILY_REVIEW_FIXTURE,
        post_close_review_fixture=POST_CLOSE_FIXTURE,
        preopen_review_fixture=PREOPEN_FIXTURE,
    )

    assert result.chain_ok
    assert result.workflow_review_source_stage == "preopen"
    assert result.strict_count >= 1
    assert (result.post_close_stage_dir / "buy_point_review_internal.csv").is_file()
    assert (result.post_close_stage_dir / "post_close_review_state.json").is_file()
    assert (result.preopen_stage_dir / "buy_point_review_internal.csv").is_file()
    assert (result.preopen_stage_dir / "preopen_review_state.json").is_file()
    assert (result.market_gate_stage_dir / "market_gated_candidates.csv").is_file()
    assert result.summary_path.is_file()

    payload = json.loads(result.summary_path.read_text(encoding="utf-8-sig"))
    assert payload["schema"] == WORKFLOW_CHAIN_SUMMARY_SCHEMA
    assert payload["chain_ok"] is True
    assert payload["workflow_review_source_stage"] == "preopen"


def test_run_workflow_chain_empty_strict_still_ok(tmp_path: Path) -> None:
    result = run_workflow_chain_skeleton(
        trade_date=EMPTY_STRICT_DATE,
        artifact_root=tmp_path,
        daily_review_fixture=DAILY_REVIEW_FIXTURE,
        post_close_review_fixture=POST_CLOSE_FIXTURE,
        preopen_review_fixture=PREOPEN_EMPTY_STRICT_FIXTURE,
    )

    assert result.chain_ok
    assert result.strict_count == 0


def test_run_workflow_chain_missing_daily_review_fixture(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="daily-review fixture"):
        run_workflow_chain_skeleton(
            trade_date=TRADE_DATE,
            artifact_root=tmp_path,
            daily_review_fixture=tmp_path / "missing.yaml",
            post_close_review_fixture=POST_CLOSE_FIXTURE,
            preopen_review_fixture=PREOPEN_FIXTURE,
        )


def test_run_workflow_chain_missing_post_close_fixture(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="post-close review fixture"):
        run_workflow_chain_skeleton(
            trade_date=TRADE_DATE,
            artifact_root=tmp_path,
            daily_review_fixture=DAILY_REVIEW_FIXTURE,
            post_close_review_fixture=tmp_path / "missing.csv",
            preopen_review_fixture=PREOPEN_FIXTURE,
        )


def test_run_workflow_chain_missing_preopen_fixture(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="preopen review fixture"):
        run_workflow_chain_skeleton(
            trade_date=TRADE_DATE,
            artifact_root=tmp_path,
            daily_review_fixture=DAILY_REVIEW_FIXTURE,
            post_close_review_fixture=POST_CLOSE_FIXTURE,
            preopen_review_fixture=tmp_path / "missing.csv",
        )

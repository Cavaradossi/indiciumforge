from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from indiciumforge_core.artifacts.paths import synthetic_e2e_summary_path
from indiciumforge_workflow.e2e.synthetic import (
    SYNTHETIC_E2E_SUMMARY_SCHEMA,
    run_synthetic_e2e,
)

ROOT = Path(__file__).resolve().parents[2]
DAILY_REVIEW_FIXTURE = ROOT / "tests" / "fixtures" / "market_awareness" / "theme_sectors_demo.yaml"
PREOPEN_FIXTURE = ROOT / "tests" / "fixtures" / "workflow" / "preopen_buy_point_review_demo.csv"
TRADE_DATE = date(2026, 6, 23)


def test_run_synthetic_e2e_writes_stages_audits_and_summary(tmp_path: Path) -> None:
    result = run_synthetic_e2e(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        daily_review_fixture=DAILY_REVIEW_FIXTURE,
        preopen_review_fixture=PREOPEN_FIXTURE,
    )

    assert result.audit_ok
    assert result.daily_review_audit_ok
    assert result.market_gate_audit_ok
    assert result.daily_review_stage_dir.is_dir()
    assert result.market_gate_stage_dir.is_dir()
    assert (result.daily_review_stage_dir / "theme_state_ranking.csv").is_file()
    assert (result.daily_review_stage_dir / "market_daily_review_state.json").is_file()
    assert (result.market_gate_stage_dir / "market_gated_candidates.csv").is_file()
    assert result.summary_path == synthetic_e2e_summary_path(tmp_path, TRADE_DATE)
    assert result.summary_path.is_file()

    payload = json.loads(result.summary_path.read_text(encoding="utf-8-sig"))
    assert payload["schema"] == SYNTHETIC_E2E_SUMMARY_SCHEMA
    assert payload["trade_date"] == "2026-06-23"
    assert payload["audit_ok"] is True
    assert payload["stages"]["daily_review"]["audit_ok"] is True
    assert payload["stages"]["market_gate"]["audit_ok"] is True


def test_run_synthetic_e2e_missing_daily_review_fixture(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="daily-review fixture"):
        run_synthetic_e2e(
            trade_date=TRADE_DATE,
            artifact_root=tmp_path,
            daily_review_fixture=tmp_path / "missing.yaml",
            preopen_review_fixture=PREOPEN_FIXTURE,
        )


def test_run_synthetic_e2e_missing_preopen_fixture(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="preopen review fixture"):
        run_synthetic_e2e(
            trade_date=TRADE_DATE,
            artifact_root=tmp_path,
            daily_review_fixture=DAILY_REVIEW_FIXTURE,
            preopen_review_fixture=tmp_path / "missing.csv",
        )

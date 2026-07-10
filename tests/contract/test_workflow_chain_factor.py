from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from indiciumforge_core.factors.universe import load_assets_from_fixture_list
from indiciumforge_workflow.factor_scan.runner import FactorScanStageConfig
from indiciumforge_workflow.workflow_chain.runner import (
    WORKFLOW_CHAIN_SUMMARY_SCHEMA,
    run_workflow_chain_skeleton,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures"
DAILY_REVIEW_FIXTURE = FIXTURE_ROOT / "market_awareness" / "theme_sectors_demo.yaml"
POST_CLOSE_FIXTURE = FIXTURE_ROOT / "workflow" / "post_close_buy_point_review_demo.csv"
PREOPEN_FIXTURE = FIXTURE_ROOT / "workflow" / "preopen_buy_point_review_demo.csv"
PACK_PATH = FIXTURE_ROOT / "factor_pack_demo.yaml"
ASSET_LIST = FIXTURE_ROOT / "factor_scan_assets.yaml"
OHLCV_ROOT = FIXTURE_ROOT / "ohlcv"
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


def _factor_config() -> FactorScanStageConfig:
    assets = tuple(load_assets_from_fixture_list(ASSET_LIST))
    return FactorScanStageConfig(
        pack_config=PACK_PATH,
        ohlcv_fixture_root=OHLCV_ROOT,
        asset_fixture_list=ASSET_LIST,
        assets=assets,
        asset_universe_source="fixture_asset_list",
    )


def test_workflow_chain_with_factor_scan_enabled(tmp_path: Path) -> None:
    result = run_workflow_chain_skeleton(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        daily_review_fixture=DAILY_REVIEW_FIXTURE,
        post_close_review_fixture=POST_CLOSE_FIXTURE,
        preopen_review_fixture=PREOPEN_FIXTURE,
        factor_scan_config=_factor_config(),
    )

    assert result.chain_ok
    assert result.factor_scan_enabled
    assert result.factor_scan_stage_dir is not None
    assert result.factor_scan_audit_ok is True
    assert result.signal_count >= 1

    payload = json.loads(result.summary_path.read_text(encoding="utf-8-sig"))
    assert payload["schema"] == WORKFLOW_CHAIN_SUMMARY_SCHEMA
    assert payload["factor_scan_enabled"] is True
    assert payload["factor_scan_audit_ok"] is True
    assert "factor_scan" in payload["stages"]


def test_workflow_chain_factor_scan_does_not_change_strict_count(tmp_path: Path) -> None:
    result = run_workflow_chain_skeleton(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        daily_review_fixture=DAILY_REVIEW_FIXTURE,
        post_close_review_fixture=POST_CLOSE_FIXTURE,
        preopen_review_fixture=PREOPEN_FIXTURE,
        factor_scan_config=_factor_config(),
    )

    baseline = json.loads(BASELINE_SUMMARY.read_text(encoding="utf-8-sig"))
    summary = json.loads(
        (result.market_gate_stage_dir / "market_gate_summary.json").read_text(encoding="utf-8-sig")
    )
    assert summary["strict_count"] == baseline["strict_count"]


def test_workflow_chain_factor_audit_failure_does_not_fail_chain(tmp_path: Path) -> None:
    result = run_workflow_chain_skeleton(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        daily_review_fixture=DAILY_REVIEW_FIXTURE,
        post_close_review_fixture=POST_CLOSE_FIXTURE,
        preopen_review_fixture=PREOPEN_FIXTURE,
        factor_scan_config=_factor_config(),
    )
    assert result.factor_scan_stage_dir is not None
    scan_json = result.factor_scan_stage_dir / "factor_scan_20260623.json"
    scan_json.unlink()

    from indiciumforge_core.artifacts.manifest import validate_factor_scan_stage

    audit = validate_factor_scan_stage(
        result.factor_scan_stage_dir,
        expected_trade_date=TRADE_DATE.isoformat(),
    )
    assert not audit.ok
    assert result.chain_ok

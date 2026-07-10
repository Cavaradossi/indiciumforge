from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from indiciumforge_core.artifacts.manifest import validate_factor_scan_stage
from indiciumforge_core.factors.artifacts import FACTOR_SCAN_SCHEMA, FACTOR_SCAN_STATE_SCHEMA
from indiciumforge_workflow.factor_scan.runner import FactorScanStageConfig, run_factor_scan_stage

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures"
PACK_PATH = FIXTURE_ROOT / "factor_pack_demo.yaml"
ASSET_LIST = FIXTURE_ROOT / "factor_scan_assets.yaml"
OHLCV_ROOT = FIXTURE_ROOT / "ohlcv"
TRADE_DATE = date(2026, 5, 10)


def test_run_factor_scan_stage_writes_artifacts(tmp_path: Path) -> None:
    from indiciumforge_core.factors.universe import load_assets_from_fixture_list

    assets = tuple(load_assets_from_fixture_list(ASSET_LIST))
    result = run_factor_scan_stage(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        config=FactorScanStageConfig(
            pack_config=PACK_PATH,
            ohlcv_fixture_root=OHLCV_ROOT,
            asset_fixture_list=ASSET_LIST,
            assets=assets,
            asset_universe_source="fixture_asset_list",
        ),
    )

    assert result.signal_count >= 1
    assert result.detector_count == 2
    assert (result.stage_dir / "factor_scan_state.json").is_file()

    stem = f"factor_scan_{TRADE_DATE.strftime('%Y%m%d')}"
    json_path = result.stage_dir / f"{stem}.json"
    assert json_path.is_file()
    payload = json.loads(json_path.read_text(encoding="utf-8-sig"))
    assert payload["schema"] == FACTOR_SCAN_SCHEMA

    state = json.loads(
        (result.stage_dir / "factor_scan_state.json").read_text(encoding="utf-8-sig")
    )
    assert state["schema"] == FACTOR_SCAN_STATE_SCHEMA
    assert state["asset_universe_source"] == "fixture_asset_list"

    audit = validate_factor_scan_stage(result.stage_dir, expected_trade_date="2026-05-10")
    assert audit.ok

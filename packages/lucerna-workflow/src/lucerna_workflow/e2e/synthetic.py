from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from lucerna_core.artifacts.manifest import (
    validate_daily_review_stage,
    validate_market_gate_stage,
)
from lucerna_core.artifacts.paths import (
    daily_review_dir,
    market_gate_stage_dir,
    synthetic_e2e_summary_path,
    workflow_root,
)

from lucerna_workflow.market_awareness.runner import run_daily_review_skeleton
from lucerna_workflow.market_gate.runner import run_market_gate

SYNTHETIC_E2E_SUMMARY_SCHEMA = "lucerna.synthetic_e2e_summary.v1"


@dataclass(frozen=True)
class SyntheticE2EResult:
    trade_date: date
    daily_review_stage_dir: Path
    market_gate_stage_dir: Path
    summary_path: Path
    daily_review_audit_ok: bool
    market_gate_audit_ok: bool
    audit_ok: bool
    warnings: tuple[str, ...]


def _seed_preopen_review(
    artifact_root: Path,
    trade_date: date,
    preopen_review_fixture: Path,
) -> Path:
    target_dir = workflow_root(artifact_root, trade_date) / "preopen"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / "buy_point_review_internal.csv"
    shutil.copy2(preopen_review_fixture, target_path)
    return target_path


def _write_summary(
    path: Path,
    *,
    trade_date: date,
    daily_review_stage_dir: Path,
    market_gate_stage_dir: Path,
    daily_review_audit_ok: bool,
    market_gate_audit_ok: bool,
    daily_review_fixture: Path,
    preopen_review_fixture: Path,
    warnings: list[str],
) -> None:
    payload: dict[str, Any] = {
        "schema": SYNTHETIC_E2E_SUMMARY_SCHEMA,
        "trade_date": trade_date.isoformat(),
        "provenance": {
            "mode": "synthetic_e2e",
            "fixtures": {
                "daily_review": str(daily_review_fixture),
                "preopen_review": str(preopen_review_fixture),
            },
        },
        "stages": {
            "daily_review": {
                "dir": str(daily_review_stage_dir),
                "audit_ok": daily_review_audit_ok,
            },
            "market_gate": {
                "dir": str(market_gate_stage_dir),
                "audit_ok": market_gate_audit_ok,
            },
        },
        "audit_ok": daily_review_audit_ok and market_gate_audit_ok,
        "warnings": warnings,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8-sig")


def run_synthetic_e2e(
    *,
    trade_date: date,
    artifact_root: Path,
    daily_review_fixture: Path,
    preopen_review_fixture: Path,
) -> SyntheticE2EResult:
    if not daily_review_fixture.is_file():
        raise FileNotFoundError(f"missing daily-review fixture: {daily_review_fixture}")
    if not preopen_review_fixture.is_file():
        raise FileNotFoundError(f"missing preopen review fixture: {preopen_review_fixture}")

    warnings: list[str] = []
    trade_date_iso = trade_date.isoformat()

    _seed_preopen_review(artifact_root, trade_date, preopen_review_fixture)

    daily_result = run_daily_review_skeleton(
        trade_date=trade_date,
        artifact_root=artifact_root,
        fixture_path=daily_review_fixture,
    )
    warnings.extend(daily_result.warnings)

    gate_result = run_market_gate(trade_date=trade_date, artifact_root=artifact_root)
    warnings.extend(gate_result.warnings)

    dr_stage_dir = daily_review_dir(artifact_root, trade_date)
    mg_stage_dir = market_gate_stage_dir(artifact_root, trade_date)

    daily_manifest = validate_daily_review_stage(
        dr_stage_dir,
        expected_trade_date=trade_date_iso,
    )
    gate_manifest = validate_market_gate_stage(
        mg_stage_dir,
        expected_trade_date=trade_date_iso,
    )

    daily_review_audit_ok = daily_manifest.ok
    market_gate_audit_ok = gate_manifest.ok
    audit_ok = daily_review_audit_ok and market_gate_audit_ok

    summary_path = synthetic_e2e_summary_path(artifact_root, trade_date)
    _write_summary(
        summary_path,
        trade_date=trade_date,
        daily_review_stage_dir=dr_stage_dir,
        market_gate_stage_dir=mg_stage_dir,
        daily_review_audit_ok=daily_review_audit_ok,
        market_gate_audit_ok=market_gate_audit_ok,
        daily_review_fixture=daily_review_fixture,
        preopen_review_fixture=preopen_review_fixture,
        warnings=warnings,
    )

    return SyntheticE2EResult(
        trade_date=trade_date,
        daily_review_stage_dir=dr_stage_dir,
        market_gate_stage_dir=mg_stage_dir,
        summary_path=summary_path,
        daily_review_audit_ok=daily_review_audit_ok,
        market_gate_audit_ok=market_gate_audit_ok,
        audit_ok=audit_ok,
        warnings=tuple(warnings),
    )

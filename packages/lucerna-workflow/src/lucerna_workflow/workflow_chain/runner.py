from __future__ import annotations

import json
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
    post_close_review_dir,
    preopen_review_dir,
    workflow_chain_summary_path,
)

from lucerna_workflow.market_awareness.runner import run_daily_review_skeleton
from lucerna_workflow.market_gate.runner import run_market_gate
from lucerna_workflow.workflow_chain.skeleton import seed_post_close_review, seed_preopen_review

WORKFLOW_CHAIN_SUMMARY_SCHEMA = "lucerna.workflow_chain_summary.v1"


@dataclass(frozen=True)
class WorkflowChainResult:
    trade_date: date
    daily_review_stage_dir: Path
    post_close_stage_dir: Path
    preopen_stage_dir: Path
    market_gate_stage_dir: Path
    summary_path: Path
    workflow_review_source_stage: str
    strict_count: int
    daily_review_audit_ok: bool
    market_gate_audit_ok: bool
    chain_ok: bool
    warnings: tuple[str, ...]


def _write_chain_summary(
    path: Path,
    *,
    trade_date: date,
    daily_review_stage_dir: Path,
    post_close_stage_dir: Path,
    preopen_stage_dir: Path,
    market_gate_stage_dir: Path,
    daily_review_audit_ok: bool,
    market_gate_audit_ok: bool,
    workflow_review_source_stage: str,
    strict_count: int,
    fixtures: dict[str, str],
    warnings: list[str],
) -> None:
    payload: dict[str, Any] = {
        "schema": WORKFLOW_CHAIN_SUMMARY_SCHEMA,
        "trade_date": trade_date.isoformat(),
        "provenance": {"mode": "workflow_chain_skeleton", "fixtures": fixtures},
        "stages": {
            "daily_review": {
                "dir": str(daily_review_stage_dir),
                "audit_ok": daily_review_audit_ok,
            },
            "post_close": {"dir": str(post_close_stage_dir)},
            "preopen": {"dir": str(preopen_stage_dir)},
            "market_gate": {
                "dir": str(market_gate_stage_dir),
                "audit_ok": market_gate_audit_ok,
            },
        },
        "workflow_review_source_stage": workflow_review_source_stage,
        "strict_count": strict_count,
        "chain_ok": daily_review_audit_ok and market_gate_audit_ok,
        "warnings": warnings,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8-sig")


def run_workflow_chain_skeleton(
    *,
    trade_date: date,
    artifact_root: Path,
    daily_review_fixture: Path,
    post_close_review_fixture: Path,
    preopen_review_fixture: Path,
) -> WorkflowChainResult:
    if not daily_review_fixture.is_file():
        raise FileNotFoundError(f"missing daily-review fixture: {daily_review_fixture}")
    if not post_close_review_fixture.is_file():
        raise FileNotFoundError(f"missing post-close review fixture: {post_close_review_fixture}")
    if not preopen_review_fixture.is_file():
        raise FileNotFoundError(f"missing preopen review fixture: {preopen_review_fixture}")

    warnings: list[str] = []
    trade_date_iso = trade_date.isoformat()

    daily_result = run_daily_review_skeleton(
        trade_date=trade_date,
        artifact_root=artifact_root,
        fixture_path=daily_review_fixture,
    )
    warnings.extend(daily_result.warnings)

    seed_post_close_review(artifact_root, trade_date, post_close_review_fixture)
    seed_preopen_review(artifact_root, trade_date, preopen_review_fixture)

    gate_result = run_market_gate(trade_date=trade_date, artifact_root=artifact_root)
    warnings.extend(gate_result.warnings)

    dr_stage_dir = daily_review_dir(artifact_root, trade_date)
    pc_stage_dir = post_close_review_dir(artifact_root, trade_date)
    po_stage_dir = preopen_review_dir(artifact_root, trade_date)
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
    chain_ok = daily_review_audit_ok and market_gate_audit_ok

    summary_payload = json.loads(
        (mg_stage_dir / "market_gate_summary.json").read_text(encoding="utf-8-sig")
    )
    workflow_review_source_stage = str(summary_payload.get("workflow_review_source_stage", ""))
    strict_count = int(summary_payload.get("strict_count", 0))

    summary_path = workflow_chain_summary_path(artifact_root, trade_date)
    _write_chain_summary(
        summary_path,
        trade_date=trade_date,
        daily_review_stage_dir=dr_stage_dir,
        post_close_stage_dir=pc_stage_dir,
        preopen_stage_dir=po_stage_dir,
        market_gate_stage_dir=mg_stage_dir,
        daily_review_audit_ok=daily_review_audit_ok,
        market_gate_audit_ok=market_gate_audit_ok,
        workflow_review_source_stage=workflow_review_source_stage,
        strict_count=strict_count,
        fixtures={
            "daily_review": str(daily_review_fixture),
            "post_close_review": str(post_close_review_fixture),
            "preopen_review": str(preopen_review_fixture),
        },
        warnings=warnings,
    )

    return WorkflowChainResult(
        trade_date=trade_date,
        daily_review_stage_dir=dr_stage_dir,
        post_close_stage_dir=pc_stage_dir,
        preopen_stage_dir=po_stage_dir,
        market_gate_stage_dir=mg_stage_dir,
        summary_path=summary_path,
        workflow_review_source_stage=workflow_review_source_stage,
        strict_count=strict_count,
        daily_review_audit_ok=daily_review_audit_ok,
        market_gate_audit_ok=market_gate_audit_ok,
        chain_ok=chain_ok,
        warnings=tuple(warnings),
    )

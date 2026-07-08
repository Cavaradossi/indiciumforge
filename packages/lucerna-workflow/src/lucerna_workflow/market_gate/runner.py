from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from lucerna_core.artifacts.local_store import LocalArtifactStore
from lucerna_core.artifacts.paths import theme_state_ranking_path, workflow_root
from lucerna_core.artifacts.writer import (
    base_state,
    prepare_csv_bundle,
    write_json,
    write_markdown,
    write_table_bundle,
)
from lucerna_core.labels.market_gate import (
    GATE_RESULT_OBSERVATION,
    GATE_RESULT_REJECTED,
    GATE_RESULT_STRICT,
)
from lucerna_core.market.theme_rules import THEME_STATE_RULE_VERSION, THEME_STATE_RULES

from lucerna_workflow.market_gate.calibration import market_gate_calibration_audit
from lucerna_workflow.market_gate.kernel import apply_market_gate, split_market_gate_frames
from lucerna_workflow.market_gate.render import (
    render_market_gate_active_watch_markdown,
    render_market_gate_calibration_markdown,
    render_market_gate_markdown,
    render_market_gate_summary_markdown,
)
from lucerna_workflow.market_gate.resolver import resolve_market_gate_review_path


@dataclass(frozen=True)
class MarketGateRunResult:
    stage_dir: Path
    state_path: Path
    paths: dict[str, Path]
    warnings: list[str]


def run_market_gate(*, trade_date: date, artifact_root: Path) -> MarketGateRunResult:
    store = LocalArtifactStore()
    theme_path = theme_state_ranking_path(artifact_root, trade_date)
    if not theme_path.exists():
        raise FileNotFoundError(f"missing market daily-review theme state ranking: {theme_path}")

    resolution = resolve_market_gate_review_path(artifact_root, trade_date)
    warnings: list[str] = []
    if resolution.warning:
        warnings.append(resolution.warning)

    themes = store.read_csv(theme_path)
    review = store.read_csv(resolution.path)
    gated = apply_market_gate(review, themes)
    strict, observation, rejected, active_watch = split_market_gate_frames(gated)
    calibration = market_gate_calibration_audit(
        gated,
        strict=strict,
        observation=observation,
        rejected=rejected,
        active_watch=active_watch,
        trade_date=trade_date,
    )

    stage_dir = workflow_root(artifact_root, trade_date) / "market_gate"
    paths: dict[str, Path] = {}
    paths.update(
        write_table_bundle(
            stage_dir,
            "market_gated_candidates",
            prepare_csv_bundle(strict),
            render_market_gate_markdown(strict, trade_date, GATE_RESULT_STRICT),
        )
    )
    paths.update(
        write_table_bundle(
            stage_dir,
            "market_gated_observation",
            prepare_csv_bundle(observation),
            render_market_gate_markdown(observation, trade_date, GATE_RESULT_OBSERVATION),
        )
    )
    paths.update(
        write_table_bundle(
            stage_dir,
            "market_gated_rejected",
            prepare_csv_bundle(rejected),
            render_market_gate_markdown(rejected, trade_date, GATE_RESULT_REJECTED),
        )
    )
    paths.update(
        write_table_bundle(
            stage_dir,
            "market_gated_active_watch",
            prepare_csv_bundle(active_watch),
            render_market_gate_active_watch_markdown(active_watch, trade_date),
        )
    )

    calibration_json = stage_dir / "market_gate_calibration_audit.json"
    calibration_md = stage_dir / "market_gate_calibration_audit.md"
    write_json(calibration_json, calibration)
    write_markdown(calibration_md, render_market_gate_calibration_markdown(calibration))
    paths["market_gate_calibration_audit"] = calibration_json
    paths["market_gate_calibration_audit_md"] = calibration_md

    summary = {
        "schema": "indiciumgrid.workflow_market_gate_summary.v1",
        "trade_date": trade_date.isoformat(),
        "rule_version": THEME_STATE_RULE_VERSION,
        "candidate_count": int(len(review)),
        "strict_count": int(len(strict)),
        "observation_count": int(len(observation)),
        "watch_count": int(len(active_watch)),
        "rejected_count": int(len(rejected)),
        "quality_gate_warning": calibration["quality_gate_warning"],
        "theme_state_ranking": str(theme_path),
        "workflow_review": str(resolution.path),
        "workflow_review_source_stage": resolution.source_stage,
        "warnings": warnings,
    }
    summary_json = stage_dir / "market_gate_summary.json"
    summary_md = stage_dir / "market_gate_summary.md"
    write_json(summary_json, summary)
    write_markdown(summary_md, render_market_gate_summary_markdown(summary))
    paths["market_gate_summary"] = summary_json
    paths["market_gate_summary_md"] = summary_md

    state_path = stage_dir / "market_gate_state.json"
    state = base_state(
        "market_gate",
        trade_date,
        paths,
        warnings=warnings,
        extra={
            "theme_state_rule_version": THEME_STATE_RULE_VERSION,
            "theme_state_rules": THEME_STATE_RULES,
            "theme_state_ranking": str(theme_path),
            "workflow_review": str(resolution.path),
            "workflow_review_source_stage": resolution.source_stage,
            "candidate_count": int(len(review)),
            "strict_count": int(len(strict)),
            "observation_count": int(len(observation)),
            "watch_count": int(len(active_watch)),
            "rejected_count": int(len(rejected)),
            "quality_gate_warning": calibration["quality_gate_warning"],
        },
    )
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    return MarketGateRunResult(
        stage_dir=stage_dir,
        state_path=state_path,
        paths=paths,
        warnings=warnings,
    )

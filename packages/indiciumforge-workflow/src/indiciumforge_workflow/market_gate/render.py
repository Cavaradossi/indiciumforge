from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd
from indiciumforge_core.labels.market_gate import MARKET_GATE_COLUMNS, REVIEW_COLUMNS, WORKFLOW_ZH


def render_market_gate_markdown(frame: pd.DataFrame, trade_date: date, label: str) -> str:
    lines = [
        f"# {trade_date.isoformat()} workflow market gate - {label}",
        "",
        WORKFLOW_ZH["disclaimer"],
        "",
        f"- {MARKET_GATE_COLUMNS['gate_result']}: {label}",
        f"- rows: {len(frame)}",
        "",
    ]
    if not frame.empty:
        display_columns = [
            REVIEW_COLUMNS["code"],
            REVIEW_COLUMNS["stock_name"],
            REVIEW_COLUMNS["rating"],
            MARKET_GATE_COLUMNS["gate_result"],
            MARKET_GATE_COLUMNS["matched_themes"],
            MARKET_GATE_COLUMNS["theme_status"],
            MARKET_GATE_COLUMNS["reject_reason"],
            MARKET_GATE_COLUMNS["observe_reason"],
            REVIEW_COLUMNS["holding_period"],
            REVIEW_COLUMNS["narrative_stage"],
            REVIEW_COLUMNS["thesis_risk"],
        ]
        columns = [column for column in display_columns if column in frame.columns]
        lines.append(frame[columns].head(120).to_markdown(index=False))
    return "\n".join(lines)


def render_market_gate_active_watch_markdown(frame: pd.DataFrame, trade_date: date) -> str:
    lines = [
        f"# {trade_date.isoformat()} workflow market gate - active watch",
        "",
        WORKFLOW_ZH["disclaimer"],
        "",
        "- boundary: active watch is not strict execution pass",
        f"- rows: {len(frame)}",
        "",
    ]
    if not frame.empty:
        display_columns = [
            REVIEW_COLUMNS["code"],
            REVIEW_COLUMNS["stock_name"],
            REVIEW_COLUMNS["rating"],
            MARKET_GATE_COLUMNS["gate_result"],
            MARKET_GATE_COLUMNS["active_watch_level"],
            MARKET_GATE_COLUMNS["active_watch_reason"],
            MARKET_GATE_COLUMNS["active_watch_action"],
            MARKET_GATE_COLUMNS["matched_themes"],
            MARKET_GATE_COLUMNS["reject_reason"],
            MARKET_GATE_COLUMNS["observe_reason"],
        ]
        columns = [column for column in display_columns if column in frame.columns]
        lines.append(frame[columns].head(120).to_markdown(index=False))
    return "\n".join(lines)


def render_market_gate_summary_markdown(summary: dict[str, Any]) -> str:
    lines = [
        f"# workflow market gate summary - {summary.get('trade_date', '')}",
        "",
        WORKFLOW_ZH["disclaimer"],
        "",
        f"- rule_version: {summary.get('rule_version', '')}",
        f"- candidate_count: {summary.get('candidate_count', 0)}",
        f"- strict_count: {summary.get('strict_count', 0)}",
        f"- observation_count: {summary.get('observation_count', 0)}",
        f"- watch_count: {summary.get('watch_count', 0)}",
        f"- rejected_count: {summary.get('rejected_count', 0)}",
        f"- quality_gate_warning: {summary.get('quality_gate_warning', '')}",
        f"- theme_state_ranking: {summary.get('theme_state_ranking', '')}",
        f"- workflow_review: {summary.get('workflow_review', '')}",
    ]
    warnings = summary.get("warnings") or []
    if warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {item}" for item in warnings)
    return "\n".join(lines)


def render_market_gate_calibration_markdown(audit: dict[str, Any]) -> str:
    lines = [
        f"# workflow market gate calibration audit - {audit.get('trade_date', '')}",
        "",
        WORKFLOW_ZH["disclaimer"],
        "",
        "- strict execution gate stays strict; this audit is for rule calibration.",
        f"- candidate_count: {audit.get('candidate_count', 0)}",
        f"- strict_count: {audit.get('strict_count', 0)}",
        f"- observation_count: {audit.get('observation_count', 0)}",
        f"- watch_count: {audit.get('watch_count', 0)}",
        f"- rejected_count: {audit.get('rejected_count', 0)}",
        f"- quality_gate_warning: {audit.get('quality_gate_warning', '')}",
        f"- outcome_status: {audit.get('outcome_status', '')}",
        "",
    ]
    top_missed = audit.get("top_missed_candidates") or []
    if top_missed:
        table = pd.DataFrame(top_missed).to_markdown(index=False)
        lines.extend(["## top_missed_candidates", "", table])
    return "\n".join(lines)

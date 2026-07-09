from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from lucerna_core.artifacts.comparator import compare_semantic_market_gate
from lucerna_core.artifacts.manifest import DAILY_REVIEW_STATE_SCHEMA
from lucerna_core.parity.models import (
    ParityCheckResult,
    ParityDimension,
    ParityRunContext,
    ParityVerdict,
)
from lucerna_core.parity.reference import ReferenceArtifactProvider

POST_CLOSE_STATE_SCHEMA = "lucerna.post_close_review_state.v1"
PREOPEN_STATE_SCHEMA = "lucerna.preopen_review_state.v1"
WORKFLOW_CHAIN_SUMMARY_SCHEMA_V4 = "lucerna.workflow_chain_summary.v4"


class CandidateComparator:
    def __init__(self, reference: ReferenceArtifactProvider) -> None:
        self._reference = reference

    def compare(self, dimension: ParityDimension, context: ParityRunContext) -> ParityCheckResult:
        if dimension == ParityDimension.DAILY_REVIEW_STRUCTURE:
            return self._compare_daily_review(context)
        if dimension == ParityDimension.POST_CLOSE_HANDOFF_SHAPE:
            return self._compare_post_close(context)
        if dimension == ParityDimension.PREOPEN_HANDOFF_SHAPE:
            return self._compare_preopen(context)
        if dimension == ParityDimension.MARKET_GATE_STRICT_SEMANTICS:
            return self._compare_market_gate(context)
        if dimension == ParityDimension.WORKFLOW_CHAIN_SUMMARY_V4:
            return self._compare_chain_summary(context)
        return ParityCheckResult(
            dimension=dimension,
            verdict=ParityVerdict.UNSUPPORTED_GAP,
            message=f"unsupported dimension: {dimension.value}",
        )

    def _compare_daily_review(self, context: ParityRunContext) -> ParityCheckResult:
        ref_dir = self._reference.daily_review_dir(context.trade_date)
        actual_dir = context.daily_review_dir
        ref_ranking = ref_dir / "theme_state_ranking.csv"
        actual_ranking = actual_dir / "theme_state_ranking.csv"
        if not ref_ranking.is_file() or not actual_ranking.is_file():
            return ParityCheckResult(
                dimension=ParityDimension.DAILY_REVIEW_STRUCTURE,
                verdict=ParityVerdict.MISMATCH,
                message="missing theme_state_ranking.csv in actual or reference",
            )
        ref_frame = pd.read_csv(ref_ranking, encoding="utf-8-sig")
        actual_frame = pd.read_csv(actual_ranking, encoding="utf-8-sig")
        if list(ref_frame.columns) != list(actual_frame.columns):
            return ParityCheckResult(
                dimension=ParityDimension.DAILY_REVIEW_STRUCTURE,
                verdict=ParityVerdict.MISMATCH,
                message="theme_state_ranking column mismatch",
                details={
                    "reference_columns": list(ref_frame.columns),
                    "actual_columns": list(actual_frame.columns),
                },
            )
        ref_state = ref_dir / "market_daily_review_state.json"
        actual_state = actual_dir / "market_daily_review_state.json"
        if actual_state.is_file():
            payload = json.loads(actual_state.read_text(encoding="utf-8-sig"))
            if payload.get("schema") != DAILY_REVIEW_STATE_SCHEMA:
                return ParityCheckResult(
                    dimension=ParityDimension.DAILY_REVIEW_STRUCTURE,
                    verdict=ParityVerdict.MISMATCH,
                    message="daily review state schema mismatch",
                    details={"actual_schema": payload.get("schema")},
                )
        return ParityCheckResult(
            dimension=ParityDimension.DAILY_REVIEW_STRUCTURE,
            verdict=ParityVerdict.MATCH,
            message="daily review structure compatible",
            details={
                "reference_row_count": len(ref_frame),
                "actual_row_count": len(actual_frame),
                "reference_state_present": ref_state.is_file(),
            },
        )

    def _compare_review_csv_columns(
        self,
        *,
        dimension: ParityDimension,
        actual_review: Path,
        reference_review: Path,
    ) -> ParityCheckResult | None:
        if not reference_review.is_file() or not actual_review.is_file():
            return ParityCheckResult(
                dimension=dimension,
                verdict=ParityVerdict.MISMATCH,
                message="missing buy_point_review_internal.csv",
            )
        ref_frame = pd.read_csv(reference_review, encoding="utf-8-sig")
        actual_frame = pd.read_csv(actual_review, encoding="utf-8-sig")
        if list(ref_frame.columns) != list(actual_frame.columns):
            return ParityCheckResult(
                dimension=dimension,
                verdict=ParityVerdict.MISMATCH,
                message="review CSV column mismatch",
                details={
                    "reference_columns": list(ref_frame.columns),
                    "actual_columns": list(actual_frame.columns),
                },
            )
        return None

    def _compare_post_close(self, context: ParityRunContext) -> ParityCheckResult:
        ref_dir = self._reference.post_close_dir(context.trade_date)
        actual_dir = context.post_close_dir
        column_issue = self._compare_review_csv_columns(
            dimension=ParityDimension.POST_CLOSE_HANDOFF_SHAPE,
            actual_review=actual_dir / "buy_point_review_internal.csv",
            reference_review=ref_dir / "buy_point_review_internal.csv",
        )
        if column_issue is not None:
            return column_issue

        ref_pool = ref_dir / "candidate_pool_raw.json"
        actual_pool = actual_dir / "candidate_pool_raw.json"
        if ref_pool.is_file() and actual_pool.is_file():
            ref_payload = json.loads(ref_pool.read_text(encoding="utf-8-sig"))
            actual_payload = json.loads(actual_pool.read_text(encoding="utf-8-sig"))
            if set(ref_payload.keys()) != set(actual_payload.keys()):
                return ParityCheckResult(
                    dimension=ParityDimension.POST_CLOSE_HANDOFF_SHAPE,
                    verdict=ParityVerdict.MISMATCH,
                    message="candidate_pool_raw.json key mismatch",
                    details={
                        "reference_keys": sorted(ref_payload.keys()),
                        "actual_keys": sorted(actual_payload.keys()),
                    },
                )

        actual_state = actual_dir / "post_close_review_state.json"
        if actual_state.is_file():
            payload = json.loads(actual_state.read_text(encoding="utf-8-sig"))
            if payload.get("schema") != POST_CLOSE_STATE_SCHEMA:
                return ParityCheckResult(
                    dimension=ParityDimension.POST_CLOSE_HANDOFF_SHAPE,
                    verdict=ParityVerdict.MISMATCH,
                    message="post_close state schema mismatch",
                )
        return ParityCheckResult(
            dimension=ParityDimension.POST_CLOSE_HANDOFF_SHAPE,
            verdict=ParityVerdict.MATCH,
            message="post_close handoff shape compatible",
        )

    def _compare_preopen(self, context: ParityRunContext) -> ParityCheckResult:
        ref_dir = self._reference.preopen_dir(context.trade_date)
        actual_dir = context.preopen_dir
        column_issue = self._compare_review_csv_columns(
            dimension=ParityDimension.PREOPEN_HANDOFF_SHAPE,
            actual_review=actual_dir / "buy_point_review_internal.csv",
            reference_review=ref_dir / "buy_point_review_internal.csv",
        )
        if column_issue is not None:
            return column_issue

        actual_state = actual_dir / "preopen_review_state.json"
        if actual_state.is_file():
            payload = json.loads(actual_state.read_text(encoding="utf-8-sig"))
            if payload.get("schema") != PREOPEN_STATE_SCHEMA:
                return ParityCheckResult(
                    dimension=ParityDimension.PREOPEN_HANDOFF_SHAPE,
                    verdict=ParityVerdict.MISMATCH,
                    message="preopen state schema mismatch",
                )
        return ParityCheckResult(
            dimension=ParityDimension.PREOPEN_HANDOFF_SHAPE,
            verdict=ParityVerdict.MATCH,
            message="preopen handoff shape compatible",
        )

    def _compare_market_gate(self, context: ParityRunContext) -> ParityCheckResult:
        ref_dir = self._reference.market_gate_dir(context.trade_date)
        actual_dir = context.market_gate_dir
        try:
            compare_semantic_market_gate(actual_dir, ref_dir)
        except AssertionError as exc:
            return ParityCheckResult(
                dimension=ParityDimension.MARKET_GATE_STRICT_SEMANTICS,
                verdict=ParityVerdict.MISMATCH,
                message=str(exc),
            )
        summary = json.loads(
            (actual_dir / "market_gate_summary.json").read_text(encoding="utf-8-sig")
        )
        return ParityCheckResult(
            dimension=ParityDimension.MARKET_GATE_STRICT_SEMANTICS,
            verdict=ParityVerdict.MATCH,
            message="market_gate strict semantics match reference",
            details={
                "strict_count": summary.get("strict_count"),
                "workflow_review_source_stage": summary.get("workflow_review_source_stage"),
            },
        )

    def _compare_chain_summary(self, context: ParityRunContext) -> ParityCheckResult:
        if context.chain_summary_path is None or not context.chain_summary_path.is_file():
            return ParityCheckResult(
                dimension=ParityDimension.WORKFLOW_CHAIN_SUMMARY_V4,
                verdict=ParityVerdict.MISMATCH,
                message="missing workflow_chain_summary.json",
            )
        payload = json.loads(context.chain_summary_path.read_text(encoding="utf-8-sig"))
        if payload.get("schema") != WORKFLOW_CHAIN_SUMMARY_SCHEMA_V4:
            return ParityCheckResult(
                dimension=ParityDimension.WORKFLOW_CHAIN_SUMMARY_V4,
                verdict=ParityVerdict.MISMATCH,
                message="summary schema is not v4",
                details={"schema": payload.get("schema")},
            )
        stages = payload.get("stages") or {}
        audit_flags = {
            name: stage.get("audit_ok")
            for name, stage in stages.items()
            if isinstance(stage, dict) and "audit_ok" in stage
        }
        return ParityCheckResult(
            dimension=ParityDimension.WORKFLOW_CHAIN_SUMMARY_V4,
            verdict=ParityVerdict.MATCH,
            message="workflow_chain_summary v4 audit fields present",
            details={
                "chain_ok": payload.get("chain_ok"),
                "workflow_review_source_stage": payload.get("workflow_review_source_stage"),
                "stage_audit_ok": audit_flags,
                "provenance_mode": (payload.get("provenance") or {}).get("mode"),
            },
        )

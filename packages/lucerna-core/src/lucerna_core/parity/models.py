from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any


class ParityDimension(str, Enum):
    DAILY_REVIEW_STRUCTURE = "daily_review_structure"
    POST_CLOSE_HANDOFF_SHAPE = "post_close_handoff_shape"
    PREOPEN_HANDOFF_SHAPE = "preopen_handoff_shape"
    MARKET_GATE_STRICT_SEMANTICS = "market_gate_strict_semantics"
    WORKFLOW_CHAIN_SUMMARY_V4 = "workflow_chain_summary_v4"


class ParityVerdict(str, Enum):
    MATCH = "match"
    MISMATCH = "mismatch"
    INTENTIONAL_CHANGE = "intentional_change"
    UNSUPPORTED_GAP = "unsupported_gap"


PARITY_CHECK_RESULT_SCHEMA = "lucerna.parity_check_result.v1"
PARITY_RUN_REPORT_SCHEMA = "lucerna.parity_run_report.v1"


@dataclass(frozen=True)
class ParityCheckResult:
    dimension: ParityDimension
    verdict: ParityVerdict
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema": PARITY_CHECK_RESULT_SCHEMA,
            "dimension": self.dimension.value,
            "verdict": self.verdict.value,
            "message": self.message,
            "details": self.details,
        }


@dataclass(frozen=True)
class ParityRunContext:
    trade_date: date
    artifact_root: Path
    reference_root: Path
    dimensions: tuple[ParityDimension, ...]
    daily_review_dir: Path
    post_close_dir: Path
    preopen_dir: Path
    market_gate_dir: Path
    chain_summary_path: Path | None = None


@dataclass(frozen=True)
class ParityRunReport:
    trade_date: date
    artifact_root: Path
    reference_root: Path
    results: tuple[ParityCheckResult, ...]
    report_path: Path
    disclaimer: str = "research_audit_only"

    @property
    def all_match(self) -> bool:
        return all(result.verdict == ParityVerdict.MATCH for result in self.results)

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema": PARITY_RUN_REPORT_SCHEMA,
            "trade_date": self.trade_date.isoformat(),
            "artifact_root": str(self.artifact_root),
            "reference_root": str(self.reference_root),
            "disclaimer": self.disclaimer,
            "all_match": self.all_match,
            "results": [item.to_payload() for item in self.results],
        }

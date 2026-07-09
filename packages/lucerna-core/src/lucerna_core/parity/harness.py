from __future__ import annotations

from datetime import date
from pathlib import Path

from lucerna_core.artifacts.paths import workflow_chain_summary_path
from lucerna_core.parity.comparator import CandidateComparator
from lucerna_core.parity.config import write_parity_run_report
from lucerna_core.parity.models import ParityDimension, ParityRunContext, ParityRunReport
from lucerna_core.parity.reference import ReferenceArtifactProvider, actual_stage_dirs


class ParityHarness:
    """Run configured parity dimensions against a local reference artifact root."""

    def __init__(self, reference_root: Path) -> None:
        self._reference = ReferenceArtifactProvider(reference_root)
        self._comparator = CandidateComparator(self._reference)

    def run(self, context: ParityRunContext, *, report_path: Path) -> ParityRunReport:
        results = [
            self._comparator.compare(dimension, context) for dimension in context.dimensions
        ]
        report = ParityRunReport(
            trade_date=context.trade_date,
            artifact_root=context.artifact_root,
            reference_root=self._reference.reference_root,
            results=tuple(results),
            report_path=report_path,
        )
        write_parity_run_report(report)
        return report


def build_parity_context(
    *,
    trade_date: date,
    artifact_root: Path,
    reference_root: Path,
    dimensions: tuple[ParityDimension, ...],
) -> ParityRunContext:
    stages = actual_stage_dirs(artifact_root, trade_date)
    return ParityRunContext(
        trade_date=trade_date,
        artifact_root=artifact_root,
        reference_root=reference_root,
        dimensions=dimensions,
        daily_review_dir=stages["daily_review"],
        post_close_dir=stages["post_close"],
        preopen_dir=stages["preopen"],
        market_gate_dir=stages["market_gate"],
        chain_summary_path=workflow_chain_summary_path(artifact_root, trade_date),
    )

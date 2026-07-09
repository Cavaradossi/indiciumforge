from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Protocol

from lucerna_core.parity.models import (
    ParityCheckResult,
    ParityDimension,
    ParityRunContext,
    ParityRunReport,
)


class ReferenceArtifactProviderPort(Protocol):
    def daily_review_dir(self, trade_date: date) -> Path: ...

    def post_close_dir(self, trade_date: date) -> Path: ...

    def preopen_dir(self, trade_date: date) -> Path: ...

    def market_gate_dir(self, trade_date: date) -> Path: ...


class CandidateComparatorPort(Protocol):
    def compare(
        self,
        dimension: ParityDimension,
        context: ParityRunContext,
    ) -> ParityCheckResult: ...


class ParityHarnessPort(Protocol):
    def run(self, context: ParityRunContext) -> ParityRunReport: ...

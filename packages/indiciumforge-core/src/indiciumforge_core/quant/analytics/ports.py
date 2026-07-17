from __future__ import annotations

from typing import Protocol

from indiciumforge_core.quant.analytics.models import (
    FactorEvaluationRequest,
    FactorEvaluationResult,
)


class FactorAnalyticsPort(Protocol):
    """Port for cross-sectional factor analytics.

    Implementations turn a long-format factor surface plus a single-period
    return surface into information-coefficient (IC), Fama-MacBeth factor
    return, IC-decay and turnover statistics. The port is intentionally
    framework-agnostic: a concrete engine (e.g. :class:`StatsmodelsFactorEngine`)
    may back it with statsmodels, but the contract only requires ``evaluate``.
    """

    engine_id: str

    def supports(self, request: FactorEvaluationRequest) -> bool: ...

    def evaluate(self, request: FactorEvaluationRequest) -> FactorEvaluationResult: ...

from __future__ import annotations

from typing import Protocol

from indiciumforge_core.quant.portfolio.models import (
    PortfolioOptimizationRequest,
    PortfolioOptimizationResult,
)


class PortfolioOptimizationPort(Protocol):
    """Port for mean-variance / risk-based portfolio construction.

    A concrete optimizer (e.g. :class:`CvxpyOptimizer`) turns expected returns
    and a covariance matrix into long/short weights subject to linear and
    convex constraints. The contract only requires ``optimize``; the choice of
    solver is an adapter detail.
    """

    optimizer_id: str

    def supports(self, request: PortfolioOptimizationRequest) -> bool: ...

    def optimize(self, request: PortfolioOptimizationRequest) -> PortfolioOptimizationResult: ...

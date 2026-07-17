from __future__ import annotations

from indiciumforge_core.quant.portfolio.models import (
    PortfolioOptimizationRequest,
    PortfolioOptimizationResult,
)
from indiciumforge_core.quant.portfolio.ports import PortfolioOptimizationPort


class DuplicateOptimizerError(ValueError):
    """Raised when registering an optimizer with an existing optimizer_id."""


class PortfolioOptimizationRegistry:
    def __init__(self, optimizers: list[PortfolioOptimizationPort] | None = None) -> None:
        self._optimizers: dict[str, PortfolioOptimizationPort] = {}
        for opt in optimizers or []:
            self.register(opt)

    def register(self, optimizer: PortfolioOptimizationPort) -> None:
        if optimizer.optimizer_id in self._optimizers:
            raise DuplicateOptimizerError(
                f"optimizer already registered: {optimizer.optimizer_id}"
            )
        self._optimizers[optimizer.optimizer_id] = optimizer

    def list_optimizers(self) -> tuple[str, ...]:
        return tuple(self._optimizers.keys())

    def get(self, optimizer_id: str) -> PortfolioOptimizationPort:
        opt = self._optimizers.get(optimizer_id)
        if opt is None:
            raise KeyError(f"unknown optimizer: {optimizer_id}")
        return opt

    def optimize(
        self, optimizer_id: str, request: PortfolioOptimizationRequest
    ) -> PortfolioOptimizationResult:
        return self.get(optimizer_id).optimize(request)

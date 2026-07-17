from __future__ import annotations

from indiciumforge_core.quant.backtest.models import BacktestRequest, BacktestResult
from indiciumforge_core.quant.backtest.ports import BacktestPort


class DuplicateBacktesterError(ValueError):
    """Raised when registering a backtester with an existing backtester_id."""


class BacktestRegistry:
    def __init__(self, backtesters: list[BacktestPort] | None = None) -> None:
        self._backtesters: dict[str, BacktestPort] = {}
        for bt in backtesters or []:
            self.register(bt)

    def register(self, backtester: BacktestPort) -> None:
        if backtester.backtester_id in self._backtesters:
            raise DuplicateBacktesterError(
                f"backtester already registered: {backtester.backtester_id}"
            )
        self._backtesters[backtester.backtester_id] = backtester

    def list_backtesters(self) -> tuple[str, ...]:
        return tuple(self._backtesters.keys())

    def get(self, backtester_id: str) -> BacktestPort:
        bt = self._backtesters.get(backtester_id)
        if bt is None:
            raise KeyError(f"unknown backtester: {backtester_id}")
        return bt

    def run(self, backtester_id: str, request: BacktestRequest) -> BacktestResult:
        return self.get(backtester_id).run(request)

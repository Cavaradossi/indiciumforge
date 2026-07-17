from __future__ import annotations

from typing import Protocol

from indiciumforge_core.quant.backtest.models import BacktestRequest, BacktestResult


class BacktestPort(Protocol):
    """Port for strategy backtesting.

    Implementations turn a weight history and an asset-return surface into a
    portfolio return stream plus performance statistics (Sharpe, max drawdown,
    Calmar). The contract only requires ``run``; whether the engine is
    vectorized or event-driven is an adapter detail.
    """

    backtester_id: str

    def supports(self, request: BacktestRequest) -> bool: ...

    def run(self, request: BacktestRequest) -> BacktestResult: ...

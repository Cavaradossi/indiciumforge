from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class BacktestRequest:
    """Inputs for a vectorized backtest.

    ``weights_history`` and ``asset_returns`` are wide frames indexed by date
    with one column per ``asset_uid``. ``weights_history`` holds the *target*
    weights set at each rebalance; the backtester applies the **prior** period's
    weights to the current period's returns (no look-ahead). ``cost_bps`` is a
    flat per-trade cost charged on weight changes.
    """

    weights_history: pd.DataFrame
    asset_returns: pd.DataFrame
    rebalance_freq: int = 1
    cost_bps: float = 0.0
    init_capital: float = 1_000_000.0
    periods_per_year: int = 252
    as_of: date | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "rebalance_freq": self.rebalance_freq,
            "cost_bps": self.cost_bps,
            "init_capital": self.init_capital,
            "periods_per_year": self.periods_per_year,
            "n_assets": int(self.asset_returns.shape[1]),
            "n_periods": int(len(self.asset_returns)),
        }


@dataclass(frozen=True)
class BacktestResult:
    backtester_id: str
    portfolio_returns: pd.Series
    cumulative_pnl: pd.Series
    total_return: float
    annualized_return: float
    annualized_volatility: float
    sharpe: float
    max_drawdown: float
    calmar: float
    n_periods: int
    warnings: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        return {
            "backtester_id": self.backtester_id,
            "total_return": self.total_return,
            "annualized_return": self.annualized_return,
            "annualized_volatility": self.annualized_volatility,
            "sharpe": self.sharpe,
            "max_drawdown": self.max_drawdown,
            "calmar": self.calmar,
            "n_periods": self.n_periods,
            "warnings": list(self.warnings),
        }

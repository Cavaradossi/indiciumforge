from __future__ import annotations

import numpy as np
import pandas as pd

from indiciumforge_core.quant.backtest.models import BacktestRequest, BacktestResult


class VectorizedBacktester:
    """Vectorized, numpy/pandas-only backtester (no external engine).

    Portfolio return at ``t`` uses the **prior** period's target weights applied
    to period-``t`` asset returns, eliminating look-ahead. A flat ``cost_bps``
    is charged on weight changes (turnover) at each rebalance. Weights and
    returns are aligned positionally (not by DatetimeIndex shifting) so the
    "prior period" is always the immediately preceding row regardless of gaps
    in the calendar.

    Honest scope (see paper §11): this is a returns-attribution backtest, not an
    event-driven simulator. It has no intraday fills, no slippage model beyond a
    flat bps cost, no partial fills, and no corporate-action handling. A full
    event-driven engine (e.g. rqalpha) is a future optional extra on the same
    :class:`BacktestPort`.
    """

    backtester_id = "vectorized"

    def supports(self, request: BacktestRequest) -> bool:
        return len(request.asset_returns) > 0 and len(request.weights_history) > 0

    def run(self, request: BacktestRequest) -> BacktestResult:
        warnings: list[str] = []
        w = request.weights_history
        r = request.asset_returns

        common = w.index.intersection(r.index)
        if len(common) == 0:
            warnings.append("no overlapping dates between weights and returns")
            return self._empty(warnings)

        w = w.loc[common]
        r = r.loc[common]
        assets = list(w.columns.intersection(r.columns))
        if not assets:
            warnings.append("no shared assets between weights and returns")
            return self._empty(warnings)

        W = w[assets].to_numpy(dtype=float)  # (T, n)
        R = r[assets].to_numpy(dtype=float)  # (T, n)
        T = W.shape[0]

        # Prior-period weights (no look-ahead); the first row has no prior
        # position, so it starts at zero and is dropped as the warm-up day.
        prior_W = np.zeros_like(W)
        if T > 1:
            prior_W[1:] = W[:-1]

        port_ret = (prior_W * R).sum(axis=1)

        if request.cost_bps > 0:
            turnover = np.zeros(T)
            if T > 1:
                turnover[1:] = np.abs(np.diff(W, axis=0)).sum(axis=1)
            cost = (request.cost_bps / 1e4) * turnover
            port_ret = port_ret - cost

        # Drop the warm-up day (no prior weight -> no position).
        port_ret = port_ret[1:]
        idx = common[1:]

        if port_ret.size == 0:
            warnings.append("no valid backtest periods after alignment")
            return self._empty(warnings)

        port_ret = pd.Series(port_ret, index=idx)
        init = float(request.init_capital)
        cum = init * (1.0 + port_ret).cumprod()

        total_return = float(cum.iloc[-1] / init - 1.0)
        n = len(port_ret)
        ppy = max(int(request.periods_per_year), 1)

        ann_ret = float((1.0 + total_return) ** (ppy / n) - 1.0) if total_return > -1 else 0.0
        ann_vol = float(port_ret.std(ddof=1) * np.sqrt(ppy)) if n > 1 else 0.0
        sharpe = float(ann_ret / ann_vol) if ann_vol > 0 else 0.0

        running_max = cum.cummax()
        drawdown = cum / running_max - 1.0
        max_dd = float(drawdown.min())
        calmar = float(ann_ret / abs(max_dd)) if max_dd < 0 else 0.0

        return BacktestResult(
            backtester_id=self.backtester_id,
            portfolio_returns=port_ret,
            cumulative_pnl=cum,
            total_return=total_return,
            annualized_return=ann_ret,
            annualized_volatility=ann_vol,
            sharpe=sharpe,
            max_drawdown=max_dd,
            calmar=calmar,
            n_periods=n,
            warnings=tuple(warnings),
        )

    @staticmethod
    def _empty(warnings: list[str]) -> BacktestResult:
        empty = pd.Series(dtype=float)
        return BacktestResult(
            backtester_id="vectorized",
            portfolio_returns=empty,
            cumulative_pnl=empty,
            total_return=0.0,
            annualized_return=0.0,
            annualized_volatility=0.0,
            sharpe=0.0,
            max_drawdown=0.0,
            calmar=0.0,
            n_periods=0,
            warnings=tuple(warnings),
        )


# Structural subtype registration (mirrors providers/contracts_v2.py).
from indiciumforge_core.quant.backtest.ports import BacktestPort  # noqa: E402

BacktestPort.register(VectorizedBacktester)

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from indiciumforge_core.quant.analytics import FactorEvaluationRequest, StatsmodelsFactorEngine
from indiciumforge_core.quant.backtest import BacktestRequest, VectorizedBacktester
from indiciumforge_core.quant.portfolio import CvxpyOptimizer, PortfolioOptimizationRequest


@dataclass(frozen=True)
class QuantPipelineConfig:
    """Knobs for the reference A-share factor-to-backtest pipeline."""

    lookback: int = 20
    top_n: int = 10
    risk_aversion: float = 2.0
    cost_bps: float = 5.0
    rebalance_every: int = 5
    objective: str = "mean_variance"
    init_capital: float = 1_000_000.0
    # Tiny ridge added to the trailing covariance so the QP stays well-posed
    # even with a short estimation window. Negligible vs. signal scale.
    ridge: float = 1e-8


@dataclass(frozen=True)
class QuantPipelineResult:
    evaluation: Any
    optimization: Any
    backtest: Any
    weights_history: pd.DataFrame
    factor_panel: pd.DataFrame
    returns_panel: pd.DataFrame
    warnings: tuple[str, ...] = ()


def build_factor_and_returns(panel: pd.DataFrame, lookback: int = 20):
    """Derive a long momentum factor panel and a single-period return panel.

    ``panel`` is the golden/A-share long frame with at least ``asset_uid``,
    ``date`` and ``close``. The momentum factor at ``t`` is the trailing
    ``lookback``-period close return; the return panel is the one-period simple
    return used for both IC evaluation and the backtest.
    """
    wide = panel.pivot(index="date", columns="asset_uid", values="close").sort_index()
    ret = wide.pct_change(1)
    momentum = wide.pct_change(lookback)
    returns_panel = ret.stack().rename("ret").reset_index()
    factor_panel = momentum.stack().rename("factor_value").reset_index()
    factor_panel = factor_panel.dropna(subset=["factor_value"])
    return factor_panel, returns_panel


def run_quant_pipeline(
    panel: pd.DataFrame, config: QuantPipelineConfig | None = None
) -> QuantPipelineResult:
    """End-to-end reference pipeline: factor -> analytics -> optimize -> backtest.

    This is the same wiring demonstrated in the paper §9 case study. It is fully
    deterministic for a fixed ``panel`` (the committed golden snapshot), which is
    what lets the golden test lock the reported numbers.
    """
    config = config or QuantPipelineConfig()
    warnings: list[str] = []

    factor_panel, returns_panel = build_factor_and_returns(panel, config.lookback)
    evaluation = StatsmodelsFactorEngine().evaluate(
        FactorEvaluationRequest(
            factor_panel=factor_panel,
            returns_panel=returns_panel,
            horizons=(1, 5, 10),
            factor_name="momentum",
        )
    )
    warnings.extend(evaluation.warnings)

    ret_wide = returns_panel.pivot(index="date", columns="asset_uid", values="ret").sort_index()
    fac_wide = factor_panel.pivot(index="date", columns="asset_uid", values="factor_value").sort_index()
    assets = list(ret_wide.columns)
    all_dates = list(ret_wide.index)

    warmup = config.lookback + 1
    rebal_dates = all_dates[warmup:: config.rebalance_every]

    opt_cache: dict[Any, pd.Series] = {}
    last_opt = None
    for rd in rebal_dates:
        idx = all_dates.index(rd)
        start = max(0, idx - config.lookback + 1)
        window = ret_wide.iloc[start : idx + 1]
        fac_row = fac_wide.loc[rd]
        top = fac_row.dropna().sort_values(ascending=False).head(config.top_n).index.tolist()
        if len(top) < 2:
            warnings.append(f"rebalance {rd}: <2 ranked assets, holding prior weights")
            w = opt_cache[list(opt_cache)[-1]] if opt_cache else pd.Series(0.0, index=assets)
        else:
            mu = window[top].mean()
            cov = window[top].cov()
            scale = float(np.nanmax(cov.values.diagonal())) or 1.0
            cov = cov + np.eye(len(top)) * config.ridge * scale
            last_opt = CvxpyOptimizer().optimize(
                PortfolioOptimizationRequest(
                    expected_returns=mu,
                    covariance=cov,
                    objective=config.objective,
                    risk_aversion=config.risk_aversion,
                )
            )
            w = pd.Series(0.0, index=assets)
            w[top] = last_opt.weights.reindex(top).fillna(0.0).to_numpy()
        opt_cache[rd] = w

    wh = pd.DataFrame(index=ret_wide.index, columns=assets, dtype=float)
    prev = pd.Series(0.0, index=assets)
    for d in ret_wide.index:
        if d in opt_cache:
            prev = opt_cache[d]
        wh.loc[d] = prev.to_numpy()

    backtest = VectorizedBacktester().run(
        BacktestRequest(
            weights_history=wh,
            asset_returns=ret_wide,
            cost_bps=config.cost_bps,
            init_capital=config.init_capital,
        )
    )
    warnings.extend(backtest.warnings)

    return QuantPipelineResult(
        evaluation=evaluation,
        optimization=last_opt,
        backtest=backtest,
        weights_history=wh,
        factor_panel=factor_panel,
        returns_panel=returns_panel,
        warnings=tuple(warnings),
    )

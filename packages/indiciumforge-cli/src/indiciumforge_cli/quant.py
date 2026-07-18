from __future__ import annotations

import json
from pathlib import Path

import typer

quant_app = typer.Typer(help="Quant analytics, optimization, backtest and pricing.")


def _echo_payload(payload: dict) -> None:
    typer.echo(json.dumps(payload, indent=2, default=str))


@quant_app.command("analytics", help="Evaluate a factor panel (IC / Fama-MacBeth / turnover).")
def analytics(
    factor_panel: Path = typer.Option(
        ..., "--factor-panel", help="CSV: date,asset_uid,factor_value"
    ),
    returns_panel: Path = typer.Option(
        ..., "--returns-panel", help="CSV: date,asset_uid,ret"
    ),
    factor_name: str = typer.Option("factor", "--factor-name"),
    horizons: str = typer.Option("1,5,10", "--horizons"),
) -> None:
    # Lazy import: the extra is only required when the command actually runs.
    import pandas as pd
    from indiciumforge_core.quant.analytics import (
        FactorEvaluationRequest,
        StatsmodelsFactorEngine,
    )

    fp = pd.read_csv(factor_panel)
    rp = pd.read_csv(returns_panel)
    hs = tuple(int(h) for h in horizons.split(",") if h.strip())
    result = StatsmodelsFactorEngine().evaluate(
        FactorEvaluationRequest(
            factor_panel=fp, returns_panel=rp, factor_name=factor_name, horizons=hs
        )
    )
    _echo_payload(result.to_payload())


@quant_app.command("optimize", help="Mean-variance / min-variance weight optimization.")
def optimize(
    expected_returns: Path = typer.Option(
        ..., "--expected-returns", help="CSV: asset_uid,mu"
    ),
    covariance: Path = typer.Option(
        ..., "--covariance", help="CSV: square matrix, asset_uid indexed"
    ),
    objective: str = typer.Option("mean_variance", "--objective"),
    risk_aversion: float = typer.Option(2.0, "--risk-aversion"),
) -> None:
    import pandas as pd
    from indiciumforge_core.quant.portfolio import (
        CvxpyOptimizer,
        PortfolioOptimizationRequest,
    )

    mu = pd.read_csv(expected_returns, index_col=0).iloc[:, 0]
    cov = pd.read_csv(covariance, index_col=0)
    result = CvxpyOptimizer().optimize(
        PortfolioOptimizationRequest(
            expected_returns=mu,
            covariance=cov,
            objective=objective,
            risk_aversion=risk_aversion,
        )
    )
    _echo_payload(result.to_payload())


@quant_app.command("backtest", help="Vectorized backtest of a weight history.")
def backtest(
    weights: Path = typer.Option(..., "--weights", help="CSV: date-indexed, asset_uid columns"),
    returns: Path = typer.Option(..., "--returns", help="CSV: date-indexed, asset_uid columns"),
    cost_bps: float = typer.Option(0.0, "--cost-bps"),
) -> None:
    import pandas as pd
    from indiciumforge_core.quant.backtest import (
        BacktestRequest,
        VectorizedBacktester,
    )

    w = pd.read_csv(weights, index_col=0, parse_dates=True)
    r = pd.read_csv(returns, index_col=0, parse_dates=True)
    result = VectorizedBacktester().run(
        BacktestRequest(weights_history=w, asset_returns=r, cost_bps=cost_bps)
    )
    _echo_payload(result.to_payload())


@quant_app.command("price", help="Analytic Black-Scholes European option price + Greeks.")
def price(
    spot: float = typer.Option(..., "--spot"),
    strike: float = typer.Option(..., "--strike"),
    maturity: float = typer.Option(..., "--maturity"),
    rate: float = typer.Option(..., "--rate"),
    volatility: float = typer.Option(..., "--volatility"),
    option_type: str = typer.Option("call", "--type"),
) -> None:
    from indiciumforge_core.quant.pricing import BlackScholesPricer, PricingRequest

    result = BlackScholesPricer().price(
        PricingRequest(
            spot=spot,
            strike=strike,
            maturity=maturity,
            rate=rate,
            volatility=volatility,
            option_type=option_type,
        )
    )
    _echo_payload(result.to_payload())


@quant_app.command(
    "pipeline",
    help="Run the reference factor->analytics->optimize->backtest pipeline on a panel.",
)
def pipeline(
    panel: Path = typer.Option(..., "--panel", help="CSV/parquet: asset_uid,date,close,..."),
    lookback: int = typer.Option(20, "--lookback"),
    top_n: int = typer.Option(10, "--top-n"),
    rebalance_every: int = typer.Option(5, "--rebalance-every"),
    cost_bps: float = typer.Option(5.0, "--cost-bps"),
    risk_aversion: float = typer.Option(2.0, "--risk-aversion"),
) -> None:
    import pandas as pd
    from indiciumforge_core.quant.pipeline import (
        QuantPipelineConfig,
        run_quant_pipeline,
    )

    if str(panel).endswith(".parquet"):
        df = pd.read_parquet(panel)
    else:
        df = pd.read_csv(panel)
    result = run_quant_pipeline(
        df,
        QuantPipelineConfig(
            lookback=lookback,
            top_n=top_n,
            rebalance_every=rebalance_every,
            cost_bps=cost_bps,
            risk_aversion=risk_aversion,
        ),
    )
    _echo_payload(
        {
            "evaluation_ic_by_horizon": [
                s.to_payload() for s in result.evaluation.ic_by_horizon
            ],
            "optimization": result.optimization.to_payload()
            if result.optimization is not None
            else None,
            "backtest": result.backtest.to_payload(),
            "warnings": list(result.warnings),
        }
    )

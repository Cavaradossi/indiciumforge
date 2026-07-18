from __future__ import annotations

import json
from datetime import date, datetime
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


def _fetch_openbb_panel(tickers: tuple[str, ...], start: date, end: date):
    """Fetch a long US-equity OHLCV panel via OpenBB (requires the [openbb] extra)."""
    import pandas as pd
    from indiciumforge_core.providers.capabilities import DataKind
    from indiciumforge_core.providers.openbb import OpenBBDataProvider
    from indiciumforge_core.providers.query import DataQuery
    from indiciumforge_core.workflow.model import AssetDomain

    provider = OpenBBDataProvider(openbb_provider="yfinance")
    frames = []
    for ticker in tickers:
        asset = provider.asset_from_ticker(ticker)
        result = provider.fetch(
            DataQuery(
                asset=asset,
                asset_domain=AssetDomain.US_EQUITY,
                data_kind=DataKind.OHLCV,
                start=start,
                end=end,
            )
        )
        if result.frame.empty:
            continue
        frame = result.frame.copy()
        frame["asset_uid"] = asset.uid
        frames.append(frame[["asset_uid", "date", "open", "high", "low", "close", "volume"]])
    if not frames:
        raise RuntimeError("OpenBB returned no rows for any requested ticker")
    return pd.concat(frames, ignore_index=True)


@quant_app.command(
    "openbb-demo",
    help=(
        "Public OpenBB demo: run the reference factor->analytics->optimize->backtest "
        "pipeline on a US-equity panel. Offline deterministic sample by default; "
        "--online fetches real data via OpenBB ([openbb] extra)."
    ),
)
def openbb_demo(
    artifact_root: Path = typer.Option(..., "--artifact-root"),
    panel: Path | None = typer.Option(
        None, "--panel", help="Override the panel CSV (defaults to the shipped sample)."
    ),
    online: bool = typer.Option(
        False, "--online", help="Fetch live US-equity data via OpenBB instead of the sample."
    ),
    tickers: str = typer.Option(
        "AAPL,MSFT,GOOGL,AMZN,NVDA,META,TSLA,AVGO",
        "--tickers",
        help="Comma-separated (online only).",
    ),
    start: str = typer.Option("2024-01-02", "--start", help="ISO date (online only)."),
    end: str = typer.Option("2024-06-28", "--end", help="ISO date (online only)."),
    lookback: int = typer.Option(20, "--lookback"),
    top_n: int = typer.Option(5, "--top-n"),
    rebalance_every: int = typer.Option(5, "--rebalance-every"),
    cost_bps: float = typer.Option(5.0, "--cost-bps"),
) -> None:
    import pandas as pd
    from indiciumforge_core.data import openbb_demo_manifest_path, openbb_demo_panel_path
    from indiciumforge_core.quant.pipeline import QuantPipelineConfig, run_quant_pipeline

    if online:
        ts = tuple(t.strip().upper() for t in tickers.split(",") if t.strip())
        df = _fetch_openbb_panel(
            ts, date.fromisoformat(start), date.fromisoformat(end)
        )
        data_source = "openbb_live"
        universe = list(ts)
    elif panel is not None:
        df = pd.read_csv(panel)
        data_source = f"panel_override:{panel.name}"
        universe = sorted(df["asset_uid"].unique().tolist())
    else:
        sample = openbb_demo_panel_path()
        df = pd.read_csv(sample)
        data_source = "offline_sample"
        universe = sorted(df["asset_uid"].unique().tolist())

    result = run_quant_pipeline(
        df,
        QuantPipelineConfig(
            lookback=lookback,
            top_n=top_n,
            rebalance_every=rebalance_every,
            cost_bps=cost_bps,
        ),
    )

    summary = {
        "schema": "indiciumforge.openbb_demo_summary.v1",
        "data_source": data_source,
        "note": (
            "Offline sample uses synthetic deterministic values (not real quotes); "
            "run with --online for real OpenBB data."
            if data_source == "offline_sample"
            else "Live data fetched via OpenBB."
        ),
        "universe": universe,
        "rows": int(len(df)),
        "config": {
            "lookback": lookback,
            "top_n": top_n,
            "rebalance_every": rebalance_every,
            "cost_bps": cost_bps,
        },
        "evaluation_ic_by_horizon": [
            s.to_payload() for s in result.evaluation.ic_by_horizon
        ],
        "optimization": result.optimization.to_payload()
        if result.optimization is not None
        else None,
        "backtest": result.backtest.to_payload(),
        "warnings": list(result.warnings),
    }

    out_dir = artifact_root / "openbb_demo"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "summary.json"
    with summary_path.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, default=str)
        fh.write("\n")

    if data_source == "offline_sample":
        with openbb_demo_manifest_path().open(encoding="utf-8") as fh:
            (out_dir / "panel_MANIFEST.yaml").write_text(fh.read(), encoding="utf-8")

    _echo_payload(
        {
            "wrote": str(summary_path),
            "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            **{k: summary[k] for k in ("data_source", "universe", "rows")},
            "backtest": summary["backtest"],
        }
    )

from __future__ import annotations

from pathlib import Path

import pandas as pd

GOLDEN = (
    Path(__file__).resolve().parents[1] / "fixtures" / "golden_ashare" / "panel.parquet"
)


def test_golden_pipeline_deterministic():
    """Same inputs must yield byte-identical reported numbers (locks §9)."""
    from indiciumforge_core.quant.pipeline import (
        QuantPipelineConfig,
        run_quant_pipeline,
    )

    panel = pd.read_parquet(GOLDEN)
    cfg = QuantPipelineConfig(
        lookback=20, top_n=10, rebalance_every=10, cost_bps=5.0
    )

    r1 = run_quant_pipeline(panel, cfg)
    r2 = run_quant_pipeline(panel, cfg)

    assert r1.backtest.total_return == r2.backtest.total_return
    assert r1.backtest.sharpe == r2.backtest.sharpe
    assert r1.backtest.max_drawdown == r2.backtest.max_drawdown
    assert r1.backtest.calmar == r2.backtest.calmar
    # The pipeline exercises a non-trivial fraction of the panel.
    assert r1.backtest.n_periods > 100
    # IC evaluation is stable too.
    assert (
        r1.evaluation.ic_by_horizon[0].ic_mean
        == r2.evaluation.ic_by_horizon[0].ic_mean
    )

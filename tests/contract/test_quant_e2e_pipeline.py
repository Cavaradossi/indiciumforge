from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

GOLDEN = (
    Path(__file__).resolve().parents[1] / "fixtures" / "golden_ashare" / "panel.parquet"
)
DEMO_PACK = (
    Path(__file__).resolve().parents[1] / "fixtures" / "quant_pack_demo.yaml"
)


def _panel() -> pd.DataFrame:
    return pd.read_parquet(GOLDEN)


def test_e2e_pipeline_runs_and_reports_positive_ic():
    from indiciumforge_core.quant.pipeline import (
        QuantPipelineConfig,
        run_quant_pipeline,
    )

    panel = _panel()
    cfg = QuantPipelineConfig(
        lookback=20, top_n=10, rebalance_every=10, cost_bps=5.0
    )
    res = run_quant_pipeline(panel, cfg)

    # Momentum factor shows positive IC on the persistent-trend synthetic panel.
    assert res.evaluation.ic_by_horizon[0].ic_mean > 0
    # Backtest is well-formed.
    assert res.backtest.n_periods > 0
    assert np.isfinite(res.backtest.sharpe)
    assert res.backtest.max_drawdown < 0
    # At least one rebalance row is fully invested (weights sum to 1).
    assert np.any(np.isclose(res.weights_history.sum(axis=1), 1.0, atol=1e-6))
    assert res.optimization is not None


def test_demo_pack_fixture_loads():
    from indiciumforge_core.quant.analytics import load_analytics_pack

    loaded = load_analytics_pack(pack_config=DEMO_PACK)
    assert "statsmodels" in loaded.registry.list_engines()
    assert loaded.pack_id == "quant-demo"

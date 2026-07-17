from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

from indiciumforge_core.quant.backtest import (
    BacktestRequest,
    BacktesterLoadError,
    VectorizedBacktester,
    load_backtest_pack,
)

DATES = [date(2024, 1, 1) + timedelta(days=i) for i in range(3)]
ASSETS = ["a", "b"]


def _frames():
    weights = pd.DataFrame(
        [[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]],
        index=DATES,
        columns=ASSETS,
    )
    returns = pd.DataFrame(
        [[0.01, 0.04], [0.02, 0.05], [0.03, 0.06]],
        index=DATES,
        columns=ASSETS,
    )
    return weights, returns


def test_prior_weights_no_lookahead():
    w, r = _frames()
    res = VectorizedBacktester().run(BacktestRequest(weights_history=w, asset_returns=r))
    # d0 dropped (no prior weight); d1 uses d0 weights (a=1) -> r_a[d1]=0.02
    pr = res.portfolio_returns
    assert pr.iloc[0] == pytest.approx(0.02)
    assert pr.iloc[1] == pytest.approx(0.06)
    assert res.total_return == pytest.approx(1.02 * 1.06 - 1.0, abs=1e-9)


def test_cost_bps_deduction():
    w, r = _frames()
    res = VectorizedBacktester().run(
        BacktestRequest(weights_history=w, asset_returns=r, cost_bps=10.0)
    )
    # turnover d1 = |(0,1)-(1,0)|=2 -> cost 0.001*2=0.002; d2 = |(0.5,0.5)-(0,1)|=1 -> 0.001
    assert res.portfolio_returns.iloc[0] == pytest.approx(0.02 - 0.002, abs=1e-9)
    assert res.portfolio_returns.iloc[1] == pytest.approx(0.06 - 0.001, abs=1e-9)


def test_stats_finite_and_drawdown_nonpositive():
    rng = np.random.default_rng(7)
    n = 60
    dates = [date(2024, 1, 1) + timedelta(days=i) for i in range(n)]
    w = pd.DataFrame(np.ones((n, 3)) / 3.0, index=dates, columns=["x", "y", "z"])
    r = pd.DataFrame(rng.normal(0.0005, 0.01, size=(n, 3)), index=dates, columns=["x", "y", "z"])
    res = VectorizedBacktester().run(BacktestRequest(weights_history=w, asset_returns=r))
    assert res.n_periods == n - 1
    assert np.isfinite(res.sharpe)
    assert res.max_drawdown <= 0.0
    # cumulative_pnl monotonic-ish: last value positive-ish, length matches
    assert len(res.cumulative_pnl) == n - 1


def test_supports_gate():
    w, r = _frames()
    req = BacktestRequest(weights_history=w, asset_returns=r)
    assert VectorizedBacktester().supports(req) is True
    empty = BacktestRequest(
        weights_history=pd.DataFrame(), asset_returns=pd.DataFrame()
    )
    assert VectorizedBacktester().supports(empty) is False


def test_no_overlap_warns():
    w = pd.DataFrame([[1.0]], index=[date(2024, 1, 1)], columns=["a"])
    r = pd.DataFrame([[0.01]], index=[date(2025, 1, 1)], columns=["a"])
    res = VectorizedBacktester().run(BacktestRequest(weights_history=w, asset_returns=r))
    assert res.warnings
    assert res.n_periods == 0


def test_pack_loading(tmp_path):
    bt_yaml = tmp_path / "backtesters.yaml"
    bt_yaml.write_text(
        "backtesters:\n"
        "  - module: indiciumforge_core.quant.backtest.vectorized\n"
        "    class: VectorizedBacktester\n",
        encoding="utf-8",
    )
    pack_yaml = tmp_path / "pack.yaml"
    pack_yaml.write_text(
        "schema: indiciumforge.backtest_pack.v1\n"
        "pack_id: demo-bt\n"
        "version: '1.0'\n"
        "load:\n"
        "  backtesters_config: backtesters.yaml\n",
        encoding="utf-8",
    )
    loaded = load_backtest_pack(pack_config=pack_yaml)
    assert "vectorized" in loaded.registry.list_backtesters()


def test_pack_rejects_wrong_schema(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("schema: indiciumforge.wrong_pack.v1\n", encoding="utf-8")
    with pytest.raises(BacktesterLoadError):
        load_backtest_pack(pack_config=bad)

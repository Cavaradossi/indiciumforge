from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd
import pytest
from indiciumforge_core.quant.portfolio import (
    CvxpyOptimizer,
    PortfolioOptimizationRequest,
    load_portfolio_pack,
)
from indiciumforge_core.quant.portfolio.loading import PortfolioOptimizerLoadError


def _psd_cov(assets, corr=None, vols=None, seed=0):
    n = len(assets)
    rng = np.random.default_rng(seed)
    if corr is None:
        base = rng.normal(size=(n, n))
        corr = base @ base.T / n  # PSD
        np.fill_diagonal(corr, 1.0)
    if vols is None:
        vols = np.ones(n)
    d = np.diag(vols)
    return pd.DataFrame(d @ corr @ d, index=assets, columns=assets)


ASSETS = ["a00", "a01", "a02", "a03"]


def test_optimizer_identity():
    assert CvxpyOptimizer.optimizer_id == "cvxpy"
    assert CvxpyOptimizer().optimizer_id == "cvxpy"


def test_weights_sum_to_one_and_long_only():
    cov = _psd_cov(ASSETS, seed=1)
    mu = pd.Series([0.05, 0.04, 0.06, 0.03], index=ASSETS)
    res = CvxpyOptimizer().optimize(
        PortfolioOptimizationRequest(expected_returns=mu, covariance=cov, objective="mean_variance")
    )
    assert res.solver_status in ("optimal", "optimal_inaccurate")
    assert res.weights.sum() == pytest.approx(1.0, abs=1e-6)
    assert (res.weights >= -1e-6).all()
    assert res.weights.min() >= -1e-6


def test_weight_bounds_respected():
    cov = _psd_cov(ASSETS, seed=2)
    mu = pd.Series([0.05, 0.04, 0.06, 0.03], index=ASSETS)
    res = CvxpyOptimizer().optimize(
        PortfolioOptimizationRequest(
            expected_returns=mu,
            covariance=cov,
            weight_bounds=(0.1, 0.5),
        )
    )
    assert res.weights.min() >= 0.1 - 1e-6
    assert res.weights.max() <= 0.5 + 1e-6


def test_sector_caps_respected():
    cov = _psd_cov(ASSETS, seed=3)
    mu = pd.Series([0.05, 0.04, 0.06, 0.03], index=ASSETS)
    res = CvxpyOptimizer().optimize(
        PortfolioOptimizationRequest(
            expected_returns=mu,
            covariance=cov,
            sector_caps=((["a00", "a01"], 0.4),),
        )
    )
    grp = res.weights.loc[["a00", "a01"]].sum()
    assert grp <= 0.4 + 1e-6


def test_min_variance_risk_le_mean_variance_risk():
    cov = _psd_cov(ASSETS, seed=4)
    mu = pd.Series([0.05, 0.04, 0.06, 0.03], index=ASSETS)
    req = PortfolioOptimizationRequest(expected_returns=mu, covariance=cov)
    minv = CvxpyOptimizer().optimize(dataclasses.replace(req, objective="min_variance"))
    mv = CvxpyOptimizer().optimize(
        dataclasses.replace(req, objective="mean_variance", risk_aversion=2.0)
    )
    assert minv.expected_risk <= mv.expected_risk + 1e-9


def test_two_asset_closed_form_matches():
    # 2-asset global-min-variance closed form: w1 = (s22 - s12)/(s11 + s22 - 2 s12).
    s11, s22, s12 = 0.04, 0.09, 0.02
    cov = pd.DataFrame(
        [[s11, s12], [s12, s22]], index=["x", "y"], columns=["x", "y"]
    )
    mu = pd.Series([0.05, 0.06], index=["x", "y"])
    res = CvxpyOptimizer().optimize(
        PortfolioOptimizationRequest(expected_returns=mu, covariance=cov, objective="min_variance")
    )
    w1 = (s22 - s12) / (s11 + s22 - 2 * s12)
    w2 = 1.0 - w1
    assert res.weights["x"] == pytest.approx(w1, abs=1e-4)
    assert res.weights["y"] == pytest.approx(w2, abs=1e-4)
    expected_var = w1**2 * s11 + w2**2 * s22 + 2 * w1 * w2 * s12
    assert res.expected_risk == pytest.approx(np.sqrt(expected_var), abs=1e-4)


def test_supports_gate():
    req = PortfolioOptimizationRequest(
        expected_returns=pd.Series([0.0], index=["a"]),
        covariance=pd.DataFrame([[1.0]], index=["a"], columns=["a"]),
        objective="min_variance",
    )
    assert CvxpyOptimizer().supports(req) is True
    bad = dataclasses.replace(req, objective="unknown")
    assert CvxpyOptimizer().supports(bad) is False


def test_registry_and_pack_loading(tmp_path):
    opt_yaml = tmp_path / "optimizers.yaml"
    opt_yaml.write_text(
        "optimizers:\n"
        "  - module: indiciumforge_core.quant.portfolio.cvxpy_optimizer\n"
        "    class: CvxpyOptimizer\n",
        encoding="utf-8",
    )
    pack_yaml = tmp_path / "pack.yaml"
    pack_yaml.write_text(
        "schema: indiciumforge.portfolio_pack.v1\n"
        "pack_id: demo-port\n"
        "version: '1.0'\n"
        "load:\n"
        "  optimizers_config: optimizers.yaml\n",
        encoding="utf-8",
    )
    loaded = load_portfolio_pack(pack_config=pack_yaml)
    assert "cvxpy" in loaded.registry.list_optimizers()


def test_pack_rejects_wrong_schema(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("schema: indiciumforge.wrong_pack.v1\n", encoding="utf-8")
    with pytest.raises(PortfolioOptimizerLoadError):
        load_portfolio_pack(pack_config=bad)

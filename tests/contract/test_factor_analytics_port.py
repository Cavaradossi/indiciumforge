from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest
from indiciumforge_core.quant.analytics import (
    FactorAnalyticsLoadError,
    FactorAnalyticsRegistry,
    FactorEvaluationRequest,
    StatsmodelsFactorEngine,
    factor_panel_from_signals,
    load_analytics_from_config,
    load_analytics_pack,
)

N_DATES = 60
N_ASSETS = 20
ASSETS = [f"a{i:02d}" for i in range(N_ASSETS)]
DATES = [date(2024, 1, 1) + timedelta(days=i) for i in range(N_DATES)]


def _make_panels(seed: int = 0, *, planted: bool = False):
    """Return (factor_panel, returns_panel) long frames.

    With ``planted=True`` the factor value at t equals the *next* period's
    single return, so it perfectly predicts the 1-day forward return but not
    the longer horizons (the extra periods are independent noise). This yields
    IC(1) ~= 1.0 and a monotone IC decay.
    """
    rng = np.random.default_rng(seed)
    ret = rng.normal(0.0, 0.01, size=(N_DATES, N_ASSETS))
    if planted:
        factor = np.roll(ret, -1, axis=0)
        factor[-1, :] = 0.0
    else:
        factor = rng.normal(0.0, 1.0, size=(N_DATES, N_ASSETS))

    frows, rrows = [], []
    for t, d in enumerate(DATES):
        for a in range(N_ASSETS):
            frows.append({"date": d, "asset_uid": ASSETS[a], "factor_value": float(factor[t, a])})
            rrows.append({"date": d, "asset_uid": ASSETS[a], "ret": float(ret[t, a])})
    return pd.DataFrame(frows), pd.DataFrame(rrows)


def _request(factor_panel, returns_panel, **kw):
    return FactorEvaluationRequest(
        factor_panel=factor_panel,
        returns_panel=returns_panel,
        factor_name="demo",
        horizons=(1, 5, 10),
        **kw,
    )


def test_engine_identity():
    assert StatsmodelsFactorEngine.engine_id == "statsmodels"
    assert StatsmodelsFactorEngine().engine_id == "statsmodels"


def test_planted_signal_ic_approximately_one():
    fp, rp = _make_panels(seed=1, planted=True)
    result = StatsmodelsFactorEngine().evaluate(_request(fp, rp))
    ic1 = result.ic_by_horizon[0]
    assert ic1.horizon == 1
    assert ic1.ic_mean > 0.99  # factor == next-period return -> perfect rank corr
    assert ic1.positive_pct == pytest.approx(1.0)
    assert ic1.n_dates > 0


def test_random_factor_ic_near_zero():
    fp, rp = _make_panels(seed=2, planted=False)
    result = StatsmodelsFactorEngine().evaluate(_request(fp, rp))
    for stat in result.ic_by_horizon:
        assert abs(stat.ic_mean) < 0.25


def test_ic_decay_monotone_for_planted_signal():
    fp, rp = _make_panels(seed=3, planted=True)
    result = StatsmodelsFactorEngine().evaluate(_request(fp, rp))
    ics = [s.ic_mean for s in result.ic_by_horizon]
    assert ics[0] > ics[1] > ics[2], ics
    # decay magnitude is sensible: 1-day >> 10-day
    assert ics[0] > 0.9
    assert ics[2] < ics[0]


def test_fama_macbeth_tstat_sign_matches_slope():
    fp, rp = _make_panels(seed=4, planted=True)
    result = StatsmodelsFactorEngine().evaluate(_request(fp, rp))
    fr = result.factor_returns
    assert fr.n_dates > 0
    assert np.isfinite(fr.t_stat)
    # planted positive predictor -> positive mean slope and positive t-stat
    assert fr.mean > 0
    assert fr.t_stat > 0


def test_turnover_bounded():
    fp, rp = _make_panels(seed=5, planted=True)
    result = StatsmodelsFactorEngine().evaluate(_request(fp, rp))
    assert 0.0 <= result.turnover.turnover <= 2.0


def test_degenerate_cross_section_warns():
    # Build a factor panel with fewer assets than min_cross_section.
    small = pd.DataFrame(
        [
            {"date": DATES[0], "asset_uid": "a00", "factor_value": 1.0},
            {"date": DATES[0], "asset_uid": "a01", "factor_value": 2.0},
            {"date": DATES[0], "asset_uid": "a02", "factor_value": 3.0},
        ]
    )
    rp = pd.DataFrame(
        [
            {"date": DATES[0], "asset_uid": f"a{i:02d}", "ret": 0.01 * i}
            for i in range(N_ASSETS)
        ]
    )
    result = StatsmodelsFactorEngine().evaluate(_request(small, rp, min_cross_section=5))
    assert result.warnings  # at least one warning emitted
    assert all(s.n_dates == 0 for s in result.ic_by_horizon)


def test_factor_panel_from_signals_roundtrip():
    from indiciumforge_core.domain.models import AssetID, Exchange
    from indiciumforge_core.factors.models import FactorSignal

    sigs = [
        FactorSignal(
            asset=AssetID(code="600000", exchange=Exchange.SSE, asset_type=__import__(
                "indiciumforge_core.domain.models", fromlist=["AssetType"]
            ).AssetType.STOCK, currency="CNY"),
            factor="momentum",
            as_of=DATES[0],
            matched=True,
            score=1.5,
        )
    ]
    panel = factor_panel_from_signals(sigs)
    assert list(panel.columns) == ["date", "asset_uid", "factor_value"]
    assert panel.iloc[0]["asset_uid"] == "sse:stock:600000"
    assert panel.iloc[0]["factor_value"] == 1.5


def test_pack_and_config_loading(tmp_path):
    engines_yaml = tmp_path / "engines.yaml"
    engines_yaml.write_text(
        "engines:\n"
        "  - module: indiciumforge_core.quant.analytics.statsmodels_engine\n"
        "    class: StatsmodelsFactorEngine\n",
        encoding="utf-8",
    )
    registry = load_analytics_from_config(engines_yaml)
    assert "statsmodels" in registry.list_engines()
    result = registry.evaluate("statsmodels", _request(*_make_panels(seed=6, planted=True)))
    assert result.engine_id == "statsmodels"

    pack_yaml = tmp_path / "pack.yaml"
    pack_yaml.write_text(
        "schema: indiciumforge.factor_analytics_pack.v1\n"
        "pack_id: demo-pack\n"
        "version: '1.0'\n"
        "load:\n"
        "  engines_config: engines.yaml\n",
        encoding="utf-8",
    )
    loaded = load_analytics_pack(pack_config=pack_yaml)
    assert loaded.pack_id == "demo-pack"
    assert "statsmodels" in loaded.registry.list_engines()


def test_pack_rejects_wrong_schema(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("schema: indiciumforge.wrong_pack.v1\n", encoding="utf-8")
    with pytest.raises(FactorAnalyticsLoadError):
        load_analytics_pack(pack_config=bad)


def test_duplicate_engine_raises():
    from indiciumforge_core.quant.analytics.registry import DuplicateEngineError

    reg = FactorAnalyticsRegistry([StatsmodelsFactorEngine()])
    with pytest.raises(DuplicateEngineError):
        reg.register(StatsmodelsFactorEngine())

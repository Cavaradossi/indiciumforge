from __future__ import annotations

import dataclasses
import math

import pytest
from indiciumforge_core.quant.pricing import (
    BlackScholesPricer,
    PricerLoadError,
    PricingRequest,
    load_pricing_pack,
)


def _req(**overrides: object) -> PricingRequest:
    base = dict(
        spot=100.0,
        strike=100.0,
        maturity=1.0,
        rate=0.05,
        volatility=0.2,
        option_type="call",
    )
    base.update(overrides)
    return PricingRequest(**base)  # type: ignore[arg-type]


def test_atm_call_price():
    res = BlackScholesPricer().price(_req())
    # Analytic BS ATM call ~= 10.45
    assert res.price == pytest.approx(10.4506, abs=1e-3)
    assert res.pricer_id == "black_scholes"


def test_put_call_parity():
    call = BlackScholesPricer().price(_req(option_type="call"))
    put = BlackScholesPricer().price(_req(option_type="put"))
    S, K, r, T = 100.0, 100.0, 0.05, 1.0
    parity = S - K * math.exp(-r * T)
    assert (call.price - put.price) == pytest.approx(parity, abs=1e-6)


def test_greek_signs_call():
    res = BlackScholesPricer().price(_req())
    assert 0.0 < res.delta < 1.0
    assert res.gamma > 0.0
    assert res.vega > 0.0
    assert res.rho > 0.0
    assert res.theta < 0.0


def test_put_delta_negative():
    res = BlackScholesPricer().price(_req(option_type="put"))
    assert res.delta < 0.0


def test_supports_gate():
    req = _req(spot=100, strike=100, maturity=1)
    assert BlackScholesPricer().supports(req) is True
    bad = dataclasses.replace(req, option_type="straddle")
    assert BlackScholesPricer().supports(bad) is False


def test_degenerate_intrinsic():
    res = BlackScholesPricer().price(_req(spot=110.0, strike=100.0, maturity=0.0))
    assert res.price == pytest.approx(10.0)  # intrinsic
    assert res.warnings  # degenerate warning


def test_pack_loading(tmp_path):
    pr_yaml = tmp_path / "pricers.yaml"
    pr_yaml.write_text(
        "pricers:\n"
        "  - module: indiciumforge_core.quant.pricing.black_scholes\n"
        "    class: BlackScholesPricer\n",
        encoding="utf-8",
    )
    pack_yaml = tmp_path / "pack.yaml"
    pack_yaml.write_text(
        "schema: indiciumforge.pricing_pack.v1\n"
        "pack_id: demo-pr\n"
        "version: '1.0'\n"
        "load:\n"
        "  pricers_config: pricers.yaml\n",
        encoding="utf-8",
    )
    loaded = load_pricing_pack(pack_config=pack_yaml)
    assert "black_scholes" in loaded.registry.list_pricers()


def test_pack_rejects_wrong_schema(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("schema: indiciumforge.wrong_pack.v1\n", encoding="utf-8")
    with pytest.raises(PricerLoadError):
        load_pricing_pack(pack_config=bad)

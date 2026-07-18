from __future__ import annotations

import math

from indiciumforge_core.quant.pricing.models import PricingRequest, PricingResult


def _norm_cdf(x: float) -> float:
    # Standard normal CDF via the error function (stdlib, zero extra deps).
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


class BlackScholesPricer:
    """Analytic Black-Scholes pricer for European options.

    Closed-form price and Greeks. Uses only the standard library
    (``math.erf`` for the normal CDF) so the ``[pricing]`` extra is empty.
    Vega/rho are reported per 1% move; theta per calendar day. Degenerate
    inputs (``T<=0`` or ``sigma<=0``) fall back to intrinsic value with a
    warning rather than raising.
    """

    pricer_id = "black_scholes"

    def supports(self, request: PricingRequest) -> bool:
        return request.option_type in ("call", "put") and request.volatility >= 0.0

    def price(self, request: PricingRequest) -> PricingResult:
        warnings: list[str] = []
        S = float(request.spot)
        K = float(request.strike)
        T = float(request.maturity)
        r = float(request.rate)
        sigma = float(request.volatility)
        is_call = request.option_type == "call"

        if T <= 0.0 or sigma <= 0.0:
            warnings.append("degenerate inputs (T<=0 or sigma<=0): intrinsic value used")
            if is_call:
                price = max(S - K, 0.0)
            else:
                price = max(K - S, 0.0)
            return PricingResult(
                pricer_id=self.pricer_id,
                price=price,
                delta=0.0,
                gamma=0.0,
                vega=0.0,
                theta=0.0,
                rho=0.0,
                warnings=tuple(warnings),
            )

        sqrt_T = math.sqrt(T)
        d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * sqrt_T)
        d2 = d1 - sigma * sqrt_T
        disc = math.exp(-r * T)
        n_d1 = _norm_pdf(d1)

        if is_call:
            price = S * _norm_cdf(d1) - K * disc * _norm_cdf(d2)
            delta = _norm_cdf(d1)
            rho = K * T * disc * _norm_cdf(d2) / 100.0
        else:
            price = K * disc * _norm_cdf(-d2) - S * _norm_cdf(-d1)
            delta = _norm_cdf(-d1) - 1.0
            rho = -K * T * disc * _norm_cdf(-d2) / 100.0

        gamma = n_d1 / (S * sigma * sqrt_T)
        vega = S * n_d1 * sqrt_T / 100.0
        if is_call:
            theta = (
                -(S * n_d1 * sigma) / (2.0 * sqrt_T) - r * K * disc * _norm_cdf(d2)
            ) / 365.0
        else:
            theta = (
                -(S * n_d1 * sigma) / (2.0 * sqrt_T) + r * K * disc * _norm_cdf(-d2)
            ) / 365.0

        return PricingResult(
            pricer_id=self.pricer_id,
            price=price,
            delta=delta,
            gamma=gamma,
            vega=vega,
            theta=theta,
            rho=rho,
            warnings=tuple(warnings),
        )


# Structural subtype registration (mirrors providers/contracts_v2.py).
from indiciumforge_core.quant.pricing.ports import PricingPort  # noqa: E402

PricingPort.register(BlackScholesPricer)

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass(frozen=True)
class PricingRequest:
    """Standard European-option inputs.

    ``option_type`` is ``"call"`` or ``"put"``. ``maturity`` is in years.
    """

    spot: float
    strike: float
    maturity: float
    rate: float
    volatility: float
    option_type: str = "call"
    as_of: date | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "spot": self.spot,
            "strike": self.strike,
            "maturity": self.maturity,
            "rate": self.rate,
            "volatility": self.volatility,
            "option_type": self.option_type,
            "as_of": self.as_of.isoformat() if self.as_of is not None else None,
        }


@dataclass(frozen=True)
class PricingResult:
    pricer_id: str
    price: float
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float
    warnings: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        return {
            "pricer_id": self.pricer_id,
            "price": self.price,
            "delta": self.delta,
            "gamma": self.gamma,
            "vega": self.vega,
            "theta": self.theta,
            "rho": self.rho,
            "warnings": list(self.warnings),
        }

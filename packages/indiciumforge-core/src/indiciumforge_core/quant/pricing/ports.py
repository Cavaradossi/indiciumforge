from __future__ import annotations

from typing import Protocol

from indiciumforge_core.quant.pricing.models import PricingRequest, PricingResult


class PricingPort(Protocol):
    """Port for derivative pricing and Greek computation.

    A concrete pricer (e.g. :class:`BlackScholesPricer`) turns a standard
    European-option request into a price plus Greeks. The contract only
    requires ``price``; whether the math is analytic or Monte-Carlo is an
    adapter detail (QuantLib is a future ``[pricing-ql]`` extra).
    """

    pricer_id: str

    def supports(self, request: PricingRequest) -> bool: ...

    def price(self, request: PricingRequest) -> PricingResult: ...

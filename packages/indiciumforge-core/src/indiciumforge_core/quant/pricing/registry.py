from __future__ import annotations

from indiciumforge_core.quant.pricing.models import PricingRequest, PricingResult
from indiciumforge_core.quant.pricing.ports import PricingPort


class DuplicatePricerError(ValueError):
    """Raised when registering a pricer with an existing pricer_id."""


class PricingRegistry:
    def __init__(self, pricers: list[PricingPort] | None = None) -> None:
        self._pricers: dict[str, PricingPort] = {}
        for pricer in pricers or []:
            self.register(pricer)

    def register(self, pricer: PricingPort) -> None:
        if pricer.pricer_id in self._pricers:
            raise DuplicatePricerError(f"pricer already registered: {pricer.pricer_id}")
        self._pricers[pricer.pricer_id] = pricer

    def list_pricers(self) -> tuple[str, ...]:
        return tuple(self._pricers.keys())

    def get(self, pricer_id: str) -> PricingPort:
        pricer = self._pricers.get(pricer_id)
        if pricer is None:
            raise KeyError(f"unknown pricer: {pricer_id}")
        return pricer

    def price(self, pricer_id: str, request: PricingRequest) -> PricingResult:
        return self.get(pricer_id).price(request)

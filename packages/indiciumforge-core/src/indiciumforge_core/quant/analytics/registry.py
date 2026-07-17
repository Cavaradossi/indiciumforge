from __future__ import annotations

from indiciumforge_core.quant.analytics.models import (
    FactorEvaluationRequest,
    FactorEvaluationResult,
)
from indiciumforge_core.quant.analytics.ports import FactorAnalyticsPort


class DuplicateEngineError(ValueError):
    """Raised when registering an engine with an existing engine_id."""


class FactorAnalyticsRegistry:
    def __init__(self, engines: list[FactorAnalyticsPort] | None = None) -> None:
        self._engines: dict[str, FactorAnalyticsPort] = {}
        for engine in engines or []:
            self.register(engine)

    def register(self, engine: FactorAnalyticsPort) -> None:
        if engine.engine_id in self._engines:
            raise DuplicateEngineError(f"engine already registered: {engine.engine_id}")
        self._engines[engine.engine_id] = engine

    def list_engines(self) -> tuple[str, ...]:
        return tuple(self._engines.keys())

    def get(self, engine_id: str) -> FactorAnalyticsPort:
        engine = self._engines.get(engine_id)
        if engine is None:
            raise KeyError(f"unknown analytics engine: {engine_id}")
        return engine

    def evaluate(
        self, engine_id: str, request: FactorEvaluationRequest
    ) -> FactorEvaluationResult:
        return self.get(engine_id).evaluate(request)

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from lucerna_core.recipes.models import RecipeStageContext, StageRunResult


class PrivateRecipeExtensionPort(Protocol):
    extension_id: str
    recipe_ids: tuple[str, ...]

    def supports_stage(self, recipe_id: str, stage_id: str) -> bool: ...

    def execute_stage(self, context: RecipeStageContext) -> StageRunResult: ...


class CandidatePoolBuilderPort(Protocol):
    def build_candidate_pool(self, context: RecipeStageContext) -> StageRunResult: ...


class ReviewBuilderPort(Protocol):
    def build_review(self, context: RecipeStageContext) -> StageRunResult: ...


class MarketContextPort(Protocol):
    def build_market_context(self, context: RecipeStageContext) -> dict[str, object]: ...


class StageInputResolverPort(Protocol):
    def resolve_inputs(self, context: RecipeStageContext) -> dict[str, Path]: ...


class RecipeRunnerPort(Protocol):
    def run(self, *, trade_date, artifact_root, recipe, extension): ...  # noqa: ANN001

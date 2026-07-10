from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from indiciumforge_core.parity.config import ParityLocalConfig
from indiciumforge_core.parity.harness import ParityHarness, build_parity_context
from indiciumforge_core.parity.models import ParityRunReport

from indiciumforge_workflow.workflow_chain.runner import (
    WorkflowChainRecipeConfig,
    WorkflowChainResult,
    run_workflow_chain_recipe,
)


@dataclass(frozen=True)
class ParityWorkflowResult:
    chain: WorkflowChainResult
    report: ParityRunReport


def run_parity_after_recipe_chain(
    *,
    config: ParityLocalConfig,
    artifact_root: Path | None = None,
) -> ParityWorkflowResult:
    if config.recipe.daily_review_fixture is None:
        raise ValueError("parity config requires recipe.daily_review_fixture")

    resolved_artifact_root = artifact_root or config.artifact_root
    if resolved_artifact_root is None:
        raise ValueError("artifact_root is required (config or CLI override)")

    chain = run_workflow_chain_recipe(
        trade_date=config.trade_date,
        artifact_root=resolved_artifact_root,
        config=WorkflowChainRecipeConfig(
            recipe_path=config.recipe.path,
            recipe_extension_pack=config.recipe.extension_pack,
            daily_review_fixture=config.recipe.daily_review_fixture,
        ),
    )

    context = build_parity_context(
        trade_date=config.trade_date,
        artifact_root=resolved_artifact_root,
        reference_root=config.reference_artifact_root,
        dimensions=config.dimensions,
    )
    report_path = resolved_artifact_root / "parity_run_report.json"
    harness = ParityHarness(config.reference_artifact_root)
    report = harness.run(context, report_path=report_path)
    return ParityWorkflowResult(chain=chain, report=report)

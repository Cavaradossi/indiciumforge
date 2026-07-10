from __future__ import annotations

from datetime import date
from pathlib import Path

from indiciumforge_core.parity.comparator import CandidateComparator
from indiciumforge_core.parity.harness import build_parity_context
from indiciumforge_core.parity.models import ParityDimension, ParityVerdict
from indiciumforge_core.parity.reference import ReferenceArtifactProvider
from indiciumforge_workflow.workflow_chain.runner import (
    WorkflowChainRecipeConfig,
    run_workflow_chain_recipe,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures"
REFERENCE_ROOT = FIXTURE_ROOT / "parity_reference_demo" / "reference"
TRADE_DATE = date(2026, 6, 23)


def test_parity_comparator_market_gate_matches_demo_reference(tmp_path: Path) -> None:
    run_workflow_chain_recipe(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        config=WorkflowChainRecipeConfig(
            recipe_path=FIXTURE_ROOT / "workflow" / "recipe_ashare_daily_v1.yaml",
            recipe_extension_pack=FIXTURE_ROOT / "recipe_extension_pack_demo.yaml",
            daily_review_fixture=FIXTURE_ROOT / "market_awareness" / "theme_sectors_demo.yaml",
        ),
    )

    context = build_parity_context(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        reference_root=REFERENCE_ROOT,
        dimensions=(ParityDimension.MARKET_GATE_STRICT_SEMANTICS,),
    )
    comparator = CandidateComparator(ReferenceArtifactProvider(REFERENCE_ROOT))
    result = comparator.compare(ParityDimension.MARKET_GATE_STRICT_SEMANTICS, context)

    assert result.verdict == ParityVerdict.MATCH

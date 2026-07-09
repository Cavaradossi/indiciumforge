from __future__ import annotations

from pathlib import Path

from lucerna_core.parity.config import load_parity_config
from lucerna_core.parity.models import ParityDimension
from lucerna_workflow.parity.runner import run_parity_after_recipe_chain

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "tests" / "fixtures" / "parity_reference_demo" / "parity_config_demo.yaml"


def test_parity_summary_v4_audit_in_report(tmp_path: Path) -> None:
    config = load_parity_config(CONFIG)
    result = run_parity_after_recipe_chain(config=config, artifact_root=tmp_path)

    summary_check = next(
        item
        for item in result.report.results
        if item.dimension == ParityDimension.WORKFLOW_CHAIN_SUMMARY_V4
    )
    assert summary_check.verdict.value == "match"
    assert summary_check.details.get("chain_ok") is True
    assert summary_check.details.get("provenance_mode") == "workflow_chain_recipe"

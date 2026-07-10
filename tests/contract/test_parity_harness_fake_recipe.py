from __future__ import annotations

from pathlib import Path

from indiciumforge_core.parity.config import load_parity_config
from indiciumforge_workflow.parity.runner import run_parity_after_recipe_chain

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "tests" / "fixtures" / "parity_reference_demo" / "parity_config_demo.yaml"


def test_parity_harness_fake_recipe_matches_demo_reference(tmp_path: Path) -> None:
    config = load_parity_config(CONFIG)
    result = run_parity_after_recipe_chain(config=config, artifact_root=tmp_path)

    assert result.chain.chain_ok
    assert result.report.all_match
    assert result.report.report_path.is_file()
    assert all(item.verdict.value == "match" for item in result.report.results)

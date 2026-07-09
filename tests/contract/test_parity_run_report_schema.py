from __future__ import annotations

import json
from pathlib import Path

from lucerna_core.parity.config import load_parity_config
from lucerna_core.parity.models import PARITY_RUN_REPORT_SCHEMA
from lucerna_workflow.parity.runner import run_parity_after_recipe_chain

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "tests" / "fixtures" / "parity_reference_demo" / "parity_config_demo.yaml"


def test_parity_run_report_schema(tmp_path: Path) -> None:
    config = load_parity_config(CONFIG)
    result = run_parity_after_recipe_chain(config=config, artifact_root=tmp_path)

    payload = json.loads(result.report.report_path.read_text(encoding="utf-8-sig"))
    assert payload["schema"] == PARITY_RUN_REPORT_SCHEMA
    assert payload["disclaimer"] == "research_audit_only"
    assert payload["all_match"] is True
    assert len(payload["results"]) == 5
    for item in payload["results"]:
        assert item["schema"] == "lucerna.parity_check_result.v1"
        assert item["verdict"] == "match"

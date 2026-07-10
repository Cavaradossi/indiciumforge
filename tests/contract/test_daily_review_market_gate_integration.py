from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

from indiciumforge_workflow.market_awareness.runner import run_daily_review_skeleton
from indiciumforge_workflow.market_gate.runner import run_market_gate

ROOT = Path(__file__).resolve().parents[2]
DEMO_FIXTURE = ROOT / "tests" / "fixtures" / "market_awareness" / "theme_sectors_demo.yaml"
GOLDEN_INPUTS = (
    ROOT
    / "tests"
    / "golden"
    / "market_gate"
    / "strict_pass_mixed"
    / "inputs"
)
TRADE_DATE = date(2026, 6, 23)


def test_generated_ranking_feeds_market_gate(tmp_path: Path) -> None:
    workflow_inputs = tmp_path / "workflows" / "20260623" / "preopen"
    workflow_inputs.mkdir(parents=True)
    shutil.copy2(
        GOLDEN_INPUTS / "workflows" / "20260623" / "preopen" / "buy_point_review_internal.csv",
        workflow_inputs / "buy_point_review_internal.csv",
    )

    run_daily_review_skeleton(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        fixture_path=DEMO_FIXTURE,
    )

    result = run_market_gate(trade_date=TRADE_DATE, artifact_root=tmp_path)

    assert result.stage_dir.is_dir()
    assert (result.stage_dir / "market_gated_candidates.csv").is_file()

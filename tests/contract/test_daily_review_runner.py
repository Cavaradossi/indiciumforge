from __future__ import annotations

from datetime import date
from pathlib import Path

from lucerna_core.artifacts.paths import daily_review_dir, theme_state_ranking_path
from lucerna_workflow.market_awareness.runner import run_daily_review_skeleton

ROOT = Path(__file__).resolve().parents[2]
DEMO_FIXTURE = ROOT / "tests" / "fixtures" / "market_awareness" / "theme_sectors_demo.yaml"
TRADE_DATE = date(2026, 6, 23)


def test_run_daily_review_skeleton_writes_ranking_and_state(tmp_path: Path) -> None:
    result = run_daily_review_skeleton(
        trade_date=TRADE_DATE,
        artifact_root=tmp_path,
        fixture_path=DEMO_FIXTURE,
    )

    ranking_path = theme_state_ranking_path(tmp_path, TRADE_DATE)
    stage_dir = daily_review_dir(tmp_path, TRADE_DATE)

    assert result.theme_state_ranking_path == ranking_path
    assert ranking_path.is_file()
    assert result.state_path == stage_dir / "market_daily_review_state.json"
    assert result.state_path.is_file()
    assert len(result.rows) == 3

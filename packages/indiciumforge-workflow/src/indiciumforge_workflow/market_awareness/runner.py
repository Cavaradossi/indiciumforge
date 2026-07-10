from __future__ import annotations

from datetime import date
from pathlib import Path

from indiciumforge_core.artifacts.paths import daily_review_dir, theme_state_ranking_path

from indiciumforge_workflow.market_awareness.artifacts import (
    write_daily_review_state,
    write_theme_state_ranking,
)
from indiciumforge_workflow.market_awareness.classifier import classify_theme_states
from indiciumforge_workflow.market_awareness.fixtures import load_theme_sector_fixture
from indiciumforge_workflow.market_awareness.models import DailyReviewResult


def run_daily_review_skeleton(
    *,
    trade_date: date,
    artifact_root: Path,
    fixture_path: Path,
) -> DailyReviewResult:
    fixture_trade_date, metrics = load_theme_sector_fixture(fixture_path)
    warnings: list[str] = []
    if fixture_trade_date != trade_date:
        warnings.append(
            f"fixture trade_date {fixture_trade_date} differs from requested {trade_date}"
        )

    rows = classify_theme_states(metrics)
    stage_dir = daily_review_dir(artifact_root, trade_date)
    ranking_path = theme_state_ranking_path(artifact_root, trade_date)
    write_theme_state_ranking(ranking_path, rows)

    state_path = stage_dir / "market_daily_review_state.json"
    write_daily_review_state(
        state_path,
        trade_date=trade_date,
        theme_state_ranking_path=ranking_path,
        fixture_name=fixture_path.name,
        warnings=warnings,
    )

    return DailyReviewResult(
        trade_date=trade_date,
        rows=tuple(rows),
        warnings=tuple(warnings),
        fixture_path=fixture_path,
        theme_state_ranking_path=ranking_path,
        state_path=state_path,
    )

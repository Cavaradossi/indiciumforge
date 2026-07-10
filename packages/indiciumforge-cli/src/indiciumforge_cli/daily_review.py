from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from indiciumforge_workflow.market_awareness.runner import run_daily_review_skeleton

TRADE_DATE_OPTION = typer.Option(..., "--trade-date")
ARTIFACT_ROOT_OPTION = typer.Option(..., "--artifact-root")
FIXTURE_PATH_OPTION = typer.Option(..., "--fixture-path")


def workflow_daily_review(
    trade_date: str = TRADE_DATE_OPTION,
    artifact_root: Path = ARTIFACT_ROOT_OPTION,
    fixture_path: Path = FIXTURE_PATH_OPTION,
) -> None:
    parsed = datetime.strptime(trade_date, "%Y-%m-%d").date()
    result = run_daily_review_skeleton(
        trade_date=parsed,
        artifact_root=artifact_root,
        fixture_path=fixture_path,
    )
    typer.echo(f"Wrote daily-review artifacts: {result.state_path.parent}")
    typer.echo(f"  theme_state_ranking: {result.theme_state_ranking_path}")
    typer.echo(f"  state: {result.state_path}")

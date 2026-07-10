from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from indiciumforge_workflow.e2e.synthetic import run_synthetic_e2e

TRADE_DATE_OPTION = typer.Option(..., "--trade-date")
ARTIFACT_ROOT_OPTION = typer.Option(..., "--artifact-root")
DAILY_REVIEW_FIXTURE_OPTION = typer.Option(..., "--daily-review-fixture")
PREOPEN_REVIEW_FIXTURE_OPTION = typer.Option(..., "--preopen-review-fixture")


def workflow_synthetic_e2e(
    trade_date: str = TRADE_DATE_OPTION,
    artifact_root: Path = ARTIFACT_ROOT_OPTION,
    daily_review_fixture: Path = DAILY_REVIEW_FIXTURE_OPTION,
    preopen_review_fixture: Path = PREOPEN_REVIEW_FIXTURE_OPTION,
) -> None:
    parsed = datetime.strptime(trade_date, "%Y-%m-%d").date()
    try:
        result = run_synthetic_e2e(
            trade_date=parsed,
            artifact_root=artifact_root,
            daily_review_fixture=daily_review_fixture,
            preopen_review_fixture=preopen_review_fixture,
        )
    except FileNotFoundError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc

    typer.echo(f"daily-review stage: {result.daily_review_stage_dir}")
    typer.echo(
        "  theme_state_ranking: "
        f"{result.daily_review_stage_dir / 'theme_state_ranking.csv'}"
    )
    typer.echo(f"market-gate stage: {result.market_gate_stage_dir}")
    typer.echo(
        f"daily_review audit: {'ok' if result.daily_review_audit_ok else 'failed'}"
    )
    typer.echo(f"market_gate audit: {'ok' if result.market_gate_audit_ok else 'failed'}")
    typer.echo(f"audit: {'ok' if result.audit_ok else 'failed'}")
    typer.echo(f"summary: {result.summary_path}")

    if not result.audit_ok:
        raise typer.Exit(code=1)

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from lucerna_workflow.market_gate.runner import run_market_gate

from lucerna_cli.artifact import artifact_app
from lucerna_cli.daily_review import workflow_daily_review

app = typer.Typer(help="Lucerna reference CLI.")
workflow_app = typer.Typer(help="Workflow commands.")
app.add_typer(workflow_app, name="workflow")
app.add_typer(artifact_app, name="artifact")

TRADE_DATE_OPTION = typer.Option(..., "--trade-date")
ARTIFACT_ROOT_OPTION = typer.Option(..., "--artifact-root")


@workflow_app.command("market-gate")
def workflow_market_gate(
    trade_date: str = TRADE_DATE_OPTION,
    artifact_root: Path = ARTIFACT_ROOT_OPTION,
) -> None:
    parsed = datetime.strptime(trade_date, "%Y-%m-%d").date()
    result = run_market_gate(trade_date=parsed, artifact_root=artifact_root)
    typer.echo(f"Wrote market-gate artifacts: {result.stage_dir}")


@workflow_app.command("daily-review", help="Run skeleton daily-review from a synthetic fixture.")
def workflow_daily_review_command(
    trade_date: str = TRADE_DATE_OPTION,
    artifact_root: Path = ARTIFACT_ROOT_OPTION,
    fixture_path: Path = typer.Option(..., "--fixture-path"),
) -> None:
    workflow_daily_review(
        trade_date=trade_date,
        artifact_root=artifact_root,
        fixture_path=fixture_path,
    )

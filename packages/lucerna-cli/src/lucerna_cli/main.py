from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from lucerna_workflow.market_gate.runner import run_market_gate

app = typer.Typer(help="Lucerna reference CLI.")
workflow_app = typer.Typer(help="Workflow commands.")
app.add_typer(workflow_app, name="workflow")

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

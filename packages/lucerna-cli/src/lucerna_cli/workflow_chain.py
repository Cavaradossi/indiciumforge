from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from lucerna_workflow.workflow_chain.runner import run_workflow_chain_skeleton

TRADE_DATE_OPTION = typer.Option(..., "--trade-date")
ARTIFACT_ROOT_OPTION = typer.Option(..., "--artifact-root")
DAILY_REVIEW_FIXTURE_OPTION = typer.Option(..., "--daily-review-fixture")
POST_CLOSE_REVIEW_FIXTURE_OPTION = typer.Option(..., "--post-close-review-fixture")
PREOPEN_REVIEW_FIXTURE_OPTION = typer.Option(..., "--preopen-review-fixture")


def workflow_chain(
    trade_date: str = TRADE_DATE_OPTION,
    artifact_root: Path = ARTIFACT_ROOT_OPTION,
    daily_review_fixture: Path = DAILY_REVIEW_FIXTURE_OPTION,
    post_close_review_fixture: Path = POST_CLOSE_REVIEW_FIXTURE_OPTION,
    preopen_review_fixture: Path = PREOPEN_REVIEW_FIXTURE_OPTION,
) -> None:
    parsed = datetime.strptime(trade_date, "%Y-%m-%d").date()
    try:
        result = run_workflow_chain_skeleton(
            trade_date=parsed,
            artifact_root=artifact_root,
            daily_review_fixture=daily_review_fixture,
            post_close_review_fixture=post_close_review_fixture,
            preopen_review_fixture=preopen_review_fixture,
        )
    except FileNotFoundError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc

    typer.echo(f"daily-review stage: {result.daily_review_stage_dir}")
    typer.echo(f"post-close stage: {result.post_close_stage_dir}")
    typer.echo(f"preopen stage: {result.preopen_stage_dir}")
    typer.echo(f"market-gate stage: {result.market_gate_stage_dir}")
    typer.echo(f"workflow_review_source_stage: {result.workflow_review_source_stage}")
    typer.echo(f"strict_count: {result.strict_count}")
    typer.echo(
        f"daily_review audit: {'ok' if result.daily_review_audit_ok else 'failed'}"
    )
    typer.echo(f"market_gate audit: {'ok' if result.market_gate_audit_ok else 'failed'}")
    typer.echo(f"chain: {'ok' if result.chain_ok else 'failed'}")
    typer.echo(f"summary: {result.summary_path}")

    if not result.chain_ok:
        raise typer.Exit(code=1)

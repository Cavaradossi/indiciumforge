from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from lucerna_core.artifacts.manifest import (
    format_audit_report,
    list_market_gate_stages,
    resolve_market_gate_audit_target,
    validate_market_gate_stage,
)

artifact_app = typer.Typer(help="Artifact commands.")

ARTIFACT_ROOT_OPTION = typer.Option(..., "--artifact-root")
TRADE_DATE_OPTION = typer.Option(None, "--trade-date")
STAGE_DIR_OPTION = typer.Option(None, "--stage-dir")
META_PATH_OPTION = typer.Option(None, "--meta-path")


@artifact_app.command("list")
def artifact_list(artifact_root: Path = ARTIFACT_ROOT_OPTION) -> None:
    stages = list_market_gate_stages(artifact_root)
    if not stages:
        typer.echo(f"No market_gate stages found under {artifact_root}")
        raise typer.Exit(code=0)

    for ref in stages:
        typer.echo(
            f"{ref.trade_date}\t{ref.core_artifact_count}/{len(ref.present_files)}\t{ref.stage_dir}"
        )


@artifact_app.command("audit")
def artifact_audit(
    artifact_root: Path | None = typer.Option(None, "--artifact-root"),
    trade_date: str | None = TRADE_DATE_OPTION,
    stage_dir: Path | None = STAGE_DIR_OPTION,
    meta_path: Path | None = META_PATH_OPTION,
) -> None:
    parsed_trade_date = None
    if trade_date is not None:
        parsed_trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()

    if stage_dir is None and (artifact_root is None or parsed_trade_date is None):
        typer.echo("Provide --stage-dir or both --artifact-root and --trade-date.", err=True)
        raise typer.Exit(code=2)

    try:
        target_dir, expected_trade_date = resolve_market_gate_audit_target(
            artifact_root=artifact_root,
            trade_date=parsed_trade_date,
            stage_dir=stage_dir,
        )
        if stage_dir is not None and parsed_trade_date is not None:
            expected_trade_date = parsed_trade_date.isoformat()
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc

    manifest = validate_market_gate_stage(
        target_dir,
        expected_trade_date=expected_trade_date,
        meta_path=meta_path,
    )
    typer.echo(format_audit_report(manifest))
    if not manifest.ok:
        raise typer.Exit(code=1)

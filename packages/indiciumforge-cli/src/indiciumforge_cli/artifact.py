from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from indiciumforge_core.artifacts.comparator import GATE_ARTIFACTS
from indiciumforge_core.artifacts.manifest import (
    DAILY_REVIEW_REQUIRED_FILES,
    format_audit_report,
    is_daily_review_stage_dir,
    is_factor_scan_stage_dir,
    list_daily_review_stages,
    list_market_gate_stages,
    resolve_daily_review_audit_target,
    resolve_factor_scan_audit_target,
    resolve_market_gate_audit_target,
    validate_daily_review_stage,
    validate_factor_scan_stage,
    validate_market_gate_stage,
)

artifact_app = typer.Typer(help="Artifact commands.")

ARTIFACT_ROOT_OPTION = typer.Option(..., "--artifact-root")
TRADE_DATE_OPTION = typer.Option(None, "--trade-date")
STAGE_DIR_OPTION = typer.Option(None, "--stage-dir")
META_PATH_OPTION = typer.Option(None, "--meta-path")
STAGE_TYPE_OPTION = typer.Option(
    "market_gate",
    "--stage-type",
    help="Stage domain: market_gate, daily_review, or factor_scan.",
)


@artifact_app.command("list")
def artifact_list(artifact_root: Path = ARTIFACT_ROOT_OPTION) -> None:
    gate_stages = list_market_gate_stages(artifact_root)
    review_stages = list_daily_review_stages(artifact_root)
    if not gate_stages and not review_stages:
        typer.echo(f"No artifact stages found under {artifact_root}")
        raise typer.Exit(code=0)

    for ref in gate_stages:
        typer.echo(
            f"market_gate\t{ref.trade_date}\t"
            f"{ref.core_artifact_count}/{len(GATE_ARTIFACTS)}\t{ref.stage_dir}"
        )
    for ref in review_stages:
        typer.echo(
            f"daily_review\t{ref.trade_date}\t"
            f"{ref.core_artifact_count}/{len(DAILY_REVIEW_REQUIRED_FILES)}\t{ref.stage_dir}"
        )


@artifact_app.command("audit")
def artifact_audit(
    artifact_root: Path | None = typer.Option(None, "--artifact-root"),
    trade_date: str | None = TRADE_DATE_OPTION,
    stage_dir: Path | None = STAGE_DIR_OPTION,
    meta_path: Path | None = META_PATH_OPTION,
    stage_type: str = STAGE_TYPE_OPTION,
) -> None:
    parsed_trade_date = None
    if trade_date is not None:
        parsed_trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()

    if stage_dir is None and (artifact_root is None or parsed_trade_date is None):
        typer.echo("Provide --stage-dir or both --artifact-root and --trade-date.", err=True)
        raise typer.Exit(code=2)

    use_daily_review = stage_dir is not None and is_daily_review_stage_dir(stage_dir)
    use_factor_scan = stage_dir is not None and is_factor_scan_stage_dir(stage_dir)
    if stage_dir is None and stage_type == "daily_review":
        use_daily_review = True
    if stage_dir is None and stage_type == "factor_scan":
        use_factor_scan = True

    try:
        if use_factor_scan:
            target_dir, expected_trade_date = resolve_factor_scan_audit_target(
                artifact_root=artifact_root,
                trade_date=parsed_trade_date,
                stage_dir=stage_dir,
            )
            if stage_dir is not None and parsed_trade_date is not None:
                expected_trade_date = parsed_trade_date.isoformat()
            manifest = validate_factor_scan_stage(
                target_dir,
                expected_trade_date=expected_trade_date,
            )
        elif use_daily_review:
            target_dir, expected_trade_date = resolve_daily_review_audit_target(
                artifact_root=artifact_root,
                trade_date=parsed_trade_date,
                stage_dir=stage_dir,
            )
            if stage_dir is not None and parsed_trade_date is not None:
                expected_trade_date = parsed_trade_date.isoformat()
            manifest = validate_daily_review_stage(
                target_dir,
                expected_trade_date=expected_trade_date,
            )
        else:
            target_dir, expected_trade_date = resolve_market_gate_audit_target(
                artifact_root=artifact_root,
                trade_date=parsed_trade_date,
                stage_dir=stage_dir,
            )
            if stage_dir is not None and parsed_trade_date is not None:
                expected_trade_date = parsed_trade_date.isoformat()
            manifest = validate_market_gate_stage(
                target_dir,
                expected_trade_date=expected_trade_date,
                meta_path=meta_path,
            )
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc

    typer.echo(format_audit_report(manifest))
    if not manifest.ok:
        raise typer.Exit(code=1)

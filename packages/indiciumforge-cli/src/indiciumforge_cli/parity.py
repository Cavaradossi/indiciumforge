from __future__ import annotations

import json
from pathlib import Path

import typer
from indiciumforge_core.parity.config import ParityConfigError, load_parity_config
from indiciumforge_workflow.parity.runner import run_parity_after_recipe_chain


def parity_run(
    *,
    parity_config: Path,
    artifact_root: Path | None = None,
) -> None:
    try:
        config = load_parity_config(parity_config)
        result = run_parity_after_recipe_chain(config=config, artifact_root=artifact_root)
    except (ParityConfigError, FileNotFoundError, ValueError, OSError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc

    typer.echo(f"recipe chain summary: {result.chain.summary_path}")
    typer.echo(f"parity report: {result.report.report_path}")
    for check in result.report.results:
        typer.echo(f"{check.dimension.value}: {check.verdict.value} - {check.message}")

    if not result.report.all_match:
        raise typer.Exit(code=1)


def parity_report(*, report_path: Path, output_format: str = "table") -> None:
    if not report_path.is_file():
        typer.echo(f"report not found: {report_path}", err=True)
        raise typer.Exit(code=2)

    payload = json.loads(report_path.read_text(encoding="utf-8-sig"))
    if output_format == "json":
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    typer.echo(f"trade_date: {payload.get('trade_date')}")
    typer.echo(f"all_match: {payload.get('all_match')}")
    typer.echo(f"disclaimer: {payload.get('disclaimer')}")
    for item in payload.get("results", []):
        typer.echo(
            f"- {item.get('dimension')}: {item.get('verdict')} ({item.get('message')})"
        )

    if not payload.get("all_match"):
        raise typer.Exit(code=1)

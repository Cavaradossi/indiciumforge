from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from lucerna_workflow.market_gate.runner import run_market_gate

from lucerna_cli.artifact import artifact_app
from lucerna_cli.daily_review import workflow_daily_review
from lucerna_cli.factor import factor_scan
from lucerna_cli.synthetic_e2e import workflow_synthetic_e2e
from lucerna_cli.workflow_chain import workflow_chain

app = typer.Typer(help="Lucerna reference CLI.")
workflow_app = typer.Typer(help="Workflow commands.")
factor_app = typer.Typer(help="Factor commands.")
app.add_typer(workflow_app, name="workflow")
app.add_typer(artifact_app, name="artifact")
app.add_typer(factor_app, name="factor")

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


@workflow_app.command(
    "synthetic-e2e",
    help="Run synthetic end-to-end workflow: daily-review -> market-gate -> audit summary.",
)
def workflow_synthetic_e2e_command(
    trade_date: str = TRADE_DATE_OPTION,
    artifact_root: Path = ARTIFACT_ROOT_OPTION,
    daily_review_fixture: Path = typer.Option(..., "--daily-review-fixture"),
    preopen_review_fixture: Path = typer.Option(..., "--preopen-review-fixture"),
) -> None:
    workflow_synthetic_e2e(
        trade_date=trade_date,
        artifact_root=artifact_root,
        daily_review_fixture=daily_review_fixture,
        preopen_review_fixture=preopen_review_fixture,
    )


@workflow_app.command(
    "chain",
    help="Run workflow chain skeleton: daily-review -> post-close -> preopen -> market-gate.",
)
def workflow_chain_command(
    trade_date: str = TRADE_DATE_OPTION,
    artifact_root: Path = ARTIFACT_ROOT_OPTION,
    daily_review_fixture: Path = typer.Option(..., "--daily-review-fixture"),
    post_close_review_fixture: Path = typer.Option(..., "--post-close-review-fixture"),
    preopen_review_fixture: Path = typer.Option(..., "--preopen-review-fixture"),
    factor_pack: Path | None = typer.Option(None, "--factor-pack"),
    detectors_config: Path | None = typer.Option(None, "--detectors-config"),
    include_entry_points: bool = typer.Option(False, "--include-entry-points"),
    ohlcv_fixture_root: Path | None = typer.Option(None, "--ohlcv-fixture-root"),
    asset_fixture_list: Path | None = typer.Option(None, "--asset-fixture-list"),
    codes: str | None = typer.Option(
        None,
        "--codes",
        help="Local convenience only; not a production universe mechanism.",
    ),
) -> None:
    workflow_chain(
        trade_date=trade_date,
        artifact_root=artifact_root,
        daily_review_fixture=daily_review_fixture,
        post_close_review_fixture=post_close_review_fixture,
        preopen_review_fixture=preopen_review_fixture,
        factor_pack=factor_pack,
        detectors_config=detectors_config,
        include_entry_points=include_entry_points,
        ohlcv_fixture_root=ohlcv_fixture_root,
        asset_fixture_list=asset_fixture_list,
        codes=codes,
    )


@factor_app.command("scan", help="Run factor scan from a local private pack or detectors config.")
def factor_scan_command(
    trade_date: str = TRADE_DATE_OPTION,
    artifact_root: Path = ARTIFACT_ROOT_OPTION,
    ohlcv_fixture_root: Path = typer.Option(..., "--ohlcv-fixture-root"),
    asset_fixture_list: Path | None = typer.Option(None, "--asset-fixture-list"),
    codes: str | None = typer.Option(None, "--codes"),
    factor_pack: Path | None = typer.Option(None, "--factor-pack"),
    detectors_config: Path | None = typer.Option(None, "--detectors-config"),
    include_entry_points: bool = typer.Option(False, "--include-entry-points"),
) -> None:
    factor_scan(
        trade_date=trade_date,
        artifact_root=artifact_root,
        ohlcv_fixture_root=ohlcv_fixture_root,
        asset_fixture_list=asset_fixture_list,
        codes=codes,
        factor_pack=factor_pack,
        detectors_config=detectors_config,
        include_entry_points=include_entry_points,
    )

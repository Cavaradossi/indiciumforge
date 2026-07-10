from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from indiciumforge_workflow.market_gate.runner import run_market_gate

from indiciumforge_cli.artifact import artifact_app
from indiciumforge_cli.daily_review import workflow_daily_review
from indiciumforge_cli.factor import factor_scan
from indiciumforge_cli.parity import parity_report, parity_run
from indiciumforge_cli.provider import provider_fetch, provider_inspect
from indiciumforge_cli.synthetic_e2e import workflow_synthetic_e2e
from indiciumforge_cli.workflow_chain import workflow_chain

app = typer.Typer(help="IndiciumForge reference CLI.")
workflow_app = typer.Typer(help="Workflow commands.")
factor_app = typer.Typer(help="Factor commands.")
provider_app = typer.Typer(help="Data provider commands.")
parity_app = typer.Typer(help="Private-local parity harness (research audit only).")
app.add_typer(workflow_app, name="workflow")
app.add_typer(artifact_app, name="artifact")
app.add_typer(factor_app, name="factor")
app.add_typer(provider_app, name="provider")
app.add_typer(parity_app, name="parity")

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
    help="Run workflow chain: skeleton fixtures or recipe-driven private extension pack.",
)
def workflow_chain_command(
    trade_date: str = TRADE_DATE_OPTION,
    artifact_root: Path = ARTIFACT_ROOT_OPTION,
    daily_review_fixture: Path = typer.Option(..., "--daily-review-fixture"),
    post_close_review_fixture: Path | None = typer.Option(
        None, "--post-close-review-fixture"
    ),
    preopen_review_fixture: Path | None = typer.Option(None, "--preopen-review-fixture"),
    recipe: Path | None = typer.Option(None, "--recipe"),
    recipe_extension_pack: Path | None = typer.Option(None, "--recipe-extension-pack"),
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
        recipe=recipe,
        recipe_extension_pack=recipe_extension_pack,
        factor_pack=factor_pack,
        detectors_config=detectors_config,
        include_entry_points=include_entry_points,
        ohlcv_fixture_root=ohlcv_fixture_root,
        asset_fixture_list=asset_fixture_list,
        codes=codes,
    )


@provider_app.command("inspect", help="List loaded providers and capability matrix.")
def provider_inspect_command(
    provider_pack: Path | None = typer.Option(None, "--provider-pack"),
    providers_config: Path | None = typer.Option(None, "--providers-config"),
    include_entry_points: bool = typer.Option(False, "--include-entry-points"),
    ohlcv_fixture_root: Path | None = typer.Option(None, "--ohlcv-fixture-root"),
) -> None:
    provider_inspect(
        provider_pack=provider_pack,
        providers_config=providers_config,
        include_entry_points=include_entry_points,
        ohlcv_fixture_root=ohlcv_fixture_root,
    )


@provider_app.command("fetch", help="Single-query provider smoke (fixture/fake only).")
def provider_fetch_command(
    trade_date: str = TRADE_DATE_OPTION,
    code: str = typer.Option(..., "--code"),
    data_kind: str = typer.Option("ohlcv", "--data-kind"),
    provider_pack: Path | None = typer.Option(None, "--provider-pack"),
    providers_config: Path | None = typer.Option(None, "--providers-config"),
    include_entry_points: bool = typer.Option(False, "--include-entry-points"),
    ohlcv_fixture_root: Path | None = typer.Option(None, "--ohlcv-fixture-root"),
    recipe_id: str = typer.Option("indiciumforge.recipe.ashare_daily_research.v1", "--recipe-id"),
    cycle_id: str | None = typer.Option(None, "--cycle-id"),
    checkpoint_id: str | None = typer.Option(None, "--checkpoint-id"),
) -> None:
    provider_fetch(
        trade_date=trade_date,
        code=code,
        data_kind=data_kind,
        provider_pack=provider_pack,
        providers_config=providers_config,
        include_entry_points=include_entry_points,
        ohlcv_fixture_root=ohlcv_fixture_root,
        recipe_id=recipe_id,
        cycle_id=cycle_id,
        checkpoint_id=checkpoint_id,
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


@parity_app.command(
    "run",
    help="Run recipe chain then compare against a local reference artifact root.",
)
def parity_run_command(
    parity_config: Path = typer.Option(..., "--parity-config"),
    artifact_root: Path | None = typer.Option(None, "--artifact-root"),
) -> None:
    parity_run(parity_config=parity_config, artifact_root=artifact_root)


@parity_app.command("report", help="Summarize an existing parity_run_report.json.")
def parity_report_command(
    report: Path = typer.Option(..., "--report"),
    output_format: str = typer.Option("table", "--format", help="table or json"),
) -> None:
    parity_report(report_path=report, output_format=output_format)

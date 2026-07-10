from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from indiciumforge_core.factors.loading import DetectorLoadError
from indiciumforge_core.factors.universe import load_assets_from_fixture_list, parse_asset_codes
from indiciumforge_core.recipes.pack import RecipeExtensionLoadError
from indiciumforge_workflow.factor_scan.runner import FactorScanStageConfig
from indiciumforge_workflow.workflow_chain.runner import (
    WorkflowChainRecipeConfig,
    run_workflow_chain_recipe,
    run_workflow_chain_skeleton,
)


def _build_factor_scan_config(
    *,
    factor_pack: Path | None,
    detectors_config: Path | None,
    include_entry_points: bool,
    ohlcv_fixture_root: Path | None,
    asset_fixture_list: Path | None,
    codes: str | None,
) -> FactorScanStageConfig | None:
    if factor_pack is None and detectors_config is None and not include_entry_points:
        return None

    if ohlcv_fixture_root is None:
        raise ValueError(
            "--ohlcv-fixture-root is required when factor scan flags are set."
        )

    if codes is not None:
        assets = tuple(parse_asset_codes(codes))
        asset_universe_source = "cli_codes"
    elif asset_fixture_list is not None:
        assets = tuple(load_assets_from_fixture_list(asset_fixture_list))
        asset_universe_source = "fixture_asset_list"
    else:
        raise ValueError(
            "Provide --asset-fixture-list or --codes when enabling factor scan."
        )

    return FactorScanStageConfig(
        pack_config=factor_pack,
        detectors_config=detectors_config,
        include_entry_points=include_entry_points,
        ohlcv_fixture_root=ohlcv_fixture_root,
        asset_fixture_list=asset_fixture_list,
        assets=assets,
        asset_universe_source=asset_universe_source,
    )


def _echo_chain_result(result) -> None:  # noqa: ANN001
    typer.echo(f"daily-review stage: {result.daily_review_stage_dir}")
    if result.factor_scan_enabled and result.factor_scan_stage_dir is not None:
        typer.echo(f"factor-scan stage: {result.factor_scan_stage_dir}")
        typer.echo(f"factor signals: {result.signal_count}")
        typer.echo(
            "factor_scan audit: "
            f"{'ok' if result.factor_scan_audit_ok else 'failed'}"
        )
    typer.echo(f"post-close stage: {result.post_close_stage_dir}")
    typer.echo(f"preopen stage: {result.preopen_stage_dir}")
    typer.echo(f"market-gate stage: {result.market_gate_stage_dir}")
    if result.recipe_id is not None:
        typer.echo(f"recipe_id: {result.recipe_id}")
    if result.extension_pack_id is not None:
        typer.echo(f"extension_pack_id: {result.extension_pack_id}")
    if result.recipe_run_summary_path is not None:
        typer.echo(f"recipe_run_summary: {result.recipe_run_summary_path}")
    typer.echo(f"workflow_review_source_stage: {result.workflow_review_source_stage}")
    typer.echo(f"strict_count: {result.strict_count}")
    typer.echo(
        f"daily_review audit: {'ok' if result.daily_review_audit_ok else 'failed'}"
    )
    typer.echo(f"market_gate audit: {'ok' if result.market_gate_audit_ok else 'failed'}")
    typer.echo(f"chain: {'ok' if result.chain_ok else 'failed'}")
    typer.echo(f"summary: {result.summary_path}")


def workflow_chain(
    *,
    trade_date: str,
    artifact_root: Path,
    daily_review_fixture: Path,
    post_close_review_fixture: Path | None = None,
    preopen_review_fixture: Path | None = None,
    recipe: Path | None = None,
    recipe_extension_pack: Path | None = None,
    factor_pack: Path | None = None,
    detectors_config: Path | None = None,
    include_entry_points: bool = False,
    ohlcv_fixture_root: Path | None = None,
    asset_fixture_list: Path | None = None,
    codes: str | None = None,
) -> None:
    parsed = datetime.strptime(trade_date, "%Y-%m-%d").date()
    try:
        factor_scan_config = _build_factor_scan_config(
            factor_pack=factor_pack,
            detectors_config=detectors_config,
            include_entry_points=include_entry_points,
            ohlcv_fixture_root=ohlcv_fixture_root,
            asset_fixture_list=asset_fixture_list,
            codes=codes,
        )
        if recipe is not None:
            if recipe_extension_pack is None:
                raise ValueError("--recipe-extension-pack is required with --recipe")
            result = run_workflow_chain_recipe(
                trade_date=parsed,
                artifact_root=artifact_root,
                config=WorkflowChainRecipeConfig(
                    recipe_path=recipe,
                    recipe_extension_pack=recipe_extension_pack,
                    daily_review_fixture=daily_review_fixture,
                    factor_scan_config=factor_scan_config,
                ),
            )
        else:
            if post_close_review_fixture is None or preopen_review_fixture is None:
                raise ValueError(
                    "skeleton chain requires --post-close-review-fixture and "
                    "--preopen-review-fixture (or use --recipe)"
                )
            result = run_workflow_chain_skeleton(
                trade_date=parsed,
                artifact_root=artifact_root,
                daily_review_fixture=daily_review_fixture,
                post_close_review_fixture=post_close_review_fixture,
                preopen_review_fixture=preopen_review_fixture,
                factor_scan_config=factor_scan_config,
            )
    except FileNotFoundError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc
    except (ValueError, OSError, DetectorLoadError, RecipeExtensionLoadError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc

    _echo_chain_result(result)

    if not result.chain_ok:
        raise typer.Exit(code=1)

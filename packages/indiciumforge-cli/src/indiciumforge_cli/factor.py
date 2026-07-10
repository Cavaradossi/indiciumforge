from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from indiciumforge_core.artifacts.manifest import validate_factor_scan_stage
from indiciumforge_core.factors.loading import DetectorLoadError
from indiciumforge_core.factors.universe import load_assets_from_fixture_list, parse_asset_codes
from indiciumforge_workflow.factor_scan.runner import FactorScanStageConfig, run_factor_scan_stage

TRADE_DATE_OPTION = typer.Option(..., "--trade-date")
ARTIFACT_ROOT_OPTION = typer.Option(..., "--artifact-root")
OHLCV_FIXTURE_ROOT_OPTION = typer.Option(
    ...,
    "--ohlcv-fixture-root",
    help="Directory with synthetic OHLCV CSV fixtures.",
)
ASSET_FIXTURE_LIST_OPTION = typer.Option(
    None,
    "--asset-fixture-list",
    help="YAML asset universe list (default when --codes omitted).",
)
CODES_OPTION = typer.Option(
    None,
    "--codes",
    help="Local convenience: comma-separated asset codes (not a production universe).",
)
FACTOR_PACK_OPTION = typer.Option(None, "--factor-pack")
DETECTORS_CONFIG_OPTION = typer.Option(None, "--detectors-config")
INCLUDE_ENTRY_POINTS_OPTION = typer.Option(
    False,
    "--include-entry-points",
    help="Also load detectors from installed indiciumforge.factor_detectors entry points.",
)


def factor_scan(
    trade_date: str = TRADE_DATE_OPTION,
    artifact_root: Path = ARTIFACT_ROOT_OPTION,
    ohlcv_fixture_root: Path = OHLCV_FIXTURE_ROOT_OPTION,
    asset_fixture_list: Path | None = ASSET_FIXTURE_LIST_OPTION,
    codes: str | None = CODES_OPTION,
    factor_pack: Path | None = FACTOR_PACK_OPTION,
    detectors_config: Path | None = DETECTORS_CONFIG_OPTION,
    include_entry_points: bool = INCLUDE_ENTRY_POINTS_OPTION,
) -> None:
    if factor_pack is None and detectors_config is None and not include_entry_points:
        typer.echo(
            "Provide --factor-pack, --detectors-config, or --include-entry-points.",
            err=True,
        )
        raise typer.Exit(code=2)

    parsed = datetime.strptime(trade_date, "%Y-%m-%d").date()

    if codes is not None:
        assets = tuple(parse_asset_codes(codes))
        asset_universe_source = "cli_codes"
    elif asset_fixture_list is not None:
        assets = tuple(load_assets_from_fixture_list(asset_fixture_list))
        asset_universe_source = "fixture_asset_list"
    else:
        typer.echo("Provide --asset-fixture-list or --codes.", err=True)
        raise typer.Exit(code=2)

    try:
        result = run_factor_scan_stage(
            trade_date=parsed,
            artifact_root=artifact_root,
            config=FactorScanStageConfig(
                pack_config=factor_pack,
                detectors_config=detectors_config,
                include_entry_points=include_entry_points,
                ohlcv_fixture_root=ohlcv_fixture_root,
                asset_fixture_list=asset_fixture_list,
                assets=assets,
                asset_universe_source=asset_universe_source,
            ),
        )
    except (ValueError, OSError, DetectorLoadError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc

    audit = validate_factor_scan_stage(result.stage_dir, expected_trade_date=parsed.isoformat())
    typer.echo(f"factor-scan stage: {result.stage_dir}")
    typer.echo(f"pack_id: {result.pack.pack_id or '(none)'}")
    typer.echo(f"detectors: {', '.join(result.pack.registry.list_detectors())}")
    typer.echo(f"signals: {result.signal_count}")
    typer.echo(f"factor_scan audit: {'ok' if audit.ok else 'failed'}")

    if not audit.ok:
        raise typer.Exit(code=1)

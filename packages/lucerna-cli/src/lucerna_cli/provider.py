from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import typer
from lucerna_core.domain.models import AssetID, AssetType, Exchange
from lucerna_core.providers.capabilities import DataKind
from lucerna_core.providers.config import ProviderLoadError, load_provider_pack
from lucerna_core.providers.local_fixture_v2 import LocalFixtureProviderV2
from lucerna_core.providers.query import DataQuery
from lucerna_core.providers.registry_v2 import ProviderRegistryV2
from lucerna_core.workflow.model import (
    AssetDomain,
    SessionModel,
    WorkflowSessionMetadata,
    ashare_cycle_id,
)

PROVIDER_PACK_OPTION = typer.Option(None, "--provider-pack")
PROVIDERS_CONFIG_OPTION = typer.Option(None, "--providers-config")
INCLUDE_ENTRY_POINTS_OPTION = typer.Option(
    False,
    "--include-entry-points",
    help="Also load providers from installed lucerna.data_providers entry points.",
)
OHLCV_FIXTURE_ROOT_OPTION = typer.Option(
    None,
    "--ohlcv-fixture-root",
    help="Fixture root when no pack/config is supplied (local_fixture only).",
)
TRADE_DATE_OPTION = typer.Option(..., "--trade-date")
CODE_OPTION = typer.Option(..., "--code", help="Asset code (SSE stock for smoke tests).")
DATA_KIND_OPTION = typer.Option("ohlcv", "--data-kind")
RECIPE_ID_OPTION = typer.Option(
    "lucerna.recipe.ashare_daily_research.v1",
    "--recipe-id",
)
CYCLE_ID_OPTION = typer.Option(None, "--cycle-id")
CHECKPOINT_ID_OPTION = typer.Option(None, "--checkpoint-id")


def _load_registry(
    *,
    provider_pack: Path | None,
    providers_config: Path | None,
    include_entry_points: bool,
    ohlcv_fixture_root: Path | None,
) -> ProviderRegistryV2:
    if provider_pack is not None or providers_config is not None or include_entry_points:
        loaded = load_provider_pack(
            pack_config=provider_pack,
            providers_config=providers_config,
            include_entry_points=include_entry_points,
        )
        return ProviderRegistryV2(list(loaded.providers))

    if ohlcv_fixture_root is None:
        raise ProviderLoadError(
            "provide --provider-pack, --providers-config, --include-entry-points, "
            "or --ohlcv-fixture-root"
        )
    return ProviderRegistryV2([LocalFixtureProviderV2(ohlcv_fixture_root)])


def provider_inspect(
    provider_pack: Path | None = PROVIDER_PACK_OPTION,
    providers_config: Path | None = PROVIDERS_CONFIG_OPTION,
    include_entry_points: bool = INCLUDE_ENTRY_POINTS_OPTION,
    ohlcv_fixture_root: Path | None = OHLCV_FIXTURE_ROOT_OPTION,
) -> None:
    try:
        if provider_pack is not None or providers_config is not None or include_entry_points:
            loaded = load_provider_pack(
                pack_config=provider_pack,
                providers_config=providers_config,
                include_entry_points=include_entry_points,
            )
            if loaded.pack_id:
                typer.echo(f"pack_id: {loaded.pack_id}")
            if loaded.version:
                typer.echo(f"version: {loaded.version}")
            typer.echo(f"sources: {', '.join(loaded.sources)}")
            providers = loaded.providers
        elif ohlcv_fixture_root is not None:
            providers = (LocalFixtureProviderV2(ohlcv_fixture_root),)
        else:
            typer.echo(
                "Provide --provider-pack, --providers-config, --include-entry-points, "
                "or --ohlcv-fixture-root.",
                err=True,
            )
            raise typer.Exit(code=2)
    except ProviderLoadError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc

    for provider in providers:
        typer.echo(f"provider_id: {provider.provider_id}")
        typer.echo(f"  authority_level: {provider.authority_level.value}")
        for capability in provider.capabilities:
            venues = ",".join(capability.venues) if capability.venues else "-"
            typer.echo(
                "  capability: "
                f"{capability.asset_domain.value}/"
                f"{capability.data_kind.value}/"
                f"{capability.latency_profile.value} venues={venues}"
            )


def provider_fetch(
    trade_date: str = TRADE_DATE_OPTION,
    code: str = CODE_OPTION,
    data_kind: str = DATA_KIND_OPTION,
    provider_pack: Path | None = PROVIDER_PACK_OPTION,
    providers_config: Path | None = PROVIDERS_CONFIG_OPTION,
    include_entry_points: bool = INCLUDE_ENTRY_POINTS_OPTION,
    ohlcv_fixture_root: Path | None = OHLCV_FIXTURE_ROOT_OPTION,
    recipe_id: str = RECIPE_ID_OPTION,
    cycle_id: str | None = CYCLE_ID_OPTION,
    checkpoint_id: str | None = CHECKPOINT_ID_OPTION,
) -> None:
    try:
        parsed = datetime.strptime(trade_date, "%Y-%m-%d").date()
        kind = DataKind(data_kind)
        registry = _load_registry(
            provider_pack=provider_pack,
            providers_config=providers_config,
            include_entry_points=include_entry_points,
            ohlcv_fixture_root=ohlcv_fixture_root,
        )
    except (ProviderLoadError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc

    session = WorkflowSessionMetadata(
        recipe_id=recipe_id,
        asset_domain=AssetDomain.CHINA_A_SHARE,
        session_model=SessionModel.CALENDAR_DAY_CYCLE,
        cycle_id=cycle_id or ashare_cycle_id(parsed),
    )
    query = DataQuery.from_session(
        asset=AssetID(code, Exchange.SSE, AssetType.STOCK),
        data_kind=kind,
        session=session,
        as_of=parsed,
        checkpoint_id=checkpoint_id,
    )
    result = registry.fetch(query)
    payload = {
        "rows": len(result.frame),
        "provenance": result.provenance.to_payload(),
        "attempted_providers": list(result.attempted_providers),
    }
    typer.echo(json.dumps(payload, indent=2, default=str))

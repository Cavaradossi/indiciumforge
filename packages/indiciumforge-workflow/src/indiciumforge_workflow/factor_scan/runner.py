from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from indiciumforge_core.artifacts.paths import factor_scan_dir
from indiciumforge_core.domain.models import AssetID
from indiciumforge_core.factors.artifacts import write_factor_scan_bundle, write_factor_scan_state
from indiciumforge_core.factors.pack import LoadedFactorPack, load_factor_pack
from indiciumforge_core.factors.scan import FactorScanRunner
from indiciumforge_core.providers.local_fixture import LocalFixtureProvider
from indiciumforge_core.providers.registry import ProviderRegistry


@dataclass(frozen=True)
class FactorScanStageConfig:
    pack_config: Path | None = None
    detectors_config: Path | None = None
    include_entry_points: bool = False
    ohlcv_fixture_root: Path | None = None
    asset_fixture_list: Path | None = None
    assets: tuple[AssetID, ...] = ()
    asset_universe_source: str = "fixture_asset_list"


@dataclass(frozen=True)
class FactorScanStageResult:
    stage_dir: Path
    pack: LoadedFactorPack
    signal_count: int
    detector_count: int
    warnings: tuple[str, ...]


def run_factor_scan_stage(
    *,
    trade_date: date,
    artifact_root: Path,
    config: FactorScanStageConfig,
) -> FactorScanStageResult:
    if not config.assets:
        raise ValueError("factor scan stage requires at least one asset")

    if config.ohlcv_fixture_root is None:
        raise ValueError("factor scan stage requires ohlcv_fixture_root")

    loaded = load_factor_pack(
        pack_config=config.pack_config,
        detectors_config=config.detectors_config,
        include_entry_points=config.include_entry_points,
    )
    provider_registry = ProviderRegistry(
        [LocalFixtureProvider(config.ohlcv_fixture_root)]
    )
    runner = FactorScanRunner(provider_registry, loaded.registry)
    result = runner.scan(list(config.assets), trade_date)

    stage_dir = factor_scan_dir(artifact_root, trade_date)
    write_factor_scan_bundle(stage_dir, trade_date, result)
    write_factor_scan_state(
        stage_dir,
        trade_date=trade_date,
        pack_id=loaded.pack_id,
        detector_names=loaded.registry.list_detectors(),
        asset_universe_source=config.asset_universe_source,
        signal_count=len(result.signals),
        warning_count=len(result.warnings),
    )

    return FactorScanStageResult(
        stage_dir=stage_dir,
        pack=loaded,
        signal_count=len(result.signals),
        detector_count=len(loaded.registry.list_detectors()),
        warnings=result.warnings,
    )

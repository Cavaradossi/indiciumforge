from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from indiciumforge_core.quant.portfolio.loading import (
    PortfolioOptimizerLoadError,
    load_portfolio_optimizers_from_config,
    load_portfolio_optimizers_from_entry_points,
)
from indiciumforge_core.quant.portfolio.registry import (
    DuplicateOptimizerError,
    PortfolioOptimizationRegistry,
)
from indiciumforge_core.schema_compat import accepts_schema

PORTFOLIO_PACK_SCHEMA = "indiciumforge.portfolio_pack.v1"


@dataclass(frozen=True)
class LoadedPortfolioPack:
    pack_id: str | None
    version: str | None
    registry: PortfolioOptimizationRegistry
    sources: tuple[str, ...]


def _merge_registries(
    base: PortfolioOptimizationRegistry,
    incoming: PortfolioOptimizationRegistry,
    source: str,
) -> PortfolioOptimizationRegistry:
    merged = PortfolioOptimizationRegistry(list(base._optimizers.values()))  # noqa: SLF001
    for oid in incoming.list_optimizers():
        opt = incoming._optimizers[oid]  # noqa: SLF001
        if oid in merged._optimizers:  # noqa: SLF001
            raise DuplicateOptimizerError(f"duplicate optimizer {oid!r} while merging {source}")
        merged.register(opt)
    return merged


def _resolve_relative_path(base: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return (base.parent / candidate).resolve()


def _parse_pack_config(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PortfolioOptimizerLoadError("pack config root must be a mapping")
    schema = payload.get("schema")
    if not accepts_schema(schema, PORTFOLIO_PACK_SCHEMA, context=str(path)):
        raise PortfolioOptimizerLoadError(
            f"expected pack schema {PORTFOLIO_PACK_SCHEMA!r}, got {schema!r}"
        )
    return payload


def load_portfolio_pack(
    *,
    pack_config: Path | None = None,
    optimizers_config: Path | None = None,
    include_entry_points: bool = False,
    entry_point_group: str = "indiciumforge.portfolio_optimizers",
) -> LoadedPortfolioPack:
    if pack_config is None and optimizers_config is None and not include_entry_points:
        raise PortfolioOptimizerLoadError(
            "provide pack_config, optimizers_config, or include_entry_points=True"
        )

    pack_id: str | None = None
    version: str | None = None
    sources: list[str] = []
    registry = PortfolioOptimizationRegistry()

    if pack_config is not None:
        if not pack_config.is_file():
            raise PortfolioOptimizerLoadError(f"pack config not found: {pack_config}")
        payload = _parse_pack_config(pack_config)
        pack_id = str(payload.get("pack_id")) if payload.get("pack_id") else None
        version = str(payload.get("version")) if payload.get("version") else None
        load_section = payload.get("load")
        if not isinstance(load_section, dict):
            raise PortfolioOptimizerLoadError("pack config requires load mapping")

        opt_path_value = load_section.get("optimizers_config")
        if opt_path_value:
            opt_path = _resolve_relative_path(pack_config, str(opt_path_value))
            registry = _merge_registries(
                registry,
                load_portfolio_optimizers_from_config(opt_path),
                "optimizers_config",
            )
            sources.append("optimizers_config")

        if load_section.get("include_entry_points"):
            group = str(load_section.get("entry_point_group", entry_point_group))
            registry = _merge_registries(
                registry,
                load_portfolio_optimizers_from_entry_points(group=group),
                "entry_points",
            )
            sources.append("entry_points")

    if optimizers_config is not None:
        if not optimizers_config.is_file():
            raise PortfolioOptimizerLoadError(f"optimizers config not found: {optimizers_config}")
        registry = _merge_registries(
            registry,
            load_portfolio_optimizers_from_config(optimizers_config),
            "optimizers_config",
        )
        if "optimizers_config" not in sources:
            sources.append("optimizers_config")

    if include_entry_points:
        registry = _merge_registries(
            registry,
            load_portfolio_optimizers_from_entry_points(group=entry_point_group),
            "entry_points",
        )
        if "entry_points" not in sources:
            sources.append("entry_points")

    if not registry.list_optimizers():
        raise PortfolioOptimizerLoadError("no optimizers loaded from portfolio pack")

    return LoadedPortfolioPack(
        pack_id=pack_id,
        version=version,
        registry=registry,
        sources=tuple(sources),
    )

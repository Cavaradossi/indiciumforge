from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from indiciumforge_core.quant.pricing.loading import (
    PricerLoadError,
    load_pricers_from_config,
    load_pricers_from_entry_points,
)
from indiciumforge_core.quant.pricing.registry import DuplicatePricerError, PricingRegistry
from indiciumforge_core.schema_compat import accepts_schema

PRICING_PACK_SCHEMA = "indiciumforge.pricing_pack.v1"


@dataclass(frozen=True)
class LoadedPricingPack:
    pack_id: str | None
    version: str | None
    registry: PricingRegistry
    sources: tuple[str, ...]


def _merge_registries(
    base: PricingRegistry, incoming: PricingRegistry, source: str
) -> PricingRegistry:
    merged = PricingRegistry(list(base._pricers.values()))  # noqa: SLF001
    for pid in incoming.list_pricers():
        pricer = incoming._pricers[pid]  # noqa: SLF001
        if pid in merged._pricers:  # noqa: SLF001
            raise DuplicatePricerError(f"duplicate pricer {pid!r} while merging {source}")
        merged.register(pricer)
    return merged


def _resolve_relative_path(base: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return (base.parent / candidate).resolve()


def _parse_pack_config(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PricerLoadError("pack config root must be a mapping")
    schema = payload.get("schema")
    if not accepts_schema(schema, PRICING_PACK_SCHEMA, context=str(path)):
        raise PricerLoadError(
            f"expected pack schema {PRICING_PACK_SCHEMA!r}, got {schema!r}"
        )
    return payload


def load_pricing_pack(
    *,
    pack_config: Path | None = None,
    pricers_config: Path | None = None,
    include_entry_points: bool = False,
    entry_point_group: str = "indiciumforge.pricers",
) -> LoadedPricingPack:
    if pack_config is None and pricers_config is None and not include_entry_points:
        raise PricerLoadError(
            "provide pack_config, pricers_config, or include_entry_points=True"
        )

    pack_id: str | None = None
    version: str | None = None
    sources: list[str] = []
    registry = PricingRegistry()

    if pack_config is not None:
        if not pack_config.is_file():
            raise PricerLoadError(f"pack config not found: {pack_config}")
        payload = _parse_pack_config(pack_config)
        pack_id = str(payload.get("pack_id")) if payload.get("pack_id") else None
        version = str(payload.get("version")) if payload.get("version") else None
        load_section = payload.get("load")
        if not isinstance(load_section, dict):
            raise PricerLoadError("pack config requires load mapping")

        pricer_path_value = load_section.get("pricers_config")
        if pricer_path_value:
            pricer_path = _resolve_relative_path(pack_config, str(pricer_path_value))
            registry = _merge_registries(
                registry, load_pricers_from_config(pricer_path), "pricers_config"
            )
            sources.append("pricers_config")

        if load_section.get("include_entry_points"):
            group = str(load_section.get("entry_point_group", entry_point_group))
            registry = _merge_registries(
                registry, load_pricers_from_entry_points(group=group), "entry_points"
            )
            sources.append("entry_points")

    if pricers_config is not None:
        if not pricers_config.is_file():
            raise PricerLoadError(f"pricers config not found: {pricers_config}")
        registry = _merge_registries(
            registry, load_pricers_from_config(pricers_config), "pricers_config"
        )
        if "pricers_config" not in sources:
            sources.append("pricers_config")

    if include_entry_points:
        registry = _merge_registries(
            registry, load_pricers_from_entry_points(group=entry_point_group), "entry_points"
        )
        if "entry_points" not in sources:
            sources.append("entry_points")

    if not registry.list_pricers():
        raise PricerLoadError("no pricers loaded from pricing pack")

    return LoadedPricingPack(
        pack_id=pack_id, version=version, registry=registry, sources=tuple(sources)
    )

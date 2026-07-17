from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from indiciumforge_core.quant.analytics.loading import (
    FactorAnalyticsLoadError,
    load_analytics_from_config,
    load_analytics_from_entry_points,
)
from indiciumforge_core.quant.analytics.registry import (
    DuplicateEngineError,
    FactorAnalyticsRegistry,
)
from indiciumforge_core.schema_compat import accepts_schema

FACTOR_ANALYTICS_PACK_SCHEMA = "indiciumforge.factor_analytics_pack.v1"


@dataclass(frozen=True)
class LoadedAnalyticsPack:
    pack_id: str | None
    version: str | None
    registry: FactorAnalyticsRegistry
    sources: tuple[str, ...]


def _merge_registries(
    base: FactorAnalyticsRegistry,
    incoming: FactorAnalyticsRegistry,
    source: str,
) -> FactorAnalyticsRegistry:
    merged = FactorAnalyticsRegistry(list(base._engines.values()))  # noqa: SLF001
    for eid in incoming.list_engines():
        engine = incoming._engines[eid]  # noqa: SLF001
        if eid in merged._engines:  # noqa: SLF001
            raise DuplicateEngineError(f"duplicate engine {eid!r} while merging {source}")
        merged.register(engine)
    return merged


def _resolve_relative_path(base: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return (base.parent / candidate).resolve()


def _parse_pack_config(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise FactorAnalyticsLoadError("pack config root must be a mapping")
    schema = payload.get("schema")
    if not accepts_schema(schema, FACTOR_ANALYTICS_PACK_SCHEMA, context=str(path)):
        raise FactorAnalyticsLoadError(
            f"expected pack schema {FACTOR_ANALYTICS_PACK_SCHEMA!r}, got {schema!r}"
        )
    return payload


def load_analytics_pack(
    *,
    pack_config: Path | None = None,
    engines_config: Path | None = None,
    include_entry_points: bool = False,
    entry_point_group: str = "indiciumforge.factor_analytics",
) -> LoadedAnalyticsPack:
    if pack_config is None and engines_config is None and not include_entry_points:
        raise FactorAnalyticsLoadError(
            "provide pack_config, engines_config, or include_entry_points=True"
        )

    pack_id: str | None = None
    version: str | None = None
    sources: list[str] = []
    registry = FactorAnalyticsRegistry()

    if pack_config is not None:
        if not pack_config.is_file():
            raise FactorAnalyticsLoadError(f"pack config not found: {pack_config}")
        payload = _parse_pack_config(pack_config)
        pack_id = str(payload.get("pack_id")) if payload.get("pack_id") else None
        version = str(payload.get("version")) if payload.get("version") else None
        load_section = payload.get("load")
        if not isinstance(load_section, dict):
            raise FactorAnalyticsLoadError("pack config requires load mapping")

        engines_path_value = load_section.get("engines_config")
        if engines_path_value:
            engines_path = _resolve_relative_path(pack_config, str(engines_path_value))
            registry = _merge_registries(
                registry,
                load_analytics_from_config(engines_path),
                "engines_config",
            )
            sources.append("engines_config")

        if load_section.get("include_entry_points"):
            group = str(load_section.get("entry_point_group", entry_point_group))
            registry = _merge_registries(
                registry,
                load_analytics_from_entry_points(group=group),
                "entry_points",
            )
            sources.append("entry_points")

    if engines_config is not None:
        if not engines_config.is_file():
            raise FactorAnalyticsLoadError(f"engines config not found: {engines_config}")
        registry = _merge_registries(
            registry,
            load_analytics_from_config(engines_config),
            "engines_config",
        )
        if "engines_config" not in sources:
            sources.append("engines_config")

    if include_entry_points:
        registry = _merge_registries(
            registry,
            load_analytics_from_entry_points(group=entry_point_group),
            "entry_points",
        )
        if "entry_points" not in sources:
            sources.append("entry_points")

    if not registry.list_engines():
        raise FactorAnalyticsLoadError("no engines loaded from analytics pack")

    return LoadedAnalyticsPack(
        pack_id=pack_id,
        version=version,
        registry=registry,
        sources=tuple(sources),
    )

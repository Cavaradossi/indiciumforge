from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from indiciumforge_core.factors.loading import (
    DetectorLoadError,
    load_detectors_from_config,
    load_detectors_from_entry_points,
)
from indiciumforge_core.factors.registry import DuplicateDetectorError, FactorDetectorRegistry
from indiciumforge_core.schema_compat import accepts_schema

FACTOR_PACK_SCHEMA = "indiciumforge.factor_pack.v1"


@dataclass(frozen=True)
class LoadedFactorPack:
    pack_id: str | None
    version: str | None
    registry: FactorDetectorRegistry
    sources: tuple[str, ...]


def _merge_registries(
    base: FactorDetectorRegistry,
    incoming: FactorDetectorRegistry,
    source: str,
) -> FactorDetectorRegistry:
    merged = FactorDetectorRegistry(list(base._detectors.values()))  # noqa: SLF001
    for name in incoming.list_detectors():
        detector = incoming._detectors[name]  # noqa: SLF001
        if name in merged._detectors:  # noqa: SLF001
            raise DuplicateDetectorError(
                f"duplicate detector {name!r} while merging {source}"
            )
        merged.register(detector)
    return merged


def _resolve_relative_path(base: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return (base.parent / candidate).resolve()


def _parse_pack_config(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DetectorLoadError("pack config root must be a mapping")
    schema = payload.get("schema")
    if not accepts_schema(schema, FACTOR_PACK_SCHEMA, context=str(path)):
        raise DetectorLoadError(
            f"expected pack schema {FACTOR_PACK_SCHEMA!r}, got {schema!r}"
        )
    return payload


def load_factor_pack(
    *,
    pack_config: Path | None = None,
    detectors_config: Path | None = None,
    include_entry_points: bool = False,
    entry_point_group: str = "indiciumforge.factor_detectors",
) -> LoadedFactorPack:
    if pack_config is None and detectors_config is None and not include_entry_points:
        raise DetectorLoadError(
            "provide pack_config, detectors_config, or include_entry_points=True"
        )

    pack_id: str | None = None
    version: str | None = None
    sources: list[str] = []
    registry = FactorDetectorRegistry()

    if pack_config is not None:
        if not pack_config.is_file():
            raise DetectorLoadError(f"pack config not found: {pack_config}")
        payload = _parse_pack_config(pack_config)
        pack_id = str(payload.get("pack_id")) if payload.get("pack_id") else None
        version = str(payload.get("version")) if payload.get("version") else None
        load_section = payload.get("load")
        if not isinstance(load_section, dict):
            raise DetectorLoadError("pack config requires load mapping")

        detectors_path_value = load_section.get("detectors_config")
        if detectors_path_value:
            detectors_path = _resolve_relative_path(
                pack_config, str(detectors_path_value)
            )
            registry = _merge_registries(
                registry,
                load_detectors_from_config(detectors_path),
                "detectors_config",
            )
            sources.append("detectors_config")

        if load_section.get("include_entry_points"):
            group = str(load_section.get("entry_point_group", entry_point_group))
            registry = _merge_registries(
                registry,
                load_detectors_from_entry_points(group=group),
                "entry_points",
            )
            sources.append("entry_points")

    if detectors_config is not None:
        if not detectors_config.is_file():
            raise DetectorLoadError(f"detectors config not found: {detectors_config}")
        registry = _merge_registries(
            registry,
            load_detectors_from_config(detectors_config),
            "detectors_config",
        )
        if "detectors_config" not in sources:
            sources.append("detectors_config")

    if include_entry_points:
        registry = _merge_registries(
            registry,
            load_detectors_from_entry_points(group=entry_point_group),
            "entry_points",
        )
        if "entry_points" not in sources:
            sources.append("entry_points")

    if not registry.list_detectors():
        raise DetectorLoadError("no detectors loaded from factor pack")

    return LoadedFactorPack(
        pack_id=pack_id,
        version=version,
        registry=registry,
        sources=tuple(sources),
    )

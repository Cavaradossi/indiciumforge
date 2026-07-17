from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from indiciumforge_core.quant.backtest.loading import (
    BacktesterLoadError,
    load_backtesters_from_config,
    load_backtesters_from_entry_points,
)
from indiciumforge_core.quant.backtest.registry import (
    BacktestRegistry,
    DuplicateBacktesterError,
)
from indiciumforge_core.schema_compat import accepts_schema

BACKTEST_PACK_SCHEMA = "indiciumforge.backtest_pack.v1"


@dataclass(frozen=True)
class LoadedBacktestPack:
    pack_id: str | None
    version: str | None
    registry: BacktestRegistry
    sources: tuple[str, ...]


def _merge_registries(
    base: BacktestRegistry, incoming: BacktestRegistry, source: str
) -> BacktestRegistry:
    merged = BacktestRegistry(list(base._backtesters.values()))  # noqa: SLF001
    for bid in incoming.list_backtesters():
        bt = incoming._backtesters[bid]  # noqa: SLF001
        if bid in merged._backtesters:  # noqa: SLF001
            raise DuplicateBacktesterError(f"duplicate backtester {bid!r} while merging {source}")
        merged.register(bt)
    return merged


def _resolve_relative_path(base: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return (base.parent / candidate).resolve()


def _parse_pack_config(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise BacktesterLoadError("pack config root must be a mapping")
    schema = payload.get("schema")
    if not accepts_schema(schema, BACKTEST_PACK_SCHEMA, context=str(path)):
        raise BacktesterLoadError(
            f"expected pack schema {BACKTEST_PACK_SCHEMA!r}, got {schema!r}"
        )
    return payload


def load_backtest_pack(
    *,
    pack_config: Path | None = None,
    backtesters_config: Path | None = None,
    include_entry_points: bool = False,
    entry_point_group: str = "indiciumforge.backtesters",
) -> LoadedBacktestPack:
    if pack_config is None and backtesters_config is None and not include_entry_points:
        raise BacktesterLoadError(
            "provide pack_config, backtesters_config, or include_entry_points=True"
        )

    pack_id: str | None = None
    version: str | None = None
    sources: list[str] = []
    registry = BacktestRegistry()

    if pack_config is not None:
        if not pack_config.is_file():
            raise BacktesterLoadError(f"pack config not found: {pack_config}")
        payload = _parse_pack_config(pack_config)
        pack_id = str(payload.get("pack_id")) if payload.get("pack_id") else None
        version = str(payload.get("version")) if payload.get("version") else None
        load_section = payload.get("load")
        if not isinstance(load_section, dict):
            raise BacktesterLoadError("pack config requires load mapping")

        bt_path_value = load_section.get("backtesters_config")
        if bt_path_value:
            bt_path = _resolve_relative_path(pack_config, str(bt_path_value))
            registry = _merge_registries(
                registry, load_backtesters_from_config(bt_path), "backtesters_config"
            )
            sources.append("backtesters_config")

        if load_section.get("include_entry_points"):
            group = str(load_section.get("entry_point_group", entry_point_group))
            registry = _merge_registries(
                registry, load_backtesters_from_entry_points(group=group), "entry_points"
            )
            sources.append("entry_points")

    if backtesters_config is not None:
        if not backtesters_config.is_file():
            raise BacktesterLoadError(f"backtesters config not found: {backtesters_config}")
        registry = _merge_registries(
            registry, load_backtesters_from_config(backtesters_config), "backtesters_config"
        )
        if "backtesters_config" not in sources:
            sources.append("backtesters_config")

    if include_entry_points:
        registry = _merge_registries(
            registry, load_backtesters_from_entry_points(group=entry_point_group), "entry_points"
        )
        if "entry_points" not in sources:
            sources.append("entry_points")

    if not registry.list_backtesters():
        raise BacktesterLoadError("no backtesters loaded from backtest pack")

    return LoadedBacktestPack(
        pack_id=pack_id, version=version, registry=registry, sources=tuple(sources)
    )

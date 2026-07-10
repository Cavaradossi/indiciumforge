from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from indiciumforge_core.recipes.config import (
    RecipeExtensionLoadError,
    _parse_pack_config,
    _resolve_relative_path,
    load_extensions_from_config,
    load_extensions_from_entry_points,
)
from indiciumforge_core.recipes.ports import PrivateRecipeExtensionPort


@dataclass(frozen=True)
class LoadedRecipeExtensionPack:
    pack_id: str | None
    version: str | None
    recipe_ids: tuple[str, ...]
    extensions: tuple[PrivateRecipeExtensionPort, ...]
    sources: tuple[str, ...]


def load_recipe_extension_pack(
    *,
    pack_config: Path | None = None,
    extensions_config: Path | None = None,
    include_entry_points: bool = False,
    entry_point_group: str = "indiciumforge.recipe_extensions",
) -> LoadedRecipeExtensionPack:
    if pack_config is None and extensions_config is None and not include_entry_points:
        raise RecipeExtensionLoadError(
            "provide pack_config, extensions_config, or include_entry_points=True"
        )

    pack_id: str | None = None
    version: str | None = None
    recipe_ids: tuple[str, ...] = ()
    sources: list[str] = []
    extensions: list[PrivateRecipeExtensionPort] = []
    seen: set[str] = set()

    def _merge(incoming: tuple[PrivateRecipeExtensionPort, ...], source: str) -> None:
        for extension in incoming:
            if extension.extension_id in seen:
                raise RecipeExtensionLoadError(
                    f"duplicate extension_id: {extension.extension_id}"
                )
            seen.add(extension.extension_id)
            extensions.append(extension)
        if source not in sources:
            sources.append(source)

    if pack_config is not None:
        if not pack_config.is_file():
            raise RecipeExtensionLoadError(f"pack config not found: {pack_config}")
        payload = _parse_pack_config(pack_config)
        pack_id = str(payload.get("pack_id")) if payload.get("pack_id") else None
        version = str(payload.get("version")) if payload.get("version") else None
        raw_recipe_ids = payload.get("recipe_ids") or []
        if isinstance(raw_recipe_ids, list):
            recipe_ids = tuple(str(item) for item in raw_recipe_ids)
        load_section = payload.get("load")
        if not isinstance(load_section, dict):
            raise RecipeExtensionLoadError("pack config requires load mapping")

        extensions_path_value = load_section.get("extensions_config")
        if extensions_path_value:
            extensions_path = _resolve_relative_path(
                pack_config, str(extensions_path_value)
            )
            _merge(load_extensions_from_config(extensions_path), "extensions_config")

        if load_section.get("include_entry_points"):
            group = str(load_section.get("entry_point_group", entry_point_group))
            _merge(load_extensions_from_entry_points(group=group), "entry_points")

    if extensions_config is not None:
        if not extensions_config.is_file():
            raise RecipeExtensionLoadError(f"extensions config not found: {extensions_config}")
        _merge(load_extensions_from_config(extensions_config), "extensions_config")

    if include_entry_points:
        _merge(load_extensions_from_entry_points(group=entry_point_group), "entry_points")

    if not extensions:
        raise RecipeExtensionLoadError("no extensions loaded from recipe extension pack")

    return LoadedRecipeExtensionPack(
        pack_id=pack_id,
        version=version,
        recipe_ids=recipe_ids,
        extensions=tuple(extensions),
        sources=tuple(sources),
    )

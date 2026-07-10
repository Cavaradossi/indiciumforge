from __future__ import annotations

import importlib
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any

import yaml

from indiciumforge_core.recipes.ports import PrivateRecipeExtensionPort
from indiciumforge_core.recipes.schemas import RECIPE_EXTENSION_PACK_SCHEMA
from indiciumforge_core.schema_compat import accepts_schema


class RecipeExtensionLoadError(ValueError):
    """Raised when a recipe extension cannot be loaded."""


def _validate_extension(candidate: object, source: str) -> PrivateRecipeExtensionPort:
    extension_id = getattr(candidate, "extension_id", None)
    if not isinstance(extension_id, str):
        raise RecipeExtensionLoadError(f"{source}: missing string extension_id")
    recipe_ids = getattr(candidate, "recipe_ids", None)
    if not isinstance(recipe_ids, tuple):
        raise RecipeExtensionLoadError(f"{source}: recipe_ids must be a tuple")
    if not callable(getattr(candidate, "supports_stage", None)):
        raise RecipeExtensionLoadError(f"{source}: missing supports_stage()")
    if not callable(getattr(candidate, "execute_stage", None)):
        raise RecipeExtensionLoadError(f"{source}: missing execute_stage()")
    return candidate  # type: ignore[return-value]


def _import_object(module_path: str, class_name: str) -> object:
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise RecipeExtensionLoadError(f"cannot import module {module_path}: {exc}") from exc
    try:
        return getattr(module, class_name)
    except AttributeError as exc:
        raise RecipeExtensionLoadError(f"{module_path}.{class_name} not found") from exc


def _resolve_relative_path(base: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    root = base if base.is_dir() else base.parent
    return (root / candidate).resolve()


def _resolve_kwargs_paths(base: Path, kwargs: dict[str, Any]) -> dict[str, Any]:
    resolved: dict[str, Any] = {}
    for key, value in kwargs.items():
        if isinstance(value, str) and (
            key.endswith("_root")
            or key.endswith("_path")
            or key.endswith("_config")
            or key.endswith("_fixture")
            or key.endswith("_list")
        ):
            resolved[key] = _resolve_relative_path(base, value)
        else:
            resolved[key] = value
    return resolved


def _instantiate(
    entry: dict[str, Any],
    *,
    config_base: Path | None = None,
) -> PrivateRecipeExtensionPort:
    module_path = entry.get("module")
    class_name = entry.get("class")
    if not module_path or not class_name:
        raise RecipeExtensionLoadError("extension entry requires module+class")

    candidate_cls = _import_object(str(module_path), str(class_name))
    kwargs = entry.get("kwargs") or {}
    if not isinstance(kwargs, dict):
        raise RecipeExtensionLoadError("extension kwargs must be a mapping")
    if config_base is not None:
        kwargs = _resolve_kwargs_paths(config_base, kwargs)
    if isinstance(candidate_cls, type):
        candidate = candidate_cls(**kwargs)
    else:
        candidate = candidate_cls
    return _validate_extension(candidate, f"{module_path}.{class_name}")


def load_extensions_from_config(path: Path) -> tuple[PrivateRecipeExtensionPort, ...]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RecipeExtensionLoadError("config root must be a mapping")
    entries = payload.get("extensions")
    if not isinstance(entries, list):
        raise RecipeExtensionLoadError("config requires extensions list")
    extensions: list[PrivateRecipeExtensionPort] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise RecipeExtensionLoadError("each extension entry must be a mapping")
        extension = _instantiate(entry, config_base=path.parent)
        if extension.extension_id in seen:
            raise RecipeExtensionLoadError(f"duplicate extension_id: {extension.extension_id}")
        seen.add(extension.extension_id)
        extensions.append(extension)
    return tuple(extensions)


def load_extensions_from_entry_points(
    group: str = "indiciumforge.recipe_extensions",
) -> tuple[PrivateRecipeExtensionPort, ...]:
    extensions: list[PrivateRecipeExtensionPort] = []
    seen: set[str] = set()
    for entry_point in entry_points(group=group):
        candidate = entry_point.load()
        if callable(candidate) and not isinstance(getattr(candidate, "extension_id", None), str):
            candidate = candidate()
        extension = _validate_extension(candidate, f"entry_point={entry_point.name}")
        if extension.extension_id in seen:
            raise RecipeExtensionLoadError(f"duplicate extension_id: {extension.extension_id}")
        seen.add(extension.extension_id)
        extensions.append(extension)
    return tuple(extensions)


def _parse_pack_config(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RecipeExtensionLoadError("pack config root must be a mapping")
    schema = payload.get("schema")
    if not accepts_schema(schema, RECIPE_EXTENSION_PACK_SCHEMA, context=str(path)):
        raise RecipeExtensionLoadError(
            f"expected pack schema {RECIPE_EXTENSION_PACK_SCHEMA!r}, got {schema!r}"
        )
    return payload

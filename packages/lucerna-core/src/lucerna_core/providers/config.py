from __future__ import annotations

import importlib
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any

import yaml

from lucerna_core.providers.contracts_v2 import DataProviderPortV2
from lucerna_core.providers.pack import PROVIDER_PACK_SCHEMA, LoadedProviderPack


class ProviderLoadError(ValueError):
    """Raised when a configured provider cannot be imported or validated."""


def _validate_provider(candidate: object, source: str) -> DataProviderPortV2:
    provider_id = getattr(candidate, "provider_id", None)
    if not isinstance(provider_id, str):
        raise ProviderLoadError(f"{source}: missing string provider_id attribute")
    if not callable(getattr(candidate, "supports_query", None)):
        raise ProviderLoadError(f"{source}: missing supports_query()")
    if not callable(getattr(candidate, "fetch", None)):
        raise ProviderLoadError(f"{source}: missing fetch()")
    authority = getattr(candidate, "authority_level", None)
    if authority is None:
        raise ProviderLoadError(f"{source}: missing authority_level")
    capabilities = getattr(candidate, "capabilities", None)
    if not isinstance(capabilities, tuple):
        raise ProviderLoadError(f"{source}: capabilities must be a tuple")
    return candidate  # type: ignore[return-value]


def _import_object(module_path: str, class_name: str) -> object:
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise ProviderLoadError(f"cannot import module {module_path}: {exc}") from exc
    try:
        return getattr(module, class_name)
    except AttributeError as exc:
        raise ProviderLoadError(f"{module_path}.{class_name} not found") from exc


def _parse_entry_point_ref(value: str) -> tuple[str, str]:
    if ":" not in value:
        raise ProviderLoadError(f"invalid entry_point reference: {value}")
    group, name = value.split(":", 1)
    if not group or not name:
        raise ProviderLoadError(f"invalid entry_point reference: {value}")
    return group, name


def _load_entry_point(group: str, name: str) -> object:
    for entry_point in entry_points(group=group):
        if entry_point.name == name:
            return entry_point.load()
    raise ProviderLoadError(f"entry point not found: {group}:{name}")


def _resolve_kwargs_paths(base: Path, kwargs: dict[str, Any]) -> dict[str, Any]:
    resolved: dict[str, Any] = {}
    for key, value in kwargs.items():
        if isinstance(value, str) and (key.endswith("_root") or key.endswith("_path")):
            resolved[key] = _resolve_relative_path(base, value)
        else:
            resolved[key] = value
    return resolved


def _instantiate(entry: dict[str, Any], *, config_base: Path | None = None) -> DataProviderPortV2:
    if "entry_point" in entry:
        group, name = _parse_entry_point_ref(str(entry["entry_point"]))
        candidate = _load_entry_point(group, name)
        if callable(candidate) and not isinstance(getattr(candidate, "provider_id", None), str):
            kwargs = entry.get("kwargs") or {}
            if not isinstance(kwargs, dict):
                raise ProviderLoadError("provider kwargs must be a mapping")
            if config_base is not None:
                kwargs = _resolve_kwargs_paths(config_base, kwargs)
            candidate = candidate(**kwargs)
        return _validate_provider(candidate, f"entry_point={entry['entry_point']}")

    module_path = entry.get("module")
    class_name = entry.get("class")
    if not module_path or not class_name:
        raise ProviderLoadError("provider entry requires module+class or entry_point")

    candidate_cls = _import_object(str(module_path), str(class_name))
    kwargs = entry.get("kwargs") or {}
    if not isinstance(kwargs, dict):
        raise ProviderLoadError("provider kwargs must be a mapping")
    if config_base is not None:
        kwargs = _resolve_kwargs_paths(config_base, kwargs)
    if isinstance(candidate_cls, type):
        candidate = candidate_cls(**kwargs)
    else:
        candidate = candidate_cls
    return _validate_provider(candidate, f"{module_path}.{class_name}")


def load_providers_from_config(path: Path) -> tuple[DataProviderPortV2, ...]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ProviderLoadError("config root must be a mapping")
    entries = payload.get("providers")
    if not isinstance(entries, list):
        raise ProviderLoadError("config requires providers list")
    providers: list[DataProviderPortV2] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ProviderLoadError("each provider entry must be a mapping")
        provider = _instantiate(entry, config_base=path.parent)
        if provider.provider_id in seen:
            raise ProviderLoadError(f"duplicate provider_id: {provider.provider_id}")
        seen.add(provider.provider_id)
        providers.append(provider)
    return tuple(providers)


def load_providers_from_entry_points(
    group: str = "lucerna.data_providers",
) -> tuple[DataProviderPortV2, ...]:
    providers: list[DataProviderPortV2] = []
    seen: set[str] = set()
    for entry_point in entry_points(group=group):
        candidate = entry_point.load()
        if callable(candidate) and not isinstance(getattr(candidate, "provider_id", None), str):
            candidate = candidate()
        provider = _validate_provider(candidate, f"entry_point={entry_point.name}")
        if provider.provider_id in seen:
            raise ProviderLoadError(f"duplicate provider_id: {provider.provider_id}")
        seen.add(provider.provider_id)
        providers.append(provider)
    return tuple(providers)


def _resolve_relative_path(base: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    root = base if base.is_dir() else base.parent
    return (root / candidate).resolve()


def _parse_pack_config(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ProviderLoadError("pack config root must be a mapping")
    schema = payload.get("schema")
    if schema != PROVIDER_PACK_SCHEMA:
        raise ProviderLoadError(
            f"expected pack schema {PROVIDER_PACK_SCHEMA!r}, got {schema!r}"
        )
    return payload


def load_provider_pack(
    *,
    pack_config: Path | None = None,
    providers_config: Path | None = None,
    include_entry_points: bool = False,
    entry_point_group: str = "lucerna.data_providers",
) -> LoadedProviderPack:
    if pack_config is None and providers_config is None and not include_entry_points:
        raise ProviderLoadError(
            "provide pack_config, providers_config, or include_entry_points=True"
        )

    pack_id: str | None = None
    version: str | None = None
    sources: list[str] = []
    providers: list[DataProviderPortV2] = []
    seen: set[str] = set()

    def _merge(incoming: tuple[DataProviderPortV2, ...], source: str) -> None:
        for provider in incoming:
            if provider.provider_id in seen:
                raise ProviderLoadError(f"duplicate provider_id: {provider.provider_id}")
            seen.add(provider.provider_id)
            providers.append(provider)
        if source not in sources:
            sources.append(source)

    if pack_config is not None:
        if not pack_config.is_file():
            raise ProviderLoadError(f"pack config not found: {pack_config}")
        payload = _parse_pack_config(pack_config)
        pack_id = str(payload.get("pack_id")) if payload.get("pack_id") else None
        version = str(payload.get("version")) if payload.get("version") else None
        load_section = payload.get("load")
        if not isinstance(load_section, dict):
            raise ProviderLoadError("pack config requires load mapping")

        providers_path_value = load_section.get("providers_config")
        if providers_path_value:
            providers_path = _resolve_relative_path(pack_config, str(providers_path_value))
            _merge(load_providers_from_config(providers_path), "providers_config")

        if load_section.get("include_entry_points"):
            group = str(load_section.get("entry_point_group", entry_point_group))
            _merge(load_providers_from_entry_points(group=group), "entry_points")

    if providers_config is not None:
        if not providers_config.is_file():
            raise ProviderLoadError(f"providers config not found: {providers_config}")
        _merge(load_providers_from_config(providers_config), "providers_config")

    if include_entry_points:
        _merge(load_providers_from_entry_points(group=entry_point_group), "entry_points")

    if not providers:
        raise ProviderLoadError("no providers loaded from provider pack")

    return LoadedProviderPack(
        pack_id=pack_id,
        version=version,
        providers=tuple(providers),
        sources=tuple(sources),
    )

from __future__ import annotations

import importlib
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any

import yaml

from indiciumforge_core.quant.analytics.ports import FactorAnalyticsPort
from indiciumforge_core.quant.analytics.registry import FactorAnalyticsRegistry


class FactorAnalyticsLoadError(ValueError):
    """Raised when a configured analytics engine cannot be imported/validated."""


def _validate_engine(candidate: object, source: str) -> FactorAnalyticsPort:
    if not isinstance(getattr(candidate, "engine_id", None), str):
        raise FactorAnalyticsLoadError(f"{source}: missing string engine_id attribute")
    if not callable(getattr(candidate, "supports", None)):
        raise FactorAnalyticsLoadError(f"{source}: missing supports()")
    if not callable(getattr(candidate, "evaluate", None)):
        raise FactorAnalyticsLoadError(f"{source}: missing evaluate()")
    return candidate  # type: ignore[return-value]


def _import_object(module_path: str, class_name: str) -> object:
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise FactorAnalyticsLoadError(f"cannot import module {module_path}: {exc}") from exc
    try:
        return getattr(module, class_name)
    except AttributeError as exc:
        raise FactorAnalyticsLoadError(f"{module_path}.{class_name} not found") from exc


def _instantiate(entry: dict[str, Any]) -> FactorAnalyticsPort:
    module_path = entry.get("module")
    class_name = entry.get("class")
    if not module_path or not class_name:
        raise FactorAnalyticsLoadError("engine entry requires module+class")
    candidate_cls = _import_object(str(module_path), str(class_name))
    if isinstance(candidate_cls, type):
        candidate = candidate_cls()
    else:
        candidate = candidate_cls
    return _validate_engine(candidate, f"{module_path}.{class_name}")


def _parse_entry_point_ref(value: str) -> tuple[str, str]:
    if ":" not in value:
        raise FactorAnalyticsLoadError(f"invalid entry_point reference: {value}")
    group, name = value.split(":", 1)
    if not group or not name:
        raise FactorAnalyticsLoadError(f"invalid entry_point reference: {value}")
    return group, name


def _load_entry_point(group: str, name: str) -> object:
    for entry_point in entry_points(group=group):
        if entry_point.name == name:
            return entry_point.load()
    raise FactorAnalyticsLoadError(f"entry point not found: {group}:{name}")


def load_analytics_from_config(path: Path) -> FactorAnalyticsRegistry:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise FactorAnalyticsLoadError("config root must be a mapping")
    entries = payload.get("engines")
    if not isinstance(entries, list):
        raise FactorAnalyticsLoadError("config requires engines list")
    registry = FactorAnalyticsRegistry()
    for entry in entries:
        if not isinstance(entry, dict):
            raise FactorAnalyticsLoadError("each engine entry must be a mapping")
        registry.register(_instantiate(entry))
    return registry


def load_analytics_from_entry_points(
    group: str = "indiciumforge.factor_analytics",
) -> FactorAnalyticsRegistry:
    registry = FactorAnalyticsRegistry()
    for entry_point in entry_points(group=group):
        candidate = entry_point.load()
        if callable(candidate) and not isinstance(getattr(candidate, "engine_id", None), str):
            candidate = candidate()
        registry.register(_validate_engine(candidate, f"entry_point={entry_point.name}"))
    return registry

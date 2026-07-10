from __future__ import annotations

import importlib
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any

import yaml

from indiciumforge_core.factors.ports import FactorDetectorPort
from indiciumforge_core.factors.registry import FactorDetectorRegistry


class DetectorLoadError(ValueError):
    """Raised when a configured detector cannot be imported or validated."""


def _validate_detector(candidate: object, source: str) -> FactorDetectorPort:
    if not isinstance(getattr(candidate, "name", None), str):
        raise DetectorLoadError(f"{source}: missing string name attribute")
    if not callable(getattr(candidate, "supports", None)):
        raise DetectorLoadError(f"{source}: missing supports()")
    if not callable(getattr(candidate, "detect", None)):
        raise DetectorLoadError(f"{source}: missing detect()")
    return candidate  # type: ignore[return-value]


def _import_object(module_path: str, class_name: str) -> object:
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise DetectorLoadError(f"cannot import module {module_path}: {exc}") from exc
    try:
        return getattr(module, class_name)
    except AttributeError as exc:
        raise DetectorLoadError(f"{module_path}.{class_name} not found") from exc


def _instantiate(entry: dict[str, Any]) -> FactorDetectorPort:
    if "entry_point" in entry:
        group, name = _parse_entry_point_ref(str(entry["entry_point"]))
        candidate = _load_entry_point(group, name)
        if callable(candidate) and not isinstance(getattr(candidate, "name", None), str):
            candidate = candidate()
        return _validate_detector(candidate, f"entry_point={entry['entry_point']}")

    module_path = entry.get("module")
    class_name = entry.get("class")
    if not module_path or not class_name:
        raise DetectorLoadError("detector entry requires module+class or entry_point")

    candidate_cls = _import_object(str(module_path), str(class_name))
    if isinstance(candidate_cls, type):
        candidate = candidate_cls()
    else:
        candidate = candidate_cls
    return _validate_detector(candidate, f"{module_path}.{class_name}")


def _parse_entry_point_ref(value: str) -> tuple[str, str]:
    if ":" not in value:
        raise DetectorLoadError(f"invalid entry_point reference: {value}")
    group, name = value.split(":", 1)
    if not group or not name:
        raise DetectorLoadError(f"invalid entry_point reference: {value}")
    return group, name


def _load_entry_point(group: str, name: str) -> object:
    for entry_point in entry_points(group=group):
        if entry_point.name == name:
            return entry_point.load()
    raise DetectorLoadError(f"entry point not found: {group}:{name}")


def load_detectors_from_config(path: Path) -> FactorDetectorRegistry:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DetectorLoadError("config root must be a mapping")
    entries = payload.get("detectors")
    if not isinstance(entries, list):
        raise DetectorLoadError("config requires detectors list")

    registry = FactorDetectorRegistry()
    for entry in entries:
        if not isinstance(entry, dict):
            raise DetectorLoadError("each detector entry must be a mapping")
        registry.register(_instantiate(entry))
    return registry


def load_detectors_from_entry_points(
    group: str = "indiciumforge.factor_detectors",
) -> FactorDetectorRegistry:
    registry = FactorDetectorRegistry()
    for entry_point in entry_points(group=group):
        candidate = entry_point.load()
        if callable(candidate) and not isinstance(getattr(candidate, "name", None), str):
            candidate = candidate()
        registry.register(_validate_detector(candidate, f"entry_point={entry_point.name}"))
    return registry

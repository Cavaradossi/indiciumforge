from __future__ import annotations

import importlib
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any

import yaml

from indiciumforge_core.quant.pricing.ports import PricingPort
from indiciumforge_core.quant.pricing.registry import PricingRegistry


class PricerLoadError(ValueError):
    """Raised when a configured pricer cannot be imported/validated."""


def _validate_pricer(candidate: object, source: str) -> PricingPort:
    if not isinstance(getattr(candidate, "pricer_id", None), str):
        raise PricerLoadError(f"{source}: missing string pricer_id attribute")
    if not callable(getattr(candidate, "supports", None)):
        raise PricerLoadError(f"{source}: missing supports()")
    if not callable(getattr(candidate, "price", None)):
        raise PricerLoadError(f"{source}: missing price()")
    return candidate  # type: ignore[return-value]


def _import_object(module_path: str, class_name: str) -> object:
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise PricerLoadError(f"cannot import module {module_path}: {exc}") from exc
    try:
        return getattr(module, class_name)
    except AttributeError as exc:
        raise PricerLoadError(f"{module_path}.{class_name} not found") from exc


def _instantiate(entry: dict[str, Any]) -> PricingPort:
    module_path = entry.get("module")
    class_name = entry.get("class")
    if not module_path or not class_name:
        raise PricerLoadError("pricer entry requires module+class")
    candidate_cls = _import_object(str(module_path), str(class_name))
    if isinstance(candidate_cls, type):
        candidate = candidate_cls()
    else:
        candidate = candidate_cls
    return _validate_pricer(candidate, f"{module_path}.{class_name}")


def load_pricers_from_config(path: Path) -> PricingRegistry:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PricerLoadError("config root must be a mapping")
    entries = payload.get("pricers")
    if not isinstance(entries, list):
        raise PricerLoadError("config requires pricers list")
    registry = PricingRegistry()
    for entry in entries:
        if not isinstance(entry, dict):
            raise PricerLoadError("each pricer entry must be a mapping")
        registry.register(_instantiate(entry))
    return registry


def load_pricers_from_entry_points(
    group: str = "indiciumforge.pricers",
) -> PricingRegistry:
    registry = PricingRegistry()
    for entry_point in entry_points(group=group):
        candidate = entry_point.load()
        if callable(candidate) and not isinstance(getattr(candidate, "pricer_id", None), str):
            candidate = candidate()
        registry.register(_validate_pricer(candidate, f"entry_point={entry_point.name}"))
    return registry

from __future__ import annotations

import importlib
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any

import yaml

from indiciumforge_core.quant.portfolio.ports import PortfolioOptimizationPort
from indiciumforge_core.quant.portfolio.registry import PortfolioOptimizationRegistry


class PortfolioOptimizerLoadError(ValueError):
    """Raised when a configured optimizer cannot be imported/validated."""


def _validate_optimizer(candidate: object, source: str) -> PortfolioOptimizationPort:
    if not isinstance(getattr(candidate, "optimizer_id", None), str):
        raise PortfolioOptimizerLoadError(f"{source}: missing string optimizer_id attribute")
    if not callable(getattr(candidate, "supports", None)):
        raise PortfolioOptimizerLoadError(f"{source}: missing supports()")
    if not callable(getattr(candidate, "optimize", None)):
        raise PortfolioOptimizerLoadError(f"{source}: missing optimize()")
    return candidate  # type: ignore[return-value]


def _import_object(module_path: str, class_name: str) -> object:
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise PortfolioOptimizerLoadError(f"cannot import module {module_path}: {exc}") from exc
    try:
        return getattr(module, class_name)
    except AttributeError as exc:
        raise PortfolioOptimizerLoadError(f"{module_path}.{class_name} not found") from exc


def _instantiate(entry: dict[str, Any]) -> PortfolioOptimizationPort:
    module_path = entry.get("module")
    class_name = entry.get("class")
    if not module_path or not class_name:
        raise PortfolioOptimizerLoadError("optimizer entry requires module+class")
    candidate_cls = _import_object(str(module_path), str(class_name))
    if isinstance(candidate_cls, type):
        candidate = candidate_cls()
    else:
        candidate = candidate_cls
    return _validate_optimizer(candidate, f"{module_path}.{class_name}")


def load_portfolio_optimizers_from_config(path: Path) -> PortfolioOptimizationRegistry:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PortfolioOptimizerLoadError("config root must be a mapping")
    entries = payload.get("optimizers")
    if not isinstance(entries, list):
        raise PortfolioOptimizerLoadError("config requires optimizers list")
    registry = PortfolioOptimizationRegistry()
    for entry in entries:
        if not isinstance(entry, dict):
            raise PortfolioOptimizerLoadError("each optimizer entry must be a mapping")
        registry.register(_instantiate(entry))
    return registry


def load_portfolio_optimizers_from_entry_points(
    group: str = "indiciumforge.portfolio_optimizers",
) -> PortfolioOptimizationRegistry:
    registry = PortfolioOptimizationRegistry()
    for entry_point in entry_points(group=group):
        candidate = entry_point.load()
        if callable(candidate) and not isinstance(
            getattr(candidate, "optimizer_id", None), str
        ):
            candidate = candidate()
        registry.register(
            _validate_optimizer(candidate, f"entry_point={entry_point.name}")
        )
    return registry

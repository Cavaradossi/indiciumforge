from __future__ import annotations

import importlib
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any

import yaml

from indiciumforge_core.quant.backtest.ports import BacktestPort
from indiciumforge_core.quant.backtest.registry import BacktestRegistry


class BacktesterLoadError(ValueError):
    """Raised when a configured backtester cannot be imported/validated."""


def _validate_backtester(candidate: object, source: str) -> BacktestPort:
    if not isinstance(getattr(candidate, "backtester_id", None), str):
        raise BacktesterLoadError(f"{source}: missing string backtester_id attribute")
    if not callable(getattr(candidate, "supports", None)):
        raise BacktesterLoadError(f"{source}: missing supports()")
    if not callable(getattr(candidate, "run", None)):
        raise BacktesterLoadError(f"{source}: missing run()")
    return candidate  # type: ignore[return-value]


def _import_object(module_path: str, class_name: str) -> object:
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise BacktesterLoadError(f"cannot import module {module_path}: {exc}") from exc
    try:
        return getattr(module, class_name)
    except AttributeError as exc:
        raise BacktesterLoadError(f"{module_path}.{class_name} not found") from exc


def _instantiate(entry: dict[str, Any]) -> BacktestPort:
    module_path = entry.get("module")
    class_name = entry.get("class")
    if not module_path or not class_name:
        raise BacktesterLoadError("backtester entry requires module+class")
    candidate_cls = _import_object(str(module_path), str(class_name))
    if isinstance(candidate_cls, type):
        candidate = candidate_cls()
    else:
        candidate = candidate_cls
    return _validate_backtester(candidate, f"{module_path}.{class_name}")


def load_backtesters_from_config(path: Path) -> BacktestRegistry:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise BacktesterLoadError("config root must be a mapping")
    entries = payload.get("backtesters")
    if not isinstance(entries, list):
        raise BacktesterLoadError("config requires backtesters list")
    registry = BacktestRegistry()
    for entry in entries:
        if not isinstance(entry, dict):
            raise BacktesterLoadError("each backtester entry must be a mapping")
        registry.register(_instantiate(entry))
    return registry


def load_backtesters_from_entry_points(
    group: str = "indiciumforge.backtesters",
) -> BacktestRegistry:
    registry = BacktestRegistry()
    for entry_point in entry_points(group=group):
        candidate = entry_point.load()
        if callable(candidate) and not isinstance(
            getattr(candidate, "backtester_id", None), str
        ):
            candidate = candidate()
        registry.register(
            _validate_backtester(candidate, f"entry_point={entry_point.name}")
        )
    return registry

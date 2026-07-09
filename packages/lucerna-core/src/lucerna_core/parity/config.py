from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from lucerna_core.parity.models import (
    PARITY_RUN_REPORT_SCHEMA,
    ParityDimension,
    ParityRunReport,
)
from lucerna_core.parity.schemas import PARITY_LOCAL_CONFIG_SCHEMA


class ParityConfigError(ValueError):
    """Raised when a parity config document is invalid."""


@dataclass(frozen=True)
class ParityRecipeConfig:
    path: Path
    extension_pack: Path
    daily_review_fixture: Path | None = None


@dataclass(frozen=True)
class ParityLocalConfig:
    reference_artifact_root: Path
    trade_date: date
    recipe: ParityRecipeConfig
    artifact_root: Path | None
    dimensions: tuple[ParityDimension, ...]
    disclaimer: str = "research_audit_only"


def _resolve_relative_path(base: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    root = base if base.is_dir() else base.parent
    return (root / candidate).resolve()


def _parse_dimensions(values: Any) -> tuple[ParityDimension, ...]:
    if not isinstance(values, list) or not values:
        raise ParityConfigError("dimensions must be a non-empty list")
    parsed: list[ParityDimension] = []
    for item in values:
        try:
            parsed.append(ParityDimension(str(item)))
        except ValueError as exc:
            raise ParityConfigError(f"unknown parity dimension: {item}") from exc
    return tuple(parsed)


def load_parity_config(path: Path) -> ParityLocalConfig:
    if not path.is_file():
        raise ParityConfigError(f"parity config not found: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ParityConfigError("parity config root must be a mapping")
    schema = payload.get("schema")
    if schema != PARITY_LOCAL_CONFIG_SCHEMA:
        raise ParityConfigError(
            f"expected schema {PARITY_LOCAL_CONFIG_SCHEMA!r}, got {schema!r}"
        )

    reference_value = payload.get("reference_artifact_root")
    if not reference_value:
        raise ParityConfigError("reference_artifact_root is required")
    reference_root = _resolve_relative_path(path.parent, str(reference_value))

    trade_date_raw = payload.get("trade_date")
    if not trade_date_raw:
        raise ParityConfigError("trade_date is required")
    trade_date = datetime.strptime(str(trade_date_raw), "%Y-%m-%d").date()

    recipe_section = payload.get("recipe")
    if not isinstance(recipe_section, dict):
        raise ParityConfigError("recipe section must be a mapping")
    recipe_path = recipe_section.get("path")
    extension_pack = recipe_section.get("extension_pack")
    if not recipe_path or not extension_pack:
        raise ParityConfigError("recipe.path and recipe.extension_pack are required")
    daily_review_fixture = recipe_section.get("daily_review_fixture")
    recipe = ParityRecipeConfig(
        path=_resolve_relative_path(path.parent, str(recipe_path)),
        extension_pack=_resolve_relative_path(path.parent, str(extension_pack)),
        daily_review_fixture=(
            _resolve_relative_path(path.parent, str(daily_review_fixture))
            if daily_review_fixture
            else None
        ),
    )

    artifact_root_value = payload.get("artifact_root")
    artifact_root = (
        _resolve_relative_path(path.parent, str(artifact_root_value))
        if artifact_root_value
        else None
    )

    dimensions = _parse_dimensions(payload.get("dimensions"))
    disclaimer = str(payload.get("disclaimer", "research_audit_only"))
    return ParityLocalConfig(
        reference_artifact_root=reference_root,
        trade_date=trade_date,
        recipe=recipe,
        artifact_root=artifact_root,
        dimensions=dimensions,
        disclaimer=disclaimer,
    )


def write_parity_run_report(report: ParityRunReport) -> Path:
    payload = report.to_payload()
    assert payload["schema"] == PARITY_RUN_REPORT_SCHEMA
    report.report_path.parent.mkdir(parents=True, exist_ok=True)
    report.report_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )
    return report.report_path

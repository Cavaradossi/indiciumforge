from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from lucerna_core.artifacts.comparator import GATE_ARTIFACTS, load_meta
from lucerna_core.artifacts.paths import market_gate_stage_dir

MARKET_GATE_STAGE = "market_gate"

MARKET_GATE_JSON_SCHEMAS: dict[str, str] = {
    "market_gate_calibration_audit.json": (
        "indiciumgrid.workflow_market_gate_calibration_audit.v1"
    ),
    "market_gate_summary.json": "indiciumgrid.workflow_market_gate_summary.v1",
    "market_gate_state.json": "indiciumgrid.workflow.v1",
}


@dataclass(frozen=True)
class AuditViolation:
    code: str
    message: str
    path: str | None = None


@dataclass
class ArtifactManifest:
    stage: str
    stage_dir: Path
    trade_date: str | None
    required_files: tuple[str, ...]
    present_files: tuple[str, ...]
    violations: list[AuditViolation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations


@dataclass(frozen=True)
class MarketGateStageRef:
    trade_date: str
    stage_dir: Path
    present_files: tuple[str, ...]

    @property
    def core_artifact_count(self) -> int:
        return sum(1 for name in GATE_ARTIFACTS if name in self.present_files)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _normalize_trade_date(raw: Any) -> str | None:
    if raw is None:
        return None
    if isinstance(raw, date):
        return raw.isoformat()
    return str(raw)


def scan_stage_dir(stage_dir: Path) -> list[str]:
    if not stage_dir.is_dir():
        return []
    return sorted(path.name for path in stage_dir.iterdir() if path.is_file())


def list_market_gate_stages(artifact_root: Path) -> list[MarketGateStageRef]:
    workflows = artifact_root / "workflows"
    if not workflows.is_dir():
        return []

    refs: list[MarketGateStageRef] = []
    for day_dir in sorted(workflows.iterdir()):
        if not day_dir.is_dir():
            continue
        stage_dir = day_dir / MARKET_GATE_STAGE
        if not stage_dir.is_dir():
            continue
        raw = day_dir.name
        if len(raw) == 8 and raw.isdigit():
            trade_date = f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
        else:
            trade_date = raw
        refs.append(
            MarketGateStageRef(
                trade_date=trade_date,
                stage_dir=stage_dir,
                present_files=tuple(scan_stage_dir(stage_dir)),
            )
        )
    return refs


def validate_market_gate_stage(
    stage_dir: Path,
    *,
    expected_trade_date: str | None = None,
    meta_path: Path | None = None,
) -> ArtifactManifest:
    violations: list[AuditViolation] = []
    present = scan_stage_dir(stage_dir)

    if not stage_dir.is_dir():
        violations.append(
            AuditViolation("missing_stage_dir", f"stage directory not found: {stage_dir}")
        )
        return ArtifactManifest(
            stage=MARKET_GATE_STAGE,
            stage_dir=stage_dir,
            trade_date=expected_trade_date,
            required_files=GATE_ARTIFACTS,
            present_files=tuple(present),
            violations=violations,
        )

    for name in GATE_ARTIFACTS:
        path = stage_dir / name
        if not path.is_file():
            violations.append(
                AuditViolation(
                    "missing_file",
                    f"missing required artifact: {name}",
                    str(path),
                )
            )

    trade_dates: list[str] = []
    if expected_trade_date:
        trade_dates.append(expected_trade_date)

    if meta_path and meta_path.is_file():
        meta_trade_date = _normalize_trade_date(load_meta(meta_path).get("trade_date"))
        if meta_trade_date:
            trade_dates.append(meta_trade_date)

    for json_name, expected_schema in MARKET_GATE_JSON_SCHEMAS.items():
        path = stage_dir / json_name
        if not path.is_file():
            continue
        try:
            payload = _load_json(path)
        except json.JSONDecodeError as exc:
            violations.append(
                AuditViolation("invalid_json", f"{json_name}: {exc}", str(path))
            )
            continue

        actual_schema = payload.get("schema")
        if actual_schema != expected_schema:
            violations.append(
                AuditViolation(
                    "schema_mismatch",
                    (
                        f"{json_name}: expected schema {expected_schema!r}, "
                        f"got {actual_schema!r}"
                    ),
                    str(path),
                )
            )

        if json_name == "market_gate_state.json" and payload.get("stage") != MARKET_GATE_STAGE:
            violations.append(
                AuditViolation(
                    "invalid_stage",
                    (
                        f"state.stage must be {MARKET_GATE_STAGE!r}, "
                        f"got {payload.get('stage')!r}"
                    ),
                    str(path),
                )
            )

        trade_date = _normalize_trade_date(payload.get("trade_date"))
        if trade_date:
            trade_dates.append(trade_date)

    unique_dates = {value for value in trade_dates if value}
    if len(unique_dates) > 1:
        violations.append(
            AuditViolation(
                "trade_date_mismatch",
                f"inconsistent trade_date values: {sorted(unique_dates)}",
            )
        )

    resolved_trade_date = next(iter(unique_dates)) if len(unique_dates) == 1 else None

    return ArtifactManifest(
        stage=MARKET_GATE_STAGE,
        stage_dir=stage_dir,
        trade_date=resolved_trade_date or expected_trade_date,
        required_files=GATE_ARTIFACTS,
        present_files=tuple(present),
        violations=violations,
    )


def resolve_market_gate_audit_target(
    *,
    artifact_root: Path | None,
    trade_date: date | None,
    stage_dir: Path | None,
) -> tuple[Path, str | None]:
    if stage_dir is not None:
        return stage_dir, None
    if artifact_root is None or trade_date is None:
        raise ValueError("provide --stage-dir or both --artifact-root and --trade-date")
    return market_gate_stage_dir(artifact_root, trade_date), trade_date.isoformat()


def format_audit_report(manifest: ArtifactManifest) -> str:
    lines = [
        f"stage: {manifest.stage}",
        f"dir: {manifest.stage_dir}",
        f"trade_date: {manifest.trade_date or '(unknown)'}",
        f"required: {len(manifest.required_files)}",
        f"present: {len(manifest.present_files)}",
    ]
    if manifest.ok:
        lines.append("status: ok")
    else:
        lines.append("status: failed")
        for violation in manifest.violations:
            location = f" ({violation.path})" if violation.path else ""
            lines.append(f"  [{violation.code}] {violation.message}{location}")
    return "\n".join(lines)

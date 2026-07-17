from __future__ import annotations

import json
import uuid
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from indiciumforge_core.artifacts.formatting import format_code_text
from indiciumforge_core.clock import utc_now_iso
from indiciumforge_core.labels.market_gate import WORKFLOW_ZH


def write_table_bundle(
    stage_dir: Path,
    stem: str,
    csv_frame: pd.DataFrame,
    markdown: str,
    *,
    run_id: str = "default",
) -> dict[str, Path]:
    stage_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        stem: stage_dir / f"{stem}.csv",
        f"{stem}_md": stage_dir / f"{stem}.md",
        f"{stem}_txt": stage_dir / f"{stem}.txt",
    }
    try:
        csv_frame.to_csv(paths[stem], index=False, encoding="utf-8")
    except PermissionError:
        token = uuid.uuid4().hex[:8]
        fallback = stage_dir / f"{stem}_{run_id}_{token}.csv"
        csv_frame.to_csv(fallback, index=False, encoding="utf-8")
        paths[stem] = fallback
    paths[f"{stem}_md"].write_text(markdown, encoding="utf-8")
    paths[f"{stem}_txt"].write_text(markdown, encoding="utf-8")
    return paths


def base_state(
    stage: str,
    trade_date: date,
    paths: dict[str, Path],
    *,
    warnings: list[str] | None = None,
    extra: dict[str, Any] | None = None,
    run_id: str = "default",
) -> dict[str, Any]:
    state = {
        "schema": "indiciumgrid.workflow.v1",
        "stage": stage,
        "status": "completed",
        "trade_date": trade_date.isoformat(),
        "run_id": run_id,
        "updated_at": utc_now_iso(),
        "paths": {key: str(value) for key, value in paths.items()},
        "warnings": warnings or [],
        "disclaimer": WORKFLOW_ZH["disclaimer"],
    }
    if extra:
        state.update(extra)
    if state.get("empty_result_reason") and state.get("status") == "completed":
        state["status"] = "completed_with_warnings"
    return state


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def prepare_csv_bundle(frame: pd.DataFrame) -> pd.DataFrame:
    return format_code_text(frame.copy())

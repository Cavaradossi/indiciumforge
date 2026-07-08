from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from lucerna_core.artifacts.formatting import format_code_text
from lucerna_core.labels.market_gate import WORKFLOW_ZH


def write_table_bundle(
    stage_dir: Path,
    stem: str,
    csv_frame: pd.DataFrame,
    markdown: str,
) -> dict[str, Path]:
    stage_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        stem: stage_dir / f"{stem}.csv",
        f"{stem}_md": stage_dir / f"{stem}.md",
        f"{stem}_txt": stage_dir / f"{stem}.txt",
    }
    try:
        csv_frame.to_csv(paths[stem], index=False, encoding="utf-8-sig")
    except PermissionError:
        fallback = stage_dir / f"{stem}_{datetime.now().strftime('%H%M%S')}.csv"
        csv_frame.to_csv(fallback, index=False, encoding="utf-8-sig")
        paths[stem] = fallback
    paths[f"{stem}_md"].write_text(markdown, encoding="utf-8-sig")
    paths[f"{stem}_txt"].write_text(markdown, encoding="utf-8-sig")
    return paths


def base_state(
    stage: str,
    trade_date: date,
    paths: dict[str, Path],
    *,
    warnings: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    state = {
        "schema": "indiciumgrid.workflow.v1",
        "stage": stage,
        "status": "completed",
        "trade_date": trade_date.isoformat(),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
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
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8-sig")


def write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8-sig")


def prepare_csv_bundle(frame: pd.DataFrame) -> pd.DataFrame:
    return format_code_text(frame.copy())

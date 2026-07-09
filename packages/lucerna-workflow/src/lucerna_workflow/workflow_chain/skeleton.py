from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path
from typing import Any

from lucerna_core.artifacts.paths import post_close_review_dir, preopen_review_dir

POST_CLOSE_REVIEW_STATE_SCHEMA = "lucerna.post_close_review_state.v1"
PREOPEN_REVIEW_STATE_SCHEMA = "lucerna.preopen_review_state.v1"


def _write_review_state(
    path: Path,
    *,
    schema: str,
    trade_date: date,
    review_path: Path,
    fixture_path: Path,
    stage: str,
) -> Path:
    payload: dict[str, Any] = {
        "schema": schema,
        "trade_date": trade_date.isoformat(),
        "stage": stage,
        "paths": {"buy_point_review_internal": str(review_path)},
        "provenance": {
            "source": "synthetic_fixture",
            "fixture": fixture_path.name,
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8-sig")
    return path


def seed_post_close_review(
    artifact_root: Path,
    trade_date: date,
    fixture_path: Path,
) -> Path:
    stage_dir = post_close_review_dir(artifact_root, trade_date)
    stage_dir.mkdir(parents=True, exist_ok=True)
    review_path = stage_dir / "buy_point_review_internal.csv"
    shutil.copy2(fixture_path, review_path)
    _write_review_state(
        stage_dir / "post_close_review_state.json",
        schema=POST_CLOSE_REVIEW_STATE_SCHEMA,
        trade_date=trade_date,
        review_path=review_path,
        fixture_path=fixture_path,
        stage="post_close",
    )
    return review_path


def seed_preopen_review(
    artifact_root: Path,
    trade_date: date,
    fixture_path: Path,
) -> Path:
    stage_dir = preopen_review_dir(artifact_root, trade_date)
    stage_dir.mkdir(parents=True, exist_ok=True)
    review_path = stage_dir / "buy_point_review_internal.csv"
    shutil.copy2(fixture_path, review_path)
    _write_review_state(
        stage_dir / "preopen_review_state.json",
        schema=PREOPEN_REVIEW_STATE_SCHEMA,
        trade_date=trade_date,
        review_path=review_path,
        fixture_path=fixture_path,
        stage="preopen",
    )
    return review_path

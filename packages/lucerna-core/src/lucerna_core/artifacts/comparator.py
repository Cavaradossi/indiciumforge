from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from lucerna_core.labels.market_gate import REVIEW_COLUMNS
from lucerna_core.text import normalize_code_series

GATE_ARTIFACTS = (
    "market_gated_candidates.csv",
    "market_gated_observation.csv",
    "market_gated_active_watch.csv",
    "market_gated_rejected.csv",
    "market_gate_calibration_audit.json",
    "market_gate_summary.json",
    "market_gate_state.json",
)


def assert_schema_exists(actual_dir: Path, expected_dir: Path) -> None:
    for name in GATE_ARTIFACTS:
        assert (expected_dir / name).exists(), f"missing expected artifact {name}"
        if name.endswith(".json"):
            continue
        assert (actual_dir / name).exists(), f"missing actual artifact {name}"


def compare_semantic_market_gate(actual_dir: Path, expected_dir: Path) -> None:
    assert_schema_exists(actual_dir, expected_dir)
    for stem in (
        "market_gated_candidates",
        "market_gated_observation",
        "market_gated_active_watch",
        "market_gated_rejected",
    ):
        actual = pd.read_csv(actual_dir / f"{stem}.csv", encoding="utf-8-sig")
        expected = pd.read_csv(expected_dir / f"{stem}.csv", encoding="utf-8-sig")
        assert list(actual.columns) == list(expected.columns), stem
        if REVIEW_COLUMNS["code"] in actual.columns:
            assert set(normalize_code_series(actual[REVIEW_COLUMNS["code"]])) == set(
                normalize_code_series(expected[REVIEW_COLUMNS["code"]])
            ), stem
    for json_name in ("market_gate_calibration_audit.json", "market_gate_summary.json"):
        actual_payload = json.loads((actual_dir / json_name).read_text(encoding="utf-8-sig"))
        expected_payload = json.loads((expected_dir / json_name).read_text(encoding="utf-8-sig"))
        for key in (
            "strict_count",
            "observation_count",
            "watch_count",
            "rejected_count",
            "candidate_count",
            "quality_gate_warning",
        ):
            if key in expected_payload:
                assert actual_payload.get(key) == expected_payload.get(key), f"{json_name}:{key}"
    actual_state = json.loads(
        (actual_dir / "market_gate_state.json").read_text(encoding="utf-8-sig")
    )
    expected_state = json.loads(
        (expected_dir / "market_gate_state.json").read_text(encoding="utf-8-sig")
    )
    for key in (
        "workflow_review_source_stage",
        "strict_count",
        "observation_count",
        "watch_count",
        "rejected_count",
        "candidate_count",
        "quality_gate_warning",
    ):
        assert actual_state.get(key) == expected_state.get(key), f"state:{key}"
    if expected_state.get("warnings"):
        assert actual_state.get("warnings"), "state warnings missing"


def load_meta(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))

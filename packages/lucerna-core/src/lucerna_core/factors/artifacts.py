from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from lucerna_core.factors.models import FactorScanResult, FactorSignal

FACTOR_SCAN_COLUMNS: tuple[str, ...] = (
    "code",
    "factor",
    "as_of",
    "matched",
    "score",
    "metrics",
)

UNSTABLE_FIELDS: frozenset[str] = frozenset({"data_path", "updated_at"})


def signal_to_row(signal: FactorSignal) -> dict[str, Any]:
    return {
        "code": signal.asset.code,
        "factor": signal.factor,
        "as_of": signal.as_of.isoformat(),
        "matched": signal.matched,
        "score": signal.score,
        "metrics": json.dumps(signal.metrics, ensure_ascii=False, sort_keys=True),
    }


def scan_result_to_frame(result: FactorScanResult) -> pd.DataFrame:
    rows = [signal_to_row(signal) for signal in result.signals]
    if not rows:
        return pd.DataFrame(columns=list(FACTOR_SCAN_COLUMNS))
    return pd.DataFrame(rows)


def scan_result_to_payload(result: FactorScanResult) -> dict[str, Any]:
    return {
        "as_of": result.as_of.isoformat(),
        "warnings": list(result.warnings),
        "detector_runs": list(result.detector_runs),
        "signals": [
            {
                "code": signal.asset.code,
                "exchange": signal.asset.exchange.value,
                "asset_type": signal.asset.asset_type.value,
                "factor": signal.factor,
                "as_of": signal.as_of.isoformat(),
                "matched": signal.matched,
                "score": signal.score,
                "metrics": signal.metrics,
            }
            for signal in result.signals
        ],
    }


def write_factor_scan_bundle(
    stage_dir: Path,
    as_of: date,
    result: FactorScanResult,
) -> dict[str, Path]:
    stage_dir.mkdir(parents=True, exist_ok=True)
    stem = f"factor_scan_{as_of.strftime('%Y%m%d')}"
    frame = scan_result_to_frame(result)
    json_path = stage_dir / f"{stem}.json"
    csv_path = stage_dir / f"{stem}.csv"

    json_path.write_text(
        json.dumps(scan_result_to_payload(result), ensure_ascii=False, indent=2),
        encoding="utf-8-sig",
    )
    frame.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return {"json": json_path, "csv": csv_path}

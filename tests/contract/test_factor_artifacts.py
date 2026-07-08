from __future__ import annotations

from datetime import date
from pathlib import Path

from lucerna_core.domain.models import AssetID, AssetType, Exchange
from lucerna_core.factors.artifacts import (
    FACTOR_SCAN_COLUMNS,
    UNSTABLE_FIELDS,
    scan_result_to_frame,
    scan_result_to_payload,
    write_factor_scan_bundle,
)
from lucerna_core.factors.models import FactorScanResult, FactorSignal

AS_OF = date(2026, 5, 10)
ASSET = AssetID("DEMO001", Exchange.SSE, AssetType.STOCK)


def test_scan_result_frame_has_required_columns() -> None:
    result = FactorScanResult(
        as_of=AS_OF,
        signals=(
            FactorSignal(
                asset=ASSET,
                factor="demo_volume_breakout",
                as_of=AS_OF,
                matched=True,
                score=2.5,
                metrics={"volume_ratio": 2.5},
            ),
        ),
    )

    frame = scan_result_to_frame(result)

    assert list(frame.columns) == list(FACTOR_SCAN_COLUMNS)
    assert frame.iloc[0]["factor"] == "demo_volume_breakout"
    assert bool(frame.iloc[0]["matched"]) is True


def test_scan_result_payload_excludes_unstable_fields() -> None:
    result = FactorScanResult(as_of=AS_OF, signals=())

    payload = scan_result_to_payload(result)

    assert UNSTABLE_FIELDS.isdisjoint(payload.keys())
    assert payload["as_of"] == "2026-05-10"
    assert payload["signals"] == []


def test_write_factor_scan_bundle_writes_json_and_csv(tmp_path: Path) -> None:
    result = FactorScanResult(
        as_of=AS_OF,
        signals=(
            FactorSignal(
                asset=ASSET,
                factor="demo_quiet_accumulation",
                as_of=AS_OF,
                matched=True,
                score=1.0,
            ),
        ),
    )

    paths = write_factor_scan_bundle(tmp_path, AS_OF, result)

    assert paths["json"].is_file()
    assert paths["csv"].is_file()
    assert "demo_quiet_accumulation" in paths["json"].read_text(encoding="utf-8-sig")

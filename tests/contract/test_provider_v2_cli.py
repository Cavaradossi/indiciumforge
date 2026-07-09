from __future__ import annotations

import json
from pathlib import Path

from lucerna_cli.main import app
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures"
OHLCV_ROOT = FIXTURE_ROOT / "ohlcv"
PACK_PATH = FIXTURE_ROOT / "provider_pack_demo.yaml"

runner = CliRunner()


def test_provider_inspect_with_fixture_root() -> None:
    result = runner.invoke(
        app,
        ["provider", "inspect", "--ohlcv-fixture-root", str(OHLCV_ROOT)],
    )

    assert result.exit_code == 0
    assert "local_fixture" in result.stdout
    assert "ohlcv" in result.stdout


def test_provider_inspect_with_pack() -> None:
    result = runner.invoke(
        app,
        ["provider", "inspect", "--provider-pack", str(PACK_PATH)],
    )

    assert result.exit_code == 0
    assert "demo-provider-pack" in result.stdout


def test_provider_fetch_smoke() -> None:
    result = runner.invoke(
        app,
        [
            "provider",
            "fetch",
            "--trade-date",
            "2026-04-30",
            "--code",
            "600000",
            "--ohlcv-fixture-root",
            str(OHLCV_ROOT),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["rows"] == 3
    assert payload["provenance"]["provider_id"] == "local_fixture"
    assert payload["provenance"]["cycle_id"] == "2026-04-30"

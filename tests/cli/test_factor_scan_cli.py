from __future__ import annotations

from pathlib import Path

from lucerna_cli.main import app
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures"
PACK_PATH = FIXTURE_ROOT / "factor_pack_demo.yaml"
ASSET_LIST = FIXTURE_ROOT / "factor_scan_assets.yaml"
OHLCV_ROOT = FIXTURE_ROOT / "ohlcv"
DAILY_REVIEW_FIXTURE = FIXTURE_ROOT / "market_awareness" / "theme_sectors_demo.yaml"
POST_CLOSE_FIXTURE = FIXTURE_ROOT / "workflow" / "post_close_buy_point_review_demo.csv"
PREOPEN_FIXTURE = FIXTURE_ROOT / "workflow" / "preopen_buy_point_review_demo.csv"


def test_cli_factor_scan_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["factor", "scan", "--help"])

    assert result.exit_code == 0
    assert "--factor-pack" in result.stdout
    assert "--detectors-config" in result.stdout


def test_cli_factor_scan_smoke(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "factor",
            "scan",
            "--trade-date",
            "2026-05-10",
            "--artifact-root",
            str(tmp_path),
            "--ohlcv-fixture-root",
            str(OHLCV_ROOT),
            "--asset-fixture-list",
            str(ASSET_LIST),
            "--factor-pack",
            str(PACK_PATH),
        ],
    )

    assert result.exit_code == 0, result.stdout + result.stderr
    assert "factor-scan stage:" in result.stdout
    assert "factor_scan audit: ok" in result.stdout


def test_cli_workflow_chain_with_factor_flags(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "workflow",
            "chain",
            "--trade-date",
            "2026-06-23",
            "--artifact-root",
            str(tmp_path),
            "--daily-review-fixture",
            str(DAILY_REVIEW_FIXTURE),
            "--post-close-review-fixture",
            str(POST_CLOSE_FIXTURE),
            "--preopen-review-fixture",
            str(PREOPEN_FIXTURE),
            "--factor-pack",
            str(PACK_PATH),
            "--ohlcv-fixture-root",
            str(OHLCV_ROOT),
            "--asset-fixture-list",
            str(ASSET_LIST),
        ],
    )

    assert result.exit_code == 0, result.stdout + result.stderr
    assert "factor-scan stage:" in result.stdout
    assert "chain: ok" in result.stdout

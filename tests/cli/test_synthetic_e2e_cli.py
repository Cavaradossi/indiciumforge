from __future__ import annotations

from pathlib import Path

from indiciumforge_cli.main import app
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[2]
DAILY_REVIEW_FIXTURE = ROOT / "tests" / "fixtures" / "market_awareness" / "theme_sectors_demo.yaml"
PREOPEN_FIXTURE = ROOT / "tests" / "fixtures" / "workflow" / "preopen_buy_point_review_demo.csv"


def test_cli_workflow_synthetic_e2e_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["workflow", "synthetic-e2e", "--help"])

    assert result.exit_code == 0
    assert "--daily-review-fixture" in result.stdout
    assert "--preopen-review-fixture" in result.stdout


def test_cli_workflow_synthetic_e2e_smoke(tmp_path: Path) -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "workflow",
            "synthetic-e2e",
            "--trade-date",
            "2026-06-23",
            "--artifact-root",
            str(tmp_path),
            "--daily-review-fixture",
            str(DAILY_REVIEW_FIXTURE),
            "--preopen-review-fixture",
            str(PREOPEN_FIXTURE),
        ],
    )

    assert result.exit_code == 0, result.stdout + result.stderr
    assert "daily-review stage:" in result.stdout
    assert "market-gate stage:" in result.stdout
    assert "audit: ok" in result.stdout
    assert "summary:" in result.stdout

    summary_path = tmp_path / "workflows" / "20260623" / "synthetic_e2e_summary.json"
    assert summary_path.is_file()


def test_cli_workflow_synthetic_e2e_missing_fixture(tmp_path: Path) -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "workflow",
            "synthetic-e2e",
            "--trade-date",
            "2026-06-23",
            "--artifact-root",
            str(tmp_path),
            "--daily-review-fixture",
            str(tmp_path / "missing.yaml"),
            "--preopen-review-fixture",
            str(PREOPEN_FIXTURE),
        ],
    )

    assert result.exit_code == 2
    assert "daily-review fixture" in result.stderr

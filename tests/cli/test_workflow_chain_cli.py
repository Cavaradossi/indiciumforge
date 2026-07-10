from __future__ import annotations

from pathlib import Path

from indiciumforge_cli.main import app
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures"
DAILY_REVIEW_FIXTURE = FIXTURE_ROOT / "market_awareness" / "theme_sectors_demo.yaml"
POST_CLOSE_FIXTURE = FIXTURE_ROOT / "workflow" / "post_close_buy_point_review_demo.csv"
PREOPEN_FIXTURE = FIXTURE_ROOT / "workflow" / "preopen_buy_point_review_demo.csv"


def test_cli_workflow_chain_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["workflow", "chain", "--help"])

    assert result.exit_code == 0
    assert "--post-close-review-fixture" in result.stdout
    assert "--preopen-review-fixture" in result.stdout


def test_cli_workflow_chain_smoke(tmp_path: Path) -> None:
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
        ],
    )

    assert result.exit_code == 0, result.stdout + result.stderr
    assert "post-close stage:" in result.stdout
    assert "preopen stage:" in result.stdout
    assert "market-gate stage:" in result.stdout
    assert "chain: ok" in result.stdout
    assert "summary:" in result.stdout

    summary_path = tmp_path / "workflows" / "20260623" / "workflow_chain_summary.json"
    assert summary_path.is_file()

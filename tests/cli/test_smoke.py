from __future__ import annotations

import shutil
from pathlib import Path

from lucerna_cli.main import app
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[2]
SCENARIO = ROOT / "tests" / "golden" / "market_gate" / "strict_pass_mixed"


def _copy_scenario_inputs(artifact_root: Path) -> None:
    inputs = SCENARIO / "inputs"
    for rel in inputs.rglob("*"):
        if rel.is_file():
            target = artifact_root / rel.relative_to(inputs)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(rel, target)


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Lucerna reference CLI" in result.stdout


def test_cli_workflow_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["workflow", "--help"])

    assert result.exit_code == 0
    assert "market-gate" in result.stdout


def test_cli_workflow_market_gate_smoke(tmp_path: Path) -> None:
    runner = CliRunner()
    _copy_scenario_inputs(tmp_path)

    result = runner.invoke(
        app,
        [
            "workflow",
            "market-gate",
            "--trade-date",
            "2026-06-23",
            "--artifact-root",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.stdout + result.stderr
    assert "Wrote market-gate artifacts" in result.stdout

    stage_dirs = list(tmp_path.glob("**/market_gate"))
    assert stage_dirs
    stage_dir = stage_dirs[0]
    for name in (
        "market_gate_summary.json",
        "market_gated_candidates.csv",
        "market_gate_state.json",
    ):
        assert (stage_dir / name).is_file()


def test_cli_rejects_invalid_trade_date(tmp_path: Path) -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "workflow",
            "market-gate",
            "--trade-date",
            "not-a-date",
            "--artifact-root",
            str(tmp_path),
        ],
    )

    assert result.exit_code != 0

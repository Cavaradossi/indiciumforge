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
    assert "daily-review" in result.stdout


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


def test_cli_artifact_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["artifact", "--help"])

    assert result.exit_code == 0
    assert "audit" in result.stdout
    assert "list" in result.stdout


def test_cli_artifact_audit_golden_expected() -> None:
    runner = CliRunner()
    stage_dir = SCENARIO / "expected" / "market_gate"
    meta_path = SCENARIO / "expected" / "meta.json"

    result = runner.invoke(
        app,
        [
            "artifact",
            "audit",
            "--stage-dir",
            str(stage_dir),
            "--meta-path",
            str(meta_path),
        ],
    )

    assert result.exit_code == 0, result.stdout + result.stderr
    assert "status: ok" in result.stdout


def test_cli_artifact_list_after_market_gate(tmp_path: Path) -> None:
    runner = CliRunner()
    _copy_scenario_inputs(tmp_path)

    run_result = runner.invoke(
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
    assert run_result.exit_code == 0

    list_result = runner.invoke(
        app,
        [
            "artifact",
            "list",
            "--artifact-root",
            str(tmp_path),
        ],
    )

    assert list_result.exit_code == 0, list_result.stdout + list_result.stderr
    assert "market_gate" in list_result.stdout
    assert "2026-06-23" in list_result.stdout


def test_cli_artifact_audit_stage_dir_checks_trade_date() -> None:
    runner = CliRunner()
    stage_dir = SCENARIO / "expected" / "market_gate"

    result = runner.invoke(
        app,
        [
            "artifact",
            "audit",
            "--stage-dir",
            str(stage_dir),
            "--trade-date",
            "2026-06-24",
        ],
    )

    assert result.exit_code == 1
    assert "trade_date_mismatch" in result.stdout


DEMO_FIXTURE = ROOT / "tests" / "fixtures" / "market_awareness" / "theme_sectors_demo.yaml"


def test_cli_workflow_daily_review_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["workflow", "daily-review", "--help"])

    assert result.exit_code == 0
    assert "--fixture-path" in result.stdout


def test_cli_workflow_daily_review_smoke(tmp_path: Path) -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "workflow",
            "daily-review",
            "--trade-date",
            "2026-06-23",
            "--artifact-root",
            str(tmp_path),
            "--fixture-path",
            str(DEMO_FIXTURE),
        ],
    )

    assert result.exit_code == 0, result.stdout + result.stderr
    assert "Wrote daily-review artifacts" in result.stdout
    stage_dir = tmp_path / "market_awareness" / "20260623" / "daily_review"
    assert (stage_dir / "theme_state_ranking.csv").is_file()
    assert (stage_dir / "market_daily_review_state.json").is_file()


def test_cli_artifact_audit_daily_review_after_run(tmp_path: Path) -> None:
    runner = CliRunner()

    run_result = runner.invoke(
        app,
        [
            "workflow",
            "daily-review",
            "--trade-date",
            "2026-06-23",
            "--artifact-root",
            str(tmp_path),
            "--fixture-path",
            str(DEMO_FIXTURE),
        ],
    )
    assert run_result.exit_code == 0

    audit_result = runner.invoke(
        app,
        [
            "artifact",
            "audit",
            "--artifact-root",
            str(tmp_path),
            "--trade-date",
            "2026-06-23",
            "--stage-type",
            "daily_review",
        ],
    )

    assert audit_result.exit_code == 0, audit_result.stdout + audit_result.stderr
    assert "status: ok" in audit_result.stdout
    assert "stage: daily_review" in audit_result.stdout


def test_cli_artifact_list_includes_daily_review(tmp_path: Path) -> None:
    runner = CliRunner()

    run_result = runner.invoke(
        app,
        [
            "workflow",
            "daily-review",
            "--trade-date",
            "2026-06-23",
            "--artifact-root",
            str(tmp_path),
            "--fixture-path",
            str(DEMO_FIXTURE),
        ],
    )
    assert run_result.exit_code == 0

    list_result = runner.invoke(
        app,
        [
            "artifact",
            "list",
            "--artifact-root",
            str(tmp_path),
        ],
    )

    assert list_result.exit_code == 0, list_result.stdout + list_result.stderr
    assert "daily_review" in list_result.stdout
    assert "2026-06-23" in list_result.stdout

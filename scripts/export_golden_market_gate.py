"""Export market-gate golden fixtures from frozen IndiciumGrid reference."""

from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path

import pandas as pd
from indiciumgrid.market_awareness import DAILY as MARKET_DAILY
from indiciumgrid.market_awareness import ZH as MARKET_ZH
from indiciumgrid.workflow import REVIEW_COLUMNS, run_market_gate_workflow

ROOT = Path(__file__).resolve().parents[1]
GOLDEN_ROOT = ROOT / "tests" / "golden" / "market_gate"


def _write_inputs(
    scenario_dir: Path,
    *,
    trade_date: date,
    theme_rows: list[dict],
    review_path: Path,
    review_rows: list[dict],
) -> None:
    day = trade_date.strftime("%Y%m%d")
    theme_dir = scenario_dir / "inputs" / "market_awareness" / day / "daily_review"
    theme_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(theme_rows).to_csv(
        theme_dir / "theme_state_ranking.csv", index=False, encoding="utf-8-sig"
    )
    review_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(review_rows).to_csv(review_path, index=False, encoding="utf-8-sig")


def _copy_outputs(tmp_root: Path, trade_date: date, expected_dir: Path) -> None:
    day = trade_date.strftime("%Y%m%d")
    source = tmp_root / "workflows" / day / "market_gate"
    if expected_dir.exists():
        shutil.rmtree(expected_dir)
    shutil.copytree(source, expected_dir)


def export_strict_pass_mixed(work_dir: Path) -> None:
    trade_date = date(2026, 6, 23)
    day = trade_date.strftime("%Y%m%d")
    review_path = (
        work_dir / "inputs" / "workflows" / day / "preopen" / "buy_point_review_internal.csv"
    )
    _write_inputs(
        work_dir,
        trade_date=trade_date,
        theme_rows=[
            {
                MARKET_ZH["theme_name"]: "强方向",
                MARKET_DAILY["status"]: MARKET_DAILY["daily_strong"],
                MARKET_DAILY["daily_state"]: MARKET_DAILY["daily_strong"],
                MARKET_DAILY["mid_state"]: MARKET_ZH["neutral_theme"],
                MARKET_DAILY["risk_state"]: MARKET_DAILY["normal_risk"],
                MARKET_DAILY["divergence_state"]: MARKET_DAILY["normal_divergence"],
            },
            {
                MARKET_ZH["theme_name"]: "硬弱方向",
                MARKET_DAILY["status"]: MARKET_DAILY["hard_weak"],
                MARKET_DAILY["daily_state"]: MARKET_DAILY["daily_weak"],
                MARKET_DAILY["mid_state"]: MARKET_ZH["neutral_theme"],
                MARKET_DAILY["risk_state"]: MARKET_DAILY["hard_weak"],
                MARKET_DAILY["divergence_state"]: MARKET_DAILY["normal_divergence"],
            },
            {
                MARKET_ZH["theme_name"]: "转弱方向",
                MARKET_DAILY["status"]: MARKET_DAILY["mid_strong_daily_weak"],
                MARKET_DAILY["daily_state"]: MARKET_DAILY["daily_weak"],
                MARKET_DAILY["mid_state"]: MARKET_DAILY["mid_strong"],
                MARKET_DAILY["risk_state"]: MARKET_DAILY["normal_risk"],
                MARKET_DAILY["divergence_state"]: MARKET_DAILY["normal_divergence"],
            },
        ],
        review_path=review_path,
        review_rows=[
            {
                REVIEW_COLUMNS["rating"]: "A-可重点复核",
                REVIEW_COLUMNS["code"]: "000001",
                REVIEW_COLUMNS["stock_name"]: "干净候选",
                REVIEW_COLUMNS["board_info"]: "强方向",
                REVIEW_COLUMNS["strong_boards_hit"]: "强方向",
                REVIEW_COLUMNS["weak_boards_hit"]: "",
                REVIEW_COLUMNS["holding_period"]: "波段观察",
                REVIEW_COLUMNS["narrative_stage"]: "主线扩散",
                REVIEW_COLUMNS["thesis_risk"]: "暂无",
                REVIEW_COLUMNS["trigger_count"]: "0项",
                REVIEW_COLUMNS["accounting_risk_overview"]: "未见明显风险",
            },
            {
                REVIEW_COLUMNS["rating"]: "A-可重点复核",
                REVIEW_COLUMNS["code"]: "000002",
                REVIEW_COLUMNS["stock_name"]: "硬弱候选",
                REVIEW_COLUMNS["board_info"]: "硬弱方向",
                REVIEW_COLUMNS["strong_boards_hit"]: "",
                REVIEW_COLUMNS["weak_boards_hit"]: "硬弱方向",
                REVIEW_COLUMNS["holding_period"]: "波段观察",
                REVIEW_COLUMNS["narrative_stage"]: "主线扩散",
                REVIEW_COLUMNS["thesis_risk"]: "暂无",
                REVIEW_COLUMNS["trigger_count"]: "0项",
                REVIEW_COLUMNS["accounting_risk_overview"]: "未见明显风险",
            },
            {
                REVIEW_COLUMNS["rating"]: "A-可重点复核",
                REVIEW_COLUMNS["code"]: "000003",
                REVIEW_COLUMNS["stock_name"]: "修复观察",
                REVIEW_COLUMNS["board_info"]: "转弱方向",
                REVIEW_COLUMNS["strong_boards_hit"]: "",
                REVIEW_COLUMNS["weak_boards_hit"]: "",
                REVIEW_COLUMNS["holding_period"]: "波段观察",
                REVIEW_COLUMNS["narrative_stage"]: "主线扩散",
                REVIEW_COLUMNS["thesis_risk"]: "暂无",
                REVIEW_COLUMNS["trigger_count"]: "0项",
                REVIEW_COLUMNS["accounting_risk_overview"]: "未见明显风险",
            },
            {
                REVIEW_COLUMNS["rating"]: "A-可重点复核",
                REVIEW_COLUMNS["code"]: "000004",
                REVIEW_COLUMNS["stock_name"]: "仅复盘",
                REVIEW_COLUMNS["board_info"]: "强方向",
                REVIEW_COLUMNS["strong_boards_hit"]: "强方向",
                REVIEW_COLUMNS["weak_boards_hit"]: "",
                REVIEW_COLUMNS["holding_period"]: "仅复盘",
                REVIEW_COLUMNS["narrative_stage"]: "主线扩散",
                REVIEW_COLUMNS["thesis_risk"]: "暂无",
                REVIEW_COLUMNS["trigger_count"]: "0项",
                REVIEW_COLUMNS["accounting_risk_overview"]: "未见明显风险",
            },
            {
                REVIEW_COLUMNS["rating"]: "A-可重点复核",
                REVIEW_COLUMNS["code"]: "000005",
                REVIEW_COLUMNS["stock_name"]: "风险观察",
                REVIEW_COLUMNS["board_info"]: "强方向",
                REVIEW_COLUMNS["strong_boards_hit"]: "强方向",
                REVIEW_COLUMNS["weak_boards_hit"]: "",
                REVIEW_COLUMNS["holding_period"]: "波段观察",
                REVIEW_COLUMNS["narrative_stage"]: "主线扩散",
                REVIEW_COLUMNS["thesis_risk"]: "暂无",
                REVIEW_COLUMNS["trigger_count"]: "1项",
                REVIEW_COLUMNS["accounting_risk_overview"]: "触发1项",
            },
        ],
    )
    tmp = work_dir / "_run"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    for rel in work_dir.glob("inputs/**/*"):
        if rel.is_file():
            target = tmp / rel.relative_to(work_dir / "inputs")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(rel, target)
    run_market_gate_workflow(trade_date=trade_date, output_dir=tmp)
    _copy_outputs(tmp, trade_date, work_dir / "expected" / "market_gate")
    meta = {
        "trade_date": trade_date.isoformat(),
        "workflow_review_source_stage": "preopen",
        "warnings": [],
    }
    (work_dir / "expected" / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def export_empty_strict_c_grade(work_dir: Path) -> None:
    trade_date = date(2026, 6, 24)
    day = trade_date.strftime("%Y%m%d")
    review_path = (
        work_dir / "inputs" / "workflows" / day / "preopen" / "buy_point_review_internal.csv"
    )
    _write_inputs(
        work_dir,
        trade_date=trade_date,
        theme_rows=[
            {
                MARKET_ZH["theme_name"]: "强方向",
                MARKET_DAILY["status"]: MARKET_DAILY["daily_strong"],
                MARKET_DAILY["daily_state"]: MARKET_DAILY["daily_strong"],
                MARKET_DAILY["mid_state"]: MARKET_ZH["neutral_theme"],
                MARKET_DAILY["risk_state"]: MARKET_DAILY["normal_risk"],
                MARKET_DAILY["divergence_state"]: MARKET_DAILY["normal_divergence"],
            },
        ],
        review_path=review_path,
        review_rows=[
            {
                REVIEW_COLUMNS["rating"]: "C-历史样本/行情可能后段",
                REVIEW_COLUMNS["code"]: "000006",
                REVIEW_COLUMNS["stock_name"]: "强势C",
                REVIEW_COLUMNS["board_info"]: "强方向",
                REVIEW_COLUMNS["strong_boards_hit"]: "强方向",
                REVIEW_COLUMNS["weak_boards_hit"]: "",
                REVIEW_COLUMNS["holding_period"]: "仅复盘",
                REVIEW_COLUMNS["narrative_stage"]: "主线扩散",
                REVIEW_COLUMNS["thesis_risk"]: "暂无",
                REVIEW_COLUMNS["short_level"]: "高",
                REVIEW_COLUMNS["priority_bucket"]: "重点盯盘",
                REVIEW_COLUMNS["mainline_strength"]: "strong_short_pulse",
                REVIEW_COLUMNS["pattern_confidence"]: "高",
                REVIEW_COLUMNS["trigger_count"]: "0项",
                REVIEW_COLUMNS["accounting_risk_overview"]: "未见明显风险",
            },
        ],
    )
    tmp = work_dir / "_run"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    for rel in work_dir.glob("inputs/**/*"):
        if rel.is_file():
            target = tmp / rel.relative_to(work_dir / "inputs")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(rel, target)
    run_market_gate_workflow(trade_date=trade_date, output_dir=tmp)
    _copy_outputs(tmp, trade_date, work_dir / "expected" / "market_gate")
    meta = {
        "trade_date": trade_date.isoformat(),
        "workflow_review_source_stage": "preopen",
        "warnings": [],
    }
    (work_dir / "expected" / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def export_fallback_post_close(work_dir: Path) -> None:
    trade_date = date(2026, 6, 23)
    day = trade_date.strftime("%Y%m%d")
    review_path = (
        work_dir / "inputs" / "workflows" / day / "post_close" / "buy_point_review_internal.csv"
    )
    _write_inputs(
        work_dir,
        trade_date=trade_date,
        theme_rows=[
            {
                MARKET_ZH["theme_name"]: "强方向",
                MARKET_DAILY["status"]: MARKET_DAILY["daily_strong"],
                MARKET_DAILY["daily_state"]: MARKET_DAILY["daily_strong"],
                MARKET_DAILY["mid_state"]: MARKET_ZH["neutral_theme"],
                MARKET_DAILY["risk_state"]: MARKET_DAILY["normal_risk"],
                MARKET_DAILY["divergence_state"]: MARKET_DAILY["normal_divergence"],
            }
        ],
        review_path=review_path,
        review_rows=[
            {
                REVIEW_COLUMNS["rating"]: "A-可重点复核",
                REVIEW_COLUMNS["code"]: "000001",
                REVIEW_COLUMNS["stock_name"]: "盘后候选",
                REVIEW_COLUMNS["board_info"]: "强方向",
                REVIEW_COLUMNS["strong_boards_hit"]: "强方向",
                REVIEW_COLUMNS["weak_boards_hit"]: "",
                REVIEW_COLUMNS["holding_period"]: "波段观察",
                REVIEW_COLUMNS["narrative_stage"]: "主线扩散",
                REVIEW_COLUMNS["thesis_risk"]: "暂无",
                REVIEW_COLUMNS["trigger_count"]: "0项",
                REVIEW_COLUMNS["accounting_risk_overview"]: "未见明显风险",
            }
        ],
    )
    tmp = work_dir / "_run"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    for rel in work_dir.glob("inputs/**/*"):
        if rel.is_file():
            target = tmp / rel.relative_to(work_dir / "inputs")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(rel, target)
    result = run_market_gate_workflow(trade_date=trade_date, output_dir=tmp)
    _copy_outputs(tmp, trade_date, work_dir / "expected" / "market_gate")
    meta = {
        "trade_date": trade_date.isoformat(),
        "workflow_review_source_stage": "post_close",
        "warnings": result.warnings,
    }
    (work_dir / "expected" / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def export_missing_theme_fail(work_dir: Path) -> None:
    trade_date = date(2026, 6, 25)
    day = trade_date.strftime("%Y%m%d")
    review_path = (
        work_dir / "inputs" / "workflows" / day / "preopen" / "buy_point_review_internal.csv"
    )
    review_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                REVIEW_COLUMNS["rating"]: "A-可重点复核",
                REVIEW_COLUMNS["code"]: "000001",
                REVIEW_COLUMNS["stock_name"]: "无主题",
                REVIEW_COLUMNS["board_info"]: "强方向",
                REVIEW_COLUMNS["strong_boards_hit"]: "强方向",
                REVIEW_COLUMNS["weak_boards_hit"]: "",
                REVIEW_COLUMNS["holding_period"]: "波段观察",
                REVIEW_COLUMNS["narrative_stage"]: "主线扩散",
                REVIEW_COLUMNS["thesis_risk"]: "暂无",
                REVIEW_COLUMNS["trigger_count"]: "0项",
                REVIEW_COLUMNS["accounting_risk_overview"]: "未见明显风险",
            }
        ]
    ).to_csv(review_path, index=False, encoding="utf-8-sig")
    meta = {"trade_date": trade_date.isoformat(), "expects": "FileNotFoundError"}
    expected_dir = work_dir / "expected"
    expected_dir.mkdir(parents=True, exist_ok=True)
    (expected_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def export_catalyst_ignored(work_dir: Path) -> None:
    """Catalyst file present must not change strict gate output."""
    export_strict_pass_mixed(work_dir)
    catalyst = work_dir / "inputs" / "research" / "catalyst_review.json"
    catalyst.parent.mkdir(parents=True, exist_ok=True)
    catalyst.write_text(
        json.dumps({"hypothesis": "KOL mention", "codes": ["000099"]}, ensure_ascii=False),
        encoding="utf-8",
    )
    meta_path = work_dir / "expected" / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["catalyst_file"] = str(catalyst.relative_to(work_dir / "inputs"))
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    exporters = {
        "strict_pass_mixed": export_strict_pass_mixed,
        "empty_strict_c_grade": export_empty_strict_c_grade,
        "fallback_post_close": export_fallback_post_close,
        "missing_theme_fail": export_missing_theme_fail,
        "catalyst_ignored": export_catalyst_ignored,
    }
    for scenario_id, exporter in exporters.items():
        scenario_dir = GOLDEN_ROOT / scenario_id
        if scenario_dir.exists():
            shutil.rmtree(scenario_dir)
        scenario_dir.mkdir(parents=True)
        exporter(scenario_dir)
        print(f"exported {scenario_id}")


if __name__ == "__main__":
    main()

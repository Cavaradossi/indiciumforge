from __future__ import annotations

import pandas as pd
from indiciumforge_core.labels.market_gate import REVIEW_COLUMNS
from indiciumforge_core.text import clean_text, u


def trigger_count_value(value: object) -> int:
    text = str(value or "")
    digits = ""
    for char in text:
        if char.isdigit():
            digits += char
        elif digits:
            break
    return int(digits) if digits else 0


def split_candidate_boards(value: str) -> list[str]:
    out: list[str] = []
    for raw in str(value or "").replace(",", ";").split(";"):
        item = raw.strip()
        if not item or item.startswith(("TDX:", "X:")):
            continue
        if item not in out:
            out.append(item)
    return out


def candidate_gate_boards(row: pd.Series) -> list[str]:
    boards: list[str] = []
    for column in (
        REVIEW_COLUMNS["board_info"],
        REVIEW_COLUMNS["strong_boards_hit"],
        REVIEW_COLUMNS["weak_boards_hit"],
    ):
        boards.extend(split_candidate_boards(str(row.get(column) or "")))
    return list(dict.fromkeys(boards))


def theme_state_lookup(
    theme_state_ranking: pd.DataFrame,
    *,
    theme_name_key: str,
    daily_keys: dict[str, str],
) -> dict[str, dict[str, str]]:
    if theme_state_ranking.empty or theme_name_key not in theme_state_ranking.columns:
        return {}
    lookup: dict[str, dict[str, str]] = {}
    for _, row in theme_state_ranking.iterrows():
        name = str(row.get(theme_name_key) or "").strip()
        if not name:
            continue
        lookup[name] = {
            "status": clean_text(row.get(daily_keys["status"])),
            "daily_state": clean_text(row.get(daily_keys["daily_state"])),
            "mid_state": clean_text(row.get(daily_keys["mid_state"])),
            "risk_state": clean_text(row.get(daily_keys["risk_state"])),
            "divergence_state": clean_text(row.get(daily_keys["divergence_state"])),
        }
    return lookup


def market_gate_workflow_rejects(row: pd.Series) -> list[str]:
    rejects: list[str] = []
    stock_name = clean_text(row.get(REVIEW_COLUMNS["stock_name"]))
    if "ST" in stock_name.upper() or u("\\u9000") in stock_name:
        rejects.append(u("\\u98ce\\u9669\\u8bc1\\u5238"))
    if clean_text(row.get(REVIEW_COLUMNS["holding_period"])) == u("\\u4ec5\\u590d\\u76d8"):
        rejects.append(u("\\u6301\\u6709\\u5468\\u671f\\u5206\\u5c42=\\u4ec5\\u590d\\u76d8"))
    if clean_text(row.get(REVIEW_COLUMNS["narrative_stage"])) == u("\\u540e\\u6bb5\\u62e5\\u6324"):
        rejects.append(u("\\u4e3b\\u7ebf\\u9636\\u6bb5=\\u540e\\u6bb5\\u62e5\\u6324"))
    return rejects


def market_gate_workflow_risks(row: pd.Series) -> list[str]:
    risks: list[str] = []
    thesis_risk = clean_text(row.get(REVIEW_COLUMNS["thesis_risk"]))
    if thesis_risk and thesis_risk != u("\\u6682\\u65e0"):
        risks.append(f"{REVIEW_COLUMNS['thesis_risk']}={thesis_risk}")
    trigger_count = clean_text(row.get(REVIEW_COLUMNS["trigger_count"]))
    accounting_overview = clean_text(row.get(REVIEW_COLUMNS["accounting_risk_overview"]))
    if trigger_count == u("\\u6570\\u636e\\u4e0d\\u8db3"):
        risks.append(u("\\u4f1a\\u8ba1\\u6570\\u636e\\u4e0d\\u8db3"))
    elif trigger_count_value(trigger_count) > 0:
        risks.append(f"{REVIEW_COLUMNS['trigger_count']}={trigger_count}")
    if accounting_overview and accounting_overview not in {
        u("\\u672a\\u89c1\\u660e\\u663e\\u98ce\\u9669"),
        u("\\u4e0d\\u9002\\u7528"),
    }:
        risks.append(f"{REVIEW_COLUMNS['accounting_risk_overview']}={accounting_overview}")
    return risks

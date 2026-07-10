from __future__ import annotations

import pandas as pd
from indiciumforge_core.labels.market_gate import (
    GATE_RESULT_OBSERVATION,
    GATE_RESULT_REJECTED,
    GATE_RESULT_STRICT,
    MARKET_DAILY,
    MARKET_GATE_COLUMNS,
    MARKET_ZH,
    REVIEW_COLUMNS,
)
from indiciumforge_core.text import clean_text, join_unique, u

from indiciumforge_workflow.market_gate.active_watch import market_gate_active_watch
from indiciumforge_workflow.market_gate.helpers import (
    candidate_gate_boards,
    market_gate_workflow_rejects,
    market_gate_workflow_risks,
    theme_state_lookup,
)


def apply_market_gate(review: pd.DataFrame, theme_state_ranking: pd.DataFrame) -> pd.DataFrame:
    if review.empty:
        out = review.copy()
        for column in MARKET_GATE_COLUMNS.values():
            out[column] = ""
        return out
    theme_lookup = theme_state_lookup(
        theme_state_ranking,
        theme_name_key=MARKET_ZH["theme_name"],
        daily_keys=MARKET_DAILY,
    )
    out = review.copy()
    rows = [_market_gate_row(row, theme_lookup) for _, row in out.iterrows()]
    for key, column in MARKET_GATE_COLUMNS.items():
        out[column] = [item[key] for item in rows]
    order = {
        GATE_RESULT_STRICT: 0,
        GATE_RESULT_OBSERVATION: 1,
        GATE_RESULT_REJECTED: 2,
    }
    out["_market_gate_order"] = out[MARKET_GATE_COLUMNS["gate_result"]].map(order).fillna(9)
    sort_columns = ["_market_gate_order"]
    if REVIEW_COLUMNS["rating"] in out.columns:
        sort_columns.append(REVIEW_COLUMNS["rating"])
    return out.sort_values(sort_columns, ascending=True).drop(columns=["_market_gate_order"])


def _market_gate_row(row: pd.Series, themes: dict[str, dict[str, str]]) -> dict[str, str]:
    boards = candidate_gate_boards(row)
    matched = [(board, themes[board]) for board in boards if board in themes]
    allowed_statuses = {
        MARKET_DAILY["daily_strong"],
        MARKET_DAILY["persistent"],
        MARKET_DAILY["short_pulse"],
    }
    strong = [
        board
        for board, info in matched
        if info["status"] in allowed_statuses
        and info["risk_state"] != MARKET_DAILY["hard_weak"]
        and info["divergence_state"] != MARKET_DAILY["divergent"]
    ]
    hard_weak = [
        board
        for board, info in matched
        if info["risk_state"] == MARKET_DAILY["hard_weak"]
        or info["status"] == MARKET_DAILY["hard_weak"]
    ]
    turning_weak = [
        board
        for board, info in matched
        if info["status"] == MARKET_DAILY["mid_strong_daily_weak"]
    ]
    divergent = [
        board
        for board, info in matched
        if info["divergence_state"] == MARKET_DAILY["divergent"]
        or info["status"] == MARKET_DAILY["divergent"]
    ]
    workflow_rejects = market_gate_workflow_rejects(row)
    workflow_risks = market_gate_workflow_risks(row)
    reasons: list[str] = []
    observe_reasons: list[str] = []
    if not matched:
        reasons.append(u("\\u672a\\u547d\\u4e2d\\u76d8\\u9762\\u65e5\\u62a5\\u65b9\\u5411"))
    if hard_weak:
        reasons.append(f"{MARKET_DAILY['hard_weak']}={join_unique(hard_weak)}")
    if workflow_rejects:
        reasons.extend(workflow_rejects)
    if turning_weak:
        observe_reasons.append(
            f"{MARKET_DAILY['mid_strong_daily_weak']}={join_unique(turning_weak)}"
        )
    if divergent:
        observe_reasons.append(f"{MARKET_DAILY['divergent']}={join_unique(divergent)}")
    if workflow_risks:
        observe_reasons.extend(workflow_risks)
    if reasons:
        gate_result = GATE_RESULT_REJECTED
    elif strong and not observe_reasons:
        gate_result = GATE_RESULT_STRICT
    elif strong or observe_reasons:
        gate_result = GATE_RESULT_OBSERVATION
    else:
        gate_result = GATE_RESULT_REJECTED
        reasons.append(u("\\u672a\\u547d\\u4e2d\\u53ef\\u4e25\\u683c\\u901a\\u8fc7\\u65b9\\u5411"))
    active = market_gate_active_watch(row, gate_result, strong, observe_reasons, reasons)
    return {
        "gate_result": gate_result,
        "active_watch_level": active["level"],
        "active_watch_reason": active["reason"],
        "active_watch_action": active["action"],
        "matched_themes": join_unique([board for board, _ in matched]),
        "theme_status": join_unique(
            [f"{board}={info['status']}" for board, info in matched if info["status"]]
        ),
        "daily_state": join_unique(
            [f"{board}={info['daily_state']}" for board, info in matched if info["daily_state"]]
        ),
        "mid_state": join_unique(
            [f"{board}={info['mid_state']}" for board, info in matched if info["mid_state"]]
        ),
        "risk_state": join_unique(
            [f"{board}={info['risk_state']}" for board, info in matched if info["risk_state"]]
        ),
        "divergence_state": join_unique(
            [
                f"{board}={info['divergence_state']}"
                for board, info in matched
                if info["divergence_state"]
            ]
        ),
        "reject_reason": join_unique(reasons),
        "observe_reason": join_unique(observe_reasons),
        "workflow_layer": clean_text(row.get(REVIEW_COLUMNS["holding_period"])),
    }


def split_market_gate_frames(
    gated: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    strict = gated[gated[MARKET_GATE_COLUMNS["gate_result"]].eq(GATE_RESULT_STRICT)].copy()
    observation = gated[
        gated[MARKET_GATE_COLUMNS["gate_result"]].eq(GATE_RESULT_OBSERVATION)
    ].copy()
    rejected = gated[gated[MARKET_GATE_COLUMNS["gate_result"]].eq(GATE_RESULT_REJECTED)].copy()
    active_watch = market_gate_active_watch_frame(gated)
    return strict, observation, rejected, active_watch


def market_gate_active_watch_frame(gated: pd.DataFrame) -> pd.DataFrame:
    if gated.empty or MARKET_GATE_COLUMNS["active_watch_level"] not in gated.columns:
        return gated.head(0).copy()
    active = gated[
        gated[MARKET_GATE_COLUMNS["active_watch_level"]].astype(str).str.strip().ne("")
        & ~gated[MARKET_GATE_COLUMNS["gate_result"]].eq(GATE_RESULT_STRICT)
    ].copy()
    order = {
        u("\\u53ef\\u4e3b\\u52a8\\u590d\\u6838"): 0,
        u("\\u9057\\u6f0f\\u5ba1\\u8ba1"): 1,
        u("\\u9ad8\\u6f6e\\u4e0d\\u8ffd"): 2,
        u("\\u4ec5\\u89c2\\u5bdf"): 3,
    }
    active["_active_watch_order"] = (
        active[MARKET_GATE_COLUMNS["active_watch_level"]].map(order).fillna(9)
    )
    sort_columns = ["_active_watch_order"]
    if REVIEW_COLUMNS["rating"] in active.columns:
        sort_columns.append(REVIEW_COLUMNS["rating"])
    return active.sort_values(sort_columns).drop(columns=["_active_watch_order"])

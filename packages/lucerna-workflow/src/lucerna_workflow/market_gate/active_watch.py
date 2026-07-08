from __future__ import annotations

import pandas as pd
from lucerna_core.labels.market_gate import (
    GATE_RESULT_OBSERVATION,
    GATE_RESULT_STRICT,
    MARKET_DAILY,
    REVIEW_COLUMNS,
    WORKFLOW_ZH,
)
from lucerna_core.text import clean_text, join_unique, u


def market_gate_active_watch(
    row: pd.Series,
    gate_result: str,
    strong: list[str],
    observe_reasons: list[str],
    reject_reasons: list[str],
) -> dict[str, str]:
    if gate_result == GATE_RESULT_STRICT:
        return {"level": u("\\u4e25\\u683c\\u6267\\u884c\\u95e8"), "reason": "", "action": ""}

    stock_name = clean_text(row.get(REVIEW_COLUMNS["stock_name"]))
    if "ST" in stock_name.upper() or u("\\u9000") in stock_name:
        return {"level": "", "reason": "", "action": ""}

    rating = clean_text(row.get(REVIEW_COLUMNS["rating"]))
    short_level = clean_text(row.get(REVIEW_COLUMNS["short_level"]))
    priority = clean_text(row.get(REVIEW_COLUMNS["priority_bucket"]))
    mainline_strength = clean_text(row.get(REVIEW_COLUMNS["mainline_strength"]))
    pattern_confidence = clean_text(row.get(REVIEW_COLUMNS["pattern_confidence"]))
    narrative_stage = clean_text(row.get(REVIEW_COLUMNS["narrative_stage"]))
    holding_period = clean_text(row.get(REVIEW_COLUMNS["holding_period"]))
    reasons: list[str] = []

    if strong:
        resonance_label = u("\\u76d8\\u9762\\u5171\\u632f")
        reasons.append(f"{resonance_label}={join_unique(strong)}")
    if observe_reasons:
        reasons.extend(observe_reasons)
    if short_level == WORKFLOW_ZH["short_high"]:
        reasons.append(f"{REVIEW_COLUMNS['short_level']}={short_level}")
    if priority in {u("\\u91cd\\u70b9\\u76ef\\u76d8"), u("\\u89c2\\u5bdf\\u8ddf\\u8e2a")}:
        reasons.append(f"{REVIEW_COLUMNS['priority_bucket']}={priority}")
    if mainline_strength in {"strong_persistent", "strong_short_pulse"}:
        reasons.append(f"{REVIEW_COLUMNS['mainline_strength']}={mainline_strength}")
    if pattern_confidence in {u("\\u9ad8"), "high"}:
        reasons.append(f"{REVIEW_COLUMNS['pattern_confidence']}={pattern_confidence}")
    if rating.startswith("C-") and (
        strong
        or short_level == WORKFLOW_ZH["short_high"]
        or mainline_strength in {"strong_persistent", "strong_short_pulse"}
    ):
        reasons.append(u("C\\u7ea7\\u4f46\\u5177\\u5907\\u5f3a\\u52bf/\\u627f\\u63a5\\u7ebf\\u7d22"))

    hard_reject = any(
        token in join_unique(reject_reasons)
        for token in (
            u("\\u98ce\\u9669\\u8bc1\\u5238"),
            MARKET_DAILY["hard_weak"],
        )
    )
    if hard_reject or not reasons:
        return {"level": "", "reason": "", "action": ""}

    if gate_result == GATE_RESULT_OBSERVATION:
        level = u("\\u53ef\\u4e3b\\u52a8\\u590d\\u6838")
        action = u(
            "\\u89c2\\u5bdf\\u627f\\u63a5\\u4e0e\\u56de\\u8e29\\uff0c"
            "\\u4e0d\\u89c6\\u4e3a\\u4e25\\u683c\\u4e70\\u70b9"
        )
    elif rating.startswith("C-") or holding_period == u("\\u4ec5\\u590d\\u76d8"):
        level = u("\\u9057\\u6f0f\\u5ba1\\u8ba1")
        action = u(
            "\\u8ddf\\u8e2a\\u662f\\u5426\\u89c4\\u5219\\u8fc7\\u4e25\\uff0c"
            "\\u4e0d\\u8fdb\\u5165\\u6267\\u884c\\u95e8"
        )
    elif narrative_stage == u("\\u540e\\u6bb5\\u62e5\\u6324"):
        level = u("\\u9ad8\\u6f6e\\u4e0d\\u8ffd")
        action = u("\\u53ea\\u770b\\u98ce\\u9669\\u4e0e\\u9000\\u6f6e")
    else:
        level = u("\\u4ec5\\u89c2\\u5bdf")
        action = u("\\u4fdd\\u7559\\u89c2\\u5bdf\\uff0c\\u7b49\\u66f4\\u5f3a\\u8bc1\\u636e")
    return {"level": level, "reason": join_unique(reasons), "action": action}

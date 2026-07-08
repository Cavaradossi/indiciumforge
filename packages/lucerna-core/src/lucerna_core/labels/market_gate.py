from __future__ import annotations

from lucerna_core.text import u

REVIEW_COLUMNS = {
    "rating": u("\\u5019\\u9009\\u7b49\\u7ea7"),
    "code": u("\\u4ee3\\u7801"),
    "stock_name": u("\\u80a1\\u7968\\u540d\\u79f0"),
    "board_info": u("\\u677f\\u5757\\u4fe1\\u606f"),
    "strong_boards_hit": u("\\u5f3a\\u52bf\\u677f\\u5757\\u547d\\u4e2d"),
    "weak_boards_hit": u("\\u5f31\\u52bf\\u677f\\u5757\\u547d\\u4e2d"),
    "holding_period": u("\\u6301\\u6709\\u5468\\u671f\\u5206\\u5c42"),
    "narrative_stage": u("\\u4e3b\\u7ebf\\u9636\\u6bb5"),
    "thesis_risk": u("\\u4e3b\\u903b\\u8f91\\u98ce\\u9669"),
    "trigger_count": u("\\u89e6\\u53d1\\u9879\\u6570"),
    "accounting_risk_overview": u("\\u4f1a\\u8ba1\\u98ce\\u9669\\u6982\\u89c8"),
    "short_level": u("\\u77ed\\u7ebf\\u89c2\\u5bdf\\u7b49\\u7ea7"),
    "priority_bucket": u("\\u76ef\\u76d8\\u5206\\u5c42"),
    "mainline_strength": u("\\u4e3b\\u7ebf\\u5f3a\\u5ea6"),
    "pattern_confidence": u("\\u5f62\\u6001\\u53ef\\u4fe1\\u5ea6"),
}

MARKET_GATE_COLUMNS = {
    "gate_result": u("\\u76d8\\u9762\\u95e8\\u63a7\\u7ed3\\u8bba"),
    "active_watch_level": u("\\u4e3b\\u52a8\\u89c2\\u5bdf\\u7ea7\\u522b"),
    "active_watch_reason": u("\\u4e3b\\u52a8\\u89c2\\u5bdf\\u539f\\u56e0"),
    "active_watch_action": u("\\u4e3b\\u52a8\\u89c2\\u5bdf\\u52a8\\u4f5c"),
    "matched_themes": u("\\u547d\\u4e2d\\u65b9\\u5411"),
    "theme_status": u("\\u65b9\\u5411\\u72b6\\u6001"),
    "daily_state": u("\\u5f53\\u65e5\\u5f3a\\u5f31"),
    "mid_state": u("\\u4e2d\\u671f\\u8d8b\\u52bf"),
    "risk_state": u("\\u65b9\\u5411\\u98ce\\u9669\\u72b6\\u6001"),
    "divergence_state": u("\\u5206\\u5316\\u72b6\\u6001"),
    "reject_reason": u("\\u5254\\u9664\\u539f\\u56e0"),
    "observe_reason": u("\\u89c2\\u5bdf\\u539f\\u56e0"),
    "workflow_layer": u("workflow\\u539f\\u59cb\\u5206\\u5c42"),
}

WORKFLOW_ZH = {
    "short_high": u("\\u9ad8"),
    "disclaimer": u(
        "\\u672c\\u62a5\\u544a\\u4ec5\\u7528\\u4e8e\\u7814\\u7a76\\u590d\\u6838\\uff0c"
        "\\u4e0d\\u662f\\u5b9e\\u76d8\\u4e70\\u5165\\u6307\\u4ee4\\u3002"
    ),
}

MARKET_ZH = {
    "theme_name": u("\\u65b9\\u5411\\u540d\\u79f0"),
    "neutral_theme": u("\\u4e2d\\u6027"),
}

MARKET_DAILY = {
    "status": u("\\u65b9\\u5411\\u72b6\\u6001"),
    "daily_state": u("\\u5f53\\u65e5\\u5f3a\\u5f31"),
    "mid_state": u("\\u4e2d\\u671f\\u8d8b\\u52bf"),
    "risk_state": u("\\u65b9\\u5411\\u98ce\\u9669\\u72b6\\u6001"),
    "divergence_state": u("\\u5206\\u5316\\u72b6\\u6001"),
    "daily_strong": u("\\u5f53\\u65e5\\u5f3a"),
    "daily_weak": u("\\u5f53\\u65e5\\u5f31"),
    "hard_weak": u("\\u786c\\u5f31\\u52bf"),
    "mid_strong": u("\\u4e2d\\u671f\\u5f3a"),
    "mid_strong_daily_weak": u("\\u4e2d\\u671f\\u5f3a\\u4f46\\u5f53\\u65e5\\u8f6c\\u5f31"),
    "divergent": u("\\u5185\\u90e8\\u5206\\u5316"),
    "normal_divergence": u("\\u672a\\u89c1\\u660e\\u663e\\u5206\\u5316"),
    "normal_risk": u("\\u672a\\u89c1\\u660e\\u663e\\u98ce\\u9669"),
    "short_pulse": u("\\u77ed\\u7ebf\\u8109\\u51b2"),
    "persistent": u("\\u6301\\u7eed\\u5f3a\\u52bf"),
}

GATE_RESULT_STRICT = u("\\u4e25\\u683c\\u901a\\u8fc7")
GATE_RESULT_OBSERVATION = u("\\u4ec5\\u89c2\\u5bdf")
GATE_RESULT_REJECTED = u("\\u5254\\u9664")

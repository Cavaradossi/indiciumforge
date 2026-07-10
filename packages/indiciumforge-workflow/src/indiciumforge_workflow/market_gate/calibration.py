from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd
from indiciumforge_core.labels.market_gate import MARKET_GATE_COLUMNS, REVIEW_COLUMNS
from indiciumforge_core.text import u


def market_gate_calibration_audit(
    gated: pd.DataFrame,
    *,
    strict: pd.DataFrame,
    observation: pd.DataFrame,
    rejected: pd.DataFrame,
    active_watch: pd.DataFrame,
    trade_date: date,
) -> dict[str, Any]:
    watch_columns = [
        REVIEW_COLUMNS["code"],
        REVIEW_COLUMNS["stock_name"],
        REVIEW_COLUMNS["rating"],
        MARKET_GATE_COLUMNS["gate_result"],
        MARKET_GATE_COLUMNS["active_watch_level"],
        MARKET_GATE_COLUMNS["active_watch_reason"],
        MARKET_GATE_COLUMNS["reject_reason"],
        MARKET_GATE_COLUMNS["observe_reason"],
    ]
    available = [column for column in watch_columns if column in active_watch.columns]
    top_missed = active_watch[available].head(30).to_dict(orient="records") if available else []
    warning = ""
    if len(gated) > 0 and len(strict) == 0:
        warning = u(
            "\\u4e25\\u683c\\u6267\\u884c\\u95e8\\u4e3a0\\uff1a\\u4e0d\\u4ee3\\u8868"
            "\\u5e02\\u573a\\u6ca1\\u6709\\u673a\\u4f1a\\uff0c\\u9700\\u540c\\u65f6\\u67e5\\u770b"
            "\\u4e3b\\u52a8\\u89c2\\u5bdf\\u548c\\u9057\\u6f0f\\u5ba1\\u8ba1"
        )
    elif len(strict) <= max(1, int(len(gated) * 0.002)) and len(gated) >= 200:
        warning = u(
            "\\u4e25\\u683c\\u6267\\u884c\\u95e8\\u547d\\u4e2d\\u7387\\u6781\\u4f4e\\uff1a"
            "\\u9700\\u5b9a\\u671f\\u6821\\u51c6\\u89c4\\u5219\\u662f\\u5426\\u8fc7\\u4e25"
        )
    return {
        "schema": "indiciumgrid.workflow_market_gate_calibration_audit.v1",
        "trade_date": trade_date.isoformat(),
        "candidate_count": int(len(gated)),
        "strict_count": int(len(strict)),
        "observation_count": int(len(observation)),
        "watch_count": int(len(active_watch)),
        "rejected_count": int(len(rejected)),
        "quality_gate_warning": warning,
        "outcome_status": u("\\u5f85\\u540e\\u7eed\\u6536\\u76d8\\u6570\\u636e\\u56de\\u586b"),
        "future_metrics": {
            "d1_return": None,
            "d2_return": None,
            "max_drawdown": None,
            "missed_strong_move": None,
        },
        "top_missed_candidates": top_missed,
        "notes": [
            u(
                "\\u672c\\u5ba1\\u8ba1\\u4e0d\\u653e\\u677emarket-gate\\u4e25\\u683c\\u6267\\u884c\\u95e8"
            ),
            u(
                "\\u8d22\\u52a1\\u7ea2\\u65d7\\u662f\\u89c2\\u5bdf\\u98ce\\u9669\\u4e0a\\u4e0b\\u6587\\uff0c"
                "\\u4e0d\\u662f\\u4e3b\\u52a8\\u89c2\\u5bdf\\u5c42\\u7684\\u4e00\\u7968\\u5426\\u51b3"
            ),
            u(
                "C\\u7ea7\\u5019\\u9009\\u9700\\u533a\\u5206\\u5f62\\u6001\\u8d70\\u574f\\u4e0e"
                "\\u89c4\\u5219\\u672a\\u8986\\u76d6\\u7684\\u5f3a\\u52bf\\u6837\\u672c"
            ),
        ],
    }

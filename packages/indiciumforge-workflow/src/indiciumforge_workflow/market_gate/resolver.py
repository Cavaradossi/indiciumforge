from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from indiciumforge_core.artifacts.paths import workflow_root
from indiciumforge_core.text import u


@dataclass(frozen=True)
class ReviewResolution:
    path: Path
    source_stage: str
    warning: str


def resolve_market_gate_review_path(artifact_root: Path, trade_date: date) -> ReviewResolution:
    root = workflow_root(artifact_root, trade_date)
    candidates = [
        ("preopen", root / "preopen" / "buy_point_review_internal.csv", ""),
        (
            "preopen",
            root / "preopen" / "buy_point_review.csv",
            u(
                "\\u672a\\u627e\\u5230preopen internal\\u5019\\u9009\\u8868\\uff0c"
                "\\u5df2\\u56de\\u9000\\u8bfb\\u53d6preopen\\u516c\\u5f00\\u8868"
            ),
        ),
        (
            "post_close",
            root / "post_close" / "buy_point_review_internal.csv",
            u(
                "\\u672a\\u627e\\u5230preopen\\u5019\\u9009\\u8868\\uff0c"
                "\\u5df2\\u56de\\u9000\\u8bfb\\u53d6post_close internal\\u5019\\u9009\\u8868"
            ),
        ),
        (
            "post_close",
            root / "post_close" / "buy_point_review.csv",
            u(
                "\\u672a\\u627e\\u5230preopen\\u5019\\u9009\\u8868\\uff0c"
                "\\u5df2\\u56de\\u9000\\u8bfb\\u53d6post_close\\u516c\\u5f00\\u8868"
            ),
        ),
    ]
    for stage, path, warning in candidates:
        if path.exists():
            return ReviewResolution(path=path, source_stage=stage, warning=warning)
    searched = ", ".join(str(path) for _, path, _ in candidates)
    raise FileNotFoundError(f"missing workflow review for market-gate: {searched}")

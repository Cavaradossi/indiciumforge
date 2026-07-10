from __future__ import annotations

from datetime import date
from pathlib import Path

from indiciumforge_core.artifacts.paths import (
    daily_review_dir,
    market_gate_stage_dir,
    post_close_review_dir,
    preopen_review_dir,
)


class ReferenceArtifactProvider:
    """Resolve IG-shaped reference artifact paths under a configured local root."""

    def __init__(self, reference_root: Path) -> None:
        if not reference_root.is_dir():
            raise FileNotFoundError(f"reference artifact root not found: {reference_root}")
        self._reference_root = reference_root

    @property
    def reference_root(self) -> Path:
        return self._reference_root

    def _day_token(self, trade_date: date) -> str:
        return trade_date.strftime("%Y%m%d")

    def daily_review_dir(self, trade_date: date) -> Path:
        return (
            self._reference_root
            / "market_awareness"
            / self._day_token(trade_date)
            / "daily_review"
        )

    def post_close_dir(self, trade_date: date) -> Path:
        return self._reference_root / "workflows" / self._day_token(trade_date) / "post_close"

    def preopen_dir(self, trade_date: date) -> Path:
        return self._reference_root / "workflows" / self._day_token(trade_date) / "preopen"

    def market_gate_dir(self, trade_date: date) -> Path:
        return self._reference_root / "workflows" / self._day_token(trade_date) / "market_gate"


def actual_stage_dirs(artifact_root: Path, trade_date: date) -> dict[str, Path]:
    return {
        "daily_review": daily_review_dir(artifact_root, trade_date),
        "post_close": post_close_review_dir(artifact_root, trade_date),
        "preopen": preopen_review_dir(artifact_root, trade_date),
        "market_gate": market_gate_stage_dir(artifact_root, trade_date),
    }

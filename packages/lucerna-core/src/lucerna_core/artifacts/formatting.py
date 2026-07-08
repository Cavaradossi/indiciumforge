from __future__ import annotations

import pandas as pd

from lucerna_core.labels.market_gate import REVIEW_COLUMNS


def format_code_text(frame: pd.DataFrame) -> pd.DataFrame:
    column = REVIEW_COLUMNS["code"]
    if column not in frame.columns:
        return frame

    def _format(value: object) -> str:
        text = str(value).strip()
        if text.startswith('="') and text.endswith('"'):
            return text
        return f'="{text.zfill(6)}"'

    out = frame.copy()
    out[column] = out[column].map(_format)
    return out

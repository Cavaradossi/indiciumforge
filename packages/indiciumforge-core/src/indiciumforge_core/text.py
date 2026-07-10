from __future__ import annotations

import pandas as pd


def u(value: str) -> str:
    return value.encode("ascii").decode("unicode_escape")


def clean_text(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def join_unique(values: list[str]) -> str:
    out: list[str] = []
    for value in values:
        if value and value not in out:
            out.append(value)
    return ";".join(out)


def normalize_code_series(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace('="', "", regex=False)
        .str.replace('"', "", regex=False)
        .str.zfill(6)
    )

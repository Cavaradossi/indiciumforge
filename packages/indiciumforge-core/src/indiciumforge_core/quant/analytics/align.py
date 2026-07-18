from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from indiciumforge_core.domain.models import AssetID
from indiciumforge_core.factors.models import FactorScanResult, FactorSignal


def _uid_of(asset: AssetID | str) -> str:
    if isinstance(asset, AssetID):
        return asset.uid
    return str(asset)


def factor_panel_from_signals(
    signals: Iterable[FactorSignal],
    *,
    value_key: str = "score",
) -> pd.DataFrame:
    """Build a long-format factor panel from :class:`FactorSignal` objects.

    Returns a DataFrame with columns ``date``, ``asset_uid``, ``factor_value``
    suitable for :class:`FactorEvaluationRequest.factor_panel`. Signals whose
    requested value is ``None`` are skipped.
    """
    rows: list[dict[str, object]] = []
    for sig in signals:
        value = sig.score if value_key == "score" else sig.metrics.get(value_key)
        if value is None:
            continue
        rows.append(
            {
                "date": sig.as_of,
                "asset_uid": _uid_of(sig.asset),
                "factor_value": float(value),
            }
        )
    return pd.DataFrame(rows, columns=["date", "asset_uid", "factor_value"])


def factor_panel_from_scan(
    scan: FactorScanResult,
    *,
    value_key: str = "score",
) -> pd.DataFrame:
    """Convenience wrapper that flattens a :class:`FactorScanResult`."""
    return factor_panel_from_signals(scan.signals, value_key=value_key)

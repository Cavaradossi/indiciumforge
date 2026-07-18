from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class FactorEvaluationRequest:
    """Inputs for a factor analytics evaluation.

    ``factor_panel`` is a long frame with columns ``date``, ``asset_uid``,
    ``factor_value``. ``returns_panel`` is a long frame with columns ``date``,
    ``asset_uid``, ``ret`` where ``ret`` is the single-period simple return;
    the engine derives forward returns at each requested ``horizon`` internally
    so IC-decay can be swept without the caller pre-computing every horizon.
    """

    factor_panel: pd.DataFrame
    returns_panel: pd.DataFrame
    factor_name: str = "factor"
    horizons: tuple[int, ...] = (1, 5, 10)
    min_cross_section: int = 5
    as_of: date | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "factor_name": self.factor_name,
            "horizons": list(self.horizons),
            "min_cross_section": self.min_cross_section,
            "as_of": self.as_of.isoformat() if self.as_of is not None else None,
            "n_factor_rows": int(len(self.factor_panel)),
            "n_return_rows": int(len(self.returns_panel)),
        }


@dataclass(frozen=True)
class ICStat:
    horizon: int
    ic_mean: float
    ic_std: float
    ir: float
    ic_t_stat: float
    positive_pct: float
    n_dates: int

    def to_payload(self) -> dict[str, Any]:
        return {
            "horizon": self.horizon,
            "ic_mean": self.ic_mean,
            "ic_std": self.ic_std,
            "ir": self.ir,
            "ic_t_stat": self.ic_t_stat,
            "positive_pct": self.positive_pct,
            "n_dates": self.n_dates,
        }


@dataclass(frozen=True)
class FactorReturnStat:
    """Fama-MacBeth cross-sectional factor-return statistics.

    ``slope_series`` holds the per-date slope ``lambda_t`` (the return earned
    per unit of factor exposure) before temporal aggregation.
    """

    mean: float
    t_stat: float
    n_dates: int
    slope_series: tuple[float, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        return {
            "mean": self.mean,
            "t_stat": self.t_stat,
            "n_dates": self.n_dates,
            "n_slopes": len(self.slope_series),
        }


@dataclass(frozen=True)
class TurnoverStat:
    """Rank-weight day-to-day turnover proxy, bounded in ``[0, 2]``."""

    turnover: float
    method: str = "rank_weight_abs_change"

    def to_payload(self) -> dict[str, Any]:
        return {"turnover": self.turnover, "method": self.method}


@dataclass(frozen=True)
class FactorEvaluationResult:
    engine_id: str
    factor_name: str
    ic_by_horizon: tuple[ICStat, ...]
    factor_returns: FactorReturnStat
    turnover: TurnoverStat
    warnings: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        return {
            "engine_id": self.engine_id,
            "factor_name": self.factor_name,
            "ic_by_horizon": [s.to_payload() for s in self.ic_by_horizon],
            "factor_returns": self.factor_returns.to_payload(),
            "turnover": self.turnover.to_payload(),
            "warnings": list(self.warnings),
        }

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class PortfolioOptimizationRequest:
    """Inputs for a single-period portfolio optimization.

    ``expected_returns`` is a Series indexed by ``asset_uid``; ``covariance`` is
    a square DataFrame over the same ``asset_uid`` index. ``sector_caps`` is a
    sequence of ``(member_uids, cap)`` pairs constraining the summed weight of
    each group.
    """

    expected_returns: pd.Series
    covariance: pd.DataFrame
    objective: str = "mean_variance"  # "mean_variance" | "min_variance"
    risk_aversion: float = 1.0
    long_only: bool = True
    weight_bounds: tuple[float, float] = (0.0, 1.0)
    sector_caps: tuple[tuple[list[str], float], ...] = ()
    sum_to_one: bool = True
    as_of: date | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "objective": self.objective,
            "risk_aversion": self.risk_aversion,
            "long_only": self.long_only,
            "weight_bounds": list(self.weight_bounds),
            "n_assets": int(len(self.expected_returns)),
            "n_sector_caps": len(self.sector_caps),
            "as_of": self.as_of.isoformat() if self.as_of is not None else None,
        }


@dataclass(frozen=True)
class PortfolioOptimizationResult:
    optimizer_id: str
    weights: pd.Series
    expected_return: float
    expected_risk: float
    sharpe: float
    objective_value: float
    solver_status: str
    warnings: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        payload = {
            "optimizer_id": self.optimizer_id,
            "expected_return": self.expected_return,
            "expected_risk": self.expected_risk,
            "sharpe": self.sharpe,
            "objective_value": self.objective_value,
            "solver_status": self.solver_status,
            "n_assets": int(len(self.weights)),
            "warnings": list(self.warnings),
        }
        # Keep the (potentially large) weight vector out of the default payload.
        return payload

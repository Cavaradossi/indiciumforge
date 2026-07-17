from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from indiciumforge_core.quant.portfolio.models import (
    PortfolioOptimizationRequest,
    PortfolioOptimizationResult,
)


def _require_cvxpy() -> Any:
    try:
        import cvxpy as cp  # noqa: F401
    except ImportError as exc:  # pragma: no cover - exercised via missing extra
        raise ImportError(
            "The portfolio optimizer requires the 'portfolio' extra: "
            "pip install 'indiciumforge-core[portfolio]'"
        ) from exc
    return cp


class CvxpyOptimizer:
    """Markowitz mean-variance / min-variance optimizer backed by cvxpy.

    Solves, over weights ``w``:

    * ``mean_variance``:  maximize  ``lambda * mu^T w - w^T Sigma w``
    * ``min_variance``:   minimize  ``w^T Sigma w``

    subject to ``sum(w) == 1`` (when ``sum_to_one``), long-only / weight bounds,
    and optional per-group caps ``sum(w[members]) <= cap``. ``Sigma`` is
    symmetrized defensively; a non-optimal solve is reported via ``warnings``
    rather than raising, so callers can fall back or log.
    """

    optimizer_id = "cvxpy"

    def supports(self, request: PortfolioOptimizationRequest) -> bool:
        return request.objective in ("mean_variance", "min_variance")

    def optimize(self, request: PortfolioOptimizationRequest) -> PortfolioOptimizationResult:
        cp = _require_cvxpy()

        assets = [str(a) for a in request.expected_returns.index]
        n = len(assets)
        mu = np.asarray(request.expected_returns.to_numpy(dtype=float), dtype=float)
        cov = request.covariance.reindex(index=assets, columns=assets).to_numpy(dtype=float)
        # Defensive symmetrization; quad_form expects a symmetric matrix.
        sigma = 0.5 * (cov + cov.T)

        warnings: list[str] = []
        w = cp.Variable(n)

        constraints: list[Any] = []
        lb, ub = request.weight_bounds
        if request.long_only and lb < 0:
            lb = 0.0
            warnings.append("weight_bounds lower clamped to 0 for long_only")
        constraints.append(w >= lb)
        constraints.append(w <= ub)
        if request.sum_to_one:
            constraints.append(cp.sum(w) == 1)

        for members, cap in request.sector_caps:
            if not members:
                continue
            idx = [assets.index(str(u)) for u in members if str(u) in assets]
            if idx:
                constraints.append(cp.sum(w[idx]) <= float(cap))

        if request.objective == "min_variance":
            objective = cp.Minimize(cp.quad_form(w, sigma))
        else:
            lam = float(request.risk_aversion)
            objective = cp.Maximize(lam * mu @ w - cp.quad_form(w, sigma))

        try:
            prob = cp.Problem(objective, constraints)
            prob.solve()
        except Exception as exc:  # noqa: BLE001 - surface as warning, not crash
            warnings.append(f"solver error: {exc}")
            return PortfolioOptimizationResult(
                optimizer_id=self.optimizer_id,
                weights=pd.Series(0.0, index=assets),
                expected_return=0.0,
                expected_risk=0.0,
                sharpe=0.0,
                objective_value=0.0,
                solver_status="error",
                warnings=tuple(warnings),
            )

        status = prob.status
        if status not in ("optimal", "optimal_inaccurate"):
            warnings.append(f"solver status {status!r} (not optimal)")

        wv = np.asarray(w.value, dtype=float) if w.value is not None else np.zeros(n)
        weights = pd.Series(wv, index=assets)
        expected_return = float(mu @ wv)
        variance = float(wv @ sigma @ wv)
        expected_risk = float(np.sqrt(max(variance, 0.0)))
        sharpe = expected_return / expected_risk if expected_risk > 0 else 0.0
        objective_value = float(prob.value) if prob.value is not None else 0.0

        return PortfolioOptimizationResult(
            optimizer_id=self.optimizer_id,
            weights=weights,
            expected_return=expected_return,
            expected_risk=expected_risk,
            sharpe=sharpe,
            objective_value=objective_value,
            solver_status=status,
            warnings=tuple(warnings),
        )


# Structural subtype registration (mirrors providers/contracts_v2.py).
from indiciumforge_core.quant.portfolio.ports import PortfolioOptimizationPort  # noqa: E402

PortfolioOptimizationPort.register(CvxpyOptimizer)

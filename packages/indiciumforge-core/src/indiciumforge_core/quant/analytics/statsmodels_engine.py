from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from indiciumforge_core.quant.analytics.models import (
    FactorEvaluationRequest,
    FactorEvaluationResult,
    FactorReturnStat,
    ICStat,
    TurnoverStat,
)


def _require_analytics() -> Any:
    """Import the optional ``[analytics]`` dependencies, or raise helpfully."""
    try:
        import scipy  # noqa: F401
        import statsmodels.api as sm  # noqa: F401
    except ImportError as exc:  # pragma: no cover - exercised via missing extra
        raise ImportError(
            "The analytics engine requires the 'analytics' extra: "
            "pip install 'indiciumforge-core[analytics]'"
        ) from exc
    return sm


def _as_date(series: pd.Series) -> pd.Series:
    if pd.api.types.is_datetime64_any_dtype(series):
        return series.dt.date
    return pd.to_datetime(series).dt.date


def _forward_return_wide(returns_wide: pd.DataFrame, horizon: int) -> pd.DataFrame:
    """Cumulative simple return over the next ``horizon`` single periods.

    ``returns_wide`` is indexed by date with one column per asset. We shift the
    surface back by one period so row ``t`` carries the *next* period's return,
    then roll a window of size ``horizon`` — giving the forward cumulative
    return starting the day after ``t``. The trailing ``horizon - 1`` rows are
    left as ``NaN`` (incomplete future) and dropped downstream.
    """
    if horizon <= 0:
        raise ValueError("horizon must be a positive integer")

    def _cumprod_minus_1(x: np.ndarray) -> float:
        return float(np.prod(1.0 + x) - 1.0)

    future = returns_wide.shift(-1)
    return future.rolling(horizon, min_periods=horizon).apply(_cumprod_minus_1, raw=True)


def _long_forward(returns_wide: pd.DataFrame, horizon: int) -> pd.DataFrame:
    fwd = _forward_return_wide(returns_wide, horizon)
    return fwd.stack().rename("fwd").reset_index()


class StatsmodelsFactorEngine:
    """Factor analytics engine backed by scipy + statsmodels.

    Computes, per requested horizon:

    * **IC** — mean cross-sectional Spearman rank correlation between the factor
      values and the forward return, with std / information-ratio / t-stat and
      the share of positive-IC cross-sections.
    * **Fama-MacBeth factor return** — per-date cross-sectional OLS of the
      one-period forward return on the factor value; the slope ``lambda_t`` is
      aggregated to a mean and t-stat.
    * **Turnover** — day-to-day change in rank-weighted exposures (bounded in
      ``[0, 2]``).

    Cross-sections smaller than ``min_cross_section`` or with degenerate
    (zero-variance) factor/return series are skipped with a warning rather than
    crashing the evaluation.
    """

    engine_id = "statsmodels"

    def supports(self, request: FactorEvaluationRequest) -> bool:
        return bool(request.horizons) and len(request.factor_panel) > 0

    def evaluate(self, request: FactorEvaluationRequest) -> FactorEvaluationResult:
        _require_analytics()
        from scipy import stats as scipy_stats
        import statsmodels.api as sm

        warnings: list[str] = []
        factor_name = request.factor_name
        min_cs = request.min_cross_section

        fp = request.factor_panel.copy()
        rp = request.returns_panel.copy()
        fp["_date"] = _as_date(fp["date"])
        rp["_date"] = _as_date(rp["date"])

        ret_wide = rp.pivot(index="_date", columns="asset_uid", values="ret").sort_index()

        ic_by_horizon: list[ICStat] = []
        for h in request.horizons:
            merged = fp.merge(
                _long_forward(ret_wide, h),
                on=["_date", "asset_uid"],
                how="inner",
            )
            ic_per_date: list[float] = []
            for d, grp in merged.groupby("_date"):
                if len(grp) < min_cs:
                    warnings.append(f"horizon {h}: {d} skipped (n={len(grp)}<{min_cs})")
                    continue
                fv = grp["factor_value"].to_numpy(dtype=float)
                fw = grp["fwd"].to_numpy(dtype=float)
                if np.allclose(fv, fv[0]) or np.allclose(fw, fw[0]):
                    warnings.append(f"horizon {h}: {d} skipped (zero variance)")
                    continue
                rho, _ = scipy_stats.spearmanr(fv, fw)
                if np.isnan(rho):
                    continue
                ic_per_date.append(float(rho))

            if ic_per_date:
                arr = np.asarray(ic_per_date, dtype=float)
                ic_mean = float(arr.mean())
                ic_std = float(arr.std(ddof=1)) if arr.size > 1 else 0.0
                ir = ic_mean / ic_std if ic_std > 0 else 0.0
                t = ic_mean / (ic_std / np.sqrt(arr.size)) if ic_std > 0 else 0.0
                pos = float((arr > 0).mean())
            else:
                ic_mean = ic_std = ir = t = pos = 0.0
                warnings.append(f"horizon {h}: no valid cross-sections")
            ic_by_horizon.append(
                ICStat(
                    horizon=h,
                    ic_mean=ic_mean,
                    ic_std=ic_std,
                    ir=ir,
                    ic_t_stat=t,
                    positive_pct=pos,
                    n_dates=len(ic_per_date),
                )
            )

        # Fama-MacBeth: per-date cross-sectional OLS fwd ~ factor_value.
        fmb_slopes: list[float] = []
        merged_fmb = fp.merge(
            _long_forward(ret_wide, 1),
            on=["_date", "asset_uid"],
            how="inner",
        )
        for d, grp in merged_fmb.groupby("_date"):
            if len(grp) < min_cs:
                continue
            x = grp["factor_value"].to_numpy(dtype=float)
            y = grp["fwd"].to_numpy(dtype=float)
            if np.allclose(x, x[0]) or np.allclose(y, y[0]):
                continue
            model = sm.OLS(y, sm.add_constant(x)).fit()
            fmb_slopes.append(float(model.params[1]))

        if fmb_slopes:
            sarr = np.asarray(fmb_slopes, dtype=float)
            sarr = sarr[np.isfinite(sarr)]  # drop any non-finite slope (singular X'X)
            if sarr.size > 0:
                s_mean = float(sarr.mean())
                s_std = float(sarr.std(ddof=1)) if sarr.size > 1 else 0.0
                s_t = s_mean / (s_std / np.sqrt(sarr.size)) if s_std > 0 else 0.0
            else:
                s_mean = s_t = 0.0
                warnings.append("fama_macbeth: all slopes non-finite")
        else:
            s_mean = s_t = 0.0
            warnings.append("fama_macbeth: no valid cross-sections")
        factor_returns = FactorReturnStat(
            mean=s_mean,
            t_stat=s_t,
            n_dates=len(fmb_slopes),
            slope_series=tuple(fmb_slopes),
        )

        # Turnover: rank-weight absolute day-to-day change.
        fw_factor = fp.pivot(
            index="_date", columns="asset_uid", values="factor_value"
        ).sort_index()
        if fw_factor.shape[0] < 2:
            turnover = 0.0
            warnings.append("turnover: <2 dates, set to 0.0")
        else:
            ranks = fw_factor.rank(axis=1)
            weights = ranks.div(ranks.sum(axis=1), axis=0)
            day_change = weights.diff().abs().sum(axis=1)
            turnover = float(day_change.mean())
            if not np.isfinite(turnover):
                turnover = 0.0

        return FactorEvaluationResult(
            engine_id=self.engine_id,
            factor_name=factor_name,
            ic_by_horizon=tuple(ic_by_horizon),
            factor_returns=factor_returns,
            turnover=TurnoverStat(turnover=turnover),
            warnings=tuple(warnings),
        )


# Structural subtype registration (mirrors providers/contracts_v2.py).
from indiciumforge_core.quant.analytics.ports import FactorAnalyticsPort  # noqa: E402

FactorAnalyticsPort.register(StatsmodelsFactorEngine)

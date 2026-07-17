#!/usr/bin/env python3
"""Capture a golden A-share OHLCV snapshot for reproducible tests / paper §9.

Run manually (NOT in CI)::

    python scripts/snapshot_golden_ashare.py            # akshare live fetch
    python scripts/snapshot_golden_ashare.py --synthetic # deterministic fallback

The snapshot is a single long-format parquet panel under
``tests/fixtures/golden_ashare/panel.parquet`` with columns
``asset_uid, date, open, high, low, close, volume``. A companion ``MANIFEST.yaml``
records provenance (source, captured_at, universe, date_range, akshare version).

The ``--synthetic`` mode generates a deterministic panel with realistic
momentum/cross-sectional structure (seeded GBM + factor drift) so the factor
analytics demo produces IC > 0. Use it when the sandbox has no network access;
the MANIFEST records ``source: synthetic_fallback`` so the paper is honest.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "tests" / "fixtures" / "golden_ashare"
PANEL_PATH = OUT_DIR / "panel.parquet"
MANIFEST_PATH = OUT_DIR / "MANIFEST.yaml"

# ~30 liquid large-cap A-shares (SSE + SZSE) — a credible cross-section.
UNIVERSE_CODES: tuple[str, ...] = (
    "600000", "600009", "600010", "600011", "600015", "600016", "600018",
    "600019", "600025", "600028", "600029", "600030", "600031", "600036",
    "600048", "600050", "600089", "600104", "600196", "600276", "600309",
    "600406", "600519", "600547", "600588", "600585", "600690", "600703",
    "000001", "000063", "000333", "000651", "000858", "002594", "300015",
    "300750",
)
START = date(2024, 1, 2)
END = date(2025, 12, 31)


def _trade_dates(start: date, end: date) -> list[date]:
    """Approximate A-share trading calendar (skip weekends; ignore holidays)."""
    days = []
    cur = start
    while cur <= end:
        if cur.weekday() < 5:  # Mon-Fri
            days.append(cur)
        cur += timedelta(days=1)
    return days


def fetch_akshare() -> pd.DataFrame:
    """Live fetch via AkshareDataProvider. Requires the [data] extra."""
    sys.path.insert(0, str(REPO / "packages" / "indiciumforge-core" / "src"))
    from indiciumforge_core.providers.akshare import AkshareDataProvider
    from indiciumforge_core.providers.query import DataQuery
    from indiciumforge_core.providers.capabilities import DataKind
    from indiciumforge_core.workflow.model import AssetDomain

    provider = AkshareDataProvider(adjust="qfq")
    frames = []
    for code in UNIVERSE_CODES:
        asset = provider.asset_from_code(code)
        query = DataQuery(
            asset=asset,
            asset_domain=AssetDomain.CHINA_A_SHARE,
            data_kind=DataKind.OHLCV,
            start=START,
            end=END,
        )
        result = provider.fetch(query)
        if result.frame.empty:
            print(f"  SKIP {code}: empty ({result.provenance.failure_status.value})", file=sys.stderr)
            continue
        frame = result.frame.copy()
        frame["asset_uid"] = asset.uid
        frames.append(frame[["asset_uid", "date", "open", "high", "low", "close", "volume"]])
        print(f"  ok {code}: {len(frame)} rows")
    if not frames:
        raise RuntimeError("akshare returned no data for any universe member")
    return pd.concat(frames, ignore_index=True)


def generate_synthetic() -> pd.DataFrame:
    """Deterministic synthetic panel with a *detectable* momentum structure.

    Each asset carries a persistent AR(1) trend plus a constant per-asset drift
    level. The persistence is what gives a trailing-return momentum factor its
    cross-sectional predictive power, so the factor-analytics demo reports a
    clearly positive IC (the docstring's promise). Prices stay positive because
    returns are applied in log space.
    """
    rng = np.random.default_rng(seed=20240102)
    dates = _trade_dates(START, END)
    n_dates = len(dates)
    rows = []
    for i, code in enumerate(UNIVERSE_CODES):
        from indiciumforge_core.providers.akshare import _exchange_for_code
        from indiciumforge_core.domain.models import AssetID, AssetType
        asset = AssetID(
            code=code,
            exchange=_exchange_for_code(code),
            asset_type=AssetType.STOCK,
            currency="CNY",
        )
        # Constant per-asset drift level (cross-sectionally varied via sin) +
        # a persistent AR(1) trend. Both are asset-specific and slow-moving,
        # which is exactly what a momentum factor exploits. Tuned to keep the
        # reference backtest in a credible (not absurd) return range while
        # still yielding a clearly positive IC.
        level = 0.00015 * np.sin(i * 0.7)
        trend = np.zeros(n_dates)
        for t in range(1, n_dates):
            trend[t] = 0.85 * trend[t - 1] + rng.normal(0.0, 0.0008)
        log_ret = level + trend + rng.normal(0.0, 0.008, size=n_dates)
        price0 = 10.0 + 50.0 * (i / len(UNIVERSE_CODES))
        log_price = np.log(price0) + np.cumsum(log_ret)
        close = np.exp(log_price)
        open_ = close * np.exp(rng.normal(0, 0.004, size=n_dates))
        high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.006, size=n_dates)))
        low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.006, size=n_dates)))
        volume = rng.integers(5_000_000, 80_000_000, size=n_dates).astype(float)
        for d in range(n_dates):
            rows.append(
                (
                    asset.uid,
                    dates[d],
                    round(open_[d], 2),
                    round(high[d], 2),
                    round(low[d], 2),
                    round(close[d], 2),
                    float(volume[d]),
                )
            )
    return pd.DataFrame(
        rows, columns=["asset_uid", "date", "open", "high", "low", "close", "volume"]
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--synthetic", action="store_true", help="generate deterministic synthetic panel")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.synthetic:
        print("Generating synthetic golden panel ...")
        panel = generate_synthetic()
        source = "synthetic_fallback"
        ak_version = None
    else:
        print("Fetching live A-share data via akshare ...")
        try:
            panel = fetch_akshare()
            source = "akshare_live"
            try:
                import akshare as ak
                ak_version = ak.__version__
            except Exception:
                ak_version = "unknown"
        except Exception as exc:
            print(f"akshare fetch failed: {exc}", file=sys.stderr)
            print("Falling back to --synthetic. Re-run with network to capture real data.", file=sys.stderr)
            panel = generate_synthetic()
            source = "synthetic_fallback"
            ak_version = None

    panel.to_parquet(PANEL_PATH, index=False)
    print(f"Wrote {PANEL_PATH} ({len(panel)} rows, {panel['asset_uid'].nunique()} assets)")

    manifest = {
        "schema": "indiciumforge.golden_ashare.v1",
        "source": source,
        "captured_at": pd.Timestamp.now("UTC").isoformat(),
        "universe": list(UNIVERSE_CODES),
        "date_range": {"start": START.isoformat(), "end": END.isoformat()},
        "akshare_version": ak_version,
        "n_assets": int(panel["asset_uid"].nunique()),
        "n_rows": int(len(panel)),
        "columns": ["asset_uid", "date", "open", "high", "low", "close", "volume"],
    }
    with MANIFEST_PATH.open("w") as fh:
        yaml.safe_dump(manifest, fh, allow_unicode=True, sort_keys=False)
    print(f"Wrote {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

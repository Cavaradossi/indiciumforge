#!/usr/bin/env python3
"""Capture the OpenBB public-demo OHLCV sample panel.

Run manually (NOT in CI)::

    python scripts/snapshot_openbb_demo.py               # deterministic sample (default)
    python scripts/snapshot_openbb_demo.py --online      # real OpenBB fetch ([openbb] extra)

The panel is a single long-format CSV shipped as **package data** under
``indiciumforge_core/data/openbb_demo/sample_us_equity_ohlcv.csv`` (so the demo
resolves it regardless of cwd or install source) with columns
``asset_uid, date, open, high, low, close, volume``. A companion ``MANIFEST.yaml``
records provenance so the demo is honest about its data source.

HONESTY NOTE: the default output is a **deterministic synthetic sample**, not real
market quotes. It exists so the public demo and CI run offline and byte-stable.
Use ``--online`` to snapshot real OpenBB data (yfinance vendor, no API key). The
MANIFEST ``source`` field distinguishes ``synthetic_sample`` from ``openbb_live``.
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
OUT_DIR = (
    REPO
    / "packages"
    / "indiciumforge-core"
    / "src"
    / "indiciumforge_core"
    / "data"
    / "openbb_demo"
)
PANEL_PATH = OUT_DIR / "sample_us_equity_ohlcv.csv"
MANIFEST_PATH = OUT_DIR / "MANIFEST.yaml"

# A small, familiar large-cap US cross-section (NASDAQ). Ticker symbols are public
# identifiers; the sample OHLCV *values* are synthetic unless --online is used.
UNIVERSE_TICKERS: tuple[str, ...] = (
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AVGO",
)
START = date(2024, 1, 2)
END = date(2024, 6, 28)


def _trade_dates(start: date, end: date) -> list[date]:
    """Approximate US trading calendar (skip weekends; ignore holidays)."""
    days = []
    cur = start
    while cur <= end:
        if cur.weekday() < 5:  # Mon-Fri
            days.append(cur)
        cur += timedelta(days=1)
    return days


def fetch_openbb() -> pd.DataFrame:
    """Live fetch via OpenBBDataProvider. Requires the [openbb] extra."""
    sys.path.insert(0, str(REPO / "packages" / "indiciumforge-core" / "src"))
    from indiciumforge_core.providers.capabilities import DataKind
    from indiciumforge_core.providers.openbb import OpenBBDataProvider
    from indiciumforge_core.providers.query import DataQuery
    from indiciumforge_core.workflow.model import AssetDomain

    provider = OpenBBDataProvider(openbb_provider="yfinance")
    frames = []
    for ticker in UNIVERSE_TICKERS:
        asset = provider.asset_from_ticker(ticker)
        query = DataQuery(
            asset=asset,
            asset_domain=AssetDomain.US_EQUITY,
            data_kind=DataKind.OHLCV,
            start=START,
            end=END,
        )
        result = provider.fetch(query)
        if result.frame.empty:
            print(
                f"  SKIP {ticker}: empty ({result.provenance.failure_status.value})",
                file=sys.stderr,
            )
            continue
        frame = result.frame.copy()
        frame["asset_uid"] = asset.uid
        frames.append(
            frame[["asset_uid", "date", "open", "high", "low", "close", "volume"]]
        )
        print(f"  ok {ticker}: {len(frame)} rows")
    if not frames:
        raise RuntimeError("openbb returned no data for any universe member")
    return pd.concat(frames, ignore_index=True)


def generate_sample() -> pd.DataFrame:
    """Deterministic synthetic panel with a *detectable* momentum structure.

    Mirrors ``snapshot_golden_ashare.py --synthetic``: each asset carries a
    persistent AR(1) trend plus a per-asset drift so a trailing-return momentum
    factor has cross-sectional predictive power (IC > 0). Prices are generated in
    log space (always positive). Values are synthetic, NOT real quotes.
    """
    sys.path.insert(0, str(REPO / "packages" / "indiciumforge-core" / "src"))
    from indiciumforge_core.providers.openbb import OpenBBDataProvider

    rng = np.random.default_rng(seed=20240102)
    dates = _trade_dates(START, END)
    n_dates = len(dates)
    rows = []
    for i, ticker in enumerate(UNIVERSE_TICKERS):
        asset = OpenBBDataProvider.asset_from_ticker(ticker)
        level = 0.00018 * np.sin(i * 0.7)
        trend = np.zeros(n_dates)
        for t in range(1, n_dates):
            trend[t] = 0.85 * trend[t - 1] + rng.normal(0.0, 0.0009)
        log_ret = level + trend + rng.normal(0.0, 0.010, size=n_dates)
        price0 = 80.0 + 140.0 * (i / len(UNIVERSE_TICKERS))
        log_price = np.log(price0) + np.cumsum(log_ret)
        close = np.exp(log_price)
        open_ = close * np.exp(rng.normal(0, 0.004, size=n_dates))
        high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.006, size=n_dates)))
        low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.006, size=n_dates)))
        volume = rng.integers(10_000_000, 120_000_000, size=n_dates).astype(float)
        for d in range(n_dates):
            rows.append(
                (
                    asset.uid,
                    dates[d].isoformat(),
                    round(float(open_[d]), 2),
                    round(float(high[d]), 2),
                    round(float(low[d]), 2),
                    round(float(close[d]), 2),
                    float(volume[d]),
                )
            )
    return pd.DataFrame(
        rows, columns=["asset_uid", "date", "open", "high", "low", "close", "volume"]
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--online", action="store_true", help="fetch real data via OpenBB ([openbb] extra)"
    )
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.online:
        print("Fetching OpenBB live panel ...")
        panel = fetch_openbb()
        source = "openbb_live"
    else:
        print("Generating deterministic sample panel ...")
        panel = generate_sample()
        source = "synthetic_sample"

    panel = panel.sort_values(["asset_uid", "date"]).reset_index(drop=True)
    panel.to_csv(PANEL_PATH, index=False)

    manifest = {
        "schema": "indiciumforge.openbb_demo_panel.v1",
        "source": source,
        "not_real_market_data": source == "synthetic_sample",
        "universe": list(UNIVERSE_TICKERS),
        "date_range": [START.isoformat(), END.isoformat()],
        "rows": int(len(panel)),
        "columns": list(panel.columns),
        "note": (
            "Synthetic deterministic sample for the offline public demo and CI; "
            "ticker symbols are public identifiers but OHLCV values are generated. "
            "Real data requires: python scripts/snapshot_openbb_demo.py --online "
            "(pip install 'indiciumforge-core[openbb]')."
        ),
    }
    with MANIFEST_PATH.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, allow_unicode=True)

    print(f"Wrote {PANEL_PATH} ({len(panel)} rows) [source={source}]")
    print(f"Wrote {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

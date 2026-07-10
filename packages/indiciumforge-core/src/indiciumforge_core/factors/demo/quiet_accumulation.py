from __future__ import annotations

from datetime import date

import pandas as pd

from indiciumforge_core.domain.models import AssetID
from indiciumforge_core.factors.models import FactorSignal

LOOKBACK = 5
RANGE_COMPRESSION_RATIO = 0.5


class DemoQuietAccumulationDetector:
    name = "demo_quiet_accumulation"

    def supports(self, asset: AssetID) -> bool:
        return True

    def detect(
        self,
        asset: AssetID,
        ohlcv: pd.DataFrame,
        as_of: date,
    ) -> FactorSignal | None:
        if len(ohlcv) < LOOKBACK + 1:
            return FactorSignal(
                asset=asset,
                factor=self.name,
                as_of=as_of,
                matched=False,
                score=0.0,
                metrics={"reason": "insufficient_bars"},
            )

        frame = ohlcv.sort_values("date").reset_index(drop=True)
        volume_median = float(frame["volume"].median())
        recent = frame.iloc[-LOOKBACK:]
        baseline = frame.iloc[: -LOOKBACK]

        recent_volume_max = float(recent["volume"].max())
        quiet_volume = recent_volume_max < volume_median

        recent_range = float((recent["high"] - recent["low"]).mean())
        if len(baseline):
            baseline_range = float((baseline["high"] - baseline["low"]).mean())
        else:
            baseline_range = recent_range
        compressed_range = recent_range <= baseline_range * RANGE_COMPRESSION_RATIO

        matched = quiet_volume and compressed_range and len(baseline) > 0

        return FactorSignal(
            asset=asset,
            factor=self.name,
            as_of=as_of,
            matched=matched,
            score=1.0 if matched else 0.0,
            metrics={
                "recent_range": round(recent_range, 4),
                "baseline_range": round(baseline_range, 4),
                "volume_median": round(volume_median, 2),
                "recent_volume_max": round(recent_volume_max, 2),
            },
        )

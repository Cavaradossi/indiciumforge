from __future__ import annotations

from datetime import date

import pandas as pd

from lucerna_core.domain.models import AssetID
from lucerna_core.factors.models import FactorSignal

LOOKBACK = 5
VOLUME_MULTIPLIER = 2.0


class DemoVolumeBreakoutDetector:
    name = "demo_volume_breakout"

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
        prior = frame.iloc[-(LOOKBACK + 1) : -1]
        last = frame.iloc[-1]
        prior_mean_volume = float(prior["volume"].mean())
        last_volume = float(last["volume"])
        prior_close = float(frame.iloc[-2]["close"])
        last_close = float(last["close"])

        volume_breakout = last_volume > prior_mean_volume * VOLUME_MULTIPLIER
        price_up = last_close > prior_close
        matched = volume_breakout and price_up
        ratio = last_volume / prior_mean_volume if prior_mean_volume else 0.0

        return FactorSignal(
            asset=asset,
            factor=self.name,
            as_of=as_of,
            matched=matched,
            score=ratio if matched else 0.0,
            metrics={
                "volume_ratio": round(ratio, 4),
                "prior_mean_volume": round(prior_mean_volume, 2),
                "last_volume": round(last_volume, 2),
            },
        )

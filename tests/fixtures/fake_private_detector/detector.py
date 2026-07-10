from __future__ import annotations

from datetime import date

import pandas as pd
from indiciumforge_core.domain.models import AssetID
from indiciumforge_core.factors.models import FactorSignal


class FakePrivateHitDetector:
    name = "fake_private_hit_detector"

    def supports(self, asset: AssetID) -> bool:
        return asset.code == "DEMO001"

    def detect(
        self,
        asset: AssetID,
        ohlcv: pd.DataFrame,
        as_of: date,
    ) -> FactorSignal | None:
        return FactorSignal(
            asset=asset,
            factor=self.name,
            as_of=as_of,
            matched=True,
            score=1.0,
            metrics={"synthetic_metric": 1.0},
        )

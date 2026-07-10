from __future__ import annotations

from datetime import date

import pandas as pd
from indiciumforge_core.domain.models import AssetID
from indiciumforge_core.factors.models import FactorSignal


class EmptyDetector:
    name = "empty_detector"

    def supports(self, asset: AssetID) -> bool:
        return True

    def detect(
        self,
        asset: AssetID,
        ohlcv: pd.DataFrame,
        as_of: date,
    ) -> FactorSignal | None:
        return None


class FailingDetector:
    name = "failing_detector"

    def supports(self, asset: AssetID) -> bool:
        return True

    def detect(
        self,
        asset: AssetID,
        ohlcv: pd.DataFrame,
        as_of: date,
    ) -> FactorSignal | None:
        raise RuntimeError("simulated detector failure")


class SuccessDetector:
    name = "success_detector"

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
        )

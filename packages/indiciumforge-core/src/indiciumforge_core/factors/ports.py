from __future__ import annotations

from datetime import date
from typing import Protocol

import pandas as pd

from indiciumforge_core.domain.models import AssetID
from indiciumforge_core.factors.models import FactorSignal


class FactorDetectorPort(Protocol):
    name: str

    def supports(self, asset: AssetID) -> bool: ...

    def detect(
        self,
        asset: AssetID,
        ohlcv: pd.DataFrame,
        as_of: date,
    ) -> FactorSignal | None: ...

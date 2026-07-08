from __future__ import annotations

from pathlib import Path
from typing import Protocol

import pandas as pd

from lucerna_core.domain.models import Provenance


class ArtifactStorePort(Protocol):
    def read_csv(self, path: Path) -> pd.DataFrame: ...

    def write_csv(self, path: Path, frame: pd.DataFrame) -> None: ...


class DataProviderPort(Protocol):
    def provenance(self) -> Provenance: ...

from __future__ import annotations

from pathlib import Path

import pandas as pd


class LocalArtifactStore:
    def read_csv(self, path: Path, **kwargs: object) -> pd.DataFrame:
        return pd.read_csv(path, **kwargs)

    def write_csv(self, path: Path, frame: pd.DataFrame) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False, encoding="utf-8-sig")

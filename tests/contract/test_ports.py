from __future__ import annotations

from pathlib import Path

import pandas as pd
from lucerna_core.artifacts.local_store import LocalArtifactStore
from lucerna_core.domain.models import AssetID, AssetType, Exchange
from lucerna_core.providers.registry import ProviderRegistry
from provider_stubs import EmptyProvider, FailingProvider, SuccessProvider


def test_local_artifact_store_roundtrip(tmp_path: Path) -> None:
    store = LocalArtifactStore()
    path = tmp_path / "artifact.csv"
    frame = pd.DataFrame([{"code": "000001", "score": 1}])

    store.write_csv(path, frame)
    out = store.read_csv(path, dtype={"code": str})

    assert out.to_dict(orient="records") == [{"code": "000001", "score": 1}]


def test_registry_preserves_fallback_warnings() -> None:
    registry = ProviderRegistry([FailingProvider(), EmptyProvider(), SuccessProvider()])
    asset = AssetID("600000", Exchange.SSE, AssetType.STOCK)

    frame, provenance = registry.fetch_ohlcv(asset)

    assert provenance.provider == "success"
    assert provenance.tier == "local"
    assert any("simulated timeout" in warning for warning in provenance.warnings)
    assert any("empty data" in warning for warning in provenance.warnings)
    assert not frame.empty


def test_registry_returns_explicit_empty_result() -> None:
    registry = ProviderRegistry([FailingProvider(), EmptyProvider()])
    asset = AssetID("600000", Exchange.SSE, AssetType.STOCK)

    frame, provenance = registry.fetch_ohlcv(asset)

    assert frame.empty
    assert provenance.provider == "none"
    assert provenance.warnings

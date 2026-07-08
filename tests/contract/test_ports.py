from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
from lucerna_core.artifacts.local_store import LocalArtifactStore
from lucerna_core.domain.models import AssetID, AssetType, Exchange, MissingData, Provenance

FetchResult = tuple[pd.DataFrame, Provenance]


class EmptyProvider:
    name = "empty"
    tier = "free"

    def supports(self, asset: AssetID) -> bool:
        return True

    def fetch_ohlcv(self, asset: AssetID, start: date | None, end: date | None) -> FetchResult:
        return pd.DataFrame(), Provenance(provider=self.name, tier=self.tier)


class FailingProvider:
    name = "failing"
    tier = "paid"

    def supports(self, asset: AssetID) -> bool:
        return True

    def fetch_ohlcv(self, asset: AssetID, start: date | None, end: date | None) -> FetchResult:
        raise MissingData("simulated timeout")


class SuccessProvider:
    name = "success"
    tier = "local"

    def supports(self, asset: AssetID) -> bool:
        return True

    def fetch_ohlcv(self, asset: AssetID, start: date | None, end: date | None) -> FetchResult:
        return (
            pd.DataFrame(
                [
                    {
                        "date": "2026-04-30",
                        "open": 1.0,
                        "high": 1.1,
                        "low": 0.9,
                        "close": 1.0,
                        "volume": 1,
                    }
                ]
            ),
            Provenance(provider=self.name, tier=self.tier, as_of=date(2026, 4, 30)),
        )


class ProviderRegistry:
    def __init__(self, providers: list[object]) -> None:
        self._providers = providers

    def fetch_ohlcv(self, asset: AssetID, start: date | None = None, end: date | None = None):
        warnings: list[str] = []
        for provider in self._providers:
            try:
                frame, provenance = provider.fetch_ohlcv(asset, start, end)
            except MissingData as exc:
                warnings.append(str(exc))
                continue
            if frame.empty:
                warnings.append(f"{provider.name}: empty data")
                continue
            return frame, Provenance(
                provider=provenance.provider,
                tier=provenance.tier,
                as_of=provenance.as_of,
                warnings=tuple(warnings),
            )
        return pd.DataFrame(), Provenance(provider="none", tier="none", warnings=tuple(warnings))


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

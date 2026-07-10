from __future__ import annotations

from pathlib import Path

import pytest
from indiciumforge_core.providers.config import ProviderLoadError, load_provider_pack
from indiciumforge_core.providers.pack import PROVIDER_PACK_SCHEMA

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures"
PACK_PATH = FIXTURE_ROOT / "provider_pack_demo.yaml"
PROVIDERS_PATH = FIXTURE_ROOT / "providers_fixture.yaml"
FAKE_PROVIDERS_PATH = FIXTURE_ROOT / "providers_fake.yaml"


def test_load_provider_pack_from_demo_pack_yaml() -> None:
    loaded = load_provider_pack(pack_config=PACK_PATH)

    assert loaded.pack_id == "demo-provider-pack"
    assert loaded.providers[0].provider_id == "local_fixture"
    assert loaded.sources == ("providers_config",)


def test_load_provider_pack_from_providers_config_shorthand() -> None:
    loaded = load_provider_pack(providers_config=PROVIDERS_PATH)

    assert loaded.pack_id is None
    assert loaded.providers[0].provider_id == "local_fixture"


def test_load_provider_pack_loads_fake_private_provider() -> None:
    loaded = load_provider_pack(providers_config=FAKE_PROVIDERS_PATH)

    assert loaded.providers[0].provider_id == "fake_private_ohlcv"


def test_load_provider_pack_rejects_invalid_schema(tmp_path: Path) -> None:
    config = tmp_path / "bad-pack.yaml"
    config.write_text("schema: broken\n", encoding="utf-8")

    with pytest.raises(ProviderLoadError, match=PROVIDER_PACK_SCHEMA):
        load_provider_pack(pack_config=config)


def test_load_provider_pack_merges_entry_points(monkeypatch: pytest.MonkeyPatch) -> None:
    from fake_private_provider.provider import FakePrivateOhlcvProvider

    class FakeEntryPoint:
        name = "fake_private_ohlcv"

        def load(self) -> FakePrivateOhlcvProvider:
            return FakePrivateOhlcvProvider()

    monkeypatch.setattr(
        "indiciumforge_core.providers.config.entry_points",
        lambda group: [FakeEntryPoint()] if group == "indiciumforge.data_providers" else [],
    )

    loaded = load_provider_pack(include_entry_points=True)

    assert loaded.providers[0].provider_id == "fake_private_ohlcv"
    assert loaded.sources == ("entry_points",)

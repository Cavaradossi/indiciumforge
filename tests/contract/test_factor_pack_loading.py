from __future__ import annotations

from pathlib import Path

import pytest
from lucerna_core.factors.loading import DetectorLoadError
from lucerna_core.factors.pack import FACTOR_PACK_SCHEMA, load_factor_pack
from lucerna_core.factors.registry import DuplicateDetectorError

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "tests" / "fixtures"
PACK_PATH = FIXTURE_ROOT / "factor_pack_demo.yaml"
DETECTORS_PATH = FIXTURE_ROOT / "factor_detectors.yaml"
FAKE_DETECTORS_PATH = FIXTURE_ROOT / "factor_detectors_fake.yaml"


def test_load_factor_pack_from_demo_pack_yaml() -> None:
    loaded = load_factor_pack(pack_config=PACK_PATH)

    assert loaded.pack_id == "demo-pack"
    assert loaded.registry.list_detectors() == (
        "demo_volume_breakout",
        "demo_quiet_accumulation",
    )
    assert loaded.sources == ("detectors_config",)


def test_load_factor_pack_from_detectors_config_shorthand() -> None:
    loaded = load_factor_pack(detectors_config=DETECTORS_PATH)

    assert loaded.pack_id is None
    assert len(loaded.registry.list_detectors()) == 2


def test_load_factor_pack_loads_fake_private_detector() -> None:
    loaded = load_factor_pack(detectors_config=FAKE_DETECTORS_PATH)

    assert loaded.registry.list_detectors() == ("fake_private_hit_detector",)


def test_load_factor_pack_rejects_invalid_schema(tmp_path: Path) -> None:
    config = tmp_path / "bad-pack.yaml"
    config.write_text("schema: broken\n", encoding="utf-8")

    with pytest.raises(DetectorLoadError, match=FACTOR_PACK_SCHEMA):
        load_factor_pack(pack_config=config)


def test_load_factor_pack_rejects_duplicate_detector_names(tmp_path: Path) -> None:
    config = tmp_path / "dup.yaml"
    config.write_text(
        "detectors:\n"
        "  - module: lucerna_core.factors.demo.volume_breakout\n"
        "    class: DemoVolumeBreakoutDetector\n"
        "  - module: lucerna_core.factors.demo.volume_breakout\n"
        "    class: DemoVolumeBreakoutDetector\n",
        encoding="utf-8",
    )

    with pytest.raises(DuplicateDetectorError):
        load_factor_pack(detectors_config=config)


def test_load_factor_pack_merges_entry_points(monkeypatch: pytest.MonkeyPatch) -> None:
    from fake_private_detector.detector import FakePrivateHitDetector

    class FakeEntryPoint:
        name = "fake_private_hit_detector"

        def load(self) -> FakePrivateHitDetector:
            return FakePrivateHitDetector()

    monkeypatch.setattr(
        "lucerna_core.factors.loading.entry_points",
        lambda group: [FakeEntryPoint()] if group == "lucerna.factor_detectors" else [],
    )

    loaded = load_factor_pack(include_entry_points=True)

    assert loaded.registry.list_detectors() == ("fake_private_hit_detector",)
    assert loaded.sources == ("entry_points",)

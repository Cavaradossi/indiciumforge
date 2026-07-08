from __future__ import annotations

from pathlib import Path

import pytest
from lucerna_core.factors.loading import DetectorLoadError, load_detectors_from_config

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "tests" / "fixtures" / "factor_detectors.yaml"


def test_load_detectors_from_config_registers_demo_detectors() -> None:
    registry = load_detectors_from_config(CONFIG_PATH)

    assert registry.list_detectors() == ("demo_volume_breakout", "demo_quiet_accumulation")


def test_load_detectors_from_config_rejects_invalid_module(tmp_path: Path) -> None:
    config = tmp_path / "bad.yaml"
    config.write_text(
        "detectors:\n  - module: lucerna_core.factors.missing\n    class: Missing\n",
        encoding="utf-8",
    )

    with pytest.raises(DetectorLoadError, match="cannot import module"):
        load_detectors_from_config(config)


def test_load_detectors_from_config_rejects_invalid_shape(tmp_path: Path) -> None:
    config = tmp_path / "bad-root.yaml"
    config.write_text("detectors: not-a-list\n", encoding="utf-8")

    with pytest.raises(DetectorLoadError, match="detectors list"):
        load_detectors_from_config(config)

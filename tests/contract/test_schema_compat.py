from __future__ import annotations

import warnings
from pathlib import Path

from indiciumforge_core.parity.config import load_parity_config
from indiciumforge_core.schema_compat import accepts_schema, normalize_schema_id

ROOT = Path(__file__).resolve().parents[2]


def test_normalize_schema_id_maps_lucerna_prefix() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert normalize_schema_id("lucerna.factor_pack.v1") == "indiciumforge.factor_pack.v1"
    assert len(caught) == 1
    assert issubclass(caught[0].category, DeprecationWarning)


def test_accepts_schema_legacy_alias() -> None:
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        assert accepts_schema("lucerna.factor_pack.v1", "indiciumforge.factor_pack.v1")


def test_load_parity_config_accepts_legacy_schema(tmp_path) -> None:
    config_path = tmp_path / "parity_local.yaml"
    ref_root = (ROOT / "tests/fixtures/parity_reference_demo/reference").as_posix()
    recipe_path = (ROOT / "tests/fixtures/workflow/recipe_ashare_daily_v1.yaml").as_posix()
    extension_pack = (ROOT / "tests/fixtures/recipe_extension_pack_demo.yaml").as_posix()
    config_path.write_text(
        "\n".join(
            [
                "schema: lucerna.parity_local_config.v1",
                f"reference_artifact_root: {ref_root}",
                "trade_date: '2026-06-23'",
                "recipe:",
                f"  path: {recipe_path}",
                f"  extension_pack: {extension_pack}",
                "dimensions:",
                "  - market_gate_strict_semantics",
            ]
        ),
        encoding="utf-8",
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        config = load_parity_config(config_path)
    assert config.trade_date.isoformat() == "2026-06-23"
    assert len(caught) >= 1

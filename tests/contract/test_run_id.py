from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from indiciumforge_core.run_id import (
    DEFAULT_RUN_ID,
    content_hash,
    input_descriptor_hash,
    is_isolated,
    mint_run_id,
)


def test_mint_run_id_is_unique_and_well_formed() -> None:
    a = mint_run_id()
    b = mint_run_id()
    assert a != b
    assert isinstance(a, str)
    assert len(a) == 32  # uuid4().hex
    assert a != DEFAULT_RUN_ID


@pytest.mark.parametrize(
    "run_id, expected",
    [
        ("abc123", True),
        ("default", False),
        ("", False),
    ],
)
def test_is_isolated(run_id: str, expected: bool) -> None:
    assert is_isolated(run_id) is expected


def test_content_hash_deterministic_for_dicts() -> None:
    d1 = {"b": 1, "a": 2}
    d2 = {"a": 2, "b": 1}  # different key order
    assert content_hash(d1) == content_hash(d2)
    assert content_hash(d1) != content_hash({"a": 3, "b": 1})


def test_content_hash_dataframe_schema_and_values_significant() -> None:
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    # identical frame -> identical hash
    assert content_hash(df) == content_hash(pd.DataFrame({"a": [1, 2], "b": [3, 4]}))
    # column reorder -> different hash (schema/ordering is part of the content)
    reordered = pd.DataFrame({"b": [3, 4], "a": [1, 2]})
    assert content_hash(df) != content_hash(reordered)
    # value change -> different hash
    assert content_hash(df) != content_hash(pd.DataFrame({"a": [1, 2], "b": [3, 5]}))


def test_content_hash_scalars_and_paths() -> None:
    assert content_hash("x") == content_hash("x")
    assert content_hash("x") != content_hash("y")
    assert content_hash(date(2026, 1, 1)) == content_hash(date(2026, 1, 1))
    assert content_hash(Path("/tmp/a")) == content_hash(Path("/tmp/a"))


def test_input_descriptor_hash_stable_across_key_order() -> None:
    h1 = input_descriptor_hash(
        recipe_id="r1",
        stage_id="s1",
        trade_date=date(2026, 1, 1),
        inputs={"x": Path("/a/b.csv"), "y": Path("/a/c.csv")},
        options={"k": "v"},
    )
    h2 = input_descriptor_hash(
        recipe_id="r1",
        stage_id="s1",
        trade_date=date(2026, 1, 1),
        inputs={"y": Path("/a/c.csv"), "x": Path("/a/b.csv")},  # reordered
        options={"k": "v"},
    )
    assert h1 == h2


def test_input_descriptor_hash_changes_with_identity() -> None:
    base = dict(
        recipe_id="r1",
        stage_id="s1",
        trade_date=date(2026, 1, 1),
        inputs={"x": Path("/a/b.csv")},
        options={"k": "v"},
    )
    h_recipe = input_descriptor_hash(**base)
    h_other = input_descriptor_hash(**{**base, "recipe_id": "r2"})
    assert h_recipe != h_other

"""Run identity, hashing, and idempotency primitives for reproducible runs.

A first-class ``run_id`` is introduced so that:

* every recipe run gets a stable, unique identity (``mint_run_id``), or reuses a
  caller-supplied one;
* "default" (non-isolated) runs keep the legacy flat artifact layout, while
  isolated runs get a dedicated ``runs/<run_id>`` namespace;
* stage inputs/outputs can be content-hashed (encoding-agnostic) so the runner
  can skip stages whose inputs *and* outputs are unchanged (idempotency, see
  ``RecipeRunner`` + ``MetadataStore``).
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_RUN_ID = "default"


def mint_run_id() -> str:
    """Return a fresh, collision-resistant run identifier (uuid4 hex)."""
    return uuid.uuid4().hex


def is_isolated(run_id: str) -> bool:
    """True when ``run_id`` selects an isolated (non-default) run namespace."""
    return bool(run_id) and run_id != DEFAULT_RUN_ID


def content_hash(obj: Any) -> str:
    """Canonical, encoding-agnostic SHA-256 of arbitrary content.

    * ``DataFrame`` -> row-stable hash via :func:`pandas.util.hash_pandas_object`
      (both column order and row order are significant, so logically equal
      content with a different schema/ordering hashes differently).
    * ``dict``/``list`` -> ``json.dumps(sort_keys=True)`` (key order independent).
    * scalars / ``Path`` / ``date`` / ``datetime`` -> stable string form.

    The goal is reproducibility: identical logical content yields the same hash
    regardless of dict insertion order, JSON key ordering, or string encoding.
    """
    if isinstance(obj, pd.DataFrame):
        row_hashes = pd.util.hash_pandas_object(obj, index=True)
        digest = hashlib.sha256(row_hashes.values.tobytes()).hexdigest()
        return digest
    if isinstance(obj, (dict, list, tuple)):
        payload = json.dumps(
            obj, sort_keys=True, ensure_ascii=False, default=_json_default
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return hashlib.sha256(_stable_str(obj).encode("utf-8")).hexdigest()


def _stable_str(obj: Any) -> str:
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    return str(obj)


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, pd.DataFrame):
        return content_hash(obj)
    return repr(obj)


def input_descriptor_hash(
    *,
    recipe_id: str,
    stage_id: str,
    trade_date: date | str,
    inputs: dict[str, Any] | tuple[Any, ...],
    options: dict[str, Any] | None = None,
) -> str:
    """Stable hash describing what a stage consumes.

    Built from the recipe/stage identity, the trade date, the resolved input
    artifact paths, and the run options. Two stage dispatches with identical
    effective inputs produce the same descriptor hash, which is exactly what
    ``MetadataStore.find_stage_by_input_hash`` keys on for idempotency.
    """
    if isinstance(trade_date, date):
        trade_date_str = trade_date.isoformat()
    else:
        trade_date_str = str(trade_date)

    if isinstance(inputs, dict):
        input_items = sorted(_stable_str(v) for v in inputs.values())
    else:
        input_items = sorted(_stable_str(v) for v in inputs)

    descriptor = {
        "recipe_id": recipe_id,
        "stage_id": stage_id,
        "trade_date": trade_date_str,
        "inputs": input_items,
        "options": {k: str(v) for k, v in sorted((options or {}).items())},
    }
    return content_hash(descriptor)

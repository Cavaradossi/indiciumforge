"""Deprecated lucerna.* schema ID compatibility (removed v2.1.0)."""
from __future__ import annotations

import logging
import warnings

logger = logging.getLogger(__name__)

_LEGACY_PREFIX = "lucerna."
_CANONICAL_PREFIX = "indiciumforge."


def normalize_schema_id(schema: str | None, *, context: str = "") -> str | None:
    """Map deprecated lucerna.* schema IDs to indiciumforge.* for one release."""
    if schema is None:
        return None
    text = str(schema)
    if not text.startswith(_LEGACY_PREFIX):
        return text
    canonical = _CANONICAL_PREFIX + text[len(_LEGACY_PREFIX) :]
    message = (
        f"deprecated schema ID {text!r}; use {canonical!r}"
        + (f" ({context})" if context else "")
        + " — lucerna namespace removed in IndiciumForge v2.0.0"
    )
    warnings.warn(message, DeprecationWarning, stacklevel=3)
    logger.warning(message)
    return canonical


def accepts_schema(actual: str | None, expected: str, *, context: str = "") -> bool:
    if actual is None:
        return False
    normalized = normalize_schema_id(actual, context=context)
    return normalized == expected

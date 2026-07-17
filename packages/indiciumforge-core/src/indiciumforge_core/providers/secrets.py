"""Secret resolution for data providers (W4a).

Secrets are **local runtime inputs**, never project configuration. They are read
from the ignored profile directory (``~/.indiciumforge/``) or process
environment, and must never be logged or committed.

This module centralizes the resolution chain so every provider goes through a
single path — fixing the gap observed in the legacy ``indiciumgrid`` codebase,
where a well-designed ``load_secret()`` existed but was dead code (providers
read ``os.getenv`` directly instead).

Resolution order (first hit wins):
1. Environment variable ``INDICIUMFORGE_SECRET_<NAME>_<KEY>`` (uppercased).
2. TOML table in ``~/.indiciumforge/secrets.toml`` — ``[name]`` with a ``key``
   field — read via stdlib :mod:`tomllib`.
3. ``None`` (no exception on a missing file/section).
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

_ENV_PREFIX = "INDICIUMFORGE_SECRET_"
_DEFAULT_SECRETS_FILE = Path.home() / ".indiciumforge" / "secrets.toml"


@dataclass(frozen=True)
class SecretRef:
    """Non-sensitive metadata describing where a secret *would* be resolved."""

    provider: str
    key: str
    source: str
    configured: bool


def _normalize(token: str) -> str:
    return token.strip().lower().replace("-", "_")


def _env_var_name(name: str, key: str) -> str:
    return f"{_ENV_PREFIX}{_normalize(name).upper()}_{_normalize(key).upper()}"


def _read_toml(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except (tomllib.TOMLDecodeError, OSError):
        return {}


def resolve_secret(
    name: str,
    *,
    key: str = "api_key",
    secrets_file: Path | str | None = None,
) -> str | None:
    """Resolve a secret value by name (env first, then TOML, then ``None``)."""
    env_var = _env_var_name(name, key)
    value = os.environ.get(env_var)
    if value:
        return value

    path = Path(secrets_file) if secrets_file is not None else _DEFAULT_SECRETS_FILE
    payload = _read_toml(path)
    table = payload.get(_normalize(name))
    if isinstance(table, dict):
        raw = table.get(_normalize(key))
        if isinstance(raw, str) and raw:
            return raw
    return None


def secret_status(
    name: str,
    *,
    key: str = "api_key",
    secrets_file: Path | str | None = None,
) -> SecretRef:
    """Return non-sensitive metadata about a secret (never the value)."""
    env_var = _env_var_name(name, key)
    if os.environ.get(env_var):
        return SecretRef(
            provider=name, key=key, source=f"env:{env_var}", configured=True
        )
    path = Path(secrets_file) if secrets_file is not None else _DEFAULT_SECRETS_FILE
    return SecretRef(
        provider=name,
        key=key,
        source=str(path),
        configured=resolve_secret(name, key=key, secrets_file=path) is not None,
    )

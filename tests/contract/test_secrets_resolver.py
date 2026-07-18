"""Tests for the central secret resolver (W4a)."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from indiciumforge_core.providers.secrets import resolve_secret, secret_status


def test_env_var_wins(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("INDICIUMFORGE_SECRET_TUSHARE_API_KEY", "env-token")
    # Even if a TOML file exists, env takes priority.
    toml = tmp_path / "secrets.toml"
    toml.write_text('[tushare]\napi_key = "file-token"\n')
    assert resolve_secret("tushare", secrets_file=toml) == "env-token"


def test_toml_fallback(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("INDICIUMFORGE_SECRET_TUSHARE_API_KEY", raising=False)
    toml = tmp_path / "secrets.toml"
    toml.write_text(textwrap.dedent('''
        [tushare]
        api_key = "file-token"

        [openbb]
        api_key = "openbb-token"
    '''))
    assert resolve_secret("tushare", secrets_file=toml) == "file-token"
    assert resolve_secret("openbb", secrets_file=toml) == "openbb-token"


def test_missing_returns_none_no_exception(tmp_path: Path) -> None:
    # No env, no file.
    assert resolve_secret("nobody", secrets_file=tmp_path / "absent.toml") is None
    # File exists but section missing.
    toml = tmp_path / "secrets.toml"
    toml.write_text("[other]\napi_key = 'x'\n")
    assert resolve_secret("nobody", secrets_file=toml) is None


def test_secret_status_no_value_leak(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("INDICIUMFORGE_SECRET_TUSHARE_API_KEY", "super-secret")
    ref = secret_status("tushare", secrets_file=tmp_path / "x.toml")
    assert ref.configured is True
    assert ref.provider == "tushare"
    assert "env:" in ref.source
    # The SecretRef must NOT carry the secret value.
    assert not hasattr(ref, "value") or "super-secret" not in str(ref)


def test_name_normalization(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Hyphens / case in the *name* normalize to underscores in the env var.
    monkeypatch.setenv("INDICIUMFORGE_SECRET_ZHI_TU_API_KEY", "tok")
    assert resolve_secret("zhi-tu", key="api_key", secrets_file=tmp_path / "x.toml") == "tok"
    assert resolve_secret("ZHI_TU", key="API_KEY", secrets_file=tmp_path / "x.toml") == "tok"

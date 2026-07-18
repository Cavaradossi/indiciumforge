"""Shipped package data (demo panels and companion manifests).

Kept importable so user-facing demos resolve their fixtures regardless of the
current working directory or install source (editable clone or PyPI wheel).
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path

_OPENBB_DEMO_PANEL = "openbb_demo/sample_us_equity_ohlcv.csv"
_OPENBB_DEMO_MANIFEST = "openbb_demo/MANIFEST.yaml"


def openbb_demo_panel_path() -> Path:
    """Absolute path to the committed OpenBB demo sample panel (CSV)."""
    return _resource_path(_OPENBB_DEMO_PANEL)


def openbb_demo_manifest_path() -> Path:
    """Absolute path to the OpenBB demo panel provenance manifest (YAML)."""
    return _resource_path(_OPENBB_DEMO_MANIFEST)


def _resource_path(relative: str) -> Path:
    parts = relative.split("/")
    resource = resources.files(__package__)
    for part in parts:
        resource = resource / part
    return Path(str(resource))

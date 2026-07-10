from __future__ import annotations

import os
import sys
from pathlib import Path

# Typer/Rich truncates --help panels when CI/GITHUB_ACTIONS enable terminal styling.
# Force plain help text so CliRunner captures full option lists on Linux runners.
os.environ["NO_COLOR"] = "1"
os.environ["TERM"] = "dumb"
os.environ["FORCE_COLOR"] = "0"

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "tests" / "contract"
FIXTURES = ROOT / "tests" / "fixtures"
sys.path.insert(0, str(CONTRACT))
sys.path.insert(0, str(FIXTURES))
for package_src in ROOT.glob("packages/*/src"):
    sys.path.insert(0, str(package_src))

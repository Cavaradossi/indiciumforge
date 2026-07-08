from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "tests" / "contract"
sys.path.insert(0, str(CONTRACT))
for package_src in ROOT.glob("packages/*/src"):
    sys.path.insert(0, str(package_src))

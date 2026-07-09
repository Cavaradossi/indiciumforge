from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

IG_PRIVATE_FACTOR_SLUGS = (
    "locked_float_advance",
    "ignition_from_quiet_base",
    "clustered_limit_up",
    "persistent_low_volume_grind",
    "capitulation_volume_shock",
    "dormant_ignition_memory",
    "bottom_repeated_thrust",
    "yang_line_density",
    "absorption_on_pullback",
    "high_turnover_absorption",
)

ALLOWLIST_PATHS = {
    ROOT / "docs" / "FACTOR_CORE_INVENTORY.md",
    ROOT / "FACTOR_GOLDEN_MANIFEST.yaml",
    ROOT / "docs" / "FACTOR_GOLDEN_SCENARIO_PLAN.md",
    ROOT / "docs" / "decisions" / "ADR-0010-factor-core-inventory.md",
    ROOT / "docs" / "decisions" / "ADR-0011-open-core-private-extension-boundary.md",
    ROOT / "docs" / "decisions" / "ADR-0012-factor-detector-port-v0.3.md",
    ROOT / "MIGRATION_MAP_FROM_INDICIUMGRID.md",
    ROOT / "GOLDEN_ARTIFACT_TEST_PLAN.md",
    ROOT / "tests" / "security" / "test_no_private_factor_leak.py",
}

SCAN_ROOTS = (
    ROOT / "packages",
    ROOT / "tests" / "fixtures",
    ROOT / "tests" / "contract",
)

README_QUICKSTART_MARKERS = ("## Quickstart", "## v0.7")


def _iter_scanned_files() -> list[Path]:
    files: list[Path] = []
    for scan_root in SCAN_ROOTS:
        if not scan_root.is_dir():
            continue
        for path in scan_root.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".yaml", ".yml", ".csv", ".json"}:
                if path.resolve() in {item.resolve() for item in ALLOWLIST_PATHS}:
                    continue
                files.append(path)
    readme = ROOT / "README.md"
    if readme.is_file():
        files.append(readme)
    return files


def _readme_quickstart_text(readme_path: Path) -> str:
    text = readme_path.read_text(encoding="utf-8")
    start = -1
    for marker in README_QUICKSTART_MARKERS:
        idx = text.find(marker)
        if idx != -1 and (start == -1 or idx < start):
            start = idx
    if start == -1:
        return text
    return text[start:]


def test_no_ig_private_factor_slugs_outside_allowlist() -> None:
    pattern = re.compile("|".join(re.escape(slug) for slug in IG_PRIVATE_FACTOR_SLUGS))
    violations: list[str] = []

    for path in _iter_scanned_files():
        if path.name == "test_no_private_factor_leak.py":
            continue
        content = (
            _readme_quickstart_text(path)
            if path.name == "README.md"
            else path.read_text(encoding="utf-8", errors="replace")
        )
        for match in pattern.finditer(content):
            line = content.count("\n", 0, match.start()) + 1
            violations.append(f"{path.relative_to(ROOT)}:{line}: {match.group(0)}")

    assert not violations, "IG private factor slugs found outside allowlist:\n" + "\n".join(
        violations
    )

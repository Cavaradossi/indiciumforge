from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_PATTERNS = (
    r"\.indiciumgrid",
    r"vipdoc",
    r"new_tdx64",
    r"D:/new_tdx64",
    r"D:\\new_tdx64",
    r"output/",
    r"watchlist",
    r"secrets",
    r"account/",
)

ALLOWLIST_PATHS = {
    ROOT / "docs" / "DESIGN_DEFECT_MIGRATION_AUDIT.md",
    ROOT / "docs" / "decisions" / "ADR-0019-anti-inheritance-from-indiciumgrid-v0.9.md",
    ROOT / "docs" / "decisions" / "ADR-0020-session-aware-data-provider-v2-v0.9.md",
    ROOT / "docs" / "PRIVATE_DATA_ADAPTER_TEMPLATE.md",
    ROOT / "docs" / "archive" / "MIGRATION_MAP_FROM_INDICIUMGRID.md",
    ROOT / "docs" / "PRIVATE_PARITY_HARNESS_TEMPLATE.md",
    ROOT / "docs" / "decisions" / "ADR-0022-private-local-parity-harness-v0.11.md",
    ROOT / "tests" / "security" / "test_no_provider_path_leak.py",
    # W4a OSS credential-resolution files (intentionally discuss secrets; they
    # resolve from env / ~/.indiciumforge/secrets.toml, never hardcoded paths).
    ROOT / "packages" / "indiciumforge-core" / "src" / "indiciumforge_core"
    / "providers" / "secrets.py",
    ROOT / "packages" / "indiciumforge-core" / "src" / "indiciumforge_core"
    / "providers" / "__init__.py",
    ROOT / "tests" / "contract" / "test_secrets_resolver.py",
}

SCAN_ROOTS = (
    ROOT / "packages",
    ROOT / "tests" / "fixtures",
    ROOT / "tests" / "contract",
)


def _iter_scanned_files() -> list[Path]:
    files: list[Path] = []
    allowlist = {item.resolve() for item in ALLOWLIST_PATHS}
    for scan_root in SCAN_ROOTS:
        if not scan_root.is_dir():
            continue
        for path in scan_root.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".yaml", ".yml", ".csv", ".json"}:
                if path.resolve() in allowlist:
                    continue
                files.append(path)
    return files


def test_no_ig_provider_path_leak_outside_allowlist() -> None:
    pattern = re.compile("|".join(FORBIDDEN_PATTERNS))
    violations: list[str] = []

    for path in _iter_scanned_files():
        if path.name == "test_no_provider_path_leak.py":
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        for match in pattern.finditer(content):
            line = content.count("\n", 0, match.start()) + 1
            violations.append(f"{path.relative_to(ROOT)}:{line}: {match.group(0)}")

    assert not violations, "IG path patterns found outside allowlist:\n" + "\n".join(violations)

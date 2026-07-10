# PyPI release checklist

**Status:** `indiciumforge-core`, `indiciumforge-workflow`, and `indiciumforge-cli` **v2.0.0** are on production PyPI. **v2.0.1** metadata patch is prepared in-repo — publish when operator confirms.

IndiciumForge ships three installable packages from this monorepo. They are **real packages** with working code — not empty placeholders.

## Package inventory

| Package | Version | CLI | Publish order |
| --- | --- | --- | --- |
| `indiciumforge-core` | 2.0.1 | — | 1 |
| `indiciumforge-workflow` | 2.0.1 | — | 2 (depends on core) |
| `indiciumforge-cli` | 2.0.1 | `indiciumforge` | 3 (depends on workflow) |

Workspace meta-package `indiciumforge-workspace` is **dev-only** and not intended for PyPI.

## Pre-publish metadata gate

For each package under `packages/indiciumforge-{core,workflow,cli}/`:

- [ ] `name` matches reserved PyPI slug
- [ ] `version` is `2.0.1` (or next release bump)
- [ ] `description` states reproducible workflow scope; no trading claims
- [ ] `readme = "README.md"` present in package directory
- [ ] `license = "Apache-2.0"`
- [ ] `authors` set (`IndiciumForge contributors`)
- [ ] `requires-python = ">=3.10"`
- [ ] `dependencies` use bounded ranges on sibling packages (`>=2.0.0,<3.0.0`)
- [ ] `classifiers` include Apache license and Python 3.10–3.12
- [ ] `[project.urls]` point to `https://github.com/Cavaradossi/indiciumforge`
- [ ] CLI entry point: `indiciumforge = indiciumforge_cli.main:app` (cli package only)

## Build verification

From repo root, with `build` and `twine` installed:

```bash
python -m pip install build twine
for pkg in indiciumforge-core indiciumforge-workflow indiciumforge-cli; do
  cd packages/$pkg
  python -m build
  twine check dist/*
  rm -rf dist build *.egg-info
  cd ../..
done
```

On Windows PowerShell, run each package directory separately (see [TESTPYPI_RELEASE_RUNBOOK.md](TESTPYPI_RELEASE_RUNBOOK.md)).

Expected: `twine check` passes with no errors for all three wheels/sdists.

## Content boundaries (do not publish)

- Private extension packs or operator `output/` trees
- API keys, tokens, cookies, account/watchlist paths
- Proprietary factor definitions or live data adapter credentials
- Empty stub packages or `0.0.0` name-reservation uploads

## Scope disclaimer (include in release announcement)

IndiciumForge is an **open-core toolkit for reproducible financial research workflows**. It standardizes workflow contracts, output artifacts, and extension boundaries. Outputs are for human research review — **not** order routing or portfolio actions.

## Post-publish verification

- [ ] `pip install indiciumforge-cli==2.0.1` resolves all three packages
- [ ] `indiciumforge --help` works in a clean venv
- [ ] PyPI project pages show updated README and descriptions
- [ ] GitHub Release tag matches published versions

## Related docs

- [TESTPYPI_RELEASE_RUNBOOK.md](TESTPYPI_RELEASE_RUNBOOK.md)
- [FUTURE_SURFACES.md](FUTURE_SURFACES.md)
- [RELEASE_NOTES.md](../RELEASE_NOTES.md) — v2.0.1 metadata patch, v2.0.0 breaking changes

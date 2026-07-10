---
name: indiciumforge-release-audit
description: >-
  Audit IndiciumForge releases: GitHub tag/release, PyPI metadata, security
  scan, and test gates. Use before publishing to TestPyPI or production PyPI.
---

# IndiciumForge Release Audit

## Purpose

Run a structured pre-release checklist for GitHub and PyPI. Do not upload to
TestPyPI or production PyPI unless the operator explicitly requests it.

## Locate The Repository

First locate the IndiciumForge repository root: the directory containing
`pyproject.toml`, `packages/indiciumforge-core/`, and `docs/`.

Then read, from that repository root:

1. `docs/PYPI_RELEASE_CHECKLIST.md`
2. `docs/TESTPYPI_RELEASE_RUNBOOK.md`
3. `SECURITY.md`
4. `RELEASE_NOTES.md`

## GitHub Gate

- Tag exists and points to intended commit
- Release notes document breaking changes if this is a major bump
- Repository URL is `https://github.com/Cavaradossi/indiciumforge`
- CI is green on the tag commit
- No private paths, credentials, account data, or watchlists appear in the diff

## PyPI Metadata Gate

For `indiciumforge-core`, `indiciumforge-workflow`, and `indiciumforge-cli`:

- `version` aligned across packages
- `readme`, `license`, `authors`, `classifiers`, and `[project.urls]` populated
- Sibling dependencies use a compatible version range
- CLI entry point is `indiciumforge`

## Build Gate

```bash
cd packages/indiciumforge-core && python -m build && twine check dist/*
cd packages/indiciumforge-workflow && python -m build && twine check dist/*
cd packages/indiciumforge-cli && python -m build && twine check dist/*
```

## Test Gate

```bash
python -m ruff check .
python -m pytest -q
```

## Security Scan

Search staged diffs and release artifacts for:

- API keys, tokens, cookies, passwords
- Private account or watchlist paths
- Operator `output/` trees
- Unpublished private repo content
- Contest or competition material unrelated to IndiciumForge

Do not paste scan hits containing secrets into chat logs.

## Scope Disclaimer

Include in public release text:

> IndiciumForge produces research audit artifacts and parity evidence. It is not investment advice, not a trading system, and not a broker execution platform.

## TestPyPI Before Production

1. Follow `docs/TESTPYPI_RELEASE_RUNBOOK.md`
2. Perform a clean virtualenv install smoke
3. Run `indiciumforge --help`
4. Publish to production PyPI only after operator sign-off

## Out Of Scope

- Automated upload without operator approval
- arXiv submission
- MCP or IDE plugin publication

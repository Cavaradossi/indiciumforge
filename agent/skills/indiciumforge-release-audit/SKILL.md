---
name: indiciumforge-release-audit
description: >-
  Audit IndiciumForge releases: GitHub tag/release, PyPI metadata, security
  scan, and test gates. Use before publishing to TestPyPI or production PyPI.
---

# IndiciumForge release audit

## Purpose

Structured pre-release checklist for GitHub and PyPI — **no upload** unless the operator explicitly requests it.

## Read first

1. [docs/PYPI_RELEASE_CHECKLIST.md](../../docs/PYPI_RELEASE_CHECKLIST.md)
2. [docs/TESTPYPI_RELEASE_RUNBOOK.md](../../docs/TESTPYPI_RELEASE_RUNBOOK.md)
3. [SECURITY.md](../../SECURITY.md)
4. [RELEASE_NOTES.md](../../RELEASE_NOTES.md)

## GitHub gate

- [ ] Tag exists and points to intended commit
- [ ] Release notes document breaking changes (if major bump)
- [ ] Repository URL: `https://github.com/Cavaradossi/indiciumforge`
- [ ] CI green on tag commit (`ruff` + `pytest`)
- [ ] No private paths or secrets in diff

## PyPI metadata gate

For `indiciumforge-core`, `indiciumforge-workflow`, `indiciumforge-cli`:

- [ ] `version` aligned across packages
- [ ] `readme`, `license`, `authors`, `classifiers`, `[project.urls]` populated
- [ ] Sibling deps use `>=2.0.0,<3.0.0`
- [ ] CLI entry point: `indiciumforge`

## Build gate

```bash
cd packages/indiciumforge-core && python -m build && twine check dist/*
cd packages/indiciumforge-workflow && python -m build && twine check dist/*
cd packages/indiciumforge-cli && python -m build && twine check dist/*
```

## Test gate

```bash
python -m ruff check .
python -m pytest -q
```

## Security scan (content)

Search staged diff for forbidden patterns:

- API keys, tokens, cookies, passwords
- Private account or watchlist paths
- Operator `output/` trees or unpublished private repo content

Use repo policy — do not paste scan hits containing secrets into chat logs.

## Scope disclaimer (release text)

Include in every public announcement:

> IndiciumForge produces research audit artifacts and parity evidence. It is not investment advice, not a trading system, and not a broker execution platform.

## TestPyPI vs production

1. **TestPyPI first** — follow [TESTPYPI_RELEASE_RUNBOOK.md](../../docs/TESTPYPI_RELEASE_RUNBOOK.md)
2. Clean-venv install smoke: `indiciumforge --help`
3. Production PyPI only after operator sign-off

## Out of scope

- Automated upload without operator approval
- arXiv submission (see `docs/paper/`)
- MCP or IDE plugin publish (future — see `docs/mcp/`, `docs/plugin/`)

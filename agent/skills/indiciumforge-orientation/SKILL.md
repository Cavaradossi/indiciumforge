---
name: indiciumforge-orientation
description: >-
  Orient coding agents to the IndiciumForge open-core repository: read README,
  AGENTS.md, SYSTEM_MAP, and CURRENT_STATUS before making changes. Use when
  onboarding to IndiciumForge or when asked what this project is.
---

# IndiciumForge orientation

## Purpose

Help a new agent understand **what IndiciumForge is**, **what it is not**, and **where to read next** — without private data or trading scope.

## Read first (in order)

1. [README.md](../../README.md) — product boundary and quickstart
2. [AGENTS.md](../../AGENTS.md) — hard constraints for agents
3. [docs/SYSTEM_MAP.md](../../docs/SYSTEM_MAP.md) — package and data-flow map
4. [docs/CURRENT_STATUS.md](../../docs/CURRENT_STATUS.md) — milestone and known gaps

## What IndiciumForge is

- Contract-first **open core** for evidence-first financial **research** workflows
- Artifact schemas, manifest audit, golden parity harness, recipe/session model
- Open-core + **operator-local private extensions** (packs loaded via entry points)

## What IndiciumForge is not

- **Not** a trading system, broker execution platform, or portfolio manager
- **Not** investment advice or compliance sign-off
- **Not** a drop-in replacement for every legacy workflow surface

## Frozen reference rule

- `indiciumgrid @ indiciumgrid-golden-v1` is a **read-only** behavioral reference
- Do not modify frozen `indiciumgrid` tracked files from this repo's work
- Golden diffs must be `intentional_change` or `unsupported_gap`

## Packages

| Package | Import root |
| --- | --- |
| `indiciumforge-core` | `indiciumforge_core` |
| `indiciumforge-workflow` | `indiciumforge_workflow` |
| `indiciumforge-cli` | `indiciumforge_cli` (CLI: `indiciumforge`) |

## Before editing code

1. Run `python -m ruff check .` and `python -m pytest -q` after changes
2. Check [CAPABILITY_REGISTER.md](../../CAPABILITY_REGISTER.md) for scope
3. Read relevant ADR under `docs/decisions/` for the area you touch

## Install (from source until PyPI)

```bash
pip install -e packages/indiciumforge-core -e packages/indiciumforge-workflow -e packages/indiciumforge-cli -e ".[dev]"
indiciumforge --help
```

## Out of scope for this skill

- Private extension implementation → use `indiciumforge-extension-author`
- Release/PyPI checks → use `indiciumforge-release-audit`

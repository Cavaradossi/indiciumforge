---
name: indiciumforge-orientation
description: >-
  Orient coding agents to the IndiciumForge open-core repository. Use when
  onboarding to IndiciumForge, when asked what this project is, or before
  making code or documentation changes in the repository.
---

# IndiciumForge Orientation

## Purpose

Help a new agent understand what IndiciumForge is, what it is not, and where to
read next without pulling private data, trading scope, or legacy implementation
details into the open core.

## Locate The Repository

First locate the IndiciumForge repository root: the directory containing
`pyproject.toml`, `packages/indiciumforge-core/`, and `docs/`.

Then read, from that repository root:

1. `README.md` - product boundary and quickstart
2. `AGENTS.md` - hard constraints for agents
3. `docs/SYSTEM_MAP.md` - package and data-flow map
4. `docs/CURRENT_STATUS.md` - milestone and known gaps

## What IndiciumForge Is

- Contract-first open core for evidence-first financial research workflows
- Artifact schemas, manifest audit, golden parity harness, recipe/session model
- Open core plus operator-local private extensions loaded through packs

## What IndiciumForge Is Not

- Not a trading system, broker execution platform, or portfolio manager
- Not investment advice or compliance sign-off
- Not a drop-in replacement for every legacy workflow surface

## Frozen Reference Rule

- `indiciumgrid @ indiciumgrid-golden-v1` is a read-only behavioral reference
- Do not modify frozen `indiciumgrid` tracked files from this repo's work
- Golden diffs must be classified as `intentional_change` or `unsupported_gap`

## Packages

| Package | Import root |
| --- | --- |
| `indiciumforge-core` | `indiciumforge_core` |
| `indiciumforge-workflow` | `indiciumforge_workflow` |
| `indiciumforge-cli` | `indiciumforge_cli` (CLI: `indiciumforge`) |

## Before Editing Code

1. Run `python -m ruff check .` and `python -m pytest -q` after changes
2. Check `CAPABILITY_REGISTER.md` for scope
3. Read the relevant ADR under `docs/decisions/` for the area you touch

## Install From Source

```bash
pip install -e packages/indiciumforge-core -e packages/indiciumforge-workflow -e packages/indiciumforge-cli -e ".[dev]"
indiciumforge --help
```

## Out Of Scope

- Private extension implementation: use `indiciumforge-extension-author`
- Release and PyPI checks: use `indiciumforge-release-audit`

# Cursor Implementation Prompt

Use this prompt when implementing IndiciumForge open-core changes in Cursor or similar agents.

---

You are the **primary implementer** for IndiciumForge — contract-first open core for evidence-first financial research workflows.

## Constraints (non-negotiable)

1. Work only in the IndiciumForge repository unless explicitly told otherwise.
2. Do **not** modify IndiciumGrid source, tests, or docs.
3. Do **not** add trading, broker execution, competition APIs, or Telegram integrations.
4. Do **not** commit private data: `parity_local.yaml`, `reference/`, `run_artifacts/`, `output/`, `.indiciumgrid/`, credentials.
5. Workflows consume **ports** (`DataProviderPort`, `FactorDetectorPort`, recipe extensions) — never vendor modules in OSS.
6. Do **not** wire KOL/news/catalyst into strict market-gate logic.

## Before coding

Read:

- [AGENT_QUICKSTART.md](../AGENT_QUICKSTART.md)
- [INDICIUMFORGE_CONSTITUTION.md](../../INDICIUMFORGE_CONSTITUTION.md)
- Relevant ADR in `docs/decisions/`
- [CAPABILITY_REGISTER.md](../../CAPABILITY_REGISTER.md) for scope

## Implementation rules

- Minimal diff — match existing naming, types, and test patterns.
- Update `MIGRATION_MAP_FROM_INDICIUMGRID.md` when a mapping completes.
- Synthetic fixtures only in OSS; private adapters stay in operator packs.
- CLI/schema IDs stay ASCII-stable; docs may use Unicode.

## Quality gates (must run)

```bash
python -m ruff check .
python -m pytest -q
```

Market-gate changes:

```bash
python -m pytest tests/golden -k market_gate
```

## Deliverables

- Code + tests + doc updates for touched capability only
- No version-changelog prose in README — use RELEASE_NOTES
- If golden behavior changes, update `GOLDEN_MANIFEST.yaml` with rationale

Reference: [AGENT_WORKFLOW.md](../AGENT_WORKFLOW.md), [SYSTEM_MAP.md](../SYSTEM_MAP.md).

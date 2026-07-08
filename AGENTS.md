# Lucerna Agent Rules

## Frozen reference

- `indiciumgrid @ indiciumgrid-golden-v1` is frozen.
- Do not modify IndiciumGrid source, tests, or docs.
- The only approved IndiciumGrid change is the existing golden tag.

## Migration principle

> Migration preserves behavior, not implementation.

## Hard constraints

- Do not connect KOL/news/catalyst/Agent inputs to strict gate logic.
- Do not expand v0.1 scope beyond CAPABILITY_REGISTER `implemented_v1` items.
- Golden differences must be recorded as `intentional_change` or `unsupported_gap`.
- Lucerna workflows consume ports, never vendors.

## Roles

- Cursor: primary implementer for Lucerna code, tests, and docs.
- Codex: independent reviewer for golden parity and ADR consistency.

## Allowed project agent files

- `AGENTS.md`
- `docs/AGENT_WORKFLOW.md`
- `docs/AGENT_REVIEW_CHECKLIST.md`

Hooks, MCP servers, and project-owned subagent frameworks are out of scope for v0.1.

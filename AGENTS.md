# IndiciumForge Agent Rules

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
- IndiciumForge workflows consume ports, never vendors.

## Text encoding (agents)

- Treat the repo as UTF-8; do not assume a legacy code page for reads or writes.
- Keep machine-parsed surfaces ASCII-stable: CLI flags, schema IDs, config keys, artifact filenames, and operational log lines.
- Documentation and domain artifacts may use Unicode (including Chinese labels) where appropriate.
- Do not use decorative Unicode punctuation in CLI output or logs; prefer ASCII hyphen/minus unless a domain rule requires otherwise.
- Do not mass-normalize unrelated files to ASCII; fix only surfaces you touch or explicit policy violations.

## Roles

- Cursor: primary implementer for IndiciumForge code, tests, and docs.
- Codex: independent reviewer for golden parity and ADR consistency.

## Allowed project agent files

- `AGENTS.md`
- `docs/AGENT_QUICKSTART.md` — start here for onboarding
- `docs/AGENT_WORKFLOW.md`
- `docs/AGENT_REVIEW_CHECKLIST.md`

Hooks, MCP servers, and project-owned subagent frameworks are out of scope for v0.1.

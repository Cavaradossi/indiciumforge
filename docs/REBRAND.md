# Rebrand: Lucerna → IndiciumForge

**Effective:** v2.0.0 (2026-07-10)

## Decision

Primary brand **IndiciumForge** replaces **Lucerna** to avoid namespace collision with:

- PyPI `lucerna` — unrelated LLM agent orchestration package
- npm `@upstart.gg/lucerna` — AST code indexer / MCP server
- lucerna.team — AI engineering management copilot

See [ADR-0023](decisions/ADR-0023-indiciumforge-rebrand-v2.0.md).

## Name reservation (operator)

| Surface | Target name | Status |
| --- | --- | --- |
| GitHub repo | `Cavaradossi/indiciumforge` | Rename at v2.0.0 cutover |
| PyPI | `indiciumforge-core`, `indiciumforge-workflow`, `indiciumforge-cli` | Reserve before first publish |
| CLI | `indiciumforge` | Shipped v2.0.0 |
| Agent skill (future) | `indiciumforge-agent-quickstart` | Planned |
| MCP (future) | `indiciumforge-mcp` | Planned |

## Historical tags

- `v1.0.0` — **Lucerna** open-core sign-off (immutable)
- `v2.0.0` — **IndiciumForge** rebrand (breaking schema + CLI namespace)

## Unchanged

- Frozen reference: `indiciumgrid @ indiciumgrid-golden-v1`
- Legacy golden schemas: `indiciumgrid.*` in market-gate expected artifacts

## One-release compat

Parsers accept deprecated `lucerna.*` schema IDs with a deprecation warning; removed in v2.1.0.

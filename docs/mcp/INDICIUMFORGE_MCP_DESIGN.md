# IndiciumForge MCP server — design draft

**Status:** design only — **not in v2.0.0**. No MCP server implementation ships with the open core.

## Purpose

Expose IndiciumForge **research audit surfaces** to coding agents via [Model Context Protocol](https://modelcontextprotocol.io/) — without trading APIs, secrets, or private data.

Proposed package name: `indiciumforge-mcp` (distinct from unrelated `@upstart.gg/lucerna` AST indexer).

## Non-goals

- Not a trading or broker execution MCP
- Not investment advice generation
- No account credentials, watchlists, or live order APIs
- No upload of private `output/` or reference trees to cloud
- Not shipped in v2.0.0

## Candidate tools

| Tool | Input | Output | Notes |
| --- | --- | --- | --- |
| `inspect_artifact_manifest` | `artifact_root`, `trade_date`, `stage_type` | Audit violations list | Wraps `indiciumforge artifact audit` semantics |
| `summarize_parity_report` | Path to `parity_run_report.json` | Dimension verdict table | Research audit only |
| `validate_workflow_stage` | Stage dir + expected schema | Pass/fail + schema details | Uses `indiciumforge_core` manifest validators |
| `project_status` | — | Capability matrix excerpt | Reads public docs constants, not private state |

## Candidate resources

| URI pattern | Content |
| --- | --- |
| `indiciumforge://docs/system-map` | SYSTEM_MAP excerpt |
| `indiciumforge://schemas/{id}` | Public schema ID documentation |
| `indiciumforge://capability/{id}` | CAPABILITY_REGISTER row |

## Architecture sketch

```text
Coding agent (Cursor, etc.)
        │ MCP (stdio / SSE)
        ▼
indiciumforge-mcp server
        │ imports
        ▼
indiciumforge-core / indiciumforge-cli (local install)
        │ reads only
        ▼
Operator-local artifact_root (never uploaded by default)
```

## Security model

- Read-only access to paths explicitly passed by the operator
- Reject paths outside allowed roots (configurable `--allow-root`)
- No network fetch except optional GitHub API for public release metadata
- No env vars containing secrets logged or returned

## Version plan

| Milestone | Deliverable |
| --- | --- |
| v2.0.0 | This design doc only |
| v2.1+ | MVP: `inspect_artifact_manifest` + `summarize_parity_report` |
| v2.2+ | `project_status` + schema resources |

## Related docs

- [FUTURE_SURFACES.md](../FUTURE_SURFACES.md)
- [AGENT_SKILL_ROADMAP.md](../AGENT_SKILL_ROADMAP.md)
- [PLUGIN design](../plugin/INDICIUMFORGE_PLUGIN_DESIGN.md)

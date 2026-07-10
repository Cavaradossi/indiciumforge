# IndiciumForge IDE plugin — design draft

**Status:** design only — **not in v2.0.0**. No VS Code / Cursor extension ships with the open core.

Proposed slug: `indiciumforge-extension-author` (optional marketplace listing post-v2).

## Purpose

Bundle **agent skills**, **prompts**, and **doc deep-links** for IndiciumForge extension authors — without secrets, trading APIs, or private data sync.

## Non-goals

- Not a trading terminal or broker connector
- Not investment advice UI
- No embedded API keys, tokens, or cookies
- No automatic upload of operator artifact trees
- Not shipped in v2.0.0

## Candidate features

| Feature | Description |
| --- | --- |
| Skill bundle | Ship `agent/skills/*` as installable Cursor skills |
| Prompt palette | CONTEXT_PROMPTS excerpts for implementation/review |
| Doc panel | Links to EXTENSION_AUTHOR_GUIDE, ADRs, capability register |
| Command: open parity template | Opens `parity_local.yaml.example` in editor |
| Command: run audit (local) | Invokes locally installed `indiciumforge artifact audit` |

## Architecture sketch

```text
IDE (Cursor / VS Code)
        │ extension host
        ▼
indiciumforge-extension-author
        │ reads
        ▼
Repo docs + agent/skills/ (no network required)
        │ optional spawn
        ▼
Local indiciumforge CLI (user-installed)
```

## Configuration

| Setting | Default | Notes |
| --- | --- | --- |
| `indiciumforge.cliPath` | `indiciumforge` | Path to CLI on PATH |
| `indiciumforge.allowedArtifactRoots` | `[]` | User must opt-in roots for audit commands |
| `indiciumforge.enableTradingFeatures` | `false` | Hard-disabled; no trading API surface |

## Security model

- Extension never stores credentials
- Spawned CLI inherits user env — extension does not inject secrets
- Artifact paths validated against `allowedArtifactRoots`

## Relationship to MCP

Plugin may **invoke** a future `indiciumforge-mcp` server for richer tool access. v2.0.0 ships neither; skills in `agent/skills/` are the interim agent surface.

## Version plan

| Milestone | Deliverable |
| --- | --- |
| v2.0.0 | This design doc + in-repo skills |
| v2.2+ | Marketplace extension MVP (doc panel + skill install) |
| v2.3+ | Optional MCP bridge |

## Related docs

- [AGENT_SKILL_ROADMAP.md](../AGENT_SKILL_ROADMAP.md)
- [MCP design](../mcp/INDICIUMFORGE_MCP_DESIGN.md)
- [EXTENSION_AUTHOR_GUIDE.md](../EXTENSION_AUTHOR_GUIDE.md)

# Future surfaces — IndiciumForge naming registry

**Status:** pre-publish checklist (v2.0.0+). No packages published yet.

## PyPI (reserve before announcement)

| Package | Purpose | Action |
| --- | --- | --- |
| `indiciumforge-core` | Core contracts and artifacts | `twine upload` on v2.0.0 tag |
| `indiciumforge-workflow` | Workflow services | depends on `-core` |
| `indiciumforge-cli` | Reference CLI (`indiciumforge` command) | depends on `-workflow` |
| `indiciumforge-workspace` | Monorepo meta (optional) | dev-only |

**Do not** publish under `lucerna` — PyPI name taken by unrelated AI orchestration.

## GitHub

| Item | Target |
| --- | --- |
| Repository | `Cavaradossi/indiciumforge` |
| Topics | `indiciumforge`, `evidence-first`, `open-core` |
| Historical tag | `v1.0.0` (Lucerna sign-off, immutable) |

## Agent skill (Cursor)

| Item | Target |
| --- | --- |
| Skill slug | `indiciumforge-agent-quickstart` |
| Source docs | `docs/AGENT_QUICKSTART.md`, `SYSTEM_MAP.md` |

## MCP server (future)

| Item | Target |
| --- | --- |
| Package name | `indiciumforge-mcp` |
| Avoid | `@upstart.gg/lucerna` pattern (unrelated AST indexer) |

## arXiv / research

Working title (post-rebrand):

> *IndiciumForge: Contract-First Evidence Artifacts for Point-in-Time Accounting-Risk Anomaly Detection*

- Replace Lucerna brand mentions with IndiciumForge
- Keep IndiciumGrid as frozen reference lineage only
- Link ORCID/GitHub to `Cavaradossi/indiciumforge` after rename

## Private extension packs

| Item | Target |
| --- | --- |
| Workspace | `indiciumforge-private` |
| A-share pack | `indiciumforge-private-ashare` / `indiciumforge_private_ashare` |

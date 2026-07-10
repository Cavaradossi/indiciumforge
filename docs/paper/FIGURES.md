# Figure plan

Figures for the IndiciumForge technical paper draft. All diagrams use **public OSS structure only** — no private data plots.

## Figure 1 — System boundary

**Source:** README Mermaid `IndiciumForge_OpenCore` boundary diagram

**Caption:** Open-core packages expose ports and contracts; private extensions (operator-local) supply data, factors, and recipe logic; a frozen legacy reference supports parity only.

## Figure 2 — Runtime data flow

**Source:** README Mermaid runtime flow (fixture → recipe → artifacts → audit/parity)

**Caption:** Research inputs flow through recipe runners into versioned artifacts; manifest audit checks structure; golden comparator checks semantics against reference.

## Figure 3 — Package workspace

**Source:** README Mermaid package workspace

**Caption:** Monorepo layout: `indiciumforge-core`, `indiciumforge-workflow`, `indiciumforge-cli`, tests, and docs.

## Figure 4 — Workflow chain stages

**Source:** `docs/WORKFLOW_SESSION_MODEL.md` / SYSTEM_MAP

**Caption:** Cyclic session model connecting awareness, discovery, handoff, factor scan, and market gate stages with handoff artifacts.

## Figure 5 — Parity harness dimensions

**Source:** `docs/decisions/ADR-0022-private-local-parity-harness-v0.11.md`

**Caption:** Five-dimension parity comparator: daily_review_structure, post_close_handoff_shape, preopen_handoff_shape, market_gate_strict_semantics, workflow_chain_summary_v4.

## Figure 6 — Open-core vs private extension

**Source:** EXTENSION_AUTHOR_GUIDE table

**Caption:** Boundary table: OSS ships ports and loaders; private packs ship proprietary implementations.

## Figure 7 — Schema audit pipeline (proposed)

**New diagram** — manifest audit decision flow:

```text
artifact_root → list stages → load JSON payloads
    → schema ID check (indiciumforge.*)
    → trade_date consistency
    → required files per stage
    → AuditReport (violations[])
```

**Caption:** Structural manifest audit precedes semantic golden comparison.

## Rendering notes (future LaTeX)

- Prefer vector (Mermaid export or TikZ) for print
- No performance charts until reproducible experiments exist
- No account/portfolio screenshots

## Not included (future work)

- Accounting-risk feature distribution plots (no dataset committed)
- Live market data visualizations (private adapters only)

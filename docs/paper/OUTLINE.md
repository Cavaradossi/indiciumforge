# Paper outline

**Title:** IndiciumForge: A Contract-First Open Core for Evidence-First Financial Research Workflows

**Genre:** software / systems paper (Markdown draft for Codex → LaTeX conversion)

**Status:** draft — not submitted to arXiv; no fabricated experiments or citations

**Evidence index:** [CLAIMS_REGISTER.md](CLAIMS_REGISTER.md)

**Repository:** https://github.com/Cavaradossi/indiciumforge · tag `v2.0.0`

---

## Section map

| § | Title | Primary evidence |
| --- | --- | --- |
| Abstract | Summary | CLAIMS_REGISTER rows C01–C06 |
| 1 | Introduction | README, INDICIUMFORGE_CONSTITUTION.md |
| 2 | Problem statement | ADR-0019, MIGRATION_MAP_FROM_INDICIUMGRID.md |
| 3 | Contributions | CAPABILITY_REGISTER.md, ADR-0011..0022 |
| 4 | Architecture | packages/*, docs/SYSTEM_MAP.md |
| 5 | Artifact lifecycle & audit | ADR-0008, ADR-0014, manifest.py |
| 6 | Recipe & session model | ADR-0018, WORKFLOW_SESSION_MODEL.md |
| 7 | Open-core / private boundary | ADR-0011, EXTENSION_AUTHOR_GUIDE.md |
| 8 | Golden & parity methodology | ADR-0022, GOLDEN_MANIFEST.yaml, parity tests |
| 9 | Case study | V1_0_DEFINITION.md L1–L3, parity_reference_demo |
| 10 | Agent-friendly governance | AGENTS.md, docs/decisions/, agent/skills/ |
| 11 | Limitations | V1_0_DEFINITION.md non-goals, CAPABILITY_REGISTER |
| 12 | Future work | research plan stub, MCP/plugin design docs |
| 13 | Conclusion | — |
| A | Reproducibility | pytest, CLI commands |
| B | Schema inventory | ADR-0023, indiciumforge_core constants |

---

## 1. Introduction

- Research vs execution boundary
- Evidence-first artifact outputs
- Six contributions (numbered, cross-ref register)
- Explicit non-claims (trading, advice, broker)

## 2. Problem statement

### 2.1 Entangled research pipelines

- Data ingestion, private signals, local state, execution assumptions mixed in monoliths
- Reviewers cannot reconstruct point-in-time evidence

### 2.2 Legacy migration without module copying

- Frozen reference label `indiciumgrid-golden-v1`
- Behavior preservation via artifact parity, not `import indiciumgrid`
- ADR-0019 anti-inheritance rules

## 3. Contributions (enumerated)

1. Contract-first open core (ports + pack loaders)
2. Artifact schemas + manifest audit CLI
3. Recipe / session workflow model
4. Open-core / private-extension boundary
5. Golden artifact + parity harness methodology
6. Agent-friendly governance (ADRs, agent rules, skills)

## 4. Architecture

- Three packages: core, workflow, CLI
- Extension types: provider, factor detector, recipe extension, parity reference provider
- Artifact lifecycle: produce → store → audit → compare

## 5. Artifact lifecycle & manifest audit

- Schema IDs (`indiciumforge.*`)
- Stage directories under `artifact_root`
- Structural audit vs semantic golden compare

## 6. Recipe & session model

- `WorkflowRecipe`, `SessionModel`, `HandoffArtifact`
- A-share daily recipe as one domain instance
- Cyclic vs linear operator views

## 7. Open-core / private boundary

- OSS vs operator-local table
- Entry-point pack pattern
- Templates without proprietary logic

## 8. Golden & parity methodology

- Five OSS golden market-gate scenarios
- Five parity dimensions (ADR-0022)
- Verdict taxonomy
- Synthetic `parity_reference_demo` for public CI

## 9. Case study

- L1: OSS golden strict semantics
- L2: synthetic parity demo (`strict_count: 1`)
- L3: private extension boundary validation (verdict categories only; external sign-off doc)
- No private paths, rows, or raw data

## 10. Agent-friendly governance

- AGENTS.md constraints
- 23 ADRs (0001–0023)
- In-repo Cursor skills (`agent/skills/`)

## 11. Limitations

- Not trading / advice / broker execution
- No public proprietary detectors
- Not full IndiciumGrid replacement
- Parity = research audit only

## 12. Future work

- Accounting-risk anomaly detection (planning stub)
- Research dossier contracts (`technical_reserve`)
- MCP / agent skills expansion
- Cross-domain session lessons (crypto/US) without contest framing

## 13. Conclusion

- Artifact-first research audit architecture
- Community extensions behind ports

## Appendices

- **A:** Reproducibility commands (tag `v2.0.0`)
- **B:** Schema ID inventory (ADR-0023)
- **C:** Claims register excerpt

## Figures

See [FIGURES.md](FIGURES.md) — five Mermaid diagrams + extension boundary table figure.

## Related work

See [RELATED_WORK.md](RELATED_WORK.md) — candidate areas only; no invented bibliography.

## LaTeX conversion notes (for Codex)

- Convert Mermaid via `mermaid-cli` or redraw as TikZ
- Claims register → supplemental table or appendix
- Keep disclaimer box in introduction
- Do not add citations until operator curates RELATED_WORK into BibTeX

## Authoring rules

- Every technical claim must appear in CLAIMS_REGISTER with source path/tag/test
- No fabricated metrics, Sharpe ratios, or legal findings
- No private paths, account data, or competition references

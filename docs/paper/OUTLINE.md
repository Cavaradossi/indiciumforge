# Paper outline

**Working title:** IndiciumForge: A Contract-First Open Core for Evidence-First Financial Research Workflows

**Format:** software / systems paper (Markdown draft; LaTeX deferred)

**Status:** draft — no arXiv submission, no experiment claims

## Abstract (draft)

IndiciumForge is an open-core software architecture for building reproducible financial research workflows whose primary outputs are **auditable artifacts** rather than trading actions. The system separates stable contracts (ports, schema IDs, manifest audit) from operator-local private extensions (data adapters, factor detectors, recipe stages). A golden artifact parity methodology compares new implementations against a frozen legacy reference without importing legacy code. We describe the recipe/session model, the open-core boundary, and a private extension case study conducted entirely with synthetic and anonymized structural evidence—without claiming investment performance or legal findings.

## 1. Introduction

- Motivation: research workflows need evidence trails, not opaque pipelines
- Gap: monolithic research stacks mix data, signals, and execution
- Contributions (enumerated below)
- Scope disclaimer: not trading, not investment advice

## 2. Background and problem framing

- Evidence-first research vs execution-first systems
- Legacy reference migration (behavior preservation without inheritance)
- Related work pointer → [RELATED_WORK.md](RELATED_WORK.md)

## 3. System overview

- Package architecture: core, workflow, CLI
- Artifact store layout
- Workflow chain stages (awareness → discovery → handoff → gate)
- Figure pointers → [FIGURES.md](FIGURES.md)

## 4. Contract-first architecture

- Port interfaces (provider v2, factor detector, recipe extension)
- Entry-point pack loading
- Schema IDs and versioning policy
- ADR governance model

## 5. Artifact schema and manifest audit

- Schema namespace (`indiciumforge.*`)
- Manifest audit dimensions (files, schemas, trade_date consistency)
- CLI `artifact audit` as structural gate vs semantic golden compare

## 6. Open-core / private-extension boundary

- What ships in OSS vs operator-local packs
- Security and IP boundaries
- Extension templates without proprietary logic

## 7. Golden artifact parity methodology

- Frozen reference pin (`indiciumgrid-golden-v1`)
- Five parity dimensions (daily review, post_close, preopen, market_gate, chain summary)
- Verdict taxonomy: match, mismatch, intentional_change, unsupported_gap
- Synthetic demo harness (`parity_reference_demo`)

## 8. Recipe and session model

- Cyclic session workflow (post_close → preopen → midday → market_gate)
- Recipe YAML and stage dispatch
- Handoff artifacts between stages

## 9. Case study: private extension without private data

- Structural description of IG-output adapter pattern
- Normalized candidate pool replay into IndiciumForge layout
- Parity smoke on golden date (report verdict categories only — no private rows)
- Accepted gaps (e.g., daily_review column mismatch documented as intentional)

## 10. Limitations

- OSS uses synthetic fixtures by default
- Not a compliance or fraud conviction system
- Parity harness is research audit, not production certification

## 11. Future work

- Accounting-risk anomaly detection on point-in-time disclosures (see research plan stub)
- MCP agent tools for manifest/parity inspection
- Expanded golden coverage beyond market-gate scenarios

## 12. Conclusion

- Summary of architectural contributions
- Call for community extensions behind ports

## Appendices (planned)

- A: Schema ID inventory
- B: Capability register excerpt
- C: Reproducibility package checklist (monorepo install + pytest)

## Authoring rules

- Do not fabricate experiment numbers or backtest results
- Do not claim trading system or investment advice capabilities
- Cite frozen reference only as migration methodology, not co-brand endorsement

# IndiciumForge: A Contract-First Open Core for Evidence-First Financial Research Workflows

**Document type:** technical paper draft (Markdown)  
**Status:** not submitted to arXiv; no experiment results claimed  
**Repository:** https://github.com/Cavaradossi/indiciumforge  
**Version discussed:** v2.0.0 open core

---

## Abstract

Financial research workflows often entangle data ingestion, signal generation, and execution in ways that obscure what was known at each decision point. IndiciumForge is an open-core software architecture that treats **versioned artifacts**—JSON states, CSV reviews, and stage summaries—as the primary outputs of a reproducible research pipeline. Stable contracts (Python ports, schema IDs, entry-point pack loaders) define how operator-local private extensions attach without forking core semantics. A manifest audit CLI checks structural completeness; a golden artifact parity harness compares implementations against a frozen legacy reference without importing legacy code. We present the recipe/session workflow model, the open-core boundary, parity methodology, and a private extension case study described only in structural terms. IndiciumForge is a research audit framework: it is **not** a trading system, **not** investment advice, and **not** a broker execution platform.

**Keywords:** research workflows, software architecture, artifact audit, open core, reproducibility, financial research systems

---

## 1. Introduction

Quantitative and fundamental research teams need pipelines that answer two questions for every staged decision: **what evidence existed at the time**, and **can an independent reviewer verify that evidence**. Production trading stacks optimize for latency and fill quality; they are poor substrates for publishable research audit trails. Conversely, ad-hoc notebooks lack schema discipline and make regression detection expensive.

IndiciumForge addresses this gap with a **contract-first open core**: the OSS repository ships ports, artifact schemas, synthetic fixtures, a reference CLI, manifest audit, and a parity harness. Proprietary data adapters, factor detectors, and recipe stage logic live in **operator-local extension packs** loaded via standard Python entry points.

### 1.1 Contributions

This draft describes six architectural contributions:

1. **Contract-first workflow architecture** — stage runners consume ports, not vendor SDKs.
2. **Artifact schema and manifest audit** — `indiciumforge.*` schema IDs plus structural CLI audit.
3. **Open-core / private-extension boundary** — explicit IP and security separation (ADR-0011).
4. **Golden artifact parity methodology** — five-dimension comparator vs frozen reference.
5. **Recipe and session model** — cyclic A-share daily research workflow with handoff artifacts.
6. **Private extension case study (no private data)** — structural replay pattern and parity verdict categories only.

### 1.2 Scope and non-claims

- We do **not** report trading performance, Sharpe ratios, or portfolio returns.
- We do **not** provide investment advice or compliance certification.
- We do **not** claim fraud conviction or legal findings.
- Parity `all_match` on a golden date is **research audit evidence**, not production sign-off.

---

## 2. System overview

IndiciumForge is organized as a Python monorepo with three installable packages:

| Package | Responsibility |
| --- | --- |
| `indiciumforge-core` | Domain models, ports, artifact I/O, manifest audit, parity models |
| `indiciumforge-workflow` | Market gate kernel, daily review skeleton, workflow chain runner |
| `indiciumforge-cli` | Typer CLI (`indiciumforge`) for workflow, artifact, factor, provider, parity |

Artifacts are stored under an operator-specified `artifact_root` with predictable paths for `workflows/{YYYYMMDD}/` and `market_awareness/{YYYYMMDD}/daily_review/`. Each stage emits JSON state files with explicit `schema` fields, enabling mechanical validation before semantic comparison.

See [OUTLINE.md](OUTLINE.md) for section roadmap and [FIGURES.md](FIGURES.md) for diagram plan.

---

## 3. Contract-first architecture

### 3.1 Ports and packs

Extension points are defined as Python protocols:

- `DataProviderPortV2` — session-aware OHLCV and metadata queries
- `FactorDetectorPort` — scan-time signal generation
- `PrivateRecipeExtensionPort` — per-stage recipe dispatch

Packs are YAML documents declaring `schema: indiciumforge.<pack_type>.v1` and listing entry-point modules. Loaders merge registries at runtime; duplicate detector names fail fast.

### 3.2 Schema versioning

Artifact and config documents carry namespaced schema IDs (`indiciumforge.workflow_chain_summary.v4`, etc.). Breaking changes bump major package version (v2.0.0 rebrand from legacy `lucerna.*` namespace). A one-release compatibility shim maps deprecated IDs with warnings.

### 3.3 Governance

Architecture decisions are recorded as ADRs under `docs/decisions/`. The capability register (`CAPABILITY_REGISTER.md`) marks features as implemented, signed, or explicitly deferred.

---

## 4. Artifact schema and manifest audit

Structural audit is intentionally **separate** from semantic golden comparison.

The `indiciumforge artifact audit` command verifies, per stage:

- Required files exist on disk
- JSON payloads parse and declare expected `schema` IDs
- `trade_date` fields are consistent within a stage directory

Manifest audit catches incomplete runs early—for example, a market gate stage missing `market_gate_summary.json`. Semantic correctness of gate decisions remains the responsibility of golden tests and the parity comparator.

---

## 5. Open-core / private-extension boundary

| Shipped in OSS | Operator-local private pack |
| --- | --- |
| Port interfaces and loaders | Live market data adapters |
| Demo factor detectors | Proprietary factor logic |
| Recipe runner and extension loader | Production recipe stage bodies |
| Parity harness and synthetic reference trees | Legacy output mirrors and credentials |

Private packs are installed editable from a separate repository; their YAML references use `indiciumforge.*` schemas. OSS documentation provides templates under `examples/private_extension_template/` with no proprietary logic.

This boundary keeps the public repository free of secrets, account identifiers, and calibrated production policies while still enabling real-world adoption.

---

## 6. Golden artifact parity methodology

### 6.1 Frozen reference

Behavioral migration targets a **frozen reference label** (`indiciumgrid-golden-v1`). IndiciumForge does not import legacy Python modules; it compares **exported artifacts** only. Legacy `indiciumgrid.*` schema IDs in golden expected files remain unchanged as historical contracts.

### 6.2 Parity dimensions

The private-local parity harness (ADR-0022) evaluates five dimensions for a configured `trade_date`:

1. `daily_review_structure` — CSV columns and review state schema
2. `post_close_handoff_shape` — candidate pool keys and post-close state
3. `preopen_handoff_shape` — preopen review state
4. `market_gate_strict_semantics` — strict gate counts vs reference
5. `workflow_chain_summary_v4` — chain summary audit fields

Each dimension returns `match` or `mismatch` with a message; the run report aggregates verdicts. The CLI disclaimer states `research_audit_only`.

### 6.3 OSS demonstration

The `tests/fixtures/parity_reference_demo/` tree provides a **synthetic** reference layout for public CI. Operators replicate the pattern with local reference roots described in templates—not committed to OSS.

---

## 7. Recipe and session model

Recipes are YAML documents (`indiciumforge.workflow_recipe.v1`) listing ordered stages for an asset domain. The A-share daily research recipe models a **cyclic session**: post-close discovery seeds preopen handoff; awareness daily review feeds market gate inputs.

`WorkflowSessionMetadata` ties runs to `cycle_id` and trade dates. Handoff artifacts (`indiciumforge.handoff_artifact.v1`) document cross-stage dependencies without embedding vendor-specific paths.

The workflow chain runner emits `workflow_chain_summary.json` with per-stage `audit_ok` flags consumed by parity dimension five.

---

## 8. Case study: private extension without private data

*This section describes methodology only—no proprietary rows, codes, or account data.*

A private recipe extension pack replays **normalized structural outputs** from a legacy workflow layout into IndiciumForge artifact paths. An adapter maps legacy post-close candidate pools into `candidate_pool_raw.json` with the expected schema; awareness and handoff stages populate IndiciumForge directory conventions.

**Parity outcome (categories only):** on a golden trade date, dimensions for post-close handoff, preopen handoff, market gate strict semantics, and workflow chain summary reported **match**. Daily review structure reported a **documented column mismatch** accepted as a known gap in the sign-off register—illustrating how parity separates hard semantic gates from accepted structural drift.

**Lesson:** the open-core/private split allows real-world migration evidence while keeping the public repository free of confidential inputs.

---

## 9. Limitations

- Default OSS workflows use **synthetic fixtures**; live data quality varies by private adapter.
- Manifest audit does not prove economic correctness—only structural integrity.
- Golden coverage is strongest for market-gate scenarios; other stages have thinner public golden matrices.
- The system does not replace disclosure counsel, investment policy, or execution compliance.

---

## 10. Future work

- **Accounting-risk anomaly detection** on point-in-time disclosures (planning stub only; see `docs/research/ACCOUNTING_RISK_ANOMALY_RESEARCH_PLAN.md`)
- **MCP tools** for manifest and parity report inspection (`docs/mcp/INDICIUMFORGE_MCP_DESIGN.md`)
- **Reproducibility bundle** for arXiv supplement (pinned deps + pytest + golden export script)
- Expanded golden scenarios beyond five market-gate cases

---

## 11. Conclusion

IndiciumForge demonstrates that financial research workflows can be decomposed into **auditable artifacts** behind stable ports, with a clear open-core boundary and a parity methodology that preserves behavioral evidence without code inheritance. The architecture prioritizes reviewer trust over execution latency—appropriate for research audit, not for broker routing.

---

## Reproducibility (current)

From a clean checkout of tag `v2.0.0`:

```bash
pip install -e packages/indiciumforge-core -e packages/indiciumforge-workflow -e packages/indiciumforge-cli -e ".[dev]"
python -m pytest -q
indiciumforge parity run --parity-config tests/fixtures/parity_reference_demo/parity_config_demo.yaml --artifact-root /tmp/iforge-demo
```

No fabricated metrics are produced by this procedure—it validates structural and semantic gates encoded in tests.

---

## References (draft)

See [RELATED_WORK.md](RELATED_WORK.md). Formal BibTeX deferred until LaTeX conversion.

## Appendix: schema inventory

Public schema IDs are enumerated in ADR-0023 and `indiciumforge_core` constants. Legacy `indiciumgrid.*` IDs appear only in frozen golden expected artifacts.

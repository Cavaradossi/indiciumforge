# IndiciumForge: A Contract-First Open Core for Evidence-First Financial Research Workflows

**Document type:** software / systems paper draft (Markdown)
**Audience:** Codex → LaTeX conversion
**Status:** not submitted to arXiv
**Repository:** https://github.com/Cavaradossi/indiciumforge
**Version tag:** `v2.0.0`
**Claims index:** [CLAIMS_REGISTER.md](CLAIMS_REGISTER.md)

---

## Abstract

Financial research pipelines frequently combine data ingestion, proprietary signals, operator-local state, and implicit execution assumptions in ways that obscure what was knowable at each staged decision. Migrating away from legacy systems compounds the problem when teams copy modules instead of preserving **observable behavior** against frozen references.

IndiciumForge is an open-core Python architecture whose primary outputs are **versioned research artifacts**—JSON stage states, CSV review tables, and chain summaries—rather than orders or portfolio actions. Stable contracts (`DataProviderPortV2`, `FactorDetectorPort`, `PrivateRecipeExtensionPort`) and YAML pack loaders let operator-local extensions attach without forking core semantics. A manifest audit CLI validates structural completeness; golden and parity comparators evaluate semantic agreement against exported reference trees without importing legacy runtime code.

We describe six contributions: contract-first packaging, artifact schema audit, recipe/session orchestration, an explicit open-core boundary, golden parity methodology, and agent-friendly governance documentation. A three-layer validation story (OSS golden, synthetic parity demo, operator-local sign-off categories) illustrates migration evidence without publishing private rows or paths. IndiciumForge is a **research audit framework**—not a trading system, not investment advice, and not a broker execution platform.

**Keywords:** research workflows, software architecture, artifact audit, open core, reproducibility, financial research systems

---

## 1. Introduction

Quantitative and fundamental research groups need workflows that support two audit questions at every stage: **what evidence existed at the time**, and **can an independent reviewer verify that evidence without rerunning hidden state**. Execution-optimized stacks prioritize latency and fill quality; notebook-centric workflows lack schema discipline and make regressions expensive to detect.

IndiciumForge targets the middle ground: **evidence-first financial research** implemented as auditable artifacts behind explicit contracts. The open-source repository ships ports, schemas, synthetic fixtures, a reference CLI, manifest audit, golden tests, and a parity harness. Proprietary data adapters, factor detectors, and production recipe bodies remain in operator-local packs (C12, C25).

### 1.1 Contributions

1. **Contract-first open core** — workflow stages consume port interfaces and pack loaders, not vendor SDKs (C01, C13–C15).
2. **Artifact schemas and audit CLI** — `indiciumforge.*` schema IDs plus `indiciumforge artifact audit` for structural validation (C03, C04).
3. **Recipe and session workflow model** — cyclic session contracts with domain-specific recipes, including an A-share daily instance (C16, C17).
4. **Open-core / private-extension boundary** — ADR-governed IP and security split (C12, C29).
5. **Golden artifact and parity harness methodology** — five OSS golden scenarios and five parity dimensions vs frozen reference exports (C05–C11, C21–C24).
6. **Agent-friendly governance** — constitution, 23 ADRs, AGENTS.md, and in-repo Cursor skills for safe automation (C32, C33).

### 1.2 Non-claims

IndiciumForge does **not**:

- execute live trades or broker orders (C26),
- provide investment advice or compliance certification (C25),
- ship proprietary alpha detectors in the public repository (C27),
- claim full replacement of every legacy workflow surface (C28),
- report backtest performance or fabricated experiment metrics (see forbidden claims in CLAIMS_REGISTER).

Parity `all_match` on an operator golden date is **research audit evidence**, not production certification (C31).

---

## 2. Problem statement

### 2.1 Entangled research pipelines

Production research stacks often merge:

- raw and derived data paths known only on operator machines,
- proprietary signal definitions,
- local calibration and operator-local screening state,
- implicit assumptions about session timing and execution feasibility.

When these concerns share one codebase without artifact contracts, reviewers cannot reconstruct point-in-time evidence. Regression testing devolves into manual diffing of opaque outputs.

### 2.2 Migration without module copying

Teams migrating from legacy implementations face a second failure mode: **copying modules** imports hidden path assumptions, network side effects, and domain rules that should not become universal core semantics. IndiciumForge adopts a frozen reference label (`indiciumgrid-golden-v1`) and compares **exported artifacts** only (C10, C11). Eleven anti-inheritance rules block default legacy paths, hidden network fetch in OSS CI, and direct feeding of provider output into strict market-gate promotion (C29, C30).

**Design intent:** preserve behavior where golden-covered; record `intentional_change` or `unsupported_gap` elsewhere (C08).

---

## 3. System architecture

### 3.1 Package decomposition

IndiciumForge v2.0.0 ships three installable packages (C01):

| Package | Responsibility |
| --- | --- |
| `indiciumforge-core` | Domain models, ports, artifact I/O, manifest audit, parity models, pack loaders |
| `indiciumforge-workflow` | Market gate kernel, daily review skeleton, workflow chain runner, synthetic e2e |
| `indiciumforge-cli` | Typer CLI (`indiciumforge`) exposing workflow, artifact, factor, provider, parity commands (C02) |

Figure 4 (package workspace) and Figure 1 (system boundary) in [FIGURES.md](FIGURES.md) summarize the layout.

### 3.2 Extension types

| Extension | Port / role | Pack schema | Entry point group |
| --- | --- | --- | --- |
| Data provider | `DataProviderPortV2` | `indiciumforge.provider_pack.v1` | `indiciumforge.data_providers` |
| Factor detector | `FactorDetectorPort` | `indiciumforge.factor_pack.v1` | `indiciumforge.factor_detectors` |
| Recipe stage body | `PrivateRecipeExtensionPort` | `indiciumforge.recipe_extension_pack.v1` | `indiciumforge.recipe_extensions` |
| Parity reference | `ReferenceArtifactProviderPort` | N/A (directory root) | wired via `parity_local_config` |

Loaders merge registries at runtime; duplicate detector registration fails fast (C14, C15).

### 3.3 Artifact lifecycle

```text
configure packs → run recipe/chain stage → write stage directory
    → (optional) manifest audit → (optional) golden/parity compare → record verdict
```

1. **Produce** — stage runners write JSON/CSV bundles under `artifact_root` with `schema` fields (C03).
2. **Store** — predictable paths `workflows/{YYYYMMDD}/<stage>/` and `market_awareness/{YYYYMMDD}/daily_review/`.
3. **Audit** — `indiciumforge artifact audit` lists violations (missing files, schema mismatch, trade_date drift) (C04).
4. **Compare** — golden tests and parity harness evaluate semantics against reference trees (C05–C09).

Structural audit intentionally precedes semantic comparison so incomplete runs fail before expensive diffs (C04).

---

## 4. Contract-first design

### 4.1 Ports over vendors

Workflow code depends on protocols, not concrete data vendors. `DataProviderPortV2` adds session-aware queries and explicit authority tagging so fallback success is not mistaken for primary-source quality (C13, C30). Factor and recipe extensions follow the same pattern (C14, C15).

### 4.2 Pack configuration

YAML packs declare `schema: indiciumforge.<type>.v1` and reference entry-point modules or nested config files. OSS ships demo packs under `tests/fixtures/`; operators author private packs from `examples/private_extension_template/` (C40).

### 4.3 Schema versioning

Breaking namespace changes bump major release version (v2.0.0 rebrand from legacy `lucerna.*`). A one-release compatibility shim accepts deprecated schema IDs with `DeprecationWarning` (C34).

### 4.4 Governance

Twenty-three ADRs document boundaries from evidence-first principles (ADR-0001) through rebrand policy (ADR-0023) (C33). The capability register marks each feature `implemented_*`, `private_extension`, `contract_only`, or `technical_reserve` (C26–C28).

---

## 5. Artifact schema and manifest audit

Each machine-readable artifact carries a `schema` field using the `indiciumforge.*` namespace. Representative IDs include `indiciumforge.market_daily_review_state.v1`, `indiciumforge.workflow_chain_summary.v4`, and `indiciumforge.parity_run_report.v1` (C03, C07, C18).

The manifest auditor enforces per-stage file sets—for market gate: state, summary, bucket CSVs, calibration audit, etc. Violation kinds include `missing_file`, `schema_mismatch`, `invalid_json`, and `trade_date_mismatch` (C04).

**Separation of concerns:** manifest audit does not re-derive market-gate strict semantics; golden tests and `compare_semantic_market_gate` do (C05, C06).

---

## 6. Recipe and session model

IndiciumForge generalizes operator-linear folders into **session-cyclic** checkpoints linked by typed handoff artifacts (C16). Core types include `AssetDomain`, `SessionModel`, `WorkflowRecipe`, `WorkflowCheckpoint`, `EvidenceStageRef`, and `HandoffArtifact` (see `docs/WORKFLOW_SESSION_MODEL.md`).

The default A-share daily research recipe (`indiciumforge.recipe.ashare_daily_research.v1`) composes awareness, post-close discovery, preopen handoff, optional factor scan, and market gate stages (C17). Stage folder names like `post_close` are **recipe compatibility labels**, not universal lifecycle enums—crypto and US equity domains can define alternate recipes under the same session contracts (C39).

The workflow chain runner emits `workflow_chain_summary.json` schema v4 with per-stage `audit_ok` flags consumed by parity dimension five (C18).

---

## 7. Open-core / private-extension boundary

ADR-0011 defines the authoritative split (C12):

| Open-source repository | Operator-local private packs |
| --- | --- |
| Ports, schemas, loaders | Live data adapters |
| Synthetic fixtures and demo detectors | Proprietary factor logic |
| Recipe runner and extension loader | Production recipe stage implementations |
| Parity harness + synthetic reference demo | Legacy output mirrors, credentials, reference trees |

Private capabilities load through explicit entry points—never via hidden imports from the public tree (C12). ADR-0019 adds eleven rules preventing legacy path defaults, hidden network fetch in CI, and leakage of real alpha or account evidence into Git (C29).

Figure 5 in [FIGURES.md](FIGURES.md) illustrates the boundary.

---

## 8. Golden artifact and parity methodology

### 8.1 OSS golden layer (L1)

`GOLDEN_MANIFEST.yaml` pins reference `indiciumgrid-golden-v1` and lists five market-gate scenarios: `strict_pass_mixed`, `empty_strict_c_grade`, `fallback_post_close`, `missing_theme_fail`, `catalyst_ignored` (C05, C10). `tests/golden/test_market_gate.py` asserts semantic agreement with exported expected artifacts (C06, C21).

### 8.2 Synthetic parity demo (L2)

`tests/fixtures/parity_reference_demo/` provides a public reference tree and config consumed by `indiciumforge parity run` in CI-style tests (C09, C22). The demo exercises the five ADR-0022 dimensions without operator-private paths (C07).

### 8.3 Parity flow

Figure 3 in [FIGURES.md](FIGURES.md) shows config → harness → comparator → `parity_run_report.json`. Verdict labels: `match`, `mismatch`, `intentional_change`, `unsupported_gap` (C08). Reports carry `disclaimer: research_audit_only` (C31).

### 8.4 Frozen legacy schemas

Golden **expected** market-gate artifacts retain historical `indiciumgrid.*` schema IDs as read-only contracts; IndiciumForge-native stages emit `indiciumforge.*` (C10). This preserves reference semantics without importing legacy code (C11).

---

## 9. Case study: migration evidence without private data

We summarize validation in three layers documented in `docs/V1_0_DEFINITION.md`—**no private paths, tickers, or row-level data appear below**.

### 9.1 Layer L1 — OSS golden

Public CI demonstrates market-gate strict, observation, active_watch, and rejected bucket semantics across five scenarios, including cases with `strict_count >= 1` (C21).

### 9.2 Layer L2 — synthetic parity demo

The parity_reference_demo harness reports compatible structure and market-gate strict semantics against its synthetic reference, including `strict_count: 1` in summary details (C22).

### 9.3 Layer L3 — private extension boundary validation

An operator-local recipe extension pack (external to the public repository) replays **normalized structural shapes** from a legacy output layout into IndiciumForge artifact directories. Private sign-off documentation (external) reports:

- golden trade date **2026-07-03**,
- **five parity dimensions** evaluated,
- aggregate verdict **all_match: true** for that date (C23).

A **daily_review** manifest column mismatch was recorded as accepted gap **GAP-07**—showing how parity separates hard semantic gates from documented structural drift (C24). This case study validates the **open-core boundary**, not proprietary alpha quality.

### 9.4 Public OSS fixtures

All reproducible commands in §13 use synthetic fixtures under `tests/fixtures/` only (C09, C40).

---

## 10. Agent-friendly governance

Financial research software must be maintainable by human reviewers **and** coding agents. IndiciumForge ships:

- **AGENTS.md** — frozen-reference rules, anti-inheritance constraints, encoding policy (C32),
- **23 ADRs** — architectural boundaries readable without spelunking code (C33),
- **Agent onboarding pack** — `docs/AGENT_QUICKSTART.md`, `SYSTEM_MAP.md`, `CURRENT_STATUS.md`,
- **In-repo Cursor skills** — `agent/skills/indiciumforge-{orientation,extension-author,release-audit}/` (C32).

Skills deliberately exclude private paths, credentials, and trading API guidance (C25). Future MCP tooling remains design-only (C36).

---

## 11. Limitations

1. **Not a trading system** — execution port is `technical_reserve`; no order placement (C26, C25).
2. **Not investment advice** — outputs are research audit artifacts for human review (C25).
3. **Not broker execution** — no broker connectors in OSS (C25).
4. **No public proprietary detectors** — real long-structure logic is `private_extension` (C27).
5. **Not full legacy replacement** — account analysis, intraday watch, catalyst ingestion remain deferred (C28).
6. **Synthetic default** — OSS CI uses fixtures; live data quality depends on private adapters.
7. **Manifest audit ≠ economic truth** — structure only; semantics require golden/parity (C04).
8. **Parity ≠ production sign-off** — research audit disclaimer (C31).
9. **Accounting-risk research** — planning stub only; no OSS experiments (C37).

---

## 12. Future work

| Direction | Status | Reference |
| --- | --- | --- |
| Accounting-risk anomaly detection (point-in-time disclosures) | planning stub | `docs/research/ACCOUNTING_RISK_ANOMALY_RESEARCH_PLAN.md` (C37) |
| Research dossier / evidence module contracts | `technical_reserve` | CAPABILITY_REGISTER (C38) |
| MCP tools (manifest inspect, parity summarize) | design only | `docs/mcp/INDICIUMFORGE_MCP_DESIGN.md` (C36) |
| IDE plugin bundling skills + prompts | design only | `docs/plugin/INDICIUMFORGE_PLUGIN_DESIGN.md` |
| Cross-domain session recipes (US equity, crypto spot) | contracts exist | WORKFLOW_SESSION_MODEL (C39) |
| PyPI distribution | build-ready, unpublished | PYPI_RELEASE_CHECKLIST (C35) |
| arXiv LaTeX + verified bibliography | this draft | RELATED_WORK candidate areas |

Future crypto or multi-session workflows will reuse session-cyclic checkpoints—**without** documenting contest or competition-specific execution paths.

---

## 13. Conclusion

IndiciumForge shows that financial research workflows can be restructured around **auditable artifacts** and **explicit contracts**, enabling legacy migration evidence through golden and parity methodology rather than module inheritance. The open-core / private-extension boundary keeps public semantics reviewable while allowing operator-local proprietary implementations.

The architecture prioritizes reviewer trust and reproducible stage evidence over execution latency—appropriate for research audit, not for broker routing.

---

## 14. Reproducibility

From tag `v2.0.0` (C19):

```bash
pip install -e packages/indiciumforge-core \
            -e packages/indiciumforge-workflow \
            -e packages/indiciumforge-cli \
            -e ".[dev]"
python -m ruff check .
python -m pytest -q
indiciumforge parity run \
  --parity-config tests/fixtures/parity_reference_demo/parity_config_demo.yaml \
  --artifact-root /tmp/indiciumforge-parity-demo
```

Expected: pytest reports 144 passed, 1 skipped (C19); parity demo produces `parity_run_report.json` with dimension verdicts (C09).

---

## Appendix A — Schema inventory (excerpt)

IndiciumForge-native IDs (full list in ADR-0023):

- `indiciumforge.workflow_recipe.v1`
- `indiciumforge.workflow_chain_summary.v4`
- `indiciumforge.market_daily_review_state.v1`
- `indiciumforge.factor_pack.v1` / `indiciumforge.provider_pack.v1` / `indiciumforge.recipe_extension_pack.v1`
- `indiciumforge.parity_local_config.v1` / `indiciumforge.parity_run_report.v1`

Legacy `indiciumgrid.*` IDs appear only in frozen golden expected artifacts (C10).

---

## Appendix B — Claims traceability

All sentences asserting implementable behavior map to [CLAIMS_REGISTER.md](CLAIMS_REGISTER.md). LaTeX conversion should preserve claim IDs as comments or sidenotes for review.

---

## References

Candidate literature areas are listed in [RELATED_WORK.md](RELATED_WORK.md). **No bibliography entries are asserted in this draft.** Codex should add verified citations during LaTeX conversion.

---

## Figure list

| Fig | Title | File |
| --- | --- | --- |
| 1 | System boundary | [FIGURES.md](FIGURES.md) §Figure 1 |
| 2 | Runtime data flow | [FIGURES.md](FIGURES.md) §Figure 2 |
| 3 | Artifact parity flow | [FIGURES.md](FIGURES.md) §Figure 3 |
| 4 | Package workspace | [FIGURES.md](FIGURES.md) §Figure 4 |
| 5 | Extension boundary | [FIGURES.md](FIGURES.md) §Figure 5 |
| 6 | Session model (optional) | [FIGURES.md](FIGURES.md) §Figure 6 |

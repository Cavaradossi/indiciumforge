# Related work — candidate areas

**Purpose:** orient literature review before LaTeX/BibTeX curation.

**Rule:** this file lists **candidate research areas and exemplar systems only**. It does **not** contain formal citations, DOIs, or invented bibliography entries. Codex should add verified references during LaTeX conversion.

---

## 1. Open-source scientific software papers

**Candidate area:** journals and arXiv categories that publish **software implementations** with reproducibility artifacts (JOSS, NeurIPS Datasets & Benchmarks track patterns, SciPy proceedings).

**Relevance:** IndiciumForge is positioned as reproducible research **infrastructure**, not a single-model benchmark.

**Contrast:** scientific software papers often center one library; IndiciumForge centers multi-stage **workflow artifacts** and audit.

---

## 2. Workflow orchestration systems

**Exemplar families (names only):** Luigi, Apache Airflow, Prefect, Snakemake.

**Gap:** general DAG engines schedule tasks but typically lack domain-specific **financial research stage schemas** and integrated manifest audit CLI.

**IndiciumForge distinction:** stage outputs are first-class versioned artifacts with `indiciumforge.*` schema IDs.

---

## 3. Reproducible financial ML / quant research

**Candidate area:** reproducibility checklists for financial ML, point-in-time feature construction, backtest leakage audits.

**Exemplar families (names only):** Quantopian/Zipline lineage, Qlib-style factor platforms, OpenBB-style terminals.

**Contrast:** many frameworks optimize backtest or execution simulation. IndiciumForge **explicitly excludes** broker execution and investment advice; outputs are audit artifacts.

**Evidence for contrast:** README scope disclaimer; CAPABILITY_REGISTER `execution port` = `technical_reserve`.

---

## 4. Artifact- and versioned-data pipelines

**Candidate area:** data versioning (DVC), experiment tracking (MLflow), data quality frameworks (Great Expectations).

**Complementary role:** these tools version datasets and metrics; IndiciumForge versions **multi-file stage bundles** (JSON state + CSV reviews + summaries) under predictable directory conventions.

**Potential alignment:** RO-Crate / Frictionless Data packaging for future export bundles (not implemented v2.0.0).

---

## 5. Toolbox / open-ecosystem papers (OpenMMLab style)

**Candidate area:** "toolbox" papers describing extensible frameworks with registry + config + plugin entry points (e.g., MMDetection-style ecosystems in other domains).

**Parallel:** IndiciumForge pack loaders + entry point groups (`indiciumforge.data_providers`, `indiciumforge.factor_detectors`, `indiciumforge.recipe_extensions`) follow similar **open-core + extension** ergonomics without claiming computer-vision scope.

---

## 6. Backtesting / trading frameworks (contrast)

**Exemplar families (names only):** Backtrader, VectorBT, proprietary broker APIs.

**Contrast table (draft):**

| Dimension | Trading / backtest frameworks | IndiciumForge |
| --- | --- | --- |
| Primary output | PnL, orders, positions | Artifact manifests + parity reports |
| Execution | Often simulated or live | Explicitly out of scope |
| Extension model | Strategy classes | Port + pack contracts |
| Regression | Equity curve diff | Golden artifact semantic compare |

---

## 7. Provenance and evidence models

**Candidate area:** W3C PROV, research object crates, audit-log standards.

**IndiciumForge approach:** lighter-weight JSON schema IDs + per-stage state files + manifest audit violations list—optimized for local research audit, not enterprise provenance federation.

---

## 8. Architecture decision records (governance)

**Candidate area:** Michael Nygard ADR pattern; docs-as-code governance in open source.

**Evidence:** 25 ADRs (ADR-0001–ADR-0024 and ADR-0026) in `docs/decisions/`; INDICIUMFORGE_CONSTITUTION.md; AGENTS.md agent rules.

---

## 9. Migration / characterization testing

**Candidate area:** golden-file testing (compilers, UI), characterization tests for legacy behavior capture.

**IndiciumForge instantiation:** five exported market-gate scenarios in `GOLDEN_MANIFEST.yaml`; semantic comparator in `indiciumforge_core.artifacts.comparator`.

**Frozen reference:** `indiciumgrid @ indiciumgrid-golden-v1` — behavioral reference label, not co-brand endorsement (ADR-0019).

---

## 10. Agent tooling for software engineering (adjacent)

**Candidate area:** MCP servers for code indexing; Cursor Agent Skills for repo onboarding.

**IndiciumForge surface:** in-repo skills under `agent/skills/`; future MCP design doc (not implemented v2.0.0).

**Distinction:** code-index MCPs solve repository navigation; IndiciumForge MCP design targets **artifact manifest and parity report** inspection.

---

## 11. Accounting and disclosure risk (future work only)

**Candidate area:** point-in-time disclosure anomaly detection, reporting-quality signals.

**Status:** planning stub in `docs/research/ACCOUNTING_RISK_ANOMALY_RESEARCH_PLAN.md` — **no completed experiments** in OSS.

**Paper rule:** cite as future work only; do not claim empirical results.

---

## Positioning statement (for introduction §2)

IndiciumForge occupies a middle layer:

- **Below** generic workflow schedulers (flexible, schema-agnostic)
- **Above** raw notebooks (no contract discipline)
- **Beside** backtest/trading stacks (contrast on execution)
- **Focused on** evidence-first artifact contracts for financial **research audit**

---

## Bibliography workflow (for Codex)

1. Operator selects 15–25 verified citations from candidate areas above
2. Map each citation to a subsection in this file
3. Add BibTeX only after manual verification
4. Cross-check that no citation implies IndiciumForge trading or performance claims

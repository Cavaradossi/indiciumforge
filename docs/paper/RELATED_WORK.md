# Related work

Survey notes for the IndiciumForge paper draft. **Not a formal bibliography** — refine before arXiv/LaTeX.

## Workflow and pipeline systems

- **Luigi / Airflow / Prefect** — general DAG orchestration; weak native artifact schema contracts for domain-specific audit
- **MLflow / DVC** — experiment tracking and data versioning; focus on model metrics rather than staged research artifact manifests
- **Great Expectations** — data quality tests; complementary to but not replacing workflow-stage artifact contracts

**Gap IndiciumForge addresses:** domain-specific **financial research stage artifacts** with explicit schema IDs and manifest audit integrated into the workflow CLI.

## Financial research platforms

- **Quantopian / Zipline lineage** — backtest-centric; execution simulation blur research/execution boundary
- **Backtrader / VectorBT** — strategy backtesting; not artifact-audit-first
- **OpenBB** — data terminal orientation; different contract boundary

**Distinction:** IndiciumForge explicitly **does not** ship broker execution or investment advice; outputs are research audit artifacts.

## Provenance and evidence systems

- **W3C PROV** — provenance model; IndiciumForge uses lighter-weight JSON schema IDs + manifest files
- **RO-Crate / Frictionless Data** — research object packaging; potential future alignment for export bundles

## Software product lines / open-core

- **Open-core + commercial extension** pattern (Elastic, GitLab) — analogous boundary to OSS ports vs private packs
- **ADR governance** (Nygard) — adopted in `docs/decisions/`

## Migration and regression testing

- **Golden file testing** — common in compilers/UI; IndiciumForge applies to **semantic market-gate artifacts**
- **Characterization tests** — legacy behavior capture without code inheritance (frozen `indiciumgrid-golden-v1` reference)

## Accounting and disclosure risk (future work only)

- Point-in-time disclosure anomaly literature (no experiment claims in this draft)
- See [ACCOUNTING_RISK_ANOMALY_RESEARCH_PLAN.md](../research/ACCOUNTING_RISK_ANOMALY_RESEARCH_PLAN.md) for planned direction — **not completed research**

## Agent tooling (adjacent, not core contribution)

- MCP code-index servers — different problem (AST search vs artifact audit)
- Cursor Agent Skills — IndiciumForge ships in-repo skills as documentation-adjacent agent surface

## Positioning statement (draft)

IndiciumForge sits between **generic workflow engines** (flexible but schema-agnostic) and **trading/backtest platforms** (performance-centric). Its contribution is a **contract-first artifact layer** for evidence-first financial research with an explicit open-core/private-extension split and golden parity methodology.

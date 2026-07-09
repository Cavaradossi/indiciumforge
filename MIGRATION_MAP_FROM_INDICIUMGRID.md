# Migration Map From IndiciumGrid

IndiciumGrid is frozen at `indiciumgrid-golden-v1`. This map records what Lucerna v0.1 implements, defers, or treats as reference-only.

| IndiciumGrid Source | Lucerna Target | v0.1 Scope | Golden Scenario |
| --- | --- | --- | --- |
| `workflow.apply_market_gate` | `lucerna_workflow.market_gate.kernel` | implement | `strict_pass_mixed` |
| `workflow._market_gate_row` | market-gate row evaluation | implement | `strict_pass_mixed` |
| active-watch helpers | `lucerna_workflow.market_gate.active_watch` | implement | `empty_strict_c_grade` |
| calibration audit helper | `lucerna_workflow.market_gate.calibration` | implement | all market-gate scenarios |
| market-gate review path resolver | `lucerna_workflow.market_gate.resolver` | implement | `fallback_post_close` |
| `workflow.run_market_gate_workflow` | `lucerna_workflow.market_gate.runner` | implement | all market-gate scenarios |
| `REVIEW_COLUMNS` / `MARKET_GATE_COLUMNS` | `lucerna_core.labels` | implement compat labels | all market-gate scenarios |
| `THEME_STATE_RULES` | `lucerna_core.market.theme_rules` | metadata only | state/summary artifacts |
| provider registry | `lucerna_core.providers.registry` + `DataProviderPort` | implement v0.2.1 | contract tests |
| IG `data/registry.py` priority model | `lucerna_core.providers.registry_v2` + `DataProviderPortV2` | implement v0.9 | authority + fallback tests |
| LocalFixtureProvider | `lucerna_core.providers.local_fixture` | implement v0.2.1 | `tests/fixtures/ohlcv` |
| LocalFixtureProvider v2 | `lucerna_core.providers.local_fixture_v2` | implement v0.9 | session query + pack demo |
| `report/builder.py` `build_research_report()` | forward `ResearchDossier` model (v0.10+) | **Do not migrate as-is**; ADR-0019 rule 11 | not_in_v0.9 |
| `run_factor_scan` | `lucerna_core.factors.scan.FactorScanRunner` | implemented v0.7 integration | FACTOR_DEMO_MANIFEST |
| `FACTOR_CASES` / `validate_factor_cases` | golden + contract (planned) | inventory v0.2.2; IG cases reference-only | FACTOR_GOLDEN_MANIFEST |
| `evaluate_factor_parameters` | `lucerna_core.factors.evaluation` (planned) | inventory v0.2.2; calibrated params private-extension | defer v0.3+ |
| `factors.trading` / `trading_core` | workflow slice (planned) | inventory v0.2.2; trade-plan deferred | trade-plan deferred |
| intraday watch | future watch capability | not in v0.1 | none |
| factor tracking | future research/evidence audit capability | not in v0.2.x | `output/factor_tracking/` local |
| account analysis | future account evidence capability | not in v0.1 | none |
| catalyst/research experimental branch | future capture/evidence capability | not in v0.1 | none |
| `market_awareness` daily-review | `lucerna_workflow.market_awareness` + `lucerna workflow daily-review` | implemented v0.4.1 | `theme_state_ranking` + manifest audit |
| synthetic E2E workflow | `lucerna_workflow.e2e.synthetic` + `lucerna workflow synthetic-e2e` | implemented v0.5-alpha | DR -> MG -> audit summary demo |
| workflow chain skeleton | `lucerna_workflow.workflow_chain` + `lucerna workflow chain` | implemented v0.6 | DR -> post_close -> preopen -> MG |
| IG workflow stage folders | `lucerna_core.workflow` recipe stage ids | implemented v0.8 | `recipe_ashare_daily_v1.yaml`; ADR-0018 |
| `run_post_close_workflow` | recipe stage `discovery_post_close` + `CandidatePoolBuilderPort` / `ReviewBuilderPort` | implemented v0.10 wiring; production builder private v0.11+ | fake extension OSS CI |
| `run_preopen_workflow` | recipe stage `handoff_preopen` + `ReviewBuilderPort` / `MarketContextPort` | implemented v0.10 wiring; production builder private v0.11+ | fake extension OSS CI |
| `_build_workflow_review` | `ReviewBuilderPort` (private extension) | port + fake stub v0.10 | not in OSS |
| IG `output/workflows/` golden slices | `lucerna_core.parity` + local `reference_artifact_root` | implemented v0.11 | private-local harness; ADR-0022 |

Do not use line numbers as migration anchors. Use symbol names, scenario ids, and artifact names.

Factor-core rows above inventory IG reference surface only. Real long-structure detector internals,
calibrated thresholds, and proprietary alpha logic are **private-extension only** per
[ADR-0011](docs/decisions/ADR-0011-open-core-private-extension-boundary.md). Open-source Lucerna
may implement ports, schemas, demo detectors, and golden tools; private packs load through explicit
ports/config.

Forward capability schedule: [docs/MIGRATION_ROADMAP.md](docs/MIGRATION_ROADMAP.md).

## Local Ignored Assets Migration Inventory

IndiciumGrid keeps runtime evidence, local data, secrets, caches, and temporary research outputs out
of Git. These ignored paths are not source code, but some are important migration inputs for future
Lucerna slices. Review them before migrating factor-core, factor-tracking, provider, account, or
capture capabilities.

| Ignored/local path | Classification | Migration relevance | Handling rule |
| --- | --- | --- | --- |
| `output/factors/` | golden source | Factor case validation, cycle evaluation, factor scans, and historical review outputs for long-structure factors. | Use as candidate golden/reference artifacts for future factor-core or factor-review migration; do not commit raw full outputs. |
| `output/factor_tracking/` | golden source | Preserved-signal tracking, historical rebuilds, and replay outputs. | Use to define factor-tracking golden scenarios and artifact schemas before migrating tracking logic. |
| `output/workflows/` | golden source | Daily workflow artifacts containing candidate pools, factor names, factor families, review states, and market-gate inputs/outputs. | Select small representative scenarios; keep broad runtime output local. |
| `output/market_gate_audit/` | golden source | Historical market-gate audit runs and strict/watch/rejected evidence. | Use to extend market-gate and audit CLI scenarios when needed. |
| `output/market_awareness/` | golden source | Market fact snapshots and daily-review context used upstream of market-gate. | Reference only until market daily-review is explicitly in scope. |
| `output/research/` | golden source | Research bundle and spillover experiment artifacts. | Keep out of v0.2.x unless a research/evidence slice is approved. |
| `.indiciumgrid/tdx/` | local data | Local TDX-derived market data cache and normalized source files. | Do not migrate files; abstract provider contract, schema expectations, provenance, and fixture subsets. |
| `.indiciumgrid/cache/fundamentals/` | local data | Local fundamentals cache. | Use only to design provider/fundamentals fixtures; do not publish raw cache. |
| `.indiciumgrid/accounts/` | local data | Local account statements and derived account evidence. | Never publish; future account migration must use anonymized fixtures. |
| `.indiciumgrid/browser_profiles/` | do-not-migrate | Browser login/profile state. | Never migrate or inspect for open-source artifacts. |
| `.indiciumgrid/local_archive/` | mixed local archive | Historical cleanup/archive material; may include prior outputs, cache, and temporary files. | Review by manifest only; promote selected evidence into explicit golden fixtures if needed. |
| `tmp/` | temporary experiment | Scratch scripts, CSVs, KOL/catalyst probes, market-gate audits, and one-off analysis. | Triage manually: mark absorbed, discard, or convert to tracked design/test before migration. |
| `docs/*.pdf` | local reference | Third-party research PDFs such as QMJ source material. | Keep as local citation/artifact manifest only; do not commit PDFs. |
| `ledger.sqlite` | local state | Local ledger database. | Do not migrate; future ledger/account tests must use synthetic fixtures. |
| `.cursor/` | temporary experiment | IDE/agent plans and local coordination notes. | Do not commit unless intentionally distilled into project docs. |

Migration rule: ignored paths may provide evidence, schemas, or scenario seeds, but Lucerna should
only commit curated fixtures, synthetic/anonymized data, manifests, and tests. Raw local market
outputs, account data, secrets, browser state, caches, and third-party PDFs stay local.

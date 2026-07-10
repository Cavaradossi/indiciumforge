# IndiciumForge Migration Roadmap

Authoritative forward schedule and reconciliation against the original IndiciumForge migration plan
(v0.1 walking skeleton + incremental capability migration).

Principles: see [INDICIUMFORGE_CONSTITUTION.md](../INDICIUMFORGE_CONSTITUTION.md) and
[ADR-0011](decisions/ADR-0011-open-core-private-extension-boundary.md).
Migration preserves behavior, not implementation.

Reference pin:

```text
indiciumgrid @ indiciumgrid-golden-v1
```

---

## Completed trajectory (v0.1 -> v0.3)

| IndiciumForge version | Delivered | Original plan label |
| --- | --- | --- |
| v0.1 | MRC + market-gate walking skeleton | Phase 0-5 |
| v0.2 | artifact manifest / audit CLI | not in original v0.2 table |
| v0.2.1 | DataProviderPort v1 + LocalFixtureProvider | foundation; original v0.2 prerequisite |
| v0.2.2 | factor inventory + open-core boundary | privacy governance insert |
| v0.3 | FactorDetectorPort + demo + loading | original v0.3 partial: port only, not workflow chain |
| v0.4 | market daily-review upstream skeleton | original v0.2 daily-review (partial: ranking only) |
| v0.4.1 | daily-review CLI + manifest audit | original v0.2 daily-review operator loop |
| v0.5.0 (v0.5-alpha) | synthetic end-to-end workflow | demo DR -> MG -> audit summary |
| v0.6.0 | workflow chain skeleton | DR -> post_close -> preopen -> MG chain |

---

## Reconciliation: original plan vs actual vs forward

| Capability | Original plan version | Actual status | Forward target |
| --- | --- | --- | --- |
| market daily-review (`theme_state_ranking`) | v0.2 | `implemented_v0.4.1` skeleton + CLI | optional stub bundle v0.5+ |
| post-close -> preopen workflow chain | v0.3 | `implemented_v0.6` skeleton | production review generation v0.7+ |
| factor scan port (open source) | v0.3 (partial) | `implemented_v0.3` | done |
| proprietary long-structure detectors | implicit IG migration | `private_extension` | private packs only |
| intraday watch | v0.4 | not started | v0.5+ |
| factor tracking | v0.5 | not started | v0.6+ |
| account analysis | v0.6 | not started | v0.7+ |
| live data providers (TDX/OpenBB/...) | v0.2+ deps | contract/fixture only | adapter slices post-v0.4 |

---

## Current position

IndiciumForge remains on the migration main line:

- v0.1 walking skeleton delivered with golden + contract tests
- v0.2 through v0.3 prioritized foundation (artifact audit, provider port, open-core boundary,
  factor detector port) before upstream workflow generation
- v0.4 implemented market daily-review upstream skeleton per ADR-0013
- v0.4.1 added daily-review CLI and manifest audit for `market_awareness/` per ADR-0014
- v0.5-alpha (0.5.0) added synthetic E2E demo orchestration per ADR-0015
- v0.6.0 added workflow chain skeleton per ADR-0016
- Acceptable drifts: foundation-first reordering; ADR-0011 open-core insert; v0.3/v0.4 scope narrowing
  (port/demo only, no IG detector migration, no workflow chain)

Risk guard: do not export IG factor golden trees or migrate proprietary detector internals into the
open-source repo without a private factor pack (ADR-0011).

---

## Forward slice candidates (planning only)

Owner may reprioritize via future ADR. Default orientation:

### v0.4-a: market daily-review generation (completed)

Delivered in v0.4.0: skeleton `theme_state_ranking.csv` + state JSON via synthetic fixtures.
See ADR-0013.

### v0.4-b: daily-review CLI + manifest audit (completed)

Delivered in v0.4.1: `indiciumforge workflow daily-review`, unified `artifact list/audit` for
`market_awareness/{YYYYMMDD}/daily_review/`. See ADR-0014. Full IG daily-review bundle deferred.

### v0.5-alpha: synthetic end-to-end workflow (completed)

Delivered in v0.5.0: `indiciumforge workflow synthetic-e2e` runs daily-review skeleton -> market-gate
-> dual-stage audit -> `synthetic_e2e_summary.json` using open-source fixtures only.
See ADR-0015. Demo orchestration only; not production workflow chain.

### v0.6: workflow chain skeleton (completed)

Delivered in v0.6.0: `indiciumforge workflow chain` runs daily-review -> post_close -> preopen ->
market-gate -> dual-stage audit -> `workflow_chain_summary.json`. See ADR-0016.
Skeleton only; not production IG review generation.

### v0.7: private factor pack loading integration (completed)

Delivered in v0.7.0: `load_factor_pack`, `indiciumforge factor scan`, optional workflow chain
`factor_scan` stage, artifact schemas (`indiciumforge.factor_scan.v1`, summary v2). See ADR-0017.
Integration boundary only; no IG detector migration.

### v0.8: session-cyclic workflow model (completed)

Delivered in v0.8.0: `indiciumforge_core.workflow` contracts (`AssetDomain`, `SessionModel`,
`WorkflowRecipe`, `WorkflowCheckpoint`, `HandoffArtifact`), `indiciumforge.workflow_recipe.v1`,
A-share recipe fixture, `workflow_chain_summary.v3` session metadata. See ADR-0018 and
[WORKFLOW_SESSION_MODEL.md](WORKFLOW_SESSION_MODEL.md). No global/crypto execution; no data adapter.

### v0.9: session-aware data provider contract v2 (completed)

Delivered in v0.9.0: `DataProviderPortV2`, `ProviderRegistryV2`, `load_provider_pack`,
`indiciumforge provider inspect/fetch`, fake private provider fixture. See ADR-0019, ADR-0020,
[DESIGN_DEFECT_MIGRATION_AUDIT.md](DESIGN_DEFECT_MIGRATION_AUDIT.md), and
[PRIVATE_DATA_ADAPTER_TEMPLATE.md](PRIVATE_DATA_ADAPTER_TEMPLATE.md). Contract-only; no TDX sync,
network providers, or workflow/gate coupling.

Research dossier model explicitly **not_in_v0.9** (ADR-0019 rule 11). IG
`build_research_report()` registered as anti-inheritance risk only.

### v0.10: A-share private recipe integration (completed)

Delivered in v0.10.0: `indiciumforge_core.recipes` (ports, `RecipeRunner`, `StageInputResolver`,
`load_recipe_extension_pack`), fake A-share recipe extension, recipe-driven workflow chain CLI,
`workflow_chain_summary.v4`. See ADR-0021 and
[PRIVATE_ASHARE_RECIPE_TEMPLATE.md](PRIVATE_ASHARE_RECIPE_TEMPLATE.md). Wiring + fake runtime only;
production review builder deferred v0.11+.

### v0.11: private local parity harness (completed)

Delivered in v0.11.0: `indiciumforge_core.parity`, `indiciumforge parity run/report`, synthetic
`parity_reference_demo/`. See ADR-0022 and
[PRIVATE_PARITY_HARNESS_TEMPLATE.md](PRIVATE_PARITY_HARNESS_TEMPLATE.md). Local reference roots
only; no IG runtime; v1.0 sign-off deferred.

### v1.0-rc1: readiness milestone (completed)

| Item | Detail |
| --- | --- |
| Scope | Document validated IndiciumForge open-core v0.11.0 + private `indiciumforge-private-ashare` path |
| Evidence | Golden date `2026-07-03` parity `all_match: true`; blocked dates documented |
| Open-core | Docs only on `v0.11.0-parity-harness` baseline; annotated tag `v1.0-rc1` |
| Private | External `indiciumforge-private` readiness report + optional `v0.1.0-ig-output-parity` tag |
| Not claimed | Full IG replacement; `strict_count>0` coverage; incomplete frozen layouts |

Post-v1.0-rc1 route:

- Private production review builder (replace IG-output replay adapter)
- Optional v0.12.1 open-core comparator fix for IG list-shaped `candidate_pool_raw`
- TDX adapter and proprietary factors remain private packs only

### v1.0: signed (completed)

| Item | Detail |
| --- | --- |
| Scope | Sign open-core v0.11.0 + private `indiciumforge-private-ashare` migration path |
| Evidence | L1 golden + L2 parity demo + L3 private golden `2026-07-03` |
| Tag | `v1.0.0` on sign-off docs commit; preserves `v1.0-rc1`, `v0.11.0-parity-harness` |
| Not claimed | Full IG replacement; all frozen dates runnable; real `strict_count>0` private date |

### v1.1: post-sign-off (planning)

- Production private review builder
- Partial frozen layout support (`2026-06-24` fallback era, `2026-06-23` legacy post_close)
- Real `strict_count > 0` private parity when new IG output exists

### v0.10+: research dossier model (candidate, contract-only first)

| Item | Detail |
| --- | --- |
| Scope | `ResearchSubject` / `ResearchDossier` / `EvidenceModule` contracts — not IG `builder.py` port |
| Prerequisites | v0.8 session/checkpoint model; v0.9 provider v2 provenance |
| Open-core | ADR + register in first slice; no `600000_research` tree, no account paths |
| Explicit non-goals for v0.9 | No dossier runtime, no IG builder migration |

v0.11 production review generation may consume dossier/evidence modules as downstream recipe output.

### v0.10+: private TDX adapter (candidate)

| Item | Detail |
| --- | --- |
| Scope | Real TDX private adapter via `indiciumforge.data_providers` entry points |
| Prerequisites | v0.9 provider v2 contracts + pack loader |
| Open-core | Template docs only; no vipdoc paths in repo |

### v0.11+: production review generation (candidate, private recipe)

| Item | Detail |
| --- | --- |
| Scope | Wire discovery/handoff review generation as A-share recipe implementation |
| Prerequisites | v0.8 recipe model; optional v0.9 data adapters |
| Note | Not universal IndiciumForge core lifecycle; A-share recipe only |

### Later (original long-range table)

- v0.5+: intraday watch
- v0.6+: factor tracking evidence audit
- v0.7+: account analysis
- v1.0: replace IG for daily operations (all production capabilities + golden coverage)

---

## Version numbering policy

- IndiciumForge version labels track **delivered vertical slices**, not 1:1 mapping to the original
  migration plan version table
- Sub-versions (v0.2.1, v0.2.2) denote foundation or governance inserts between major slices
- Capability status changes require implementation + tests + docs per CAPABILITY_REGISTER promotion rule

---

## Related documents

- [CAPABILITY_REGISTER.md](../CAPABILITY_REGISTER.md) — capability status
- [MIGRATION_MAP_FROM_INDICIUMGRID.md](../MIGRATION_MAP_FROM_INDICIUMGRID.md) — symbol-level mapping
- [docs/FACTOR_GOLDEN_SCENARIO_PLAN.md](FACTOR_GOLDEN_SCENARIO_PLAN.md) — factor demo vs IG private-reference

# Lucerna Capability Register

Status values:

- `implemented_v1`: implemented, tested, and documented.
- `implemented_v0.2.2`: documented inventory/planning or boundary slice for v0.2.2 (no runtime code).
- `implemented_v0.3`: implemented factor detector port slice for v0.3.
- `implemented_v0.4`: implemented market daily-review upstream skeleton for v0.4.
- `implemented_v0.4.1`: daily-review CLI + manifest audit for market_awareness stage.
- `implemented_v0.5_alpha`: synthetic end-to-end workflow demo orchestration for v0.5-alpha.
- `implemented_v0.8`: session-cyclic workflow model contracts (ADR-0018).
- `implemented_v0.9`: session-aware data provider contract v2 (ADR-0019/0020).
- `implemented_v0.10`: A-share private recipe integration — ports, RecipeRunner, fake extension (ADR-0021).
- `implemented_v0.7`: private factor pack loading integration + workflow chain factor_scan stage.
- `implemented_v0.6`: workflow chain skeleton (post_close -> preopen -> market_gate).
- `private_extension`: intentionally outside the open-source repository; implemented only by private packs/plugins.
- `contract_only`: contract exists; production adapter or domain implementation is deferred.
- `technical_reserve`: intentionally reserved for later.
- `not_in_v0.1`: explicitly outside v0.1.
- `not_in_v0.2`: explicitly outside v0.2.
- `not_in_v0.2.x`: explicitly outside v0.2.x planning slices.
- `not_in_v0.3`: explicitly outside v0.3.

| Capability | Status | Boundary |
| --- | --- | --- |
| market-gate decision kernel | `implemented_v1` | Full strict/observation/active_watch/rejected/calibration semantics with golden parity. |
| artifact store + golden compare | `implemented_v1` | Local artifact I/O, semantic comparator, five golden scenarios. |
| artifact manifest / audit CLI | `implemented_v0.4.1` | Scan + validate market_gate and daily_review stage dirs; `lucerna artifact list/audit`; ADR-0008, ADR-0014. |
| data provider port | `implemented_v1` | `DataProviderPort` v1, `ProviderRegistry`, `LocalFixtureProvider`; synthetic fixtures only; ADR-0009. |
| session-aware data provider v2 | `implemented_v0.9` | `DataProviderPortV2`, `ProviderRegistryV2`, pack loader, `lucerna provider inspect/fetch`; ADR-0019/0020. |
| open-core/private-extension boundary | `implemented_v0.2.2` | ADR-0011; authoritative split between open core and private packs. |
| factor-core inventory + golden planning | `implemented_v0.2.2` | FACTOR_CORE_INVENTORY, FACTOR_GOLDEN_MANIFEST, scenario plan; ADR-0010. |
| factor detector port + demo detector | `implemented_v0.3` | `FactorDetectorPort`, demo detectors, registry, loading boundary; ADR-0010/0011/0012. |
| factor scan runner + artifact schema | `implemented_v0.3` | `FactorScanRunner`, factor_scan JSON/CSV writer; synthetic contract tests only. |
| private factor pack loading integration | `implemented_v0.7` | `load_factor_pack`, pack YAML, entry points; `lucerna factor scan`; ADR-0017. |
| workflow chain factor_scan stage | `implemented_v0.7` | Optional chain stage; summary v3; factor audit informational only; ADR-0017. |
| session-cyclic workflow model | `implemented_v0.8` | AssetDomain, SessionModel, WorkflowRecipe, checkpoint/handoff contracts; ADR-0018. |
| A-share private recipe integration | `implemented_v0.10` | `lucerna_core.recipes`, RecipeRunner, extension pack loader, recipe-driven chain CLI; ADR-0021. |
| proprietary long-structure detectors | `private_extension` | Real IG detector rules; private factor packs only. |
| market daily-review upstream | `implemented_v0.4.1` | Skeleton `theme_state_ranking` generation + `lucerna workflow daily-review` CLI; ADR-0013/0014; synthetic fixtures only. |
| synthetic end-to-end workflow | `implemented_v0.5_alpha` | `lucerna workflow synthetic-e2e`; DR -> MG -> audit summary; ADR-0015; fixture-only demo. |
| post-close / preopen workflow chain | `implemented_v0.6` | Skeleton chain: DR -> post_close -> preopen -> MG; `lucerna workflow chain`; ADR-0016; synthetic fixtures. |
| factor tracking evidence audit | `not_in_v0.2.x` | Sample-out tracking evidence; distinct from factor-core; future ADR. |
| factor trade-plan/evaluate/backtest adapter | `technical_reserve` | Trade-plan and evaluate outputs; defer past v0.3 core slice. |
| constitution + ADR + CI | `implemented_v1` | Constitution, ADR-0001..0021, ruff, pytest, CI workflow. |
| capture/evidence port | `contract_only` | No Firecrawl/Scrapling implementation in v0.1. |
| research engine port | `contract_only` | No RQAlpha/Qlib/backtrader implementation in v0.1. |
| research dossier model | `technical_reserve` | Forward `ResearchDossier` / `EvidenceModule` contracts; **not_in_v0.9**; A-share single-stock dossier is recipe/private extension only; ADR-0019 rule 11. |
| execution port | `technical_reserve` | No broker order placement. |
| workflow enrichment port | `technical_reserve` | Explanation only, never strict gate input. |
| intraday watch | `not_in_v0.1` | Future event recorder migration. |
| account analysis | `not_in_v0.1` | Future local account evidence domain. |
| catalyst/KOL ingestion | `not_in_v0.1` | Future capture/evidence adapter. |
| global cyclic workflow | `implemented_v0.8` | Session-cyclic contracts; recipe model; execution deferred. |
| ETF workflow | `not_in_v0.1` | Future capability. |

Promotion rule: a capability can advance only when implementation, tests, and documentation agree.

## Migration roadmap

Forward schedule and original-plan reconciliation:
[docs/MIGRATION_ROADMAP.md](docs/MIGRATION_ROADMAP.md).

## v0.2 vertical slice (completed)

- v0.2 delivered: **C** (artifact manifest / audit CLI).

## v0.2.1 vertical slice (completed)

- v0.2.1 delivered: **B** (provider contract v1 + local fixture provider).

## v0.2.2 vertical slice (completed)

- v0.2.2 delivered: factor-core **inventory + golden scenario planning** and **open-core/private-extension boundary** (docs only).

## v0.3 vertical slice (completed)

- v0.3 delivered: **factor detector port + demo detectors + scan runner + loading boundary** (not proprietary detector migration).

## v0.4 vertical slice (completed)

- v0.4 delivered: **market daily-review upstream skeleton** (`theme_state_ranking.csv` from synthetic fixtures).

## v0.4-b vertical slice (completed)

- v0.4.1 delivered: **daily-review CLI** (`lucerna workflow daily-review`) and **manifest audit**
  for `market_awareness/{YYYYMMDD}/daily_review/` (ADR-0014).

## v0.5-alpha vertical slice (completed)

- v0.5.0 delivered: **synthetic end-to-end workflow** (`lucerna workflow synthetic-e2e`);
  daily-review skeleton -> market-gate -> dual-stage audit -> summary JSON (ADR-0015).

## v0.6 vertical slice (completed)

- v0.6.0 delivered: **workflow chain skeleton** (`lucerna workflow chain`);
  daily-review -> post_close -> preopen -> market-gate -> audit -> summary JSON (ADR-0016).

## v0.7 vertical slice (completed)

- v0.7.0 delivered: **private factor pack loading integration** (`lucerna factor scan`) and
  **workflow chain factor_scan stage** (ADR-0017; demo/fake detectors in open-core CI only).

## v0.8 vertical slice (completed)

- v0.8.0 delivered: **session-cyclic workflow model** — recipe/checkpoint/handoff contracts,
  `lucerna.workflow_recipe.v1`, A-share recipe fixture, summary v3 session metadata (ADR-0018).

## v0.9 vertical slice (completed)

- v0.9.0 delivered: **session-aware data provider contract v2** — `DataProviderPortV2`,
  `ProviderRegistryV2`, provider pack loading, `lucerna provider inspect/fetch`, fake private
  adapter fixture (ADR-0019/0020). v1 provider port retained for compatibility.
- Research dossier model explicitly **not_in_v0.9** (ADR-0019 rule 11; forward v0.10+).

## v0.10 vertical slice (completed)

- v0.10.0 delivered: **A-share private recipe integration** — `lucerna_core.recipes` ports,
  `RecipeRunner`, `StageInputResolver`, recipe extension pack loader, fake A-share extension,
  recipe-driven workflow chain CLI (`--recipe`, `--recipe-extension-pack`),
  `workflow_chain_summary.v4` (ADR-0021; production review builder deferred v0.11+).

## v0.11+ forward candidate (planning only)

- private TDX adapter + `lucerna data sync`; research dossier contracts; production review generation (private recipe).

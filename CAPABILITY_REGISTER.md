# Lucerna Capability Register

Status values:

- `implemented_v1`: implemented, tested, and documented.
- `implemented_v0.2.2`: documented inventory/planning or boundary slice for v0.2.2 (no runtime code).
- `implemented_v0.3`: implemented factor detector port slice for v0.3.
- `planned_v0.3`: ADR proposed or accepted; implementation targeted for v0.3 vertical slice.
- `private_extension`: intentionally outside the open-source repository; implemented only by private packs/plugins.
- `contract_only`: contract exists; production adapter or domain implementation is deferred.
- `technical_reserve`: intentionally reserved for later.
- `not_in_v0.1`: explicitly outside v0.1.
- `not_in_v0.2`: explicitly outside v0.2.
- `not_in_v0.2.x`: explicitly outside v0.2.x planning slices.

| Capability | Status | Boundary |
| --- | --- | --- |
| market-gate decision kernel | `implemented_v1` | Full strict/observation/active_watch/rejected/calibration semantics with golden parity. |
| artifact store + golden compare | `implemented_v1` | Local artifact I/O, semantic comparator, five golden scenarios. |
| artifact manifest / audit CLI | `implemented_v1` | Read-only scan + validate market-gate stage dirs; `lucerna artifact list/audit`; ADR-0008. |
| data provider port | `implemented_v1` | `DataProviderPort` v1, `ProviderRegistry`, `LocalFixtureProvider`; synthetic fixtures only; ADR-0009. |
| open-core/private-extension boundary | `implemented_v0.2.2` | ADR-0011; authoritative split between open core and private packs. |
| factor-core inventory + golden planning | `implemented_v0.2.2` | FACTOR_CORE_INVENTORY, FACTOR_GOLDEN_MANIFEST, scenario plan; ADR-0010. |
| factor detector port + demo detector | `implemented_v0.3` | `FactorDetectorPort`, demo detectors, registry, loading boundary; ADR-0010/0011/0012. |
| factor scan runner + artifact schema | `implemented_v0.3` | `FactorScanRunner`, factor_scan JSON/CSV writer; synthetic contract tests only. |
| proprietary long-structure detectors | `private_extension` | Real IG detector rules; private factor packs only. |
| factor tracking evidence audit | `not_in_v0.2.x` | Sample-out tracking evidence; distinct from factor-core; future ADR. |
| factor trade-plan/evaluate/backtest adapter | `technical_reserve` | Trade-plan and evaluate outputs; defer past v0.3 core slice. |
| constitution + ADR + CI | `implemented_v1` | Constitution, ADR-0001..0012 (0012 proposed), ruff, pytest. |
| capture/evidence port | `contract_only` | No Firecrawl/Scrapling implementation in v0.1. |
| research engine port | `contract_only` | No RQAlpha/Qlib/backtrader implementation in v0.1. |
| execution port | `technical_reserve` | No broker order placement. |
| workflow enrichment port | `technical_reserve` | Explanation only, never strict gate input. |
| market daily-review upstream | `not_in_v0.2` | Explicitly deferred; depends on provider + manifest foundations. |
| intraday watch | `not_in_v0.1` | Future event recorder migration. |
| account analysis | `not_in_v0.1` | Future local account evidence domain. |
| catalyst/KOL ingestion | `not_in_v0.1` | Future capture/evidence adapter. |
| global cyclic workflow | `not_in_v0.1` | Future scheduler and session model. |
| ETF workflow | `not_in_v0.1` | Future capability. |

Promotion rule: a capability can advance only when implementation, tests, and documentation agree.

## v0.2 vertical slice (completed)

- v0.2 delivered: **C** (artifact manifest / audit CLI).

## v0.2.1 vertical slice (completed)

- v0.2.1 delivered: **B** (provider contract v1 + local fixture provider).

## v0.2.2 vertical slice (completed)

- v0.2.2 delivered: factor-core **inventory + golden scenario planning** and **open-core/private-extension boundary** (docs only).

## v0.3 vertical slice (completed)

- v0.3 delivered: **factor detector port + demo detectors + scan runner + loading boundary** (not proprietary detector migration).

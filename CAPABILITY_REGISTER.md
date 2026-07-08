# Lucerna Capability Register

Status values:

- `implemented_v1`: implemented, tested, and documented for v0.1.
- `contract_only`: contract exists; production adapter or domain implementation is deferred.
- `technical_reserve`: intentionally reserved for later.
- `not_in_v0.1`: explicitly outside v0.1.

| Capability | v0.1 Status | Boundary |
| --- | --- | --- |
| market-gate decision kernel | `implemented_v1` | Full strict/observation/active_watch/rejected/calibration semantics with golden parity. |
| artifact store + golden compare | `implemented_v1` | Local artifact I/O, semantic comparator, five golden scenarios. |
| constitution + ADR + CI | `implemented_v1` | Constitution, ADR-0001..0007, ruff, pytest. |
| data provider port | `contract_only` | Contract tests with fixture registry only. |
| capture/evidence port | `contract_only` | No Firecrawl/Scrapling implementation in v0.1. |
| research engine port | `contract_only` | No RQAlpha/Qlib/backtrader implementation in v0.1. |
| execution port | `technical_reserve` | No broker order placement. |
| workflow enrichment port | `technical_reserve` | Explanation only, never strict gate input. |
| intraday watch | `not_in_v0.1` | Future event recorder migration. |
| factor tracking | `not_in_v0.1` | Future preserved-signal/evidence audit migration. |
| account analysis | `not_in_v0.1` | Future local account evidence domain. |
| catalyst/KOL ingestion | `not_in_v0.1` | Future capture/evidence adapter. |
| global cyclic workflow | `not_in_v0.1` | Future scheduler and session model. |
| ETF workflow | `not_in_v0.1` | Future capability. |

Promotion rule: a capability can advance only when implementation, tests, and documentation agree.

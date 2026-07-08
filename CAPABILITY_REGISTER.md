# Lucerna Capability Register

Status values:

- `implemented_v1`: implemented, tested, and documented for v0.1.
- `contract_only`: contract exists; production adapter or domain implementation is deferred.
- `planned_v0.2.1`: explicitly deferred follow-up after v0.2.
- `technical_reserve`: intentionally reserved for later.
- `not_in_v0.1`: explicitly outside v0.1.
- `not_in_v0.2`: explicitly outside v0.2.

| Capability | Status | Boundary |
| --- | --- | --- |
| market-gate decision kernel | `implemented_v1` | Full strict/observation/active_watch/rejected/calibration semantics with golden parity. |
| artifact store + golden compare | `implemented_v1` | Local artifact I/O, semantic comparator, five golden scenarios. |
| artifact manifest / audit CLI | `implemented_v1` | Read-only scan + validate market-gate stage dirs; `lucerna artifact list/audit`; ADR-0008. |
| constitution + ADR + CI | `implemented_v1` | Constitution, ADR-0001..0008, ruff, pytest. |
| data provider port | `contract_only` (`planned_v0.2.1`) | Contract tests with fixture registry only. v0.2.1: Protocol v1 + LocalFixtureProvider; no workflow wiring. |
| capture/evidence port | `contract_only` | No Firecrawl/Scrapling implementation in v0.1. |
| research engine port | `contract_only` | No RQAlpha/Qlib/backtrader implementation in v0.1. |
| execution port | `technical_reserve` | No broker order placement. |
| workflow enrichment port | `technical_reserve` | Explanation only, never strict gate input. |
| market daily-review upstream | `not_in_v0.2` | Explicitly deferred; depends on provider + manifest foundations. |
| intraday watch | `not_in_v0.1` | Future event recorder migration. |
| factor tracking | `not_in_v0.1` | Future preserved-signal/evidence audit migration. |
| account analysis | `not_in_v0.1` | Future local account evidence domain. |
| catalyst/KOL ingestion | `not_in_v0.1` | Future capture/evidence adapter. |
| global cyclic workflow | `not_in_v0.1` | Future scheduler and session model. |
| ETF workflow | `not_in_v0.1` | Future capability. |

Promotion rule: a capability can advance only when implementation, tests, and documentation agree.

## v0.2 vertical slice (completed)

- v0.2 delivered: **C** (artifact manifest / audit CLI).
- v0.2.1 candidate: **B** (provider contract v1 + local fixture).
- Explicitly not in v0.2: **A** (market daily-review upstream).

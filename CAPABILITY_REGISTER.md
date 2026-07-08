# Lucerna Capability Register

Status values:

- `implemented_v1`: implemented, tested, and documented.
- `contract_only`: contract exists; production adapter or domain implementation is deferred.
- `planned_v0.2.1`: explicitly deferred follow-up (completed for data provider in v0.2.1).
- `technical_reserve`: intentionally reserved for later.
- `not_in_v0.1`: explicitly outside v0.1.
- `not_in_v0.2`: explicitly outside v0.2.

| Capability | Status | Boundary |
| --- | --- | --- |
| market-gate decision kernel | `implemented_v1` | Full strict/observation/active_watch/rejected/calibration semantics with golden parity. |
| artifact store + golden compare | `implemented_v1` | Local artifact I/O, semantic comparator, five golden scenarios. |
| artifact manifest / audit CLI | `implemented_v1` | Read-only scan + validate market-gate stage dirs; `lucerna artifact list/audit`; ADR-0008. |
| data provider port | `implemented_v1` | `DataProviderPort` v1, `ProviderRegistry`, `LocalFixtureProvider`; synthetic fixtures only; ADR-0009. |
| constitution + ADR + CI | `implemented_v1` | Constitution, ADR-0001..0009, ruff, pytest. |
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

## v0.2.1 vertical slice (completed)

- v0.2.1 delivered: **B** (provider contract v1 + local fixture provider).
- Explicitly not in v0.2.1: live/network adapters, workflow wiring, market daily-review upstream.

# ADR-0020: Session-Aware Data Provider Contract v2 v0.9

Status: accepted

## Context

- ADR-0009 delivered `DataProviderPort` v1 (OHLCV + ordered fallback + `LocalFixtureProvider`).
- ADR-0018 delivered session-cyclic workflow contracts (`AssetDomain`, `WorkflowCheckpoint`, recipes).
- ADR-0019 binds anti-inheritance rules from IndiciumGrid.
- v0.9 must prepare private adapter integration without TDX sync, network providers, or gate coupling.

## Decision

IndiciumForge v0.9.0 delivers **Session-Aware Data Provider Contract v2**:

### New modules (`indiciumforge_core.providers`)

- `capabilities.py` — `DataKind`, `LatencyProfile`, `ProviderAuthorityLevel`, `ProviderCapability`
- `query.py` — `DataQuery` with session/checkpoint fields; `from_checkpoint()` helper
- `result.py` — `ProviderProvenance`, `ProviderResult`, `ProviderFailureStatus`
- `contracts_v2.py` — `DataProviderPortV2` protocol
- `registry_v2.py` — authority-aware fetch with fallback and cross-check warnings
- `pack.py` / `config.py` — `load_provider_pack()` mirroring v0.7 factor pack pattern
- `local_fixture_v2.py` — fixture provider implementing v2

### Entry points

- Group: `indiciumforge.data_providers`
- No `sys.path` injection; editable install for private packs

### CLI

- `indiciumforge provider inspect` — list providers and capabilities
- `indiciumforge provider fetch` — single-query smoke (fixture/fake only in open core)

### v1 compatibility

- `DataProviderPort` v1 and `ProviderRegistry` remain unchanged.
- `FactorScanRunner` unchanged in v0.9 (contract-only boundary).

## ProviderProvenance policy

- Committed artifact payloads use opaque ids (`provider_id`, `cache_policy`, `quota_policy`).
- Absolute filesystem paths MUST NOT appear in provenance JSON written to artifacts or tests.

## Out of scope (v0.9)

- Real TDX sync, vipdoc, `.indiciumgrid` cache
- Network providers (OpenBB, yfinance, pytdx)
- `indiciumforge data sync`
- Workflow chain / market_gate integration
- Crypto trading or derivatives execution

## Consequences

- CAPABILITY_REGISTER: session-aware data provider v2 -> `implemented_v0.9`
- MIGRATION_ROADMAP: v0.10 private TDX adapter; v0.11 production review
- [`docs/PRIVATE_DATA_ADAPTER_TEMPLATE.md`](../PRIVATE_DATA_ADAPTER_TEMPLATE.md) for private packs

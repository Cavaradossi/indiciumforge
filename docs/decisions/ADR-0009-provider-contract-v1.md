# ADR-0009: Provider Contract v1 and Local Fixture Provider

Status: accepted

## Context

- `DataProviderPort` was a minimal stub (`provenance()` only) while contract tests assumed `supports()` and `fetch_ohlcv()`.
- `ProviderRegistry` lived in tests, not in reusable core code.
- IndiciumGrid ignored local paths (`.indiciumgrid/tdx/`, `.indiciumgrid/cache/fundamentals/`, `output/`, `tmp/`) may inform schema and provenance semantics but must not be copied into IndiciumForge Git.

## Decision

- Formalize `DataProviderPort` v1 with `supports()` and `fetch_ohlcv()` returning OHLCV frames plus `Provenance`.
- Move `ProviderRegistry` into `indiciumforge_core.providers.registry` with ordered fallback and warning preservation.
- Add `LocalFixtureProvider` reading curated synthetic CSV fixtures from an explicit `fixture_root`.
- Fixture path convention: `{fixture_root}/{exchange}_{asset_type}_{code}.csv`.

## Scope (v0.2.1)

- OHLCV contract only (`date`, `open`, `high`, `low`, `close`, `volume`).
- Hand-authored synthetic fixtures under `tests/fixtures/ohlcv/` per MIGRATION_MAP Local Ignored Assets Migration Inventory rules.

## Out of scope (v0.2.1)

- live/network providers (OpenBB, yfinance, Zhitu, TDX production adapters).
- workflow wiring (`market_gate` runner still reads file inputs only).
- market daily-review upstream generation.
- bulk copy or commit of ignored local market/account/cache data.

## Consequences

- CAPABILITY_REGISTER: data provider port -> `implemented_v1`.
- MIGRATION_MAP: provider registry + LocalFixtureProvider rows -> `implement v0.2.1`.
- Tests: contract coverage for registry fallback and fixture provider.

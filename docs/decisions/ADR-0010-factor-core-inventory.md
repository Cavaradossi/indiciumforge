# ADR-0010: Factor Core Inventory and Golden Planning

Status: proposed

## Context

- IndiciumGrid factor-core (`factors.mining`, `case_library`) is distinct from `factor_tracking` and market-gate.
- IG ignored paths (`output/factors/`, `.indiciumgrid/tdx/`) inform schema and scenario seeds but must not enter Lucerna Git as raw data.
- Lucerna v0.2.1 delivered provider contract v1; factor scan logic is not yet migrated.

## Decision

- v0.2.2 delivers factor-core inventory, FACTOR_GOLDEN_MANIFEST.yaml, and golden scenario planning docs only.
- Factor-core implementation (scan kernel, export script, golden parity tests) is deferred to v0.3.
- Factor-tracking remains a separate capability with its own future ADR and golden manifest.

## Scope (v0.2.2)

- Taxonomy and artifact family inventory in docs/FACTOR_CORE_INVENTORY.md.
- Five `planned_export` scenarios in FACTOR_GOLDEN_MANIFEST.yaml.
- Comparison strategy in docs/FACTOR_GOLDEN_SCENARIO_PLAN.md.

## Out of scope (v0.2.2)

- `lucerna_core.factors` implementation.
- `scripts/export_golden_factor.py`.
- `tests/golden/factor_core/` exported trees.
- Factor CLI, workflow wiring, trade-plan, factor-tracking.
- Bulk copy from `output/factors/`, TDX cache, or `tmp/`.

## Consequences

- CAPABILITY_REGISTER: factor-core inventory -> `implemented_v0.2.2`; factor-core implementation -> `planned_v0.3`.
- MIGRATION_MAP: additive factor-core rows; Local Ignored Assets Inventory preserved.
- v0.3 export must use synthetic OHLCV inputs per MIGRATION_MAP handling rules.

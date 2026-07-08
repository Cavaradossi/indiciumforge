# ADR-0010: Factor Core Inventory and Golden Planning

Status: accepted

## Context

- IndiciumGrid factor-core (`factors.mining`, `case_library`) is distinct from `factor_tracking` and market-gate.
- IG ignored paths (`output/factors/`, `.indiciumgrid/tdx/`) inform schema and scenario seeds but must not enter Lucerna Git as raw data.
- Lucerna v0.2.1 delivered provider contract v1; v0.3 delivered open-source factor detector port and demo detectors.

## Decision

- v0.2.2 delivered factor-core inventory, FACTOR_GOLDEN_MANIFEST.yaml, and golden scenario planning docs only.
- v0.3 delivered `FactorDetectorPort`, demo detectors, registry, scan runner, and private-pack loading boundary.
- IG golden export and proprietary detector parity remain deferred to private extension packs.
- Factor-tracking remains a separate capability with its own future ADR and golden manifest.

## Open-source boundary

- v0.2.2 inventory records IndiciumGrid private/reference factor surface; it is not an
  open-source implementation promise.
- Lucerna open-source factor-core may include taxonomy compatibility, factor signal artifact
  schema, `FactorDetectorPort`, synthetic/demo detectors, and golden comparison tools.
- Proprietary long-structure detector rules remain in private factor packs. See ADR-0011.
- v0.3 must not directly migrate real detector internals. It should first define the detector
  port, plugin/private-pack loading mechanism, and demo detector.

## Scope (v0.2.2)

- Taxonomy and artifact family inventory in docs/FACTOR_CORE_INVENTORY.md.
- Five `private_reference` scenarios in FACTOR_GOLDEN_MANIFEST.yaml.
- Comparison strategy in docs/FACTOR_GOLDEN_SCENARIO_PLAN.md.

## Scope (v0.3)

- `lucerna_core.factors` models, port, registry, scan runner, artifact schema.
- Demo detectors and contract tests on synthetic fixtures.
- Private-pack loading via config and entry points. See ADR-0012.

## Out of scope (v0.2.2)

- `lucerna_core.factors` implementation.
- `scripts/export_golden_factor.py`.
- `tests/golden/factor_core/` exported trees.
- Factor CLI, workflow wiring, trade-plan, factor-tracking.
- Bulk copy from `output/factors/`, TDX cache, or `tmp/`.

## Consequences

- CAPABILITY_REGISTER: factor-core inventory -> `implemented_v0.2.2`; factor detector port ->
  `implemented_v0.3`; proprietary detectors -> `private_extension`.
- MIGRATION_MAP: additive factor-core rows; Local Ignored Assets Inventory preserved.
- Open-source demo scenarios live in FACTOR_DEMO_MANIFEST.yaml; IG scenarios remain private reference.
- Open-core/private-extension split is authoritative in ADR-0011.

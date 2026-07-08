# ADR-0012: Factor Detector Port v0.3

Status: proposed

## Context

- ADR-0010 and ADR-0011 established factor-core inventory and the open-core/private-extension split.
- Lucerna v0.2.1 provides `DataProviderPort` and synthetic OHLCV fixtures.
- v0.3 must deliver the open-source runtime slice without copying IndiciumGrid long-structure
  detector internals.

## Decision

Lucerna v0.3 implements in `lucerna_core.factors`:

- domain models: `FactorSignal`, `FactorScanResult`
- `FactorDetectorPort` protocol
- `FactorDetectorRegistry` with duplicate-name rejection and warning aggregation
- `FactorScanRunner` orchestrating provider fetch + detector runs
- factor scan artifact schema and writer helpers
- two neutral demo detectors: `demo_volume_breakout`, `demo_quiet_accumulation`
- private-pack loading boundary via YAML config and optional setuptools entry points
  (`lucerna.factor_detectors`)

Demo detectors use toy/synthetic rules only. They are not compatible implementations of IG
private factors.

## Demo detector scope

| Detector | Purpose |
| --- | --- |
| `demo_volume_breakout` | Illustrates volume spike + price-up toy rule |
| `demo_quiet_accumulation` | Illustrates low-volume range-compression toy rule |

Open-source tests use `tests/fixtures/ohlcv/sse_stock_DEMO001.csv` and
`sse_stock_DEMO002.csv`. Demo scenarios are listed in `FACTOR_DEMO_MANIFEST.yaml`.

## Private-pack contract

Private factor packs may register detectors through:

1. YAML config (`module` + `class` entries) loaded by `load_detectors_from_config`
2. setuptools entry points in group `lucerna.factor_detectors`

Lucerna open core does not ship IG factor name -> implementation mappings. Private packs load
through explicit config or entry points only.

## Out of scope (v0.3)

- Real IG long-structure detectors
- `scripts/export_golden_factor.py` against IG `FACTOR_CASES`
- `tests/golden/factor_core/` IG-named export trees
- Factor CLI, workflow wiring, trade-plan, factor-tracking
- Live providers and private pack implementations

## Consequences

- CAPABILITY_REGISTER: factor detector port + demo detector -> `implemented_v0.3`
- `FACTOR_GOLDEN_MANIFEST.yaml` IG scenarios remain `private_reference` until a private pack
  provides detectors
- IG golden parity export is deferred to private extension or a future slice

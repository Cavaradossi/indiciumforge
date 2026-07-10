# Factor Golden Scenario Plan

Reference manifests:

- [FACTOR_DEMO_MANIFEST.yaml](../FACTOR_DEMO_MANIFEST.yaml) — open-source demo scenarios (v0.3)
- [FACTOR_GOLDEN_MANIFEST.yaml](../FACTOR_GOLDEN_MANIFEST.yaml) — IG private/reference scenarios

IndiciumForge v0.3 implements demo detector contract tests. IG golden export remains private-reference
until a private factor pack provides real detectors.

## Open-source demo scenarios (v0.3)

| id | Seed | Expectation | Purpose |
| --- | --- | --- | --- |
| `demo_volume_breakout_hit` | synthetic DEMO001 | hit | demo volume spike rule |
| `demo_volume_breakout_miss` | synthetic DEMO001 subset | miss | insufficient bars |
| `demo_quiet_accumulation_hit` | synthetic DEMO002 | hit | demo quiet range rule |
| `demo_multi_detector_scan` | synthetic dual-asset | dual hit | scan runner integration |

Contract tests live under `tests/contract/test_factor_*.py` with fixtures in
`tests/fixtures/ohlcv/` and `tests/fixtures/factor_detectors.yaml`.

## IG private-reference scenarios (not open-source golden)

| id | Seed | Expectation | Purpose |
| --- | --- | --- | --- |
| `locked_float_advance_hit` | FACTOR_CASES 688498 | hit | private/reference only |
| `clustered_limit_up_hit` | FACTOR_CASES 600330 | hit | private/reference only |
| `clustered_limit_up_miss` | FACTOR_CASES 002969 | miss | private/reference only |
| `yang_line_density_boundary` | FACTOR_CASES 603778 | miss | private/reference only |
| `multi_primary_scan` | IG synthetic test | dual hit | private/reference only |

These scenarios require a private factor pack. IndiciumForge open core does not export or implement them.

## Directory layout (future private-pack golden export)

```text
tests/golden/factor_core/{scenario_id}/
  inputs/
    ohlcv/
      {exchange}_{asset_type}_{code}.csv
  expected/
    factor_scan/
      factor_scan_{as_of}.json
      factor_scan_{as_of}.csv
    meta.json
```

v0.3 does not create this tree for IG scenarios. Demo validation uses contract tests only.

## Comparison levels

Extend [GOLDEN_ARTIFACT_TEST_PLAN.md](../GOLDEN_ARTIFACT_TEST_PLAN.md) principles:

### Schema equality

- Required files exist under `expected/factor_scan/`.
- JSON keys present: `as_of`, signals or rows list, warnings.
- CSV columns include at minimum: code, factor, as_of, matched, score, metrics.

### Semantic equality

- Demo scenarios: `matched` aligns with `expectation` (hit/miss).
- IG scenarios: deferred to private extension packs.

### Unstable field exclusions

Do not byte-compare:

- `data_path`, absolute filesystem paths
- `updated_at`, run timestamps
- provider provenance paths

## Out of scope

- `factor_trade_plan_*` and `factor_trade_evaluate_*` artifacts (v0.3+).
- `factor_tracking` outputs under `output/factor_tracking/` (separate capability).
- Workflow or CLI integration.

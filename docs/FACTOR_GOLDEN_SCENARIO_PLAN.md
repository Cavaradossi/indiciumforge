# Factor Golden Scenario Plan

Reference: [FACTOR_GOLDEN_MANIFEST.yaml](../FACTOR_GOLDEN_MANIFEST.yaml)

Lucerna v0.2.2 plans factor-core golden scenarios. Export and parity tests are deferred to v0.3.

## Scenario set (planned_export)

| id | Seed | Expectation | Purpose |
| --- | --- | --- | --- |
| `locked_float_advance_hit` | FACTOR_CASES 688498 | hit | primary state-factor detection |
| `clustered_limit_up_hit` | FACTOR_CASES 600330 | hit | event-factor detection |
| `clustered_limit_up_miss` | FACTOR_CASES 002969 | miss | hard-negative non-detection |
| `yang_line_density_boundary` | FACTOR_CASES 603778 | miss | threshold edge case |
| `multi_primary_scan` | IG synthetic test | dual hit | two-asset scan parity |

## Directory layout (v0.3 export target)

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

Case-library scenarios use one OHLCV file per `code`. `multi_primary_scan` uses two files
(688498, 600330). Inputs must be synthetic OHLCV with columns
`date,open,high,low,close,volume` (same contract as provider v0.2.1).

Do not copy from `output/factors/`, `.indiciumgrid/tdx/`, or IG case-cache directories.

## Comparison levels

Extend [GOLDEN_ARTIFACT_TEST_PLAN.md](../GOLDEN_ARTIFACT_TEST_PLAN.md) principles:

### Schema equality

- Required files exist under `expected/factor_scan/`.
- JSON keys present: `as_of`, signals or rows list, warnings.
- CSV columns include at minimum: code, factor, as_of (exact column names follow IG compat labels in v0.3).

### Semantic equality

- Case scenarios: `matched` / signal presence aligns with `expectation` (hit/miss/context).
- `multi_primary_scan`: signal set includes `(688498, locked_float_advance)` and
  `(600330, clustered_limit_up)`.
- Score and metrics: compare rounded values or presence of key metric fields; tolerate float noise.

### Unstable field exclusions

Do not byte-compare:

- `data_path`, absolute filesystem paths
- `updated_at`, run timestamps
- provider provenance paths

Classify differences as `match`, `intentional_change`, or `unsupported_gap` per Constitution.

## Export prerequisites (v0.3)

1. `lucerna_core.factors` scan kernel implemented.
2. `scripts/export_golden_factor.py` reads FACTOR_GOLDEN_MANIFEST.yaml and writes curated synthetic inputs.
3. Provider input via explicit `fixture_root` or per-scenario OHLCV under `inputs/ohlcv/`.
4. No bulk copy from ignored local paths.

## Out of scope

- `factor_trade_plan_*` and `factor_trade_evaluate_*` artifacts (v0.3+).
- `factor_tracking` outputs under `output/factor_tracking/` (separate capability).
- Workflow or CLI integration.

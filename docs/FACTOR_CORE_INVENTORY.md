# Factor Core Inventory

Reference: frozen `indiciumgrid @ indiciumgrid-golden-v1`

Lucerna v0.3 delivered the open-source factor detector port and demo detectors; proprietary IG
detectors remain `private_extension`. See [FACTOR_GOLDEN_MANIFEST.yaml](../FACTOR_GOLDEN_MANIFEST.yaml) and
[ADR-0010](decisions/ADR-0010-factor-core-inventory.md), [ADR-0011](decisions/ADR-0011-open-core-private-extension-boundary.md), and [ADR-0012](decisions/ADR-0012-factor-detector-port-v0.3.md).

## Scope boundary

| Domain | IG entry | Lucerna v0.2.2 | Lucerna v0.3 target |
| --- | --- | --- | --- |
| Factor core | `indiciumgrid.factors.mining`, `case_library` | inventory + golden plan | `lucerna_core.factors` (TBD) |
| Factor tracking | `indiciumgrid.factor_tracking` | out of scope | separate capability / ADR later |
| Market gate | `workflow.run_market_gate_workflow` | implemented_v1 | unchanged |

Factor core produces research signals and scan evidence. It does not place trades, tune parameters
automatically, or replace factor-tracking sample-out monitoring.

## Open-source boundary

- The 10 IndiciumGrid long-structure factors listed here are private/reference inventory for
  migration planning.
- Listing factor names and compatibility labels does not mean Lucerna will publish their detector
  internals.
- Open-source Lucerna should define detector ports, signal schemas, artifact contracts, synthetic
  examples, and comparison rules.
- Real detector implementations and calibrated thresholds remain in private factor packs.
- If public release requires hiding factor names too, replace private factor names with neutral
  placeholders before publishing or squashing history.

## Open-source v0.3 modules

| Module | Purpose |
| --- | --- |
| `lucerna_core.factors.models` | `FactorSignal`, `FactorScanResult` |
| `lucerna_core.factors.ports` | `FactorDetectorPort` |
| `lucerna_core.factors.registry` | `FactorDetectorRegistry` |
| `lucerna_core.factors.loading` | config/entry-point private-pack loading boundary |
| `lucerna_core.factors.scan` | `FactorScanRunner` |
| `lucerna_core.factors.artifacts` | factor_scan JSON/CSV schema and writer |
| `lucerna_core.factors.demo.*` | neutral demo detectors only |

Demo scenarios: [FACTOR_DEMO_MANIFEST.yaml](../FACTOR_DEMO_MANIFEST.yaml).
IG private/reference scenarios: [FACTOR_GOLDEN_MANIFEST.yaml](../FACTOR_GOLDEN_MANIFEST.yaml).

## Symbol inventory

Source: `indiciumgrid.factors.mining` (`FactorName`, taxonomy dicts).

### Primary factors (7)

| Factor | Chinese label (compat) | Horizon | Type |
| --- | --- | --- | --- |
| `locked_float_advance` | 量能天花板上涨 | long | state_factor |
| `ignition_from_quiet_base` | 低换手基底首次放量 | medium | event_factor |
| `clustered_limit_up` | 非连续涨停簇 | medium | event_factor |
| `persistent_low_volume_grind` | 持续缩量慢牛 | long | state_factor |
| `capitulation_volume_shock` | 底部天量冲击 | long | event_factor |
| `dormant_ignition_memory` | 潜伏点火记忆 | long | state_factor |
| `bottom_repeated_thrust` | 底部反复试盘 | medium | event_factor |

### Auxiliary factors (3)

| Factor | Chinese label (compat) | Horizon | Type |
| --- | --- | --- | --- |
| `yang_line_density` | 阳线密度 | medium | state_factor |
| `absorption_on_pullback` | 下跌不缩量/承接吸收 | medium | state_factor |
| `high_turnover_absorption` | 高换手承接吸收 | medium | event_factor |

### Taxonomy notes

- Canonical family: `long_structure` (legacy alias `black_horse` in older IG outputs).
- `FACTOR_SIGNAL_EMISSION_RULE` in IG defines per-factor last-bar emission semantics; preserve in v0.3.
- Chinese labels are a temporary compat layer (same pattern as market-gate column names).

## IG source to Lucerna target

| IndiciumGrid source | Future Lucerna target | v0.2.2 | Golden / test anchor |
| --- | --- | --- | --- |
| `run_factor_scan` | `lucerna_core.factors.scan` | implemented v0.3 | FACTOR_DEMO_MANIFEST |
| `evaluate_factor_parameters` | `lucerna_core.factors.evaluation` | inventory | defer to v0.3+ |
| `FACTOR_CASES` / `validate_factor_cases` | golden + contract | inventory | case-library scenarios |
| `factors.trading` / `trading_core` | workflow slice | inventory | trade-plan deferred |
| `factor_tracking` | separate capability | not in v0.2.2 | `output/factor_tracking/` local only |

## Artifact families

Source: `indiciumgrid.factors._outputs` and IG factor tests. Document shape only; do not commit raw
`output/factors/` trees.

| Artifact stem | Contents | v0.3 golden relevance |
| --- | --- | --- |
| `factor_scan_{as_of}` | signals CSV/JSON/MD, diagnostics | primary |
| `factor_case_validation_{date}` | curated case rows, pass/fail status | case-library scenarios |
| `factor_trade_plan_{as_of}` | trade plan rows | v0.3+ only |
| `factor_trade_evaluate_{start}_{end}` | evaluate trades + summary | v0.3+ only |

Expected scan signal fields (semantic compare targets for v0.3):

- `code`, `factor`, `factor_label`, `as_of`, `score`, `metrics`, `matched` (case validation)

Unstable fields to exclude from byte compare: `data_path`, absolute paths, `updated_at`, run timestamps.

## Curated case library (IG seeds)

Source: `indiciumgrid.factors.case_library.FACTOR_CASES` (12 cases).

Tags: `strong_positive`, `boundary`, `hard_negative`.
Expectations: `hit`, `miss`, `context`.

v0.2.2 selects five cases for the first golden export batch (see FACTOR_GOLDEN_MANIFEST.yaml).

## Ignored local assets (mandatory)

Per [MIGRATION_MAP_FROM_INDICIUMGRID.md](../MIGRATION_MAP_FROM_INDICIUMGRID.md) Local Ignored Assets
Migration Inventory:

| Path | Factor-core handling |
| --- | --- |
| `output/factors/` | Reference artifact shape and scenario selection only; no raw full outputs in Git |
| `output/factor_tracking/` | Factor-tracking domain only; not factor-core v0.2.2 |
| `.indiciumgrid/tdx/` | Schema/provenance reference; do not copy into Lucerna |
| `.indiciumgrid/cache/` | Fixture design reference; do not copy raw cache |
| `tmp/` | Manual triage only; no automated migration |

v0.3 golden inputs must use hand-authored synthetic OHLCV (IG test pattern: `_dated_factor_frame`),
not verbatim TDX or case-cache exports.

## Explicit non-goals (v0.2.2)

- No `lucerna_core.factors` Python package
- No `scripts/export_golden_factor.py`
- No `tests/golden/factor_core/` exported tree
- No factor CLI or workflow wiring
- No factor-tracking migration

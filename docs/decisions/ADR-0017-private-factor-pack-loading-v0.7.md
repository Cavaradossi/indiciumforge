# ADR-0017: Private Factor Pack Loading Integration v0.7

Status: accepted

## Context

- v0.3 delivered `FactorDetectorPort`, demo detectors, `FactorScanRunner`, and a loading boundary
  (ADR-0012).
- v0.6 delivered workflow chain skeleton without factor integration (ADR-0016).
- ADR-0011 requires proprietary detectors to remain in private packs; open core provides ports,
  schemas, and integration boundaries only.

## Decision

Lucerna v0.7.0 delivers private factor pack loading integration:

1. **`load_factor_pack()`** — composes pack YAML (`lucerna.factor_pack.v1`), detectors YAML,
   and optional `lucerna.factor_detectors` entry points (union merge; duplicate names fail).
2. **Factor scan artifacts** — `lucerna.factor_scan.v1` JSON/CSV + `lucerna.factor_scan_state.v1`.
3. **CLI** — `lucerna factor scan` for standalone local pack development.
4. **Workflow chain optional stage** — `factor_scan` after daily_review, before post_close seed.
5. **Summary schema** — `lucerna.workflow_chain_summary.v2` with informational factor fields.

Loading mechanisms (no `sys.path` injection):

- editable-install Python packages
- YAML `module` + `class`
- setuptools entry points
- pack YAML referencing detectors YAML

## Workflow placement

```text
daily_review -> factor_scan (optional) -> post_close seed -> preopen seed -> market_gate
```

Factor scan output is an **evidence sidecar**. It does **not** feed `buy_point_review_internal.csv`
or market-gate strict gate.

## Relationship to ADR-0018 (v0.8)

v0.8 maps `factor_scan` to recipe stage `evidence_factor_scan` (optional evidence checkpoint).
Placement in the chain skeleton is unchanged; naming is recipe-level, not universal lifecycle.

## chain_ok semantics

`chain_ok` requires daily_review and market_gate structural audits only.
`factor_scan_audit_ok` is informational and does **not** affect `chain_ok`.

## Metrics policy

Writers pass through `metrics` unchanged. Private pack owners are responsible for sanitizing
shared artifacts. Open-core tests use synthetic/fake metrics only.

## Asset universe

Default: fixture asset list YAML. Optional `--codes` is local convenience only
(`asset_universe_source: cli_codes`); not a production universe mechanism.

## Out of scope (v0.7)

- IG long-structure detector migration
- Real thresholds, TDX, account/watchlist data
- Factor/KOL/catalyst in strict gate
- Production post_close review generation from scan results
- Metrics auto-redaction

## Consequences

- CAPABILITY_REGISTER: private pack loading + workflow chain factor_scan stage -> `implemented_v0.7`
- ADR-0012 promoted to accepted
- MIGRATION_ROADMAP: v0.7 factor integration; production review generation deferred to v0.8+

# ADR-0013: Market Daily-Review Upstream Skeleton v0.4

Status: proposed

## Context

- Market-gate consumes `market_awareness/{YYYYMMDD}/daily_review/theme_state_ranking.csv` as a hard
  prerequisite ([runner.py](../../packages/lucerna-workflow/src/lucerna_workflow/market_gate/runner.py)).
- Lucerna v0.2 through v0.3 built artifact audit, provider port, and factor detector port foundations.
- MIGRATION_ROADMAP v0.4-a targets upstream generation of the gate-minimal theme ranking artifact.

## Decision

Lucerna v0.4-a implements a **skeleton** daily-review upstream in `lucerna_workflow.market_awareness`:

- load synthetic theme-sector metrics from YAML fixtures
- classify theme states using `THEME_STATE_RULES` thresholds (skeleton semantics)
- write `theme_state_ranking.csv` (6 gate columns) and minimal `market_daily_review_state.json`
- expose `run_daily_review_skeleton(trade_date, artifact_root, fixture_path)`

This is not a port of IndiciumGrid `run_market_daily_review`.

## Fixture contract

Fixtures live under `tests/fixtures/market_awareness/*.yaml`:

```yaml
trade_date: 2026-06-23
themes:
  - theme_name: ...
    sample_count: 40
    median_1d: 0.02
    median_3d: 0.04
    up_rate: 0.75
```

Required fields per theme: `theme_name`, `sample_count`, `median_1d`, `median_3d`, `up_rate`.

## Classifier semantics (non-IG)

Priority order: hard weak -> divergent -> turn weak (mid strong, daily weak) -> daily strong -> neutral.

Uses existing [theme_rules.py](../../packages/lucerna-core/src/lucerna_core/market/theme_rules.py)
threshold keys. Skeleton classifier does not replicate IG `_theme_state_ranking` internals.

## Gate consumer contract

Output CSV columns match `MARKET_ZH` / `MARKET_DAILY` label keys (6 columns). Market-gate
`theme_state_lookup` consumes these columns unchanged.

State JSON schema: `lucerna.market_daily_review_state.v1` (Lucerna-native, not IG schema).

## Out of scope (v0.4-a)

- Full daily-review bundle (index, breadth, constituents, xlsx, md)
- TDX board parsing, vipdoc scan, Eastmoney/AKShare
- Live/network providers
- CLI `lucerna workflow daily-review` (v0.4-b)
- Artifact manifest audit for `market_awareness/` stage

## Consequences

- CAPABILITY_REGISTER: market daily-review upstream -> `implemented_v0.4`
- MIGRATION_MAP: daily-review row -> implemented v0.4 skeleton
- Contract tests cover classifier, runner, and market-gate integration

# ADR-0014: Daily-Review CLI + Manifest Audit v0.4.1

Status: accepted

## Context

- ADR-0013 delivered `run_daily_review_skeleton` and artifact layout under
  `market_awareness/{YYYYMMDD}/daily_review/` but deferred CLI and manifest audit.
- ADR-0008 established `indiciumforge artifact list/audit` for market-gate stages only.
- v0.4-b closes the operator loop for skeleton daily-review without live providers or
  full IG bundle generation.

## Decision

IndiciumForge v0.4.1 adds:

1. **CLI** `indiciumforge workflow daily-review` — thin wrapper over `run_daily_review_skeleton`
   with required `--trade-date`, `--artifact-root`, and `--fixture-path` (synthetic only).
2. **Manifest audit extension** — `list_daily_review_stages`, `validate_daily_review_stage`,
   and `resolve_daily_review_audit_target` in `indiciumforge_core.artifacts.manifest`.
3. **Unified artifact CLI** — `indiciumforge artifact list` scans both `market_gate` and
   `daily_review` domains; `indiciumforge artifact audit` auto-detects daily-review when
   `--stage-dir` ends with `daily_review`, or accepts `--stage-type daily_review` when
   resolving from `--artifact-root` + `--trade-date`.

## Audit rules (daily_review)

Required files:

- `theme_state_ranking.csv` — header must match 6 gate columns from `MARKET_ZH` / `MARKET_DAILY`
- `market_daily_review_state.json` — schema `indiciumforge.market_daily_review_state.v1`

Violations: `missing_file`, `csv_column_mismatch`, `schema_mismatch`, `trade_date_mismatch`,
`invalid_json`, `missing_stage_dir`.

## Out of scope (v0.4.1)

- Live/TDX/network providers
- Full IG daily-review bundle (index, breadth, constituents, xlsx, md)
- post-close -> preopen workflow chain
- Optional stub bundle artifacts (deferred)

## Consequences

- CAPABILITY_REGISTER: market daily-review upstream and artifact manifest rows updated for v0.4.1
- MIGRATION_ROADMAP: v0.4-b marked completed; workflow chain moved to v0.5 candidate
- Contract + CLI smoke tests cover run -> audit integration path

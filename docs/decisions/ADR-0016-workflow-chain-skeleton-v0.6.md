# ADR-0016: Workflow Chain Skeleton v0.6

Status: accepted

## Context

- v0.5-alpha (`synthetic-e2e`) proved daily-review skeleton + preopen seed + market-gate +
  audit in one demo command (ADR-0015).
- CAPABILITY_REGISTER deferred **production** post-close → preopen workflow chain to v0.5+.
- Market-gate resolver already supports preopen-first with post_close fallback
  ([resolver.py](../../packages/indiciumforge-workflow/src/indiciumforge_workflow/market_gate/resolver.py)).
- ADR-0011 requires open-core chain orchestration to use synthetic fixtures only.

## Decision

IndiciumForge v0.6.0 delivers a **workflow chain skeleton** in `indiciumforge_workflow.workflow_chain`:

1. `run_daily_review_skeleton` — theme ranking upstream
2. `seed_post_close_review` — synthetic post_close CSV + `post_close_review_state.json`
3. `seed_preopen_review` — synthetic preopen CSV + `preopen_review_state.json`
4. `run_market_gate` — consumes preopen review (preopen takes precedence)
5. `validate_daily_review_stage` + `validate_market_gate_stage`
6. `workflow_chain_summary.json` (`indiciumforge.workflow_chain_summary.v1`)

CLI: `indiciumforge workflow chain` with three required fixture paths.

## Stage state schemas

- `indiciumforge.post_close_review_state.v1`
- `indiciumforge.preopen_review_state.v1`
- `indiciumforge.workflow_chain_summary.v1`

## chain_ok semantics

`chain_ok` requires daily_review and market_gate structural audits to pass.
`strict_count == 0` does **not** fail the chain (empty strict is a valid outcome).

## Relationship to synthetic-e2e

`synthetic-e2e` remains unchanged — shortest two-stage demo. Workflow chain adds explicit
post_close and preopen stage boundaries for chain testing.

## Relationship to ADR-0018 (v0.8)

v0.8 clarifies that `post_close` and `preopen` folder names are **A-share recipe stage labels**,
not universal IndiciumForge lifecycle enums. This ADR's skeleton behavior is unchanged; see
[ADR-0018](ADR-0018-session-cyclic-workflow-model-v0.8.md).

## Out of scope (v0.6)

- IG production review generation
- Live providers, TDX, vipdoc, account data
- Manifest audit for post_close/preopen stages
- Factor scan integration, intraday watch, factor tracking
- Catalyst/KOL feeding strict gate (kernel behavior unchanged; tests verify)

## Consequences

- CAPABILITY_REGISTER: post-close/preopen workflow chain → `implemented_v0.6` skeleton
- MIGRATION_ROADMAP: v0.6 workflow chain milestone completed
- Contract + CLI tests cover happy path, missing fixtures, empty strict, catalyst isolation

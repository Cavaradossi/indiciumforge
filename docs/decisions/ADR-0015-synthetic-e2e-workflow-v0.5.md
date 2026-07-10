# ADR-0015: Synthetic End-to-End Workflow v0.5-alpha

Status: accepted

## Context

- v0.4.1 delivered daily-review CLI and unified artifact audit for `market_gate` and
  `daily_review` stages (ADR-0014).
- Individual runners (`run_daily_review_skeleton`, `run_market_gate`) and integration tests
  already prove the DR -> MG data path with synthetic inputs.
- v0.5-alpha closes the **demo orchestration loop**: one command runs the full open-source
  skeleton pipeline and emits an E2E summary.

## Decision

IndiciumForge v0.5-alpha (pyproject version `0.5.0`) adds:

1. **Runner** `indiciumforge_workflow.e2e.synthetic.run_synthetic_e2e` — orchestrates:
   - seed preopen review CSV from fixture
   - `run_daily_review_skeleton`
   - `run_market_gate`
   - `validate_daily_review_stage` + `validate_market_gate_stage`
   - write `workflows/{YYYYMMDD}/synthetic_e2e_summary.json`
2. **CLI** `indiciumforge workflow synthetic-e2e` with required fixture paths (no bundled defaults).
3. **Open-source fixtures** under `tests/fixtures/`:
   - `market_awareness/theme_sectors_demo.yaml` (existing)
   - `workflow/preopen_buy_point_review_demo.csv` (curated from golden `strict_pass_mixed`
     inputs; not a local `output/` or IG runtime artifact)

## Summary schema

`synthetic_e2e_summary.json` uses schema `indiciumforge.synthetic_e2e_summary.v1` with per-stage
audit status, fixture provenance, and merged warnings.

## Boundaries

**In scope**

- Synthetic/fixture-only orchestration for demo and contract tests
- Reuse existing audit functions without extending manifest rules

**Out of scope**

- Production post-close -> preopen workflow chain
- Live providers (TDX/OpenBB/yfinance), `.indiciumgrid/`, `output/` copies
- Full IG daily-review bundle
- Factor scan integration, proprietary detectors, private packs
- Manifest audit for `synthetic_e2e_summary.json` (deferred)

## Consequences

- CAPABILITY_REGISTER: `synthetic end-to-end workflow` -> `implemented_v0.5_alpha`
- MIGRATION_ROADMAP: v0.5-alpha demo E2E milestone; production workflow chain deferred
- Contract + CLI smoke tests cover run -> audit -> summary path

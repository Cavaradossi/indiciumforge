# ADR-0022: Private Local Parity Harness v0.11

Status: accepted

## Context

- v0.10 delivered recipe wiring (`RecipeRunner`, fake extension, `workflow_chain_summary.v4`).
- Lucerna market-gate kernel has public golden parity; post_close/preopen production semantics
  remain private.
- Operators need a **local** way to compare Lucerna recipe-chain outputs against IndiciumGrid
  reference artifacts without importing IG Python runtime or committing private paths to Git.

## Decision

Lucerna v0.11.0 delivers a **private-local parity harness**:

### Open core

- `lucerna_core.parity` — `ParityHarnessPort`, `ReferenceArtifactProviderPort`,
  `CandidateComparatorPort`
- Config schema `lucerna.parity_local_config.v1` (operator-local YAML; not committed with real paths)
- Synthetic demo reference tree `tests/fixtures/parity_reference_demo/`
- CLI: `lucerna parity run`, `lucerna parity report` (research audit only)
- Report schema `lucerna.parity_run_report.v1`

### Private local (outside Git)

- `reference_artifact_root` pointing at IG `output/` slices or exported golden trees
- Private recipe extension packs producing production review artifacts
- Operator-authored `parity_local.yaml` (gitignored)

### Comparison dimensions (minimum)

1. `daily_review_structure` — theme_state_ranking columns + daily review state schema
2. `post_close_handoff_shape` — candidate pool keys, review CSV columns, state schema
3. `preopen_handoff_shape` — review CSV columns, state schema
4. `market_gate_strict_semantics` — strict_count, bucket code sets (reuse market-gate comparator)
5. `workflow_chain_summary_v4` — chain_ok, stage audit flags, provenance mode

Verdict labels: `match`, `mismatch`, `intentional_change`, `unsupported_gap`.

## Preserved boundaries

- Parity reports are **research audit evidence** — not trade signals.
- market_gate inputs remain review + theme_state_ranking only (ADR-0019 rule 8).
- OSS CI uses fake extension + synthetic reference only.

## Out of scope (v0.11)

- Import/call IndiciumGrid Python runtime
- Real TDX sync, vipdoc defaults, real long-structure detectors in OSS
- `indiciumgrid/report/builder.py` / ResearchDossier runtime migration
- Committing account/watchlist/private `output/` artifacts
- Publishing private golden reference into public repo
- v1.0 parity sign-off

## Consequences

- CAPABILITY_REGISTER: private local parity harness → `implemented_v0.11`
- v1.0 still requires production private extensions + operator sign-off
- See [`docs/V1_0_DEFINITION.md`](../V1_0_DEFINITION.md)

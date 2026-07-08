# ADR-0008: Artifact Manifest and Audit CLI

Status: accepted

## Context

- v0.1 writes 7 market-gate artifact families (`GATE_ARTIFACTS` in `lucerna_core.artifacts.comparator`).
- Golden scenarios are listed in `GOLDEN_MANIFEST.yaml` but there is no standalone audit path.
- Evidence-first requires validating artifact roots without re-running workflows.

## Decision

- Introduce an `ArtifactManifest` contract in `lucerna-core` that describes required files, schema IDs, and `trade_date` for a workflow stage directory.
- Add read-only CLI: `lucerna artifact audit` and `lucerna artifact list`.
- Audit reports structural violations (missing files, schema mismatch, meta inconsistency); semantic parity remains the golden comparator's job.

## Scope (v0.2)

- market-gate stage only (`workflows/{YYYYMMDD}/market_gate/`).
- Reuse `GATE_ARTIFACTS` from `lucerna_core.artifacts.comparator` as the v0.2 manifest source of truth.

## Out of scope (v0.2)

- market daily-review upstream generation (Option A).
- live data provider adapters (Option B — deferred to v0.2.1).
- new workflow kernels or scheduler.

## Consequences

- CAPABILITY_REGISTER: artifact manifest / audit CLI → `planned_v0.2`.
- Tests: contract tests on golden `expected/` dirs; negative cases for missing artifacts.
- README: document `lucerna artifact` commands when implemented.

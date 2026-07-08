# ADR-0011: Open-Core Private-Extension Boundary

Status: accepted

## Context

- Lucerna is an open-source core decoupled from the frozen IndiciumGrid reference implementation.
- IndiciumGrid contains local private alpha logic, account evidence, watchlists, source lists,
  calibrated thresholds, historical outputs, and proprietary long-structure detector rules.
- The open-source repository must not leak proprietary alpha logic or local evidence.

## Decision

Lucerna open-source core exposes:

- ports and schemas,
- artifact contracts,
- workflow orchestration,
- synthetic fixtures,
- demo implementations,
- golden comparison tools.

The following remain outside the open-source repository:

- proprietary alpha logic,
- real long-structure detectors,
- calibrated gate policies,
- local source lists,
- account evidence,
- local historical outputs,
- private research notes.

Private capabilities should live in private packs or plugins loaded through explicit ports, config,
or entry points.

## Applies to

- factor detectors
- market-gate policies and calibrated thresholds
- factor tracking evidence
- account analysis
- catalyst/KOL/source lists
- provider secrets and token pools
- local output, cache, and archive artifacts

## Out of scope (this patch)

- No private-pack implementation.
- No detector implementation.
- No workflow wiring.

## Consequences

- v0.3 implemented `FactorDetectorPort`, demo detectors, and private-pack loading boundary per ADR-0012.
- Real IndiciumGrid long_structure detector internals must not be copied into the open-source repo.
- Golden fixtures must remain synthetic, curated, or anonymized.
- IG `FACTOR_GOLDEN_MANIFEST.yaml` scenarios require private factor packs for export/parity.

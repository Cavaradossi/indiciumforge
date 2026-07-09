# ADR-0021: A-share Private Recipe Integration Boundary v0.10

Status: accepted

## Context

- v0.8 delivered session-cyclic workflow contracts and A-share recipe YAML.
- v0.9 delivered session-aware provider v2 and anti-inheritance guards (ADR-0019/0020).
- v0.6–v0.7 chain skeleton seeds post_close/preopen from CSV fixtures; recipe YAML is not
  runtime-wired.
- IndiciumGrid production post_close/preopen embed A-share/TDX/private-factor semantics that
  must not become Lucerna open-core logic.

## Decision

Lucerna v0.10.0 delivers **A-share Private Recipe Integration** as open-core **recipe wiring**:

### Open core

- `lucerna_core.recipes` — ports, `RecipeRunner`, `StageInputResolver`, extension pack loader
- Entry point group: `lucerna.recipe_extensions`
- Fake A-share recipe extension in OSS CI (deterministic synthetic outputs)
- Recipe-driven workflow chain CLI (`--recipe`, `--recipe-extension-pack`)
- `workflow_chain_summary.v4` with recipe + extension provenance
- ADR-0021, PRIVATE_ASHARE_RECIPE_TEMPLATE, register/roadmap updates

### Private extension (outside repo)

- TDX `DataProviderPortV2` adapter
- Long-structure factor detector pack
- `ReviewBuilderPort` / `CandidatePoolBuilderPort` with IG-equivalent semantics
- `MarketContextPort` (sector snapshot, board resonance inputs)
- Local fundamentals / universe construction

### Preserved boundaries

- `post_close` / `preopen` remain **A-share recipe stage names**, not universal lifecycle.
- market_gate consumes review + `theme_state_ranking` only (ADR-0019 rule 8).
- factor_scan / provider output does not feed strict gate.
- ResearchDossier remains `technical_reserve` — no runtime in v0.10.

## Out of scope (v0.10)

- Real TDX adapter, `lucerna data sync`, vipdoc defaults
- Real private factor detectors or IG factor slugs in OSS
- Copying IG `run_post_close_workflow` / `_build_workflow_review` into open core
- intraday-watch, factor_tracking, account analysis, midday/late execution
- v1.0 parity sign-off / private golden reference publication

## Consequences

- CAPABILITY_REGISTER: A-share private recipe integration → `implemented_v0.10`
- v0.11+: private production review builder + private golden parity gate
- v1.0 definition of done documented in [`docs/V1_0_DEFINITION.md`](../V1_0_DEFINITION.md)

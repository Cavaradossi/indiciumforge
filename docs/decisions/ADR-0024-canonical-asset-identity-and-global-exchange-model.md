# ADR-0024: Canonical Asset Identity and Global Exchange Model v2.0.1

Status: accepted

## Context

- v2.0.0 rebranded IndiciumGrid → IndiciumForge as a **global quantitative finance
  framework**, but the core domain model (`indiciumforge_core.domain.models`) still
  carried A-share-only assumptions:
  - `Exchange` was a 3-member `str, Enum` (`SSE` / `SZSE` / `BSE_CN`) — impossible to
    represent US, HK, JP, or any other venue without editing framework code, violating
    the open/closed principle for a "global" framework.
  - `AssetID.currency` defaulted to `"CNY"`, implicitly assuming every asset settles in
    RMB.
  - Two near-duplicate identity types existed (`AssetID` and `AssetId`) with divergent
    `uid` semantics (`exchange:value:code` vs `market:code`), inviting drift.
- The recipe runner (`recipes/runner.py`) hard-coded `ashare_cycle_id(trade_date)` for
  **every** recipe, so a US-equity or crypto recipe would inherit an A-share cycle id.
- These were flagged in the W1 optimization plan as "域模型去 A 股烙印" (de-A-share-branding)
  and prerequisite for the storage (W2) and concurrency (W3) workflows.

## Decision

IndiciumForge v2.0.1 delivers a market-agnostic domain core:

### Exchange becomes a value object + registry

- `Exchange` is now a frozen dataclass (`code`, `name`, `region`, `mic`) instead of an enum.
- A module-level registry (`_EXCHANGE_REGISTRY`) seeds well-known venues
  (`SSE`, `SZSE`, `BSE_CN`, `XNAS`, `XNYS`, `XLON`, `XTKS`, `XHKG`) — **curated, not
  exhaustive**.
- `Exchange.from_code(code)` resolves known venues and returns an ad-hoc `region="UNKNOWN"`
  instance for any other non-empty code; it raises `ValueError` only on empty input.
- `Exchange.value` (canonical lowercase code) and `__str__` are preserved for serialization
  parity; `Exchange.SSE` / `Exchange.SZSE` / `Exchange.BSE_CN` attribute access is retained
  so existing callers and tests are unchanged.
- `A_SHARE_EXCHANGES: tuple[Exchange, ...]` captures the A-share seed list as a convenience
  constant for the A-share recipe — a slice of the model, not the model itself.

### Asset identity consolidation

- `AssetID.currency` default changed `""` (was `"CNY"`); the data provider populates it.
- `AssetID` is the single canonical identity (`code` / `exchange` / `asset_type` /
  `currency`, `uid = exchange_code:asset_type:code`).
- `AssetId` is retained as a deprecated module-level alias of `AssetID` for one release,
  then deleted.

### Recipe-driven cycle id

- `WorkflowRecipe` gains a `cycle_fn_id: str = "ashare"` field.
- `workflow.model` exposes a `CycleIdFn` registry: `register_cycle_id_fn(id, fn)` /
  `resolve_cycle_id_fn(id)`. `"ashare"` → `ashare_cycle_id` is seeded at import.
- `RecipeRunner` now computes `cycle_id = resolve_cycle_id_fn(recipe.cycle_fn_id)(trade_date)`
  instead of calling `ashare_cycle_id` directly. A US-equity recipe would register its own
  resolver and set `cycle_fn_id` accordingly.
- `recipe_to_payload` / `parse_workflow_recipe_payload` round-trip `cycle_fn_id`; the A-share
  fixture YAML declares `cycle_fn_id: ashare` explicitly.

## Out of scope (v2.0.1)

- Adding real US-equity / crypto / HK cycle resolvers (registered on demand when those
  recipes land).
- Migrating the `indiciumgrid.workflow.v1` artifact schema string (deferred to W6 — see
  W0 execution notes; it is pinned by golden fixtures and `manifest.py`).
- Removing the deprecated `AssetId` alias (one-release grace period).

## Consequences

- Domain model no longer hard-codes a single market or settlement currency.
- New venues/recipes are data/config, not framework code edits.
- `recipes/runner.py` is domain-agnostic; the A-share recipe opts into `ashare_cycle_id`.
- `Exchange.SSE` keeps working; no test caller required changes beyond the internal
  `Exchange(...)` → `Exchange.from_code(...)` swap in `factors/universe.py`.
- `AssetId` import sites remain valid until the alias is deleted in a later release.

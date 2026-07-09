# ADR-0018: Session-Cyclic Workflow Model v0.8

Status: accepted

## Context

- Lucerna v0.6/v0.7 implemented an A-share-compatible workflow chain skeleton using IG folder
  names (`post_close`, `preopen`, `market_gate`) for fixture seeding and golden compatibility.
- IndiciumGrid production workflow is China A-share shaped; `post_close` and `preopen` differ
  mainly in discovery vs handoff semantics, not in universal lifecycle type.
- IG ARCHITECTURE and ASSET_UNIVERSE_ROADMAP already state global workflows must be **cyclic
  session handoffs**, not a linear `post-close -> preopen -> midday` universal clock.
- Prior roadmap slot v0.8 ("production review generation") would cement IG linear naming into
  Lucerna core before multi-asset/crypto support is modeled.

## Decision

Lucerna v0.8.0 introduces a **session-cyclic workflow contract layer**:

1. **Core abstractions** in `lucerna_core.workflow`:
   - `AssetDomain`, `SessionModel`, `WorkflowRecipe`, `WorkflowCheckpoint`, `EvidenceStageRef`
   - `HandoffArtifact` kinds and schema ids
2. **Recipe declaration** schema `lucerna.workflow_recipe.v1` with synthetic A-share fixture
   `recipe_ashare_daily_research.v1`.
3. **IG folder names** (`post_close`, `preopen`, `midday`) are **recipe stage compatibility
   labels**, not universal Lucerna lifecycle enums.
4. **`workflow_chain_summary.v3`** adds `workflow_session` metadata (`recipe_id`,
   `asset_domain`, `session_model`, `cycle_id`) while preserving v0.6/v0.7 chain fields and CLI.
5. **Data adapter deferred to v0.9**; adapters must emit checkpoint-scoped evidence using v0.8
   contracts.

## A-share recipe mapping (compatibility)

| IG folder | Recipe stage id | Semantic |
| --- | --- | --- |
| `daily_review` | `awareness_daily_review` | Theme/market facts |
| `factor_scan` | `evidence_factor_scan` | Sidecar evidence (v0.7) |
| `post_close` | `discovery_post_close` | Factor discovery + candidate pool |
| `preopen` | `handoff_preopen` | Pre-session review handoff |
| `midday` | `refresh_midday_quotes` | Quote refresh (future) |
| `market_gate` | `gate_market_theme` | Theme gate (A-share recipe gate) |

## chain_ok semantics (unchanged)

`chain_ok` still depends only on daily_review and market_gate structural audits. Session metadata
is informational.

## Relationship to ADR-0016 / ADR-0017

ADR-0016 and ADR-0017 skeleton stages remain valid as **A-share recipe runner demos**. v0.8 adds
naming/metadata correction only; it does not remove v0.6/v0.7 CLI commands or artifact paths.

## Out of scope (v0.8)

- Global/crypto workflow execution
- Data adapter / TDX sync (v0.9)
- `GatePort` / `MarketCalendarPort` runtime implementations
- Production IG review generation
- Modifying IndiciumGrid

## Consequences

- CAPABILITY_REGISTER: session-cyclic workflow model -> `implemented_v0.8`
- MIGRATION_ROADMAP: v0.8 = session model; v0.9 = data adapter
- Golden tests prove A-share compatibility only, not universal workflow design

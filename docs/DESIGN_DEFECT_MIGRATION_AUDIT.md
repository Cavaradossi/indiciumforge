# Design Defect Migration Audit

Read-only audit: IndiciumGrid patterns that informed Lucerna and defects we intentionally do **not**
migrate. Reference: frozen `indiciumgrid @ indiciumgrid-golden-v1`. See
[ADR-0019](decisions/ADR-0019-anti-inheritance-from-indiciumgrid-v0.9.md).

## Workflow naming defects

| IG pattern | Defect | Lucerna mitigation |
| --- | --- | --- |
| `post_close` / `preopen` same `trade_date` folder | Hides session boundary (close vs next open) | v0.8: recipe stage ids + `cycle_id`; folder names = compatibility only |
| Shared `_build_workflow_review` for post_close and preopen | Stage names overstate semantic difference | Recipe kinds: `discovery` vs `handoff` |
| Linear `post-close -> preopen -> midday` operator view | Implies universal global clock | Session-cyclic model; global handoff examples in WORKFLOW_SESSION_MODEL |

## Data layer defects

| IG pattern | Defect | Lucerna mitigation |
| --- | --- | --- |
| `vipdoc -> .indiciumgrid/tdx -> pytdx` resolution | A-share-specific chain treated as default | v0.9: explicit adapter pack; no default path chain |
| `D:/new_tdx64/vipdoc` in docs/runbooks | Hardcoded operator path leaks into mental model | Private adapter config only; no open-core default |
| `ProviderRegistry.fetch_with_fallback` | Fallback indistinguishable from primary authority | v0.9: `ProviderAuthorityLevel` + `ProviderFailureStatus` |
| OHLCV-only `DataProvider` protocol | Cannot express derivatives/crypto data kinds | v0.9: `DataKind` + capability matrix |
| TDX normalization (ST, limit rules) in scan path | A-share rules in data path | Private adapter or recipe layer only |

## Provider policy defects

| IG pattern | Defect | Lucerna mitigation |
| --- | --- | --- |
| Paid/local tier names without authority enum | Ambiguous trust level | `ProviderAuthorityLevel` enum |
| Empty frame + `provider=none` as silent outcome | Loses structured failure | `ProviderFailureStatus.empty` with attempt trace |
| Cross-check not first-class | Silent override risk | Cross-check adds warnings; never replaces primary silently |

## What we keep (compatibility, not inheritance)

- Synthetic golden artifacts for A-share market-gate parity
- IG folder names as **A-share recipe** compatibility labels (v0.6–v0.8 chain skeleton)
- Read-only consumer principle: scan/research do not sync data (explicit sync deferred v0.10+)

## v0.9+ deferrals

| Capability | Target version |
| --- | --- |
| Real TDX private adapter | v0.10 |
| `lucerna data sync` | v0.10+ |
| Production post_close/preopen review generation | v0.11+ |
| Intraday watch / quote refresh execution | v0.12+ |
| Crypto live snapshot adapter | later |

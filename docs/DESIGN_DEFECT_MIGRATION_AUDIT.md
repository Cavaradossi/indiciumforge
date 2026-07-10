# Design Defect Migration Audit

Read-only audit: IndiciumGrid patterns that informed IndiciumForge and defects we intentionally do **not**
migrate. Reference: frozen `indiciumgrid @ indiciumgrid-golden-v1`. See
[ADR-0019](decisions/ADR-0019-anti-inheritance-from-indiciumgrid-v0.9.md).

## Workflow naming defects

| IG pattern | Defect | IndiciumForge mitigation |
| --- | --- | --- |
| `post_close` / `preopen` same `trade_date` folder | Hides session boundary (close vs next open) | v0.8: recipe stage ids + `cycle_id`; folder names = compatibility only |
| Shared `_build_workflow_review` for post_close and preopen | Stage names overstate semantic difference | Recipe kinds: `discovery` vs `handoff` |
| Linear `post-close -> preopen -> midday` operator view | Implies universal global clock | Session-cyclic model; global handoff examples in WORKFLOW_SESSION_MODEL |

## Data layer defects

| IG pattern | Defect | IndiciumForge mitigation |
| --- | --- | --- |
| `vipdoc -> .indiciumgrid/tdx -> pytdx` resolution | A-share-specific chain treated as default | v0.9: explicit adapter pack; no default path chain |
| `D:/new_tdx64/vipdoc` in docs/runbooks | Hardcoded operator path leaks into mental model | Private adapter config only; no open-core default |
| `ProviderRegistry.fetch_with_fallback` | Fallback indistinguishable from primary authority | v0.9: `ProviderAuthorityLevel` + `ProviderFailureStatus` |
| OHLCV-only `DataProvider` protocol | Cannot express derivatives/crypto data kinds | v0.9: `DataKind` + capability matrix |
| TDX normalization (ST, limit rules) in scan path | A-share rules in data path | Private adapter or recipe layer only |

## Provider policy defects

| IG pattern | Defect | IndiciumForge mitigation |
| --- | --- | --- |
| Paid/local tier names without authority enum | Ambiguous trust level | `ProviderAuthorityLevel` enum |
| Empty frame + `provider=none` as silent outcome | Loses structured failure | `ProviderFailureStatus.empty` with attempt trace |
| Cross-check not first-class | Silent override risk | Cross-check adds warnings; never replaces primary silently |

## Research report builder defects

IG `indiciumgrid/report/builder.py` — `build_research_report()` is a single-stock A-share package
builder. Do **not** migrate as IndiciumForge core research abstraction.

| IG assumption | Defect | IndiciumForge mitigation |
| --- | --- | --- |
| `code.zfill(6)` / 6-digit normalization | A-share TDX convention baked into identity | Universal `ResearchSubject`; domain-specific normalization in private adapters |
| TDX stock names / board info | China equity metadata path | Private adapter or recipe layer only |
| `fundamentals/normalized/company_profiles.csv` | Local IG cache layout as source of truth | Provider v2 + private fundamentals adapter; no default cache paths |
| `fundamental_scores.csv`, `fundamental_forensics.csv` | A-share fundamental modules in one builder | `EvidenceModule` per domain; not folded into stock report core |
| `output/workflows/YYYYMMDD/post_close/preopen/market_gate` | IG folder tree as `source_layer` | v0.8 checkpoint/session refs; recipe folder names = compatibility only |
| `.indiciumgrid/accounts/default/...` | Private account evidence in report path | Account dossier = separate subject; never open-core default |
| `600000_research` / `{code}_{stock_name}` output dirs | Stock-named artifact tree | `DossierScope` + opaque dossier ids; no stock-name directories in core |
| CSRC industry, theme exposure, chip distribution, accounting risk | A-share modules folded into one builder | Recipe/private extension modules; not universal core |
| `ResearchReport` dataclass shape | Subject locked to single A-share stock | Forward `ResearchDossier` / `EvidenceDossier`; not `StockResearchReport` |

### Forward IndiciumForge model (v0.10+, not implemented in v0.9)

Recommended core concepts for a future dossier ADR:

- `ResearchSubject`, `ResearchDossier`, `EvidenceModule`, `DossierRenderer`, `DossierScope`
- Scoped by: `asset_domain`, `as_of`, `workflow_checkpoint`, `provider_provenance`, `limitations`
- Subjects: equity, ETF/fund, futures, options, FX, crypto spot/perp, portfolio/account,
  theme/basket, cross-asset pairs
- A-share single-stock dossier = **recipe/private extension only**

## What we keep (compatibility, not inheritance)

- Synthetic golden artifacts for A-share market-gate parity
- IG folder names as **A-share recipe** compatibility labels (v0.6–v0.8 chain skeleton)
- Read-only consumer principle: scan/research do not sync data (explicit sync deferred v0.10+)

## v0.9+ deferrals

| Capability | Target version |
| --- | --- |
| Real TDX private adapter | v0.10 |
| `indiciumforge data sync` | v0.10+ |
| Production post_close/preopen review generation | v0.11+ |
| Intraday watch / quote refresh execution | v0.12+ |
| Crypto live snapshot adapter | later |
| Research dossier model | v0.10+ (after provider v2 + session contracts) |

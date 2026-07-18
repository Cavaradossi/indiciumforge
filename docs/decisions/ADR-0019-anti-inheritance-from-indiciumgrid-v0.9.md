# ADR-0019: Anti-Inheritance Rules from IndiciumGrid v0.9

Status: accepted (permanent boundary)

> **Note.** This ADR originated during the IndiciumGrid migration, but the anti-inheritance
> rules below are a **permanent** design boundary of the open core, not migration
> scaffolding. They are actively enforced by the security regression tests
> (`tests/security/test_no_provider_path_leak.py`,
> `tests/security/test_no_private_factor_leak.py`) and are retained in `docs/decisions/`
> rather than archived. The migration-era working tracker it references has been archived
> to [`docs/archive/`](../archive/MIGRATION_MAP_FROM_INDICIUMGRID.md).

## Context

- IndiciumForge decouples from frozen IndiciumGrid while learning from its production A-share workflow.
- v0.8 established session-cyclic workflow contracts; v0.9 extends the data adapter boundary.
- IG data and workflow layers embed China A-share / Tongdaxin assumptions that must not become
  universal IndiciumForge core semantics.

## Decision

IndiciumForge open core MUST NOT inherit the following from IndiciumGrid:

1. **No universal A-share/TDX path model** — do not treat `vipdoc`, `.indiciumgrid/tdx`, or
   `D:/new_tdx64` as default data roots.
2. **No hardcoded local paths** — no default `D:/new_tdx64/vipdoc`, `.indiciumgrid/`, or `output/`
   in open-core code, configs, or committed fixtures.
3. **OHLCV is not the only data shape** — express quote, breadth, fundamentals, funding, OI,
   options, liquidation as `DataKind` capabilities; do not collapse all data into daily bars.
4. **Fallback is not authority** — tag `ProviderAuthorityLevel`; fallback success must not imply
   primary source quality.
5. **No A-share market rules in core** — T+1, limit-up, ST, lunch break, TDX code conventions
   belong in private adapters or A-share recipe layers.
6. **Recipe stage names are not provider time semantics** — `post_close`/`preopen` are A-share recipe
   labels; provider queries use checkpoint/session metadata instead.
7. **No hidden network fetch** — live/remote data requires explicit private adapter + CLI; open-core
   CI uses fixture/fake providers only.
8. **Data adapter does not feed strict gate** — provider output flows through evidence stages; never
   directly into market_gate strict promotion.
9. **No real private alpha/account data in public repo** — no real factors, watchlists, accounts,
   or historical output trees.
10. **No crypto/derivatives crammed into A-share daily provider model** — reserve capabilities;
    separate domains and evidence stages.
11. **No single-stock research report builder as core abstraction** — do not migrate IG
    `build_research_report()` / `ResearchReport` as IndiciumForge core research model. IndiciumForge targets
    `ResearchDossier` / `EvidenceDossier` (subject-agnostic, domain-scoped), not
    `StockResearchReport`. A-share single-stock dossier is a recipe/private extension only.

## Applies to

- `indiciumforge_core.providers` v2 design and implementation
- Private adapter templates and pack loading
- CLI commands (`provider inspect`, `provider fetch`)
- Contract tests and no-leak regression tests
- Forward research dossier ADR planning (v0.10+)
- [CAPABILITY_REGISTER.md](../../CAPABILITY_REGISTER.md) and [MIGRATION_MAP_FROM_INDICIUMGRID.md](../archive/MIGRATION_MAP_FROM_INDICIUMGRID.md)

## Consequences

- ADR-0020 implements session-aware provider v2 under these guards.
- Real TDX sync deferred to v0.10 private adapter.
- Research dossier model deferred to v0.10+ (contract-only first); prerequisites: v0.8 session
  contracts + v0.9 provider provenance.
- [`docs/DESIGN_DEFECT_MIGRATION_AUDIT.md`](../DESIGN_DEFECT_MIGRATION_AUDIT.md) records IG defects
  vs IndiciumForge mitigations, including `indiciumgrid/report/builder.py` coupling inventory.

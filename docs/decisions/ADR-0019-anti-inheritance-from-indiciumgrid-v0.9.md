# ADR-0019: Anti-Inheritance Rules from IndiciumGrid v0.9

Status: accepted

## Context

- Lucerna decouples from frozen IndiciumGrid while learning from its production A-share workflow.
- v0.8 established session-cyclic workflow contracts; v0.9 extends the data adapter boundary.
- IG data and workflow layers embed China A-share / Tongdaxin assumptions that must not become
  universal Lucerna core semantics.

## Decision

Lucerna open core MUST NOT inherit the following from IndiciumGrid:

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

## Applies to

- `lucerna_core.providers` v2 design and implementation
- Private adapter templates and pack loading
- CLI commands (`provider inspect`, `provider fetch`)
- Contract tests and no-leak regression tests

## Consequences

- ADR-0020 implements session-aware provider v2 under these guards.
- Real TDX sync deferred to v0.10 private adapter.
- [`docs/DESIGN_DEFECT_MIGRATION_AUDIT.md`](../DESIGN_DEFECT_MIGRATION_AUDIT.md) records IG defects
  vs Lucerna mitigations.

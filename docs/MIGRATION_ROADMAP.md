# Lucerna Migration Roadmap

Authoritative forward schedule and reconciliation against the original Lucerna migration plan
(v0.1 walking skeleton + incremental capability migration).

Principles: see [LUCERNA_CONSTITUTION.md](../LUCERNA_CONSTITUTION.md) and
[ADR-0011](decisions/ADR-0011-open-core-private-extension-boundary.md).
Migration preserves behavior, not implementation.

Reference pin:

```text
indiciumgrid @ indiciumgrid-golden-v1
```

---

## Completed trajectory (v0.1 -> v0.3)

| Lucerna version | Delivered | Original plan label |
| --- | --- | --- |
| v0.1 | MRC + market-gate walking skeleton | Phase 0-5 |
| v0.2 | artifact manifest / audit CLI | not in original v0.2 table |
| v0.2.1 | DataProviderPort v1 + LocalFixtureProvider | foundation; original v0.2 prerequisite |
| v0.2.2 | factor inventory + open-core boundary | privacy governance insert |
| v0.3 | FactorDetectorPort + demo + loading | original v0.3 partial: port only, not workflow chain |

---

## Reconciliation: original plan vs actual vs forward

| Capability | Original plan version | Actual status | Forward target |
| --- | --- | --- | --- |
| market daily-review (`theme_state_ranking`) | v0.2 | not started (`not_in_v0.2`) | **v0.4 candidate** |
| post-close -> preopen workflow chain | v0.3 | not started | **v0.4/v0.5 candidate** |
| factor scan port (open source) | v0.3 (partial) | `implemented_v0.3` | done |
| proprietary long-structure detectors | implicit IG migration | `private_extension` | private packs only |
| intraday watch | v0.4 | not started | v0.5+ |
| factor tracking | v0.5 | not started | v0.6+ |
| account analysis | v0.6 | not started | v0.7+ |
| live data providers (TDX/OpenBB/...) | v0.2+ deps | contract/fixture only | adapter slices post-v0.4 |

---

## Current position

Lucerna remains on the migration main line:

- v0.1 walking skeleton delivered with golden + contract tests
- v0.2 through v0.3 prioritized foundation (artifact audit, provider port, open-core boundary,
  factor detector port) before upstream workflow generation
- Acceptable drifts: foundation-first reordering; ADR-0011 open-core insert; v0.3 scope narrowing
  (port/demo only, no IG detector migration, no workflow chain)

Risk guard: do not export IG factor golden trees or migrate proprietary detector internals into the
open-source repo without a private factor pack (ADR-0011).

---

## Forward slice candidates (planning only)

Owner may reprioritize via future ADR. Default orientation:

### v0.4-a: market daily-review generation (default next)

| Item | Detail |
| --- | --- |
| Scope | Generate `theme_state_ranking.csv` upstream artifact using synthetic/fixture inputs |
| Prerequisites | `DataProviderPort` v1, artifact manifest/audit, market-gate kernel |
| ADR | New ADR likely required for daily-review kernel contract |
| Golden | New scenarios under `tests/golden/market_awareness/` or equivalent |
| Open-core | No live TDX/network; no proprietary watchlist/source lists in Git |
| Out of scope | Full cyclic scheduler; live provider adapters |

### v0.4-b or v0.5: post-close -> preopen workflow chain

| Item | Detail |
| --- | --- |
| Scope | Wire review artifact paths across workflow stages (post_close, preopen) |
| Prerequisites | daily-review or stable theme inputs; artifact store paths |
| ADR | Workflow chain ADR; depends on v0.4-a progress |
| Golden | Extend market-gate golden with chain scenarios |
| Open-core | Orchestration only; no proprietary alpha in open core |

### Later (original long-range table)

- v0.5+: intraday watch
- v0.6+: factor tracking evidence audit
- v0.7+: account analysis
- v1.0: replace IG for daily operations (all production capabilities + golden coverage)

---

## Version numbering policy

- Lucerna version labels track **delivered vertical slices**, not 1:1 mapping to the original
  migration plan version table
- Sub-versions (v0.2.1, v0.2.2) denote foundation or governance inserts between major slices
- Capability status changes require implementation + tests + docs per CAPABILITY_REGISTER promotion rule

---

## Related documents

- [CAPABILITY_REGISTER.md](../CAPABILITY_REGISTER.md) — capability status
- [MIGRATION_MAP_FROM_INDICIUMGRID.md](../MIGRATION_MAP_FROM_INDICIUMGRID.md) — symbol-level mapping
- [docs/FACTOR_GOLDEN_SCENARIO_PLAN.md](FACTOR_GOLDEN_SCENARIO_PLAN.md) — factor demo vs IG private-reference

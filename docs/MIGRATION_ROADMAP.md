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
| v0.4 | market daily-review upstream skeleton | original v0.2 daily-review (partial: ranking only) |
| v0.4.1 | daily-review CLI + manifest audit | original v0.2 daily-review operator loop |
| v0.5.0 (v0.5-alpha) | synthetic end-to-end workflow | demo DR -> MG -> audit summary |
| v0.6.0 | workflow chain skeleton | DR -> post_close -> preopen -> MG chain |

---

## Reconciliation: original plan vs actual vs forward

| Capability | Original plan version | Actual status | Forward target |
| --- | --- | --- | --- |
| market daily-review (`theme_state_ranking`) | v0.2 | `implemented_v0.4.1` skeleton + CLI | optional stub bundle v0.5+ |
| post-close -> preopen workflow chain | v0.3 | `implemented_v0.6` skeleton | production review generation v0.7+ |
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
- v0.4 implemented market daily-review upstream skeleton per ADR-0013
- v0.4.1 added daily-review CLI and manifest audit for `market_awareness/` per ADR-0014
- v0.5-alpha (0.5.0) added synthetic E2E demo orchestration per ADR-0015
- v0.6.0 added workflow chain skeleton per ADR-0016
- Acceptable drifts: foundation-first reordering; ADR-0011 open-core insert; v0.3/v0.4 scope narrowing
  (port/demo only, no IG detector migration, no workflow chain)

Risk guard: do not export IG factor golden trees or migrate proprietary detector internals into the
open-source repo without a private factor pack (ADR-0011).

---

## Forward slice candidates (planning only)

Owner may reprioritize via future ADR. Default orientation:

### v0.4-a: market daily-review generation (completed)

Delivered in v0.4.0: skeleton `theme_state_ranking.csv` + state JSON via synthetic fixtures.
See ADR-0013.

### v0.4-b: daily-review CLI + manifest audit (completed)

Delivered in v0.4.1: `lucerna workflow daily-review`, unified `artifact list/audit` for
`market_awareness/{YYYYMMDD}/daily_review/`. See ADR-0014. Full IG daily-review bundle deferred.

### v0.5-alpha: synthetic end-to-end workflow (completed)

Delivered in v0.5.0: `lucerna workflow synthetic-e2e` runs daily-review skeleton -> market-gate
-> dual-stage audit -> `synthetic_e2e_summary.json` using open-source fixtures only.
See ADR-0015. Demo orchestration only; not production workflow chain.

### v0.6: workflow chain skeleton (completed)

Delivered in v0.6.0: `lucerna workflow chain` runs daily-review -> post_close -> preopen ->
market-gate -> dual-stage audit -> `workflow_chain_summary.json`. See ADR-0016.
Skeleton only; not production IG review generation.

### v0.7: private factor pack loading integration (completed)

Delivered in v0.7.0: `load_factor_pack`, `lucerna factor scan`, optional workflow chain
`factor_scan` stage, artifact schemas (`lucerna.factor_scan.v1`, summary v2). See ADR-0017.
Integration boundary only; no IG detector migration.

### v0.8+: production review generation (candidate)

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

# Lucerna Release Notes

## v1.0-rc1 — readiness milestone (documentation)

v1.0-rc1 marks **readiness** for the Lucerna open-core + private extension migration path. It is
**not** a feature release: open-core code remains v0.11.0; this milestone adds documentation and
references private parity evidence.

### Evidence summary

| Item | Status |
| --- | --- |
| Open-core baseline | `v0.11.0-parity-harness` |
| Private A-share adapter | `lucerna-private-ashare` IG-output replay extension |
| Golden parity date | `2026-07-03` — `all_match: true` on five dimensions |
| Blocked frozen dates | `2026-06-24` (missing preopen dir), `2026-06-23` (legacy post_close layout) |
| `strict_count > 0` coverage | Not available in frozen reference; documented gap |

Full summary (no private paths): see `V1_0_RC1_READINESS_REPORT.md` in the `lucerna-private` repository.

### Explicit non-goals (v1.0-rc1)

- No real TDX sync, proprietary factor detectors, or IG report builder in OSS.
- No full IndiciumGrid replacement claim.
- No committing private `output/`, reference trees, or parity reports to Lucerna Git.

## v0.11.0 — private local parity harness

Lucerna 0.11.0 delivers a **config-driven parity harness** so operators can compare recipe-chain
outputs against a local private reference artifact root — without IG Python runtime or committing
private paths to Git.

### Highlights

| Area | Delivered |
| --- | --- |
| ADR-0022 | Private local parity harness boundary |
| Parity layer | `lucerna_core.parity` — harness, reference provider, comparator |
| CLI | `lucerna parity run`, `lucerna parity report` (research audit only) |
| Demo | `tests/fixtures/parity_reference_demo/` synthetic reference tree |
| Template | [PRIVATE_PARITY_HARNESS_TEMPLATE.md](docs/PRIVATE_PARITY_HARNESS_TEMPLATE.md) |

### Quick demo

```bash
lucerna parity run \
  --parity-config tests/fixtures/parity_reference_demo/parity_config_demo.yaml \
  --artifact-root /tmp/lucerna-parity-demo
```

### Explicit non-goals (v0.11)

- No IG runtime import, TDX sync, or real private detectors in OSS.
- No committing private `output/` / `.indiciumgrid/` reference trees.
- Parity mismatch is audit evidence only — not a trade signal.

## v0.10.0 — A-share private recipe integration

Lucerna 0.10.0 delivers **recipe wiring** for A-share daily workflow — ports, `RecipeRunner`,
extension pack loading, and a fake private recipe extension for OSS CI — without production review
semantics or TDX sync.

### Highlights

| Area | Delivered |
| --- | --- |
| ADR-0021 | A-share private recipe integration boundary |
| Recipe layer | `lucerna_core.recipes` — ports, `RecipeRunner`, `StageInputResolver`, pack loader |
| Fake extension | `tests/fixtures/fake_ashare_recipe/` + `recipe_extension_pack_demo.yaml` |
| CLI | `lucerna workflow chain --recipe ... --recipe-extension-pack ...` |
| Summary v4 | `workflow_chain_summary.v4` with recipe + extension provenance |
| Template | [PRIVATE_ASHARE_RECIPE_TEMPLATE.md](docs/PRIVATE_ASHARE_RECIPE_TEMPLATE.md) |

### Quick demo

```bash
lucerna workflow chain \
  --trade-date 2026-06-23 \
  --artifact-root /tmp/lucerna-recipe \
  --recipe tests/fixtures/workflow/recipe_ashare_daily_v1.yaml \
  --recipe-extension-pack tests/fixtures/recipe_extension_pack_demo.yaml \
  --daily-review-fixture tests/fixtures/market_awareness/theme_sectors_demo.yaml
```

### Explicit non-goals (v0.10)

- No real TDX adapter, `lucerna data sync`, or vipdoc defaults.
- No IG `run_post_close_workflow` / `_build_workflow_review` in open core.
- No production review builder or private golden parity gate.
- No ResearchDossier runtime.

## v0.9.0 — session-aware data provider contract v2

Lucerna 0.9.0 delivers the data adapter **boundary** for private packs — session-aware queries,
authority-tagged provenance, and pack loading — without TDX sync or network providers.

### Highlights

| Area | Delivered |
| --- | --- |
| Anti-inheritance | ADR-0019 + [DESIGN_DEFECT_MIGRATION_AUDIT.md](docs/DESIGN_DEFECT_MIGRATION_AUDIT.md) |
| Research dossier guard | ADR-0019 rule 11: IG `build_research_report()` not migrated; dossier deferred v0.10+ |
| Provider v2 | `DataQuery`, `ProviderResult`, `DataProviderPortV2`, `ProviderRegistryV2` |
| Pack loading | `load_provider_pack()` — `lucerna.provider_pack.v1` + entry points |
| CLI | `lucerna provider inspect`, `lucerna provider fetch` (fixture/fake only) |
| Compatibility | v1 `DataProviderPort` unchanged |

### Quick demo

```bash
lucerna provider inspect --ohlcv-fixture-root tests/fixtures/ohlcv

lucerna provider fetch \
  --trade-date 2026-04-30 \
  --code 600000 \
  --ohlcv-fixture-root tests/fixtures/ohlcv
```

### Explicit non-goals (v0.9)

- No real TDX sync / vipdoc / `.indiciumgrid` paths in open core.
- No network providers in public CI.
- No workflow chain or market_gate integration.
- Provider output does not feed strict gate.
- No research dossier runtime; no IG `builder.py` migration; no `600000_research` output tree.

## v0.8.0 — session-cyclic workflow model

Lucerna 0.8.0 introduces session-cyclic workflow **contracts** before data adapter work. IG folder
names (`post_close`, `preopen`, `midday`) are documented as A-share **recipe stages**, not universal
lifecycle enums.

### Highlights

| Area | Delivered |
| --- | --- |
| Core contracts | `lucerna_core.workflow` — `AssetDomain`, `SessionModel`, `WorkflowRecipe`, checkpoints |
| Recipe schema | `lucerna.workflow_recipe.v1` + `recipe_ashare_daily_research.v1` fixture |
| Summary v3 | `workflow_chain_summary.v3` adds `workflow_session` metadata |
| Docs | ADR-0018, [WORKFLOW_SESSION_MODEL.md](docs/WORKFLOW_SESSION_MODEL.md) |

### Explicit non-goals (v0.8)

- No global/crypto workflow execution.
- No data adapter / TDX sync (deferred to v0.9).
- v0.6/v0.7 CLI commands and artifact paths unchanged.

## v0.7.0 — private factor pack loading integration

Lucerna 0.7.0 closes the factor integration boundary between v0.3 factor port and v0.6 workflow chain.

### Highlights

| Area | Delivered |
| --- | --- |
| Pack loading | `load_factor_pack()` — pack YAML + detectors YAML + optional entry points |
| Factor scan CLI | `lucerna factor scan` — standalone local pack development loop |
| Chain stage | Optional `factor_scan` between daily_review and post_close (opt-in flags) |
| Artifacts | `lucerna.factor_scan.v1`, `lucerna.factor_scan_state.v1`, summary `v2` |
| Isolation | Factor scan does not feed market-gate strict gate; audit informational only |

### Quick demo

```bash
lucerna factor scan \
  --trade-date 2026-05-10 \
  --artifact-root /tmp/lucerna-factor \
  --ohlcv-fixture-root tests/fixtures/ohlcv \
  --asset-fixture-list tests/fixtures/factor_scan_assets.yaml \
  --factor-pack tests/fixtures/factor_pack_demo.yaml
```

### Explicit non-goals (v0.7)

- No IG long-structure detector migration.
- No metrics auto-redaction (pack owner responsibility).
- No `sys.path` / module-path injection.
- Factor scan audit does not affect `chain_ok`.

See [docs/PRIVATE_FACTOR_PACK_TEMPLATE.md](docs/PRIVATE_FACTOR_PACK_TEMPLATE.md) and ADR-0017.

## v0.6.0 — workflow chain skeleton

Lucerna 0.6.0 adds a **four-stage workflow chain skeleton** on top of the v0.5-alpha walking skeleton.

### Highlights

| Area | Delivered |
| --- | --- |
| Workflow chain | `lucerna workflow chain` — DR -> post_close -> preopen -> market-gate |
| Stage artifacts | post_close/preopen review CSV + minimal state JSON per stage |
| Chain summary | `workflow_chain_summary.json` with audit status and `strict_count` |
| Tests | happy path, missing fixtures, empty strict, catalyst isolation |

### Quick demo

```bash
lucerna workflow chain \
  --trade-date 2026-06-23 \
  --artifact-root /tmp/lucerna-chain \
  --daily-review-fixture tests/fixtures/market_awareness/theme_sectors_demo.yaml \
  --post-close-review-fixture tests/fixtures/workflow/post_close_buy_point_review_demo.csv \
  --preopen-review-fixture tests/fixtures/workflow/preopen_buy_point_review_demo.csv
```

### Explicit non-goals (v0.6)

- Not production IG review generation.
- No live providers or TDX integration.
- `synthetic-e2e` unchanged (still available as shorter demo).

See [ADR-0016](docs/decisions/ADR-0016-workflow-chain-skeleton-v0.6.md).

---

## v0.5.0 (v0.5-alpha) — public alpha

Lucerna 0.5.0 is the first public open-source alpha. It packages a **synthetic research
walking skeleton** extracted from the frozen IndiciumGrid reference (`indiciumgrid-golden-v1`).
This release is for **evidence-first workflow experimentation**, not production trading.

### Highlights

| Area | Delivered |
| --- | --- |
| Market-gate kernel | Golden-tested strict/observation/active_watch/rejected/calibration semantics |
| Artifact audit | `lucerna artifact list/audit` for `market_gate` and `daily_review` stages |
| Data provider port | `DataProviderPort` v1 + `LocalFixtureProvider` (synthetic OHLCV only) |
| Factor boundary | `FactorDetectorPort`, demo detectors, scan runner, private-pack loading hook |
| Daily-review skeleton | Synthetic `theme_state_ranking.csv` + state JSON from YAML fixtures |
| Synthetic E2E | `lucerna workflow synthetic-e2e` — DR → market-gate → audit → summary JSON |

### Quick demo

```bash
cd <repo-root>
python -m pip install -e packages/lucerna-core
python -m pip install -e packages/lucerna-workflow
python -m pip install -e packages/lucerna-cli
python -m pip install -e ".[dev]"

lucerna workflow synthetic-e2e \
  --trade-date 2026-06-23 \
  --artifact-root /tmp/lucerna-demo \
  --daily-review-fixture tests/fixtures/market_awareness/theme_sectors_demo.yaml \
  --preopen-review-fixture tests/fixtures/workflow/preopen_buy_point_review_demo.csv
```

### Explicit non-goals (this release)

- Not investment advice; not a trading or execution system.
- No live market data providers (TDX, OpenBB, yfinance, etc.) in open core.
- No production post-close → preopen workflow chain.
- No full IndiciumGrid daily-review bundle (index, breadth, xlsx, md).
- No proprietary long-structure factor detectors in open source.

### Open-core / private-extension boundary (ADR-0011)

**In open source:** ports, schemas, artifact contracts, synthetic fixtures, demo implementations,
golden comparison tools, orchestration.

**Outside open source (private packs):** real detectors, calibrated policies, account evidence,
source lists, historical outputs, proprietary alpha logic.

`FACTOR_GOLDEN_MANIFEST.yaml` scenarios remain `private_reference` inventory only.

### License

Apache License 2.0 — see [LICENSE](LICENSE) and [ADR-0007](docs/decisions/ADR-0007-license-strategy.md).

### Prior slices (summary)

- **v0.4.1** — daily-review CLI + unified artifact manifest audit (ADR-0014)
- **v0.4.0** — market daily-review upstream skeleton (ADR-0013)
- **v0.3.0** — factor detector port + demo detectors (ADR-0012)
- **v0.2.x** — provider port, factor inventory, open-core boundary (ADR-0009–0011)
- **v0.2.0** — artifact manifest audit CLI (ADR-0008)
- **v0.1.0** — market-gate walking skeleton + golden parity

### Forward (not in v0.5-alpha)

- Production workflow chain (v0.5+ candidate)
- Optional stub daily-review bundle
- Intraday watch, factor tracking, account analysis

See [docs/MIGRATION_ROADMAP.md](docs/MIGRATION_ROADMAP.md) and [CAPABILITY_REGISTER.md](CAPABILITY_REGISTER.md).

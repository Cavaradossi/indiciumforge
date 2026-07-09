# Lucerna

> **Alpha research software.** Lucerna is evidence-first workflow tooling for research and
> artifact audit. It is **not investment advice**, **not a trading system**, and **not an
> execution platform**. Default workflows use **synthetic fixtures only**; live market data is
> out of scope for this public alpha.

Lucerna is an evidence-first financial research workspace extracted from the frozen IndiciumGrid reference implementation.

Licensed under [Apache License 2.0](LICENSE). See [RELEASE_NOTES.md](RELEASE_NOTES.md) for release history.

Lucerna v0.9 adds session-aware data provider contract v2 (ADR-0019/0020); `lucerna provider inspect/fetch` for fixture/fake smoke tests only.

Lucerna v0.8 adds session-cyclic workflow model contracts (ADR-0018); `post_close`/`preopen` are A-share recipe stages, not universal lifecycle.

Lucerna v0.7 adds private factor pack loading integration (`lucerna factor scan`) and optional workflow chain `factor_scan` stage.

Lucerna v0.6 adds workflow chain skeleton (`lucerna workflow chain`).

Lucerna v0.5-alpha (0.5.0) adds synthetic end-to-end workflow demo (`lucerna workflow synthetic-e2e`).

Lucerna v0.4.1 adds daily-review CLI and manifest audit for `market_awareness/` stages.

Lucerna v0.4 adds market daily-review upstream skeleton (`theme_state_ranking.csv` generation).

Lucerna v0.3 adds `FactorDetectorPort`, demo detectors, scan runner, and private-pack loading boundary.

Lucerna v0.2.2 adds factor-core inventory and golden scenario planning (docs only).

Lucerna v0.2.1 adds `DataProviderPort` v1, `ProviderRegistry`, and `LocalFixtureProvider` (synthetic CSV fixtures only).

Lucerna v0.2 extends the walking skeleton with a read-only artifact manifest and audit CLI.

Lucerna v0.1 is a **Minimum Reusable Core + Walking Skeleton**:

- a small package workspace,
- architecture and governance documents,
- artifact and port contracts,
- one golden-tested market-gate compatible workflow slice.

Reference pin:

```text
indiciumgrid @ indiciumgrid-golden-v1
```

Lucerna preserves behavior where explicitly covered by golden artifacts. It does not copy IndiciumGrid's module structure.

See [docs/MIGRATION_ROADMAP.md](docs/MIGRATION_ROADMAP.md) for original-plan reconciliation and forward schedule.

## Quickstart (public alpha)

Requirements: Python 3.10+.

```bash
cd <repo-root>
python -m pip install -e packages/lucerna-core
python -m pip install -e packages/lucerna-workflow
python -m pip install -e packages/lucerna-cli
python -m pip install -e ".[dev]"

python -m ruff check .
python -m pytest -q

lucerna workflow synthetic-e2e \
  --trade-date 2026-06-23 \
  --artifact-root /tmp/lucerna-demo \
  --daily-review-fixture tests/fixtures/market_awareness/theme_sectors_demo.yaml \
  --preopen-review-fixture tests/fixtures/workflow/preopen_buy_point_review_demo.csv

lucerna artifact list --artifact-root /tmp/lucerna-demo
lucerna artifact audit --artifact-root /tmp/lucerna-demo --trade-date 2026-06-23 --stage-type daily_review
lucerna artifact audit --artifact-root /tmp/lucerna-demo --trade-date 2026-06-23 --stage-type market_gate

lucerna workflow chain \
  --trade-date 2026-06-23 \
  --artifact-root /tmp/lucerna-chain \
  --daily-review-fixture tests/fixtures/market_awareness/theme_sectors_demo.yaml \
  --post-close-review-fixture tests/fixtures/workflow/post_close_buy_point_review_demo.csv \
  --preopen-review-fixture tests/fixtures/workflow/preopen_buy_point_review_demo.csv

lucerna factor scan \
  --trade-date 2026-05-10 \
  --artifact-root /tmp/lucerna-factor \
  --ohlcv-fixture-root tests/fixtures/ohlcv \
  --asset-fixture-list tests/fixtures/factor_scan_assets.yaml \
  --factor-pack tests/fixtures/factor_pack_demo.yaml

lucerna workflow chain \
  --trade-date 2026-06-23 \
  --artifact-root /tmp/lucerna-chain-factor \
  --daily-review-fixture tests/fixtures/market_awareness/theme_sectors_demo.yaml \
  --post-close-review-fixture tests/fixtures/workflow/post_close_buy_point_review_demo.csv \
  --preopen-review-fixture tests/fixtures/workflow/preopen_buy_point_review_demo.csv \
  --factor-pack tests/fixtures/factor_pack_demo.yaml \
  --ohlcv-fixture-root tests/fixtures/ohlcv \
  --asset-fixture-list tests/fixtures/factor_scan_assets.yaml

lucerna provider inspect --ohlcv-fixture-root tests/fixtures/ohlcv

lucerna provider fetch \
  --trade-date 2026-04-30 \
  --code 600000 \
  --ohlcv-fixture-root tests/fixtures/ohlcv
```

On Windows, use a writable temp directory (for example `%TEMP%\lucerna-demo`) and backslashes
in paths. If pytest fails with Temp/.pytest_cache permission errors:

```powershell
python -m pytest -p no:cacheprovider -q --basetemp D:\project\indiciumgrid\.tmp_lucerna_pytest\pytest-basetemp-<unique>
```

## What's next

- **v0.10+ candidate:** private TDX adapter + `lucerna data sync` (see [PRIVATE_DATA_ADAPTER_TEMPLATE.md](docs/PRIVATE_DATA_ADAPTER_TEMPLATE.md))
- **v0.11+ candidate:** production review generation (private A-share recipe)
- **Later:** intraday watch, factor tracking, account analysis per [MIGRATION_ROADMAP](docs/MIGRATION_ROADMAP.md)

## Install

Requirements: Python 3.10+.

From the repository root:

```bash
cd <repo-root>
python -m pip install -e packages/lucerna-core
python -m pip install -e packages/lucerna-workflow
python -m pip install -e packages/lucerna-cli
python -m pip install -e ".[dev]"
```

The CLI entry point is `lucerna` (from `lucerna-cli`).

Golden export (optional, needs frozen IndiciumGrid checkout):

```bash
python scripts/export_golden_market_gate.py
```

## Test

Default:

```bash
cd <repo-root>
python -m pytest -q
python -m ruff check .
```

On Windows, if pytest fails with Temp/.pytest_cache permission errors, use a unique writable basetemp:

```powershell
python -m pytest -p no:cacheprovider -q --basetemp D:\project\indiciumgrid\.tmp_lucerna_pytest\pytest-basetemp-<unique>
```

Test layers:

| Layer | Path | Purpose |
| --- | --- | --- |
| Golden | `tests/golden/` | Semantic parity vs exported IG artifacts (5 market-gate scenarios) |
| Contract | `tests/contract/` | Artifact store, provider, factor detectors, daily-review skeleton |
| Fixtures | `tests/fixtures/ohlcv/` | Hand-authored synthetic OHLCV including DEMO001/DEMO002 demo series |
| CLI smoke | `tests/cli/` | Typer help + `workflow market-gate/daily-review/synthetic-e2e/chain` + `artifact list/audit` |

## CLI

```powershell
lucerna --help
lucerna workflow --help
lucerna workflow market-gate --trade-date 2026-06-23 --artifact-root D:\path\to\artifact-root
lucerna workflow daily-review --trade-date 2026-06-23 --artifact-root D:\path\to\artifact-root --fixture-path D:\path\to\theme_sectors_demo.yaml
lucerna workflow synthetic-e2e --trade-date 2026-06-23 --artifact-root D:\path\to\artifact-root --daily-review-fixture D:\path\to\theme_sectors_demo.yaml --preopen-review-fixture D:\path\to\preopen_buy_point_review_demo.csv
lucerna workflow chain --trade-date 2026-06-23 --artifact-root D:\path\to\artifact-root --daily-review-fixture D:\path\to\theme_sectors_demo.yaml --post-close-review-fixture D:\path\to\post_close_buy_point_review_demo.csv --preopen-review-fixture D:\path\to\preopen_buy_point_review_demo.csv
lucerna artifact --help
lucerna artifact list --artifact-root D:\path\to\artifact-root
lucerna artifact audit --artifact-root D:\path\to\artifact-root --trade-date 2026-06-23
lucerna artifact audit --artifact-root D:\path\to\artifact-root --trade-date 2026-06-23 --stage-type daily_review
lucerna artifact audit --stage-dir D:\path\to\workflows\20260623\market_gate --meta-path D:\path\to\meta.json
```

`artifact audit` checks structural completeness (required files, schema IDs, trade_date consistency). Semantic parity remains the golden comparator's job.

Inputs expected under `--artifact-root` (same layout as golden scenarios):

```text
artifact-root/
  workflows/{YYYYMMDD}/preopen/buy_point_review_internal.csv
  market_awareness/{YYYYMMDD}/daily_review/theme_state_ranking.csv
```

Outputs are written under `artifact-root/workflows/{YYYYMMDD}/market_gate/` (7 artifact families: strict, observation, active_watch, rejected, calibration, summary, state).

## v0.6 boundaries

**In scope (implemented_v0.6):**

- `lucerna_workflow.workflow_chain` — chain runner (`run_workflow_chain_skeleton`)
- `lucerna workflow chain` — DR -> post_close -> preopen -> market-gate -> audit -> summary
- Stage state JSON: `post_close_review_state.json`, `preopen_review_state.json`
- Summary: `workflows/{YYYYMMDD}/workflow_chain_summary.json` (`lucerna.workflow_chain_summary.v1`)
- Fixtures: `theme_sectors_demo.yaml`, `post_close_buy_point_review_demo.csv`, `preopen_buy_point_review_demo.csv`
- ADR-0016 (accepted)

**Explicitly not in v0.6:**

- IG production review generation
- Live providers, TDX, account data
- Manifest audit for post_close/preopen stages
- Factor scan integration; catalyst/KOL in strict gate

## v0.5-alpha boundaries

**In scope (implemented_v0.5_alpha):**

- `lucerna_workflow.e2e.synthetic` — orchestration runner (`run_synthetic_e2e`)
- `lucerna workflow synthetic-e2e` — demo command wiring DR -> MG -> audit -> summary
- Summary artifact: `workflows/{YYYYMMDD}/synthetic_e2e_summary.json` (`lucerna.synthetic_e2e_summary.v1`)
- Fixtures: `tests/fixtures/market_awareness/theme_sectors_demo.yaml`, `tests/fixtures/workflow/preopen_buy_point_review_demo.csv`
- ADR-0015 (accepted)

**Explicitly not in v0.5-alpha:**

- Production post-close -> preopen workflow chain
- Live providers, TDX, `.indiciumgrid/`, `output/` copies
- Full IG daily-review bundle
- Factor scan integration, proprietary detectors, private packs

## v0.4 boundaries

**In scope (implemented_v0.4 / v0.4.1):**

- `lucerna_workflow.market_awareness` — skeleton daily-review upstream
- `run_daily_review_skeleton` — synthetic fixture -> `theme_state_ranking.csv` + state JSON
- `lucerna workflow daily-review` — CLI wrapper (v0.4.1)
- `lucerna artifact list/audit` — market_gate + daily_review stages (v0.4.1)
- Theme state classifier using `THEME_STATE_RULES` (skeleton semantics, not IG port)
- Fixtures: `tests/fixtures/market_awareness/theme_sectors_*.yaml`
- ADR-0013, ADR-0014 (accepted)

**Explicitly not in v0.4:**

- Full IG `run_market_daily_review` bundle (index, breadth, constituents, xlsx)
- TDX board parsing, live/network providers
- post-close -> preopen workflow chain (v0.5 candidate)

## v0.3 boundaries

**In scope (implemented_v0.3):**

- `lucerna_core.factors` — `FactorSignal`, `FactorScanResult`, `FactorDetectorPort`, `FactorDetectorRegistry`
- Demo detectors: `demo_volume_breakout`, `demo_quiet_accumulation` (toy/synthetic logic only)
- `FactorScanRunner` + factor_scan artifact schema/writer
- Private-pack loading boundary via config and entry points (`load_detectors_from_config`)
- [FACTOR_DEMO_MANIFEST.yaml](FACTOR_DEMO_MANIFEST.yaml) — open-source demo scenarios
- ADR-0012 (proposed); ADR-0010/0011 updated to accepted

**Explicitly not in v0.3:**

- Real IG long-structure detector migration
- `scripts/export_golden_factor.py` or `tests/golden/factor_core/` IG exports
- Factor CLI, workflow wiring, factor-tracking, trade-plan/evaluate
- Live providers and private pack implementations

## v0.2.2 boundaries

**In scope (implemented_v0.2.2):**

- [docs/FACTOR_CORE_INVENTORY.md](docs/FACTOR_CORE_INVENTORY.md) — symbol/taxonomy/artifact inventory
- [FACTOR_GOLDEN_MANIFEST.yaml](FACTOR_GOLDEN_MANIFEST.yaml) — five `private_reference` IG scenarios
- [docs/FACTOR_GOLDEN_SCENARIO_PLAN.md](docs/FACTOR_GOLDEN_SCENARIO_PLAN.md) — v0.3 compare/export strategy
- ADR-0010 (accepted) and ADR-0011 (accepted) — open-core/private-extension boundary

Lucerna open-source core does not publish proprietary alpha logic; private factor detectors and
calibrated policies live in private extension packs.

**Explicitly not in v0.2.2:**

- `lucerna_core.factors` scan implementation
- `scripts/export_golden_factor.py` or `tests/golden/factor_core/` exports
- factor-tracking migration
- copying `output/factors/`, TDX cache, or `tmp/` data into Git

## v0.2.1 boundaries

**In scope (implemented_v1):**

- `DataProviderPort` v1 (`supports`, `fetch_ohlcv`, `Provenance`)
- `ProviderRegistry` with ordered fallback and warning preservation
- `LocalFixtureProvider` reading explicit `fixture_root`
- Synthetic fixture: `tests/fixtures/ohlcv/{exchange}_{asset_type}_{code}.csv`

**Explicitly not in v0.2.1:**

- live/network providers (OpenBB, yfinance, Zhitu, TDX adapters)
- workflow wiring (`market-gate` still uses file inputs only)
- market daily-review upstream
- copying ignored IG local data (`.indiciumgrid/tdx/`, cache, `output/`, `tmp/`)

## v0.2 boundaries

**In scope (implemented_v1):**

- artifact manifest scan + structural audit CLI (`lucerna artifact list/audit`)
- contract tests on golden `expected/market_gate/` dirs

**Explicitly not in v0.2:**

- market daily-review upstream generation
- live data provider adapters (deferred to v0.2.1)

## v0.1 boundaries

**In scope (implemented_v1):**

- `market-gate` decision kernel with golden parity
- Local artifact I/O + semantic comparator
- Constitution, ADR-0001..0015, ruff, pytest
- Thin reference CLI

**Contract only (ports defined, no production adapters):**

- Capture/evidence
- Research engine

**Explicitly not in v0.1:**

- post-close / preopen / midday upstream workflows
- intraday watch, factor tracking, accounts
- catalyst/KOL ingestion, live providers
- global cyclic scheduler, ETF workflow

See `CAPABILITY_REGISTER.md` for the full capability matrix and promotion rules.

## Packages

| Package | Role |
| --- | --- |
| `lucerna-core` | Domain, labels, ports, artifacts, providers, theme rules, factor port |
| `lucerna-workflow` | `market_gate` kernel; `market_awareness` daily-review; `e2e.synthetic`; `workflow_chain` |
| `lucerna-cli` | `workflow market-gate`, `daily-review`, `synthetic-e2e`, `chain`, `artifact list/audit` |

Governance docs: `LUCERNA_CONSTITUTION.md`, `RELEASE_NOTES.md`, `SECURITY.md`, `MIGRATION_MAP_FROM_INDICIUMGRID.md`, `docs/FACTOR_CORE_INVENTORY.md`, `docs/AGENT_WORKFLOW.md`.

# Lucerna

Lucerna is an evidence-first financial research workspace extracted from the frozen IndiciumGrid reference implementation.

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

## Install

Requirements: Python 3.10+.

From the repository root:

```powershell
cd D:\project\Lucerna
python -m pip install -e packages/lucerna-core
python -m pip install -e packages/lucerna-workflow
python -m pip install -e packages/lucerna-cli
python -m pip install -e ".[dev]"
```

The CLI entry point is `lucerna` (from `lucerna-cli`).

Golden export (optional, needs frozen IndiciumGrid checkout):

```powershell
python scripts/export_golden_market_gate.py
```

## Test

Default:

```powershell
cd D:\project\Lucerna
python -m pytest
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
| Contract | `tests/contract/` | Artifact store, provider registry, fixture provider, manifest audit, factor detectors |
| Fixtures | `tests/fixtures/ohlcv/` | Hand-authored synthetic OHLCV including DEMO001/DEMO002 demo series |
| CLI smoke | `tests/cli/` | Typer help + `workflow market-gate` + `artifact list/audit` |

## CLI

```powershell
lucerna --help
lucerna workflow --help
lucerna workflow market-gate --trade-date 2026-06-23 --artifact-root D:\path\to\artifact-root
lucerna artifact --help
lucerna artifact list --artifact-root D:\path\to\artifact-root
lucerna artifact audit --artifact-root D:\path\to\artifact-root --trade-date 2026-06-23
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
- ADR-0010 (proposed) and ADR-0011 (proposed) — open-core/private-extension boundary

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
- Constitution, ADR-0001..0012, ruff, pytest
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
| `lucerna-core` | Domain, labels, ports, artifacts, providers, theme rules |
| `lucerna-workflow` | `market_gate` kernel, resolver, runner |
| `lucerna-cli` | Reference CLI (`lucerna workflow market-gate`, `lucerna artifact list/audit`) |

Governance docs: `LUCERNA_CONSTITUTION.md`, `MIGRATION_MAP_FROM_INDICIUMGRID.md`, `docs/FACTOR_CORE_INVENTORY.md`, `docs/AGENT_WORKFLOW.md`.

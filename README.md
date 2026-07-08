# Lucerna

Lucerna is an evidence-first financial research workspace extracted from the frozen IndiciumGrid reference implementation.

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
| Contract | `tests/contract/` | Artifact store roundtrip, provider registry skeleton |
| CLI smoke | `tests/cli/` | Typer help + `workflow market-gate` happy path |

## CLI

```powershell
lucerna --help
lucerna workflow --help
lucerna workflow market-gate --trade-date 2026-06-23 --artifact-root D:\path\to\artifact-root
```

Inputs expected under `--artifact-root` (same layout as golden scenarios):

```text
artifact-root/
  workflows/{YYYYMMDD}/preopen/buy_point_review_internal.csv
  market_awareness/{YYYYMMDD}/daily_review/theme_state_ranking.csv
```

Outputs are written under `artifact-root/workflows/{YYYYMMDD}/market_gate/` (7 artifact families: strict, observation, active_watch, rejected, calibration, summary, state).

## v0.1 boundaries

**In scope (implemented_v1):**

- `market-gate` decision kernel with golden parity
- Local artifact I/O + semantic comparator
- Constitution, ADR-0001..0007, ruff, pytest
- Thin reference CLI

**Contract only (ports defined, no production adapters):**

- Data provider
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
| `lucerna-core` | Domain, labels, ports, artifacts, theme rules |
| `lucerna-workflow` | `market_gate` kernel, resolver, runner |
| `lucerna-cli` | Reference CLI (`lucerna workflow market-gate`) |

Governance docs: `LUCERNA_CONSTITUTION.md`, `MIGRATION_MAP_FROM_INDICIUMGRID.md`, `docs/AGENT_WORKFLOW.md`.

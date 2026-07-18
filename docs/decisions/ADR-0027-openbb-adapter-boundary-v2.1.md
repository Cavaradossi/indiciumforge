# ADR-0027: OpenBB Adapter Boundary and Public Demo (v2.1.0)

Status: accepted

## Context

[ADR-0026](ADR-0026-quant-capability-increment.md) gave IndiciumForge a working
reference quant pipeline, but the only real data adapter was `AkshareDataProvider`
(A-share, behind the `data` extra) with a committed synthetic A-share golden panel.
The [OpenBB Public Demo Plan](../OPENBB_PUBLIC_DEMO_PLAN.md) identified two gaps for
a credible v2.1 public story:

- **No global (non-A-share) real data source.** Every provider example was
  China-A-share specific, which understates the open-core + adapter pattern.
- **No 3-minute public demo.** The default quickstart used synthetic fixtures and
  assumed familiarity with the artifact-audit workflow. A newcomer had no
  copy-paste command that produces an auditable quant summary from a familiar,
  public universe (US equities).

The plan's Implementation note requires opening an ADR for the OpenBB adapter
boundary (network opt-in, fixture fallback, CI policy) **before merging runtime
code**. This ADR is that boundary.

## Decision

Ship a first-class **global** data adapter and an offline-by-default public demo:

### 1. `OpenBBDataProvider` (opt-in, network-strict)

- Implements `DataProviderPortV2` for US-equity daily OHLCV via the
  [OpenBB Platform](https://github.com/OpenBB-finance/OpenBB) (`pip install openbb`,
  Apache-2.0), behind a new `openbb` extra on `indiciumforge-core`.
- `provider_id="openbb"`, `authority_level=PRIMARY`, capability
  `US_EQUITY / OHLCV / DELAYED`, venues `("xnas", "xnys")`.
- **Importing the module never imports openbb.** `_require_openbb()` is invoked
  only on the first `fetch`; if the extra is absent it raises a helpful
  `ImportError` pointing at `pip install 'indiciumforge-core[openbb]'`.
- Routes through OpenBB to the **yfinance** vendor by default, which needs **no API
  key** — the demo stays token-free. Other vendors resolve credentials via OpenBB's
  own credential store, never a hardcoded path in this repo.
- `_to_frame` coerces either an OpenBB `OBBject` (via `.to_dataframe()`), a plain
  `DataFrame`, or a `.results` sequence, so contract tests inject a fake without
  importing openbb types. `_normalize` promotes a `date` index and maps lowercase
  OHLCV columns; provenance mirrors the akshare adapter (no cache, explicit
  `failure_status`).

### 2. Offline public demo = committed deterministic sample (no network)

- The default `indiciumforge quant openbb-demo` reads a **committed synthetic
  sample panel** shipped as *package data* (`indiciumforge_core/data/openbb_demo/
  sample_us_equity_ohlcv.csv`, 1032 rows × 8 US tickers × 129 dates), resolved via
  `importlib.resources` so a fresh clone / PyPI install works regardless of cwd.
- The sample carries a `MANIFEST.yaml` with `not_real_market_data: true` and an
  explicit honesty note: **ticker symbols are public identifiers but OHLCV values
  are generated** (deterministic AR(1)+drift, seed-pinned). This keeps default CI
  network-free (ADR-0019 rule 7: no hidden network fetch) and byte-deterministic.
- `--online` is strictly opt-in: it fetches through `OpenBBDataProvider` (requires
  the `openbb` extra) and, being live data, is **not** exercised in default CI.
- `scripts/snapshot_openbb_demo.py` regenerates the fixture (`--online` for a real
  pull); the CLI writes `openbb_demo/summary.json` (IC-by-horizon, optimization,
  backtest) plus a copied `panel_MANIFEST.yaml` for the offline path.

## Honesty guardrails (mandatory)

1. The offline demo's numbers (e.g. the reported backtest Sharpe) are computed on a
   **synthetic sample**, not real quotes. `summary.json` records
   `data_source: offline_sample` and an inline note; the manifest flags
   `not_real_market_data: true`. These demonstrate framework wiring, **not** market
   performance and **not** investment advice — the CLAIMS_REGISTER forbidden-claim
   row on trading performance / Sharpe / alpha remains in force for any real-market
   assertion.
2. OpenBB is an **adapter example**, not a claim that IndiciumForge replaces OpenBB
   Workspace or any commercial terminal. It is a public data-integration layer, not
   a broker execution gateway; this preserves the non-trading, non-broker boundary.

## Out of scope

- vn.py and any broker/execution-gateway integration — deferred
  ([ADR-0006](ADR-0006-execution-adapter-boundary.md)); conflicts with the
  non-trading boundary.
- TDX production adapters or real vipdoc paths in OSS — remain operator-local via
  `PRIVATE_DATA_ADAPTER_TEMPLATE.md`.
- Live OpenBB fetch in default CI (only the offline sample path is exercised).
- Non-US OpenBB asset domains (FX, crypto, macro) — the adapter capability is
  US-equity OHLCV for v2.1; other domains can be added behind the same port later.

## Consequences

- IndiciumForge gains its first **global** real data adapter and a copy-paste public
  demo that produces an auditable quant summary in ~3 minutes with no private files,
  no operator paths, and no API keys in Git — satisfying the plan's acceptance
  criteria.
- Heavy `openbb` stays isolated behind the `openbb` extra and a lazy import,
  preserving the light core install and ADR-0011's open-core boundary.
- The offline sample is a single source of truth (package data), so the demo,
  contract test, and README quickstart stay consistent across fresh clones.
- Positioning stays honest: a **research audit workflow over public data**, not a
  trading system, and the synthetic sample is labelled as such everywhere it surfaces.

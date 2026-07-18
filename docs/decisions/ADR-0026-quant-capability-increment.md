# ADR-0026: Implemented Quantitative Capability (v2.0.1)

Status: accepted

## Context

IndiciumForge had, through v1.0 / v2.0.1, a complete **research-workflow** surface
(workflow chains, artifact audit, golden/parity methodology, open-core boundary) but
**no implemented quant engine**. The capability register marked `research engine port`
as `contract_only` and `research dossier model` / `factor trade-plan/evaluate/backtest
adapter` as `technical_reserve`. Two strategic options were considered:

- **Build a reference implementation in-house** — implement real, tested quant
  capability (factor analytics, portfolio optimization, backtest, pricing) behind the
  existing hexagonal port pattern, using mature OSS libraries (statsmodels, cvxpy) and a
  committed synthetic A-share golden panel.
- **Defer to external frameworks** — rely on heavyweight external frameworks
  (QuantLib, rqalpha, qlib, backtrader) for the quant substance.

The framework's open-core value proposition ("auditable artifacts + explicit
contracts") is justified only if the contracts have at least one credible reference
implementation. Pure deferral would leave the quant ports as empty
interfaces and the paper's "instantiated system" claim unbacked.

## Decision

Adopt the build-in-house approach. IndiciumForge v2.0.1 ships real quant capability
behind `indiciumforge_core.quant`, mirroring the `factors/` domain-packaging pattern
(per submodule: `ports.py` + `models.py` + adapter + `registry.py` + `loading.py` +
`pack.py` + `__init__.py`).

### Four quant ports

| Port | Reference adapter | Heavy dep | Extra |
| --- | --- | --- | --- |
| `FactorAnalyticsPort` | `StatsmodelsFactorEngine` | statsmodels, scipy | `analytics` |
| `PortfolioOptimizationPort` | `CvxpyOptimizer` | cvxpy | `portfolio` |
| `BacktestPort` | `VectorizedBacktester` | numpy, pandas | (core) |
| `PricingPort` | `BlackScholesPricer` | stdlib `math.erf` | (none) |

- **Factor analytics**: per-horizon Spearman IC (forward returns derived internally so
  an IC-decay sweep needs no caller pre-compute), Fama-MacBeth cross-sectional OLS slope
  per date then temporal t-stat, and a bounded rank-weight turnover proxy.
- **Portfolio optimization**: mean-variance (`Maximize(λ·μᵀw − wᵀΣw)`) and
  min-variance (`Minimize(wᵀΣw)`) via cvxpy, with long-only, weight-bound, and
  sector-cap constraints; `Σ` is symmetrized defensively.
- **Backtest**: fully vectorized numpy/pandas. **No look-ahead** — portfolio returns use
  *prior*-period weights (`prior_W[1:] = W[:-1]`, warm-up day dropped), a flat
  `cost_bps` on turnover, and cumulative PnL via `init_capital·(1+rets).cumprod()`;
  Sharpe / max-drawdown / calmar computed from the equity curve.
- **Pricing**: analytic Black-Scholes European price + Greeks via stdlib `math.erf`
  (zero extra deps); put-call parity and Greek-sign invariants covered by contract tests.

### Data: adapter + committed golden

- `AkshareDataProvider` implements `DataProviderPortV2` **behind the `data` extra**
  (akshare, lxml) and an offline `cache_only` mode; it contains **no private paths** in
  OSS and degrades to the golden snapshot when the network/extra is unavailable.
- `GoldenSnapshotProvider` serves a committed synthetic A-share-like panel
  (`tests/fixtures/golden_ashare/panel.parquet`, 36 assets × 521 dates) with a persistent
  AR(1) trend so factor IC is *positive and rises with horizon* — a credible demo signal,
  not a fabricated one. The panel is byte-deterministic and regenerated only by
  `scripts/snapshot_golden_ashare.py`.

### End-to-end + CLI

- `quant.pipeline.run_quant_pipeline` wires factor → analytics → optimize (per rebalance)
  → backtest. It is **byte-deterministic** on the golden panel; `tests/golden/
  test_quant_pipeline.py` locks the reported numbers (two runs identical to the byte).
- `indiciumforge quant` (Typer group with `analytics`, `optimize`, `backtest`, `price`,
  `pipeline`) imports heavy deps **lazily inside each command** so the CLI loads without
  the `[analytics]`/`[portfolio]` extras installed.

## Honesty guardrails (mandatory)

1. The vectorized backtester is **single-asset-return, daily, cost-flat only**. It does
   not model factor decay beyond the IC sweep, intraday dynamics, slippage, or
   market-impact. These are explicitly *out of scope* and must not be implied.
2. All paper numbers for the quant pipeline are computed on the **synthetic golden
   panel**. They demonstrate framework correctness and pipeline wiring; they are **not**
   market performance, not live-trading backtests, and not investment advice. The
   CLAIMS_REGISTER forbidden-claim row on "Trading performance, Sharpe, alpha" remains
   in force for any real-market assertion.

## Out of scope

- QuantLib / rqalpha / qlib integration — deferred; ports remain swappable.
- Slippage / market-impact / intraday models in the backtester.
- Live A-share data fetch in CI (only the offline `cache_only` path is exercised in OSS).
- Production-grade factor library beyond the demo momentum factor in the pipeline.

## Consequences

- The quant ports now have credible reference implementations; the paper's "instantiated
  quant system" framing is backed by passing contract + golden tests (38 quant-specific
  tests; 241 total passed, 1 skipped, zero regression).
- Heavy deps stay isolated behind extras and lazy imports, preserving the core install's
  light footprint and ADR-0011's open-core boundary.
- Framework positioning is honest: a **quantitative finance framework with a working
  reference quant pipeline on synthetic data**, not a production trading/backtest
  platform.
- Deferred engines (QuantLib, rqalpha) can later be added as alternative adapters behind
  the same ports without breaking contracts.

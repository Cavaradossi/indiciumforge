# Lucerna Release Notes

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

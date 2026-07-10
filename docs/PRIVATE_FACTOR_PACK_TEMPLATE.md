# Private Factor Pack Template

IndiciumForge open core loads private factor packs through explicit configuration. This document
describes a **local-only** private pack layout. Do not commit real detector logic or calibrated
thresholds to the public IndiciumForge repository.

## Layout

```text
my-indiciumforge-factor-pack/
  pyproject.toml
  pack.yaml
  detectors.yaml
  src/my_pack/
    detectors/
      my_detector.py
  .gitignore
```

## pack.yaml

```yaml
schema: indiciumforge.factor_pack.v1
pack_id: my-local-pack
version: "0.1.0"
load:
  detectors_config: ./detectors.yaml
  include_entry_points: true
  entry_point_group: indiciumforge.factor_detectors
```

## detectors.yaml

```yaml
detectors:
  - module: my_pack.detectors.my_detector
    class: MyDetector
```

Alternatively, reference an entry point:

```yaml
detectors:
  - entry_point: indiciumforge.factor_detectors:my_detector
```

## pyproject.toml entry points

```toml
[project.entry-points."indiciumforge.factor_detectors"]
my_detector = "my_pack.detectors.my_detector:MyDetector"
```

## Install (local venv)

```bash
pip install -e ./my-indiciumforge-factor-pack
pip install -e <indiciumforge-repo>/packages/indiciumforge-core
pip install -e <indiciumforge-repo>/packages/indiciumforge-workflow
pip install -e <indiciumforge-repo>/packages/indiciumforge-cli
```

## Run standalone scan

```bash
indiciumforge factor scan \
  --trade-date 2026-05-10 \
  --artifact-root /tmp/indiciumforge-factor \
  --ohlcv-fixture-root <indiciumforge>/tests/fixtures/ohlcv \
  --asset-fixture-list <indiciumforge>/tests/fixtures/factor_scan_assets.yaml \
  --factor-pack ./pack.yaml
```

## Run workflow chain with factor stage

```bash
indiciumforge workflow chain \
  --trade-date 2026-06-23 \
  --artifact-root /tmp/indiciumforge-chain \
  --daily-review-fixture <fixtures>/market_awareness/theme_sectors_demo.yaml \
  --post-close-review-fixture <fixtures>/workflow/post_close_buy_point_review_demo.csv \
  --preopen-review-fixture <fixtures>/workflow/preopen_buy_point_review_demo.csv \
  --factor-pack ./pack.yaml \
  --ohlcv-fixture-root <fixtures>/ohlcv \
  --asset-fixture-list <fixtures>/factor_scan_assets.yaml
```

## .gitignore checklist (private pack repo)

- `output/`, `.indiciumgrid/`, `tmp/`
- TDX vipdoc/cache paths
- calibrated threshold YAML
- account exports, watchlists
- historical factor scan trees with production tickers

## Metrics responsibility

IndiciumForge writers emit `metrics` as opaque JSON without redaction. Before sharing artifacts outside
your local environment, ensure metrics do not expose proprietary alpha logic.

## Recipe placement (v0.8)

In the A-share recipe (`indiciumforge.recipe.ashare_daily_research.v1`), factor scan attaches to the
optional evidence stage `evidence_factor_scan`. Production discovery still belongs to the
`discovery_post_close` recipe stage in IndiciumGrid; IndiciumForge v0.7 chain integration treats factor
scan as a sidecar only. See [WORKFLOW_SESSION_MODEL.md](WORKFLOW_SESSION_MODEL.md).

## Data provider at discovery (v0.9)

Factor scan and future discovery stages consume OHLCV via `DataProviderPortV2` in private packs.
Open-core boundary: [ADR-0020](decisions/ADR-0020-session-aware-data-provider-v2-v0.9.md) and
[PRIVATE_DATA_ADAPTER_TEMPLATE.md](PRIVATE_DATA_ADAPTER_TEMPLATE.md). v0.7 `FactorScanRunner` still
uses v1 registry by default; migrate adapters to v2 when wiring session-aware queries.

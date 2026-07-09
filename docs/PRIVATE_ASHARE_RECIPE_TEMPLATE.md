# Private A-share Recipe Extension Template (v0.10)

Use this template for a **private** Lucerna recipe extension pack. Open core ships ports +
fake extension only.

## Layout

```
my-ashare-recipe-pack/
  pyproject.toml
  recipe_extension_pack.yaml    # schema: lucerna.recipe_extension_pack.v1
  extensions/
    ashare_recipe.py            # PrivateRecipeExtensionPort implementation
  .gitignore                    # local paths, caches, output trees
```

## Entry point (`pyproject.toml`)

```toml
[project.entry-points."lucerna.recipe_extensions"]
my_ashare_recipe = "my_ashare_pack.extensions.ashare_recipe:AsharePrivateRecipeExtension"
```

## Extension pack YAML

```yaml
schema: lucerna.recipe_extension_pack.v1
pack_id: my-ashare-recipe
version: "0.1.0"
recipe_ids:
  - lucerna.recipe.ashare_daily_research.v1
load:
  include_entry_points: true
  entry_point_group: lucerna.recipe_extensions
```

Or module reference with kwargs (paths relative to pack file):

```yaml
load:
  extensions_config: extensions/ashare_extensions.yaml
```

## Port implementation

Implement `PrivateRecipeExtensionPort`:

- `extension_id` — stable opaque id
- `recipe_ids` — tuple of supported recipe ids
- `supports_stage(recipe_id, stage_id)` — e.g. `discovery_post_close`, `handoff_preopen`
- `execute_stage(context)` — return `StageRunResult` with handoff artifacts

Private layer may implement:

- `CandidatePoolBuilderPort` — factor signals → `candidate_pool_raw.json`
- `ReviewBuilderPort` — signals + market context → `buy_point_review_internal.csv`
- `MarketContextPort` — sector snapshot for handoff stage

## Wiring with other private packs

| Private pack | Entry point group |
| --- | --- |
| Data provider | `lucerna.data_providers` |
| Factor detectors | `lucerna.factor_detectors` |
| Recipe extension | `lucerna.recipe_extensions` |

## Provenance rules

- No absolute paths in committed artifact JSON
- No `.indiciumgrid/`, `output/`, `vipdoc/` in open-core payloads
- Tag `empty_result_reason` when universe/signals empty

## CLI smoke (open core fake)

```bash
lucerna workflow chain \
  --trade-date 2026-06-23 \
  --artifact-root /tmp/lucerna-recipe \
  --recipe tests/fixtures/workflow/recipe_ashare_daily_v1.yaml \
  --recipe-extension-pack tests/fixtures/recipe_extension_pack_demo.yaml \
  --daily-review-fixture tests/fixtures/market_awareness/theme_sectors_demo.yaml \
  --factor-pack tests/fixtures/factor_pack_demo.yaml \
  --ohlcv-fixture-root tests/fixtures/ohlcv \
  --asset-fixture-list tests/fixtures/factor_scan_assets.yaml
```

## Deferred

- Real TDX sync → private adapter + future `lucerna data sync`
- Production review builder → v0.11 private implementation
- ResearchDossier runtime → v0.10+ contract slice (register only in v0.10)

See [ADR-0021](decisions/ADR-0021-ashare-private-recipe-integration-v0.10.md) and
[PRIVATE_DATA_ADAPTER_TEMPLATE.md](PRIVATE_DATA_ADAPTER_TEMPLATE.md).

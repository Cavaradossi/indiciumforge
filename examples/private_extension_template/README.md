# Private Extension Template

Minimal **non-functional** skeleton for operator-local IndiciumForge extension packs.

Copy this directory outside the IndiciumForge OSS repo. Replace placeholders. Do not commit real paths or credentials to public Git.

## Layout

```text
my-indiciumforge-extensions/
  README.md
  pyproject.toml              # entry points for providers, factors, recipes
  provider_pack.yaml.example
  factor_pack.yaml.example
  recipe_extension_pack.yaml.example
  parity_local.yaml.example   # gitignored when copied to parity_local.yaml
  src/my_pack/
    adapters/                 # DataProviderPortV2 implementations
    detectors/                # FactorDetectorPort implementations
    recipes/                  # Recipe stage handlers
  .gitignore
```

## Quick start

1. Copy `*.example` files to active names (without `.example`).
2. Fill `<placeholder>` values with operator-local paths.
3. `pip install -e ./my-indiciumforge-extensions` in your private environment.
4. Run IndiciumForge CLI pointing at your pack YAML files.

## Guides

- [docs/EXTENSION_AUTHOR_GUIDE.md](../../docs/EXTENSION_AUTHOR_GUIDE.md)
- [docs/PRIVATE_DATA_ADAPTER_TEMPLATE.md](../../docs/PRIVATE_DATA_ADAPTER_TEMPLATE.md)
- [docs/PRIVATE_FACTOR_PACK_TEMPLATE.md](../../docs/PRIVATE_FACTOR_PACK_TEMPLATE.md)
- [docs/PRIVATE_ASHARE_RECIPE_TEMPLATE.md](../../docs/PRIVATE_ASHARE_RECIPE_TEMPLATE.md)
- [docs/PRIVATE_PARITY_HARNESS_TEMPLATE.md](../../docs/PRIVATE_PARITY_HARNESS_TEMPLATE.md)

## OSS demo parity (no private packs)

```bash
indiciumforge parity run \
  --parity-config tests/fixtures/parity_reference_demo/parity_config_demo.yaml \
  --artifact-root /tmp/indiciumforge-parity-demo
```

Run from IndiciumForge repo root after installing packages.

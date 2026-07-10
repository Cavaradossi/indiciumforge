---
name: indiciumforge-extension-author
description: >-
  Guide creation of private IndiciumForge extensions: DataProvider packs,
  FactorDetector packs, and Recipe extension packs. Use when building
  operator-local packs without forking open-core contracts.
---

# IndiciumForge extension author

## Purpose

Help authors build **private extensions** behind stable OSS ports — no fork of `indiciumforge_core` contracts.

## Read first

1. [docs/EXTENSION_AUTHOR_GUIDE.md](../../docs/EXTENSION_AUTHOR_GUIDE.md)
2. [examples/private_extension_template/](../../examples/private_extension_template/)
3. [docs/decisions/ADR-0011-open-core-private-extension-boundary.md](../../docs/decisions/ADR-0011-open-core-private-extension-boundary.md)

## Extension types

| Type | Schema | Entry point group | OSS demo |
| --- | --- | --- | --- |
| Data provider | `indiciumforge.provider_pack.v1` | `indiciumforge.data_providers` | `indiciumforge provider inspect` |
| Factor detector | `indiciumforge.factor_pack.v1` | `indiciumforge.factor_detectors` | `indiciumforge factor scan` + demo pack |
| Recipe extension | `indiciumforge.recipe_extension_pack.v1` | `indiciumforge.recipe_extensions` | fake ashare recipe in `tests/fixtures/` |

## Authoring workflow

1. Create a **separate private package** (not in the OSS repo)
2. Implement the port interface (`DataProviderPortV2`, `FactorDetectorPort`, or `PrivateRecipeExtensionPort`)
3. Register setuptools entry points in `pyproject.toml`
4. Ship a YAML pack config with correct `schema:` line
5. Wire packs via CLI flags (`--provider-pack`, `--factor-pack`, `--recipe-extension-pack`)
6. Validate with `indiciumforge artifact audit` and `indiciumforge parity run` on synthetic or operator-local reference trees

## Starter skeleton

Copy [examples/private_extension_template/](../../examples/private_extension_template/) and replace placeholders:

- `provider_pack.yaml.example`
- `factor_pack.yaml.example`
- `recipe_extension_pack.yaml.example`
- `parity_local.yaml.example`

## Rules

- **No secrets** in pack YAML or committed code (credentials stay operator-local)
- **No proprietary datasets** in OSS commits
- Provider output does **not** feed strict market-gate logic (ADR-0020)
- Use `indiciumforge.*` schema IDs (deprecated `lucerna.*` accepted one release with warning)
- Parity harness is **research audit only** — not production sign-off

## Private workspace pattern

Keep private packs in an operator-local repo with editable install:

```bash
pip install -e /path/to/private-repo/packages/your-private-pack
pip install -e packages/indiciumforge-core -e packages/indiciumforge-workflow -e packages/indiciumforge-cli
```

Do not commit private `output/`, reference artifact trees, or parity reports to the open-core repo.

## Templates

- [docs/PRIVATE_DATA_ADAPTER_TEMPLATE.md](../../docs/PRIVATE_DATA_ADAPTER_TEMPLATE.md)
- [docs/PRIVATE_FACTOR_PACK_TEMPLATE.md](../../docs/PRIVATE_FACTOR_PACK_TEMPLATE.md)
- [docs/PRIVATE_ASHARE_RECIPE_TEMPLATE.md](../../docs/PRIVATE_ASHARE_RECIPE_TEMPLATE.md)
- [docs/PRIVATE_PARITY_HARNESS_TEMPLATE.md](../../docs/PRIVATE_PARITY_HARNESS_TEMPLATE.md)

## Out of scope

- Live trading, order routing, or broker APIs
- Investment recommendations
- Publishing private logic to PyPI without explicit operator review

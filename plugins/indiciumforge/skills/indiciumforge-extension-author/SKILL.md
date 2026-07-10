---
name: indiciumforge-extension-author
description: >-
  Guide creation of private IndiciumForge extensions: DataProvider packs,
  FactorDetector packs, and Recipe extension packs. Use when building
  operator-local packs without forking open-core contracts.
---

# IndiciumForge Extension Author

## Purpose

Help authors build private extensions behind stable OSS ports without forking
`indiciumforge_core` contracts or leaking proprietary logic into the public
repository.

## Locate The Repository

First locate the IndiciumForge repository root: the directory containing
`pyproject.toml`, `packages/indiciumforge-core/`, and `docs/`.

Then read, from that repository root:

1. `docs/EXTENSION_AUTHOR_GUIDE.md`
2. `examples/private_extension_template/`
3. `docs/decisions/ADR-0011-open-core-private-extension-boundary.md`

## Extension Types

| Type | Schema | Entry point group | OSS demo |
| --- | --- | --- | --- |
| Data provider | `indiciumforge.provider_pack.v1` | `indiciumforge.data_providers` | `indiciumforge provider inspect` |
| Factor detector | `indiciumforge.factor_pack.v1` | `indiciumforge.factor_detectors` | `indiciumforge factor scan` plus demo pack |
| Recipe extension | `indiciumforge.recipe_extension_pack.v1` | `indiciumforge.recipe_extensions` | fake A-share recipe in `tests/fixtures/` |

## Authoring Workflow

1. Create a separate private package outside the OSS repo
2. Implement the relevant port interface
3. Register setuptools entry points in `pyproject.toml`
4. Ship a YAML pack config with the correct `schema:` line
5. Wire packs via CLI flags such as `--provider-pack`, `--factor-pack`, or `--recipe-extension-pack`
6. Validate with `indiciumforge artifact audit` and `indiciumforge parity run`

## Starter Skeleton

Copy `examples/private_extension_template/` and replace placeholders:

- `provider_pack.yaml.example`
- `factor_pack.yaml.example`
- `recipe_extension_pack.yaml.example`
- `parity_local.yaml.example`

## Rules

- No secrets in pack YAML or committed code
- No proprietary datasets in OSS commits
- Provider output does not feed strict market-gate logic directly
- Use `indiciumforge.*` schema IDs
- Treat deprecated `lucerna.*` compatibility as temporary
- Treat parity harness output as research audit evidence only

## Private Workspace Pattern

Keep private packs in an operator-local repo with editable install:

```bash
pip install -e /path/to/private-repo/packages/your-private-pack
pip install -e packages/indiciumforge-core -e packages/indiciumforge-workflow -e packages/indiciumforge-cli
```

Do not commit private `output/`, reference artifact trees, parity reports,
credentials, account data, or watchlists to the open-core repo.

## Templates

- `docs/PRIVATE_DATA_ADAPTER_TEMPLATE.md`
- `docs/PRIVATE_FACTOR_PACK_TEMPLATE.md`
- `docs/PRIVATE_ASHARE_RECIPE_TEMPLATE.md`
- `docs/PRIVATE_PARITY_HARNESS_TEMPLATE.md`

## Out Of Scope

- Live trading, order routing, or broker APIs
- Investment recommendations
- Publishing private logic to PyPI without explicit operator review

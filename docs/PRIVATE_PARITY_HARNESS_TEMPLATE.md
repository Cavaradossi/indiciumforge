# Private Local Parity Harness Template (v0.11)

Use this template to compare Lucerna recipe-chain outputs against a **local private reference**
artifact root. Open core ships the harness + synthetic demo only.

## Layout (operator machine)

```
my-parity-workspace/
  parity_local.yaml              # gitignored — lucerna.parity_local_config.v1
  reference/                     # curated IG export or output slice (gitignored)
    market_awareness/YYYYMMDD/daily_review/
    workflows/YYYYMMDD/post_close|preopen|market_gate/
  private-recipe-pack/           # optional private extension
```

Add to `.gitignore`:

```
parity_local.yaml
reference/
```

## Config (`parity_local.yaml`)

```yaml
schema: lucerna.parity_local_config.v1
reference_artifact_root: ./reference
trade_date: 2026-06-23
artifact_root: ./run_artifacts
recipe:
  path: path/to/recipe_ashare_daily_v1.yaml
  extension_pack: path/to/private_recipe_extension_pack.yaml
  daily_review_fixture: path/to/theme_sectors.yaml
dimensions:
  - daily_review_structure
  - post_close_handoff_shape
  - preopen_handoff_shape
  - market_gate_strict_semantics
  - workflow_chain_summary_v4
disclaimer: research_audit_only
```

Rules:

- `reference_artifact_root` must be supplied via local config — **no OSS default**
- Do not commit absolute paths (`D:/`, `.indiciumgrid/`, `output/`, `vipdoc/`)
- Parity output is audit evidence only — **not investment advice**

## CLI

```bash
lucerna parity run --parity-config parity_local.yaml

lucerna parity report --report ./run_artifacts/parity_run_report.json
```

Exit codes: `0` all match; `1` mismatches; `2` config/runtime errors.

## OSS demo (CI)

```bash
lucerna parity run \
  --parity-config tests/fixtures/parity_reference_demo/parity_config_demo.yaml \
  --artifact-root /tmp/lucerna-parity-demo
```

Demo reference: [`tests/fixtures/parity_reference_demo/reference/`](../tests/fixtures/parity_reference_demo/reference/)

## Deferred

- Production review builder parity → private extension v0.11+
- Private golden publication → sibling repo / local-only
- v1.0 sign-off → [`docs/V1_0_DEFINITION.md`](V1_0_DEFINITION.md)

See [ADR-0022](decisions/ADR-0022-private-local-parity-harness-v0.11.md).

# Private Data Adapter Template (v0.9)

Use this template for a **private** Lucerna data provider pack. Do not commit real paths,
credentials, or live network adapters to the open-core repository.

## Layout

```
my-private-data-pack/
  pyproject.toml          # entry points -> lucerna.data_providers
  provider_pack.yaml      # schema: lucerna.provider_pack.v1
  adapters/
    tdx_ohlcv.py          # implements DataProviderPortV2 (private)
  .gitignore              # cache dirs, local config with paths
```

## Entry point (`pyproject.toml`)

```toml
[project.entry-points."lucerna.data_providers"]
my_tdx_ohlcv = "my_private_pack.adapters.tdx_ohlcv:TdxOhlcvProvider"
```

Install editable in your private environment only:

```bash
pip install -e ./my-private-data-pack
```

## Provider pack YAML

```yaml
schema: lucerna.provider_pack.v1
pack_id: my-private-tdx
version: "0.1.0"
load:
  include_entry_points: true
  entry_point_group: lucerna.data_providers
```

Alternatively reference a local providers config (paths relative to pack file):

```yaml
load:
  providers_config: adapters/providers.yaml
```

## Adapter skeleton

Implement `DataProviderPortV2`:

- `provider_id` — stable opaque id (e.g. `my_tdx_ohlcv`)
- `authority_level` — `primary` for production source; never pretend fallback is primary
- `capabilities` — declare `(asset_domain, data_kind, latency_profile, venues?)`
- `supports_query(query)` — return false for undeclared kinds/domains
- `fetch(query)` — return `ProviderResult` with `ProviderProvenance` (no absolute paths in JSON)

Session fields come from v0.8 `WorkflowCheckpoint` / `WorkflowSessionMetadata` via
`DataQuery.from_checkpoint()`.

## Provenance rules

- Use opaque `cache_policy` / `quota_policy` strings
- Never write `D:/...`, `.indiciumgrid/`, `vipdoc/`, or `output/` into artifact payloads
- Tag `failure_status` explicitly for empty/stale/missing capability

## CLI smoke (open core)

```bash
lucerna provider inspect --provider-pack ./provider_pack.yaml
lucerna provider fetch --trade-date 2026-04-30 --code 600000 \
  --ohlcv-fixture-root ./fixtures/ohlcv --data-kind ohlcv
```

## Deferred (not v0.9)

- Real TDX vipdoc sync → v0.10 private adapter
- `lucerna data sync` → v0.10+
- Network providers in public CI

See [ADR-0019](decisions/ADR-0019-anti-inheritance-from-indiciumgrid-v0.9.md),
[ADR-0020](decisions/ADR-0020-session-aware-data-provider-v2-v0.9.md), and
[DESIGN_DEFECT_MIGRATION_AUDIT.md](DESIGN_DEFECT_MIGRATION_AUDIT.md).

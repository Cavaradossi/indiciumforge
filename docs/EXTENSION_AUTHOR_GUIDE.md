# Extension Author Guide

How to build **private extensions** for IndiciumForge without forking open-core contracts.

IndiciumForge OSS ships ports, schemas, demo fixtures, and harnesses. Your proprietary logic lives in **operator-local packs** installed via editable installs and YAML configuration.

## Open core vs private extension

| Belongs in OSS | Belongs in private pack |
| --- | --- |
| Port interfaces and registry loaders | Live TDX/network data adapters |
| Artifact schemas and manifest audit | Production review builders |
| Synthetic fixtures and demo detectors | Proprietary factor detectors |
| Recipe runner and extension **loader** | Real A-share recipe stage implementations |
| Parity harness and comparator | Legacy `output/` reference trees |
| ADRs and capability register | Calibrated policies, account evidence |

Authoritative ADR: [ADR-0011](decisions/ADR-0011-open-core-private-extension-boundary.md). Constitution: [INDICIUMFORGE_CONSTITUTION.md](../INDICIUMFORGE_CONSTITUTION.md).

Starter skeleton: [examples/private_extension_template/](../examples/private_extension_template/).

## DataProvider extension

Session-aware contract v2 (`DataProviderPortV2`) supports pack loading via `indiciumforge.provider_pack.v1`.

**OSS smoke:**

```bash
indiciumforge provider inspect --ohlcv-fixture-root tests/fixtures/ohlcv
indiciumforge provider fetch --trade-date 2026-04-30 --code 600000 --ohlcv-fixture-root tests/fixtures/ohlcv
```

**Private pack:**

1. Implement `DataProviderPortV2` in your private package.
2. Register entry point `indiciumforge.data_providers`.
3. Ship `provider_pack.yaml` with `schema: indiciumforge.provider_pack.v1`.

Template: [PRIVATE_DATA_ADAPTER_TEMPLATE.md](PRIVATE_DATA_ADAPTER_TEMPLATE.md).

**Rules:**

- Provider output does **not** feed strict market-gate in v0.9+.
- No vipdoc defaults or `.indiciumgrid/` paths in OSS.
- Cache dirs and credentials stay in private `.gitignore`.

## FactorDetector extension

OSS exposes `FactorDetectorPort`, `FactorScanRunner`, and `indiciumforge factor scan`.

**Private pack:**

1. Implement detectors returning `FactorSignal` / `FactorScanResult`.
2. Register `indiciumforge.factor_detectors` entry points.
3. Ship `pack.yaml` (`indiciumforge.factor_pack.v1`) + `detectors.yaml`.

Template: [PRIVATE_FACTOR_PACK_TEMPLATE.md](PRIVATE_FACTOR_PACK_TEMPLATE.md).

**Rules:**

- Factor scan is informational — does not change `chain_ok` or strict gate.
- No `sys.path` injection; use entry points or explicit module paths in private YAML only.
- Metrics redaction is pack owner responsibility.

## Recipe extension

OSS runs `RecipeRunner` with fake A-share extension in fixtures.

**Private pack:**

1. Implement recipe stage handlers for your `recipe_ids`.
2. Ship `recipe_extension_pack.yaml` (`indiciumforge.recipe_extension_pack.v1`).
3. Wire CLI: `indiciumforge workflow chain --recipe ... --recipe-extension-pack ...`.

Template: [PRIVATE_ASHARE_RECIPE_TEMPLATE.md](PRIVATE_ASHARE_RECIPE_TEMPLATE.md).

**Rules:**

- `post_close` / `preopen` are A-share **recipe stages**, not universal enums (ADR-0018).
- No IG `run_post_close_workflow` copy-paste into OSS.
- Summary artifact version must match chain expectations (`workflow_chain_summary.v4` for parity).

## Legacy artifact adapter

To compare against a legacy system without importing its runtime:

1. Export or copy reference artifacts to an **operator-local read-only root**.
2. Point parity config `reference_artifact_root` at that root.
3. Run IndiciumForge recipe chain to a writable `artifact_root`.
4. Compare via `indiciumforge parity run`.

Do not commit reference trees. Use `parity_local.yaml` (gitignored) copied from `parity_local.yaml.example`.

## Parity harness

Config schema: `indiciumforge.parity_local_config.v1`.

**Dimensions:**

- `daily_review_structure`
- `post_close_handoff_shape`
- `preopen_handoff_shape`
- `market_gate_strict_semantics`
- `workflow_chain_summary_v4`

**Verdicts:** `match`, `intentional_change`, `unsupported_gap`.

OSS demo:

```bash
indiciumforge parity run \
  --parity-config tests/fixtures/parity_reference_demo/parity_config_demo.yaml \
  --artifact-root /tmp/indiciumforge-parity-demo
```

Template: [PRIVATE_PARITY_HARNESS_TEMPLATE.md](PRIVATE_PARITY_HARNESS_TEMPLATE.md).

Parity output is **research audit evidence** — not a trade signal.

## Security checklist

Before publishing or sharing a private pack:

- [ ] No credentials in YAML or source
- [ ] `.gitignore` covers cache, local config, and reference roots
- [ ] No account numbers, watchlists, or brokerage tokens in logs
- [ ] Pack does not phone home with operator data unless explicitly documented
- [ ] Dependencies pinned and scanned in your environment

Before contributing to IndiciumForge OSS:

- [ ] Run leak scan (see below)
- [ ] Only `.example` configs with placeholders
- [ ] No real symbols beyond public demo fixtures

## Encoding policy

- UTF-8 repository encoding.
- Machine-parsed surfaces ASCII-stable: CLI flags, schema IDs, config keys, artifact filenames, operational logs.
- Documentation and domain labels may use Unicode.
- No decorative Unicode punctuation in CLI output.

## Do-not-commit list

Never commit to IndiciumForge OSS (or share in public pack repos):

| Item | Reason |
| --- | --- |
| `parity_local.yaml` | Operator paths |
| `reference/` artifact trees | Legacy private output |
| `run_artifacts/`, `output/` | Run products |
| `.indiciumgrid/`, `vipdoc` caches | Local data roots |
| API keys, tokens, passwords | Secrets |
| Real watchlists / account exports | PII and proprietary |
| Competition or broker integration configs | Out of scope |

## Leak scan (maintainers)

```bash
cd <repo-root>
rg -i "rapidx|liquidity.?arena|telegram|api.?key" --glob '!*.md' .
rg "D:\\\\project\\\\|D:/project/" .
rg "run_artifacts/|parity_local.yaml" --glob '!*.example'
```

Governance docs may mention `.indiciumgrid` / `output/` as guardrails only.

## Further reading

- [SYSTEM_MAP.md](SYSTEM_MAP.md) — ports and artifact layout
- [AGENT_QUICKSTART.md](AGENT_QUICKSTART.md) — agent rules
- [CURRENT_STATUS.md](CURRENT_STATUS.md) — v1.0 sign-off and gaps

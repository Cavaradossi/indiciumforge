# System Map

High-level map of the IndiciumForge open-core workspace: packages, ports, artifacts, and parity.

## Packages

| Package | Path | Responsibility |
| --- | --- | --- |
| `indiciumforge-core` | `packages/indiciumforge_core/` | Domain types, ports, artifact I/O, recipes, parity, providers, factors |
| `indiciumforge-workflow` | `packages/indiciumforge_workflow/` | `market_gate` kernel, daily-review skeleton, e2e, workflow chain |
| `indiciumforge-cli` | `packages/indiciumforge_cli/` | Typer CLI: `workflow`, `artifact`, `factor`, `provider`, `parity` |

## Core ports

| Port | Schema / module | OSS implementation |
| --- | --- | --- |
| `DataProviderPort` v1 | `indiciumforge_core.providers` | `LocalFixtureProvider` + synthetic OHLCV |
| `DataProviderPortV2` | session-aware v2 | Pack loader + fixture/fake smoke |
| `FactorDetectorPort` | `indiciumforge_core.factors` | Demo detectors + pack loader boundary |
| Recipe extensions | `indiciumforge_core.recipes` | `RecipeRunner`, fake A-share extension in fixtures |
| Parity harness | `indiciumforge_core.parity` | Reference comparator + demo tree |

Workflows **never** import vendor modules directly — only ports and pack loaders.

## Artifact stages

```text
artifact-root/
  market_awareness/{YYYYMMDD}/daily_review/     # theme_state_ranking.csv, state JSON
  workflows/{YYYYMMDD}/
    post_close/                                   # review CSV + state
    preopen/                                      # review CSV + state
    market_gate/                                  # strict, observation, active_watch, ...
    workflow_chain_summary.json                   # chain metadata v1–v4
  factors/{YYYYMMDD}/                             # factor_scan artifacts (optional)
```

CLI audit: `indiciumforge artifact list/audit` for `market_gate` and `daily_review` stages.

## Parity dimensions

Config-driven via `indiciumforge.parity_local_config.v1`:

- `daily_review_structure`
- `post_close_handoff_shape`
- `preopen_handoff_shape`
- `market_gate_strict_semantics`
- `workflow_chain_summary_v4`

Verdicts: `match`, `intentional_change`, `unsupported_gap` — research audit only.

Demo: `tests/fixtures/parity_reference_demo/`.

## Diagrams

### System boundary

```mermaid
flowchart TB
  subgraph openCore [IndiciumForge_OpenCore]
    Core[indiciumforge_core]
    Workflow[indiciumforge_workflow]
    CLI[indiciumforge_cli]
  end
  subgraph privateExt [Private_Extensions_OperatorLocal]
    DataPack[DataProvider_pack]
    FactorPack[FactorDetector_pack]
    RecipePack[Recipe_extension]
  end
  subgraph legacyRef [Legacy_Reference_ReadOnly]
    GoldenStore[Golden_artifact_store]
  end
  openCore -->|"ports_and_contracts"| privateExt
  openCore -->|"parity_harness"| legacyRef
```

### Runtime data flow

```mermaid
flowchart LR
  Fixture[Fixture_or_Provider] --> Recipe[RecipeRunner]
  Recipe --> Artifacts[Artifact_store]
  Artifacts --> Audit[Manifest_audit_CLI]
  Artifacts --> Parity[Golden_comparator]
  GoldenRef[Reference_artifacts] --> Parity
  Parity --> Verdict["match_or_gap_or_intentional_change"]
```

### Package workspace

```mermaid
flowchart TB
  Root[IndiciumForge_repo]
  Root --> CorePkg[packages/indiciumforge_core]
  Root --> WfPkg[packages/indiciumforge_workflow]
  Root --> CliPkg[packages/indiciumforge_cli]
  Root --> Tests[tests]
  Root --> Docs[docs]
```

### Deeper architecture

- C4 context: [diagrams/context.md](diagrams/context.md)
- DFD level 0: [diagrams/dfd-level-0.md](diagrams/dfd-level-0.md)
- Session model: [WORKFLOW_SESSION_MODEL.md](WORKFLOW_SESSION_MODEL.md)
- ADR index: [decisions/](decisions/)

## Governance cross-links

| Document | Purpose |
| --- | --- |
| [CAPABILITY_REGISTER.md](../CAPABILITY_REGISTER.md) | Capability status matrix |
| [INDICIUMFORGE_CONSTITUTION.md](../INDICIUMFORGE_CONSTITUTION.md) | Non-negotiable principles |
| [MIGRATION_ROADMAP.md](MIGRATION_ROADMAP.md) | Forward schedule |
| [V1_0_DEFINITION.md](V1_0_DEFINITION.md) | v1.0 sign-off criteria |

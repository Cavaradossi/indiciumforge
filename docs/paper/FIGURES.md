# Figures for IndiciumForge software paper

All diagrams describe **public OSS structure only**. No private data, account plots, or performance charts.

Render Mermaid for LaTeX via export or manual redraw. Figure numbers match suggested paper order.

---

## Figure 1 — System boundary

**Caption:** IndiciumForge open core exposes ports and contracts. Operator-local private extensions supply data, factors, and recipe logic. A frozen legacy reference supports parity comparison only—no runtime import of legacy code.

**Evidence:** README architecture Mermaid; ADR-0011; ADR-0019.

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

---

## Figure 2 — Runtime data flow

**Caption:** Research inputs flow through recipe runners into versioned artifacts. Manifest audit validates structure; golden and parity comparators evaluate semantics against reference trees.

**Evidence:** README; `indiciumforge artifact audit`; `tests/golden/test_market_gate.py`.

```mermaid
flowchart LR
  Fixture[Fixture_or_Provider] --> Recipe[RecipeRunner]
  Recipe --> Artifacts[Artifact_store]
  Artifacts --> Audit[Manifest_audit_CLI]
  Artifacts --> Parity[Golden_comparator]
  GoldenRef[Reference_artifacts] --> Parity
  Parity --> Verdict["match_or_gap_or_intentional_change"]
```

---

## Figure 3 — Artifact parity flow

**Caption:** Parity harness loads operator config, runs recipe chain into `artifact_root`, compares five dimensions against `reference_artifact_root`, and emits `parity_run_report.json` with per-dimension verdicts.

**Evidence:** ADR-0022; `indiciumforge_core.parity`; `tests/fixtures/parity_reference_demo/`.

```mermaid
flowchart TB
  Config[parity_local_config_yaml] --> Harness[ParityHarness]
  Recipe[Recipe_plus_extension_pack] --> Runner[Workflow_chain_runner]
  Runner --> Actual[artifact_root_outputs]
  Ref[reference_artifact_root] --> Comparator[CandidateComparator]
  Actual --> Comparator
  Comparator --> D1[daily_review_structure]
  Comparator --> D2[post_close_handoff_shape]
  Comparator --> D3[preopen_handoff_shape]
  Comparator --> D4[market_gate_strict_semantics]
  Comparator --> D5[workflow_chain_summary_v4]
  D1 --> Report[parity_run_report_json]
  D2 --> Report
  D3 --> Report
  D4 --> Report
  D5 --> Report
```

---

## Figure 4 — Package workspace map

**Caption:** Monorepo layout: three installable Python packages, contract tests, golden fixtures, and governance docs.

**Evidence:** `packages/indiciumforge-{core,workflow,cli}/`; `pyproject.toml` files; tag `v2.0.0`.

```mermaid
flowchart TB
  Root[IndiciumForge_repo]
  Root --> CorePkg[packages/indiciumforge_core]
  Root --> WfPkg[packages/indiciumforge_workflow]
  Root --> CliPkg[packages/indiciumforge_cli]
  Root --> Tests[tests_contract_golden_cli]
  Root --> Docs[docs_ADRs_paper]
  Root --> Agent[agent_skills]
```

---

## Figure 5 — Extension boundary

**Caption:** Open core ships port interfaces, schema contracts, loaders, and synthetic demos. Private packs implement proprietary logic behind entry points—never committed to the public repository.

**Evidence:** ADR-0011; EXTENSION_AUTHOR_GUIDE.md; `examples/private_extension_template/`.

```mermaid
flowchart LR
  subgraph OSS [Open_Source_Repository]
    Ports[Port_protocols]
    Schemas[Schema_IDs]
    Loaders[Pack_loaders]
    Demos[Synthetic_fixtures]
  end
  subgraph Private [Operator_Local_Packs]
    LiveData[Live_data_adapters]
    PropFactors[Proprietary_detectors]
    ProdRecipe[Production_recipe_stages]
    RefTrees[Reference_output_mirrors]
  end
  Ports -->|"entry_point_groups"| LiveData
  Ports --> PropFactors
  Ports --> ProdRecipe
  Loaders --> Demos
  RefTrees -.->|"parity_only"| OSS
```

---

## Figure 6 — Workflow session model (optional)

**Caption:** IndiciumForge session-cyclic model generalizes linear A-share operator folders via checkpoints and handoff artifacts.

**Evidence:** ADR-0018; docs/WORKFLOW_SESSION_MODEL.md.

```mermaid
flowchart TB
  subgraph linear [Ashare_Recipe_Linear_View]
    DR[daily_review]
    PC[post_close]
    PO[preopen]
    MG[market_gate]
    DR --> PC --> PO --> MG
  end
  subgraph cyclic [Session_Cyclic_Model]
    CPn[checkpoint_N]
    HO[handoff_artifact]
    CPn1[checkpoint_Nplus1]
    CPn --> HO --> CPn1
  end
```

---

## Not included

| Item | Reason |
| --- | --- |
| Performance / backtest charts | No reproducible experiment dataset in OSS |
| Account / portfolio screenshots | ADR-0011 boundary |
| Private parity row dumps | Confidential; verdict categories only in paper |
| Competition / contest workflows | Out of scope |

## LaTeX rendering notes

- Prefer vector figures; keep monospace schema IDs readable
- Caption must repeat research-audit disclaimer where parity figures appear
- Cross-reference CLAIMS_REGISTER figure-related claims (F1–F6)

# Claims register

Every major technical statement in [INDICIUMFORGE_ARXIV_DRAFT.md](INDICIUMFORGE_ARXIV_DRAFT.md) must trace to a row below. Confidence: **high** = tested in OSS CI or documented sign-off layer; **medium** = ADR/docs consensus; **low** = design-only / future.

| ID | Claim | Evidence | Source path / tag / test | Confidence | Paper wording (approved) |
| --- | --- | --- | --- | --- | --- |
| C01 | IndiciumForge is organized as three installable Python packages | Package dirs + pyproject names | `packages/indiciumforge-{core,workflow,cli}/`; tag `v2.0.0` | high | "three packages: indiciumforge-core, indiciumforge-workflow, indiciumforge-cli" |
| C02 | CLI entry point is `indiciumforge` | pyproject scripts table | `packages/indiciumforge-cli/pyproject.toml` `[project.scripts]` | high | "reference CLI command indiciumforge" |
| C03 | Artifacts use namespaced schema IDs `indiciumforge.*` | Constants + fixtures | `indiciumforge_core` workflow/factor/parity modules; ADR-0023 | high | "artifact documents declare indiciumforge.* schema IDs" |
| C04 | Manifest audit checks files, schemas, trade_date consistency | Audit implementation + CLI | `artifacts/manifest.py`; `indiciumforge artifact audit`; ADR-0008, ADR-0014 | high | "structural manifest audit precedes semantic comparison" |
| C05 | Market-gate kernel has five OSS golden scenarios | Golden manifest | `GOLDEN_MANIFEST.yaml`; `tests/golden/market_gate/*` | high | "five exported market-gate golden scenarios in public CI" |
| C06 | Semantic market-gate comparator runs in tests | Golden pytest | `tests/golden/test_market_gate.py` | high | "semantic comparator validated by golden tests" |
| C07 | Parity harness defines five comparison dimensions | ADR + enum | ADR-0022; `indiciumforge_core.parity.models.ParityDimension` | high | "five-dimension parity comparator" |
| C08 | Parity verdict labels include match/mismatch/intentional_change/unsupported_gap | ADR-0022 | `docs/decisions/ADR-0022-private-local-parity-harness-v0.11.md` | high | "verdict taxonomy per ADR-0022" |
| C09 | OSS parity demo uses synthetic reference only | Fixture tree + tests | `tests/fixtures/parity_reference_demo/`; `test_parity_harness_fake_recipe.py` | high | "public CI uses synthetic parity_reference_demo" |
| C10 | Frozen reference label is `indiciumgrid-golden-v1` | Golden manifest pin | `GOLDEN_MANIFEST.yaml` `reference:` line | high | "frozen reference label indiciumgrid-golden-v1" |
| C11 | Open core does not import IndiciumGrid Python runtime | ADR + v1 definition | ADR-0019; `docs/V1_0_DEFINITION.md` criterion 1 | high | "migration compares exported artifacts without import indiciumgrid" |
| C12 | Open-core/private split is ADR-governed | ADR-0011 | `docs/decisions/ADR-0011-open-core-private-extension-boundary.md` | high | "open-core exposes ports; proprietary logic stays operator-local" |
| C13 | Provider v2 is session-aware with pack loading | Capability + ADR | CAPABILITY_REGISTER `implemented_v0.9`; ADR-0020 | high | "DataProviderPortV2 with pack loader" |
| C14 | Factor detectors load via pack + entry points | Capability + tests | CAPABILITY_REGISTER `implemented_v0.7`; `test_factor_pack_loading.py` | high | "FactorDetectorPort with pack loading" |
| C15 | Recipe extensions dispatch per-stage via RecipeRunner | ADR + tests | ADR-0021; `test_recipe_runner_dispatch.py` | high | "RecipeRunner loads extension packs behind PrivateRecipeExtensionPort" |
| C16 | Session-cyclic workflow contracts exist (v0.8) | ADR + model doc | ADR-0018; `docs/WORKFLOW_SESSION_MODEL.md` | high | "SessionModel, WorkflowCheckpoint, HandoffArtifact contracts" |
| C17 | A-share daily recipe ID is `indiciumforge.recipe.ashare_daily_research.v1` | Recipe fixture | `tests/fixtures/workflow/recipe_ashare_daily_v1.yaml` | high | "A-share daily recipe as one WorkflowRecipe instance" |
| C18 | Workflow chain summary v4 includes per-stage audit_ok | Tests | `test_parity_summary_v4_audit.py`; `test_fake_ashare_recipe_chain.py` | high | "workflow_chain_summary.v4 carries audit_ok fields" |
| C19 | OSS pytest suite passes on v2.0.0 | CI + local pytest | `.github/workflows/ci.yml`; `python -m pytest -q` (144 passed, 1 skipped at draft time) | high | "144 contract/golden/cli tests pass (1 skipped)" |
| C20 | Ruff lint passes in CI | CI workflow | `.github/workflows/ci.yml` ruff step | high | "static analysis gate in CI" |
| C21 | L1 evidence: OSS golden covers strict_count ≥ 1 scenarios | v1 definition | `docs/V1_0_DEFINITION.md` layer L1 | high | "L1 OSS golden includes strict_pass semantics" |
| C22 | L2 evidence: synthetic parity demo reports strict_count 1 | v1 definition + demo | `docs/V1_0_DEFINITION.md` L2; parity_reference_demo | high | "L2 synthetic parity demo reproduces harness path" |
| C23 | L3 golden date 2026-07-03: five parity dimensions match, all_match true | External sign-off + OSS summary | `docs/V1_0_DEFINITION.md` L3; `RELEASE_NOTES.md` v1.0.0; private `V1_0_RC1_READINESS_REPORT.md` §2026-07-03 dimension table | high | "golden date 2026-07-03: 5/5 parity dimensions match; all_match true" |
| C24 | Blocked dates 2026-06-24 and 2026-06-23 are unsupported_gap | v1 definition + release notes | `docs/V1_0_DEFINITION.md` accepted limitations; `RELEASE_NOTES.md` blocked frozen dates | high | "2026-06-24 / 2026-06-23 blocked as unsupported_gap (layout/reference gaps)" |
| C25 | Not a trading system / not investment advice / not broker execution | README + constitution | `README.md` disclaimer; INDICIUMFORGE_CONSTITUTION.md | high | explicit scope disclaimer in abstract and §11 |
| C26 | Execution port is technical_reserve only | Capability register | CAPABILITY_REGISTER row `execution port` | high | "broker order placement out of scope" |
| C27 | No public proprietary long-structure detectors | Capability register | `proprietary long-structure detectors` = `private_extension` | high | "proprietary detectors not shipped in OSS" |
| C28 | Not full IndiciumGrid replacement | v1 definition | `docs/V1_0_DEFINITION.md` v1.0 meaning paragraph | high | "does not claim full IndiciumGrid replacement" |
| C29 | Anti-inheritance rules prevent IG path/network leakage | ADR-0019 eleven rules | `docs/decisions/ADR-0019-anti-inheritance-from-indiciumgrid-v0.9.md` | high | "eleven anti-inheritance rules guard open core" |
| C30 | Provider output must not feed strict market-gate directly | ADR-0019 rule 8 | ADR-0019; ADR-0020 | high | "data adapter does not authorize strict gate promotion" |
| C31 | Parity harness disclaimer is research_audit_only | Config schema + ADR | ADR-0022; `parity_local.yaml.example` | high | "parity outputs are research audit evidence only" |
| C32 | Agent governance docs exist for coding agents | AGENTS.md + skills | `AGENTS.md`; `agent/skills/*`; `docs/AGENT_QUICKSTART.md` | high | "agent-friendly governance via AGENTS.md and in-repo skills" |
| C33 | 23 architecture decision records document evolution | ADR index | `docs/decisions/ADR-0001` through `ADR-0023` | high | "23 ADRs govern architectural boundaries" |
| C34 | One-release lucerna.* schema compat shim | Code + test | `schema_compat.py`; `test_schema_compat.py` | high | "deprecated lucerna.* IDs accepted one release with warning" |
| C35 | PyPI packages build and pass twine check (not published) | Build logs | `docs/PYPI_RELEASE_CHECKLIST.md`; draft sprint build verification | medium | "packages are build-ready; PyPI publish pending operator gate" |
| C36 | MCP server not implemented in v2.0.0 | Design doc status | `docs/mcp/INDICIUMFORGE_MCP_DESIGN.md` | high | "MCP surface design-only" |
| C37 | Accounting-risk anomaly detection is future work only | Research plan stub | `docs/research/ACCOUNTING_RISK_ANOMALY_RESEARCH_PLAN.md` status line | high | "no completed accounting-risk experiments in OSS" |
| C38 | Research dossier model is technical_reserve | Capability register | CAPABILITY_REGISTER `research dossier model` | high | "ResearchDossier contracts deferred" |
| C39 | Crypto/session cross-domain lessons documented without contest framing | Session model doc | `docs/WORKFLOW_SESSION_MODEL.md` AssetDomain includes crypto_spot | medium | "session model generalizes beyond A-share linear folders" |
| C40 | Extension template ships without proprietary logic | Example tree | `examples/private_extension_template/` | high | "OSS ships extension skeleton only" |
| C41 | No strict_count > 0 in frozen operator reference; L1+L2 cover strict-pass | Accepted limitations | `docs/V1_0_DEFINITION.md` accepted limitations bullet 2 | high | "frozen reference lacks strict_count>0 date; OSS L1+L2 provide strict_count evidence" |
| C42 | No IndiciumForge_bug or private extension defect on golden date | RC1 report | private `V1_0_RC1_READINESS_REPORT.md` §2026-07-03 | medium | "no open-core bug or private extension defect on golden date" |

## Claims explicitly forbidden in paper

| Forbidden claim | Why |
| --- | --- |
| Trading performance, Sharpe, alpha | No OSS experiment artifacts |
| Investment recommendations | Scope violation |
| Fraud conviction / legal findings | Research plan uses "anomaly" not conviction |
| Private file paths, tickers, operator screening lists | ADR-0011 / ADR-0019 |
| Competition / contest workflows | Operator constraint |
| Invented citations | RELATED_WORK.md candidate-only rule |
| daily_review parity mismatch on golden date 2026-07-03 | Contradicts v1.0-rc1 five-dimension match evidence |

## Maintenance

When paper text changes, add or update a row before LaTeX conversion. Codex should reject draft sentences without a register ID.

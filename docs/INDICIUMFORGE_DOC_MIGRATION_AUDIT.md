# IndiciumForge documentation migration audit

Date: 2026-07-09 (updated through v0.5-alpha public alpha gate)

Source: frozen `indiciumgrid @ indiciumgrid-golden-v1`

| IndiciumGrid document | Action | IndiciumForge target |
| --- | --- | --- |
| README.md | translate | README.md + public alpha disclaimer + quickstart |
| ARCHITECTURE.md | translate | INDICIUMFORGE_CONSTITUTION.md + ADR set |
| docs/ENGINEERING_GOVERNANCE.md | carry_forward | docs/ENGINEERING_GOVERNANCE.md (v0.2) |
| docs/DOCUMENTATION_GOVERNANCE.md | carry_forward | docs/DOCUMENTATION_GOVERNANCE.md (v0.2) |
| docs/CLI_GOVERNANCE.md | carry_forward | docs/CLI_GOVERNANCE.md (v0.2) |
| docs/TRADING_LAYER_DESIGN.md | translate | ADR-0003/0004 + CAPABILITY_REGISTER |
| docs/MARKET_AWARENESS_DESIGN.md | split | v0.4 skeleton (ADR-0013); full IG bundle deferred |
| docs/DATA_SOURCE_ROADMAP.md | split | provider contract + asset universe ADR |
| Migration roadmap reconciliation | carry_forward | docs/MIGRATION_ROADMAP.md |
| Market daily-review skeleton v0.4 | carry_forward | ADR-0013 + indiciumforge_workflow.market_awareness |
| Daily-review CLI + manifest audit v0.4.1 | carry_forward | ADR-0014 + indiciumforge artifact list/audit |
| Synthetic E2E workflow v0.5-alpha | carry_forward | ADR-0015 + indiciumforge_workflow.e2e.synthetic |
| docs/INTRADAY_WATCH_DESIGN.md | archive_reference | docs/archive_reference/ |
| docs/ACCOUNT_ANALYSIS_DESIGN.md | archive_reference | docs/archive_reference/ |
| docs/IMPLEMENTATION_GAP_REGISTER.md | translate | CAPABILITY_REGISTER.md |
| docs/LONG_STRUCTURE_FACTORS.md | translate/split | docs/FACTOR_CORE_INVENTORY.md + FACTOR_GOLDEN_MANIFEST |
| Open-core/private-extension boundary | carry_forward | ADR-0011 + CAPABILITY_REGISTER |
| Factor detector port v0.3 | carry_forward | ADR-0012 + indiciumforge_core.factors |
| License strategy | carry_forward | ADR-0007 (Apache-2.0) + LICENSE |
| Public alpha governance | new | RELEASE_NOTES.md, SECURITY.md, .github/workflows/ci.yml |
| docs/DECISIONS/* | carry_forward | docs/decisions/ADR-0001..0015 |
| docs/archive/* | drop | not copied |
| docs/RUNBOOK_DAILY_WORKFLOW.md | archive_reference | operator note only |

Promotion rule inherited: implementation + tests + docs must agree before a capability changes status.

## v0.5-alpha public alpha gate (2026-07-09)

- License closed: Apache-2.0 (ADR-0007 accepted).
- Shipped ADRs promoted: 0013, 0014, 0015 → accepted.
- No IndiciumGrid modifications; no new workflow/factor/provider features in this patch.

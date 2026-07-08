# Lucerna documentation migration audit

Date: 2026-07-08

Source: frozen `indiciumgrid @ indiciumgrid-golden-v1`

| IndiciumGrid document | Action | Lucerna target |
| --- | --- | --- |
| README.md | translate | README.md |
| ARCHITECTURE.md | translate | LUCERNA_CONSTITUTION.md + ADR set |
| docs/ENGINEERING_GOVERNANCE.md | carry_forward | docs/ENGINEERING_GOVERNANCE.md (v0.2) |
| docs/DOCUMENTATION_GOVERNANCE.md | carry_forward | docs/DOCUMENTATION_GOVERNANCE.md (v0.2) |
| docs/CLI_GOVERNANCE.md | carry_forward | docs/CLI_GOVERNANCE.md (v0.2) |
| docs/TRADING_LAYER_DESIGN.md | translate | ADR-0003/0004 + CAPABILITY_REGISTER |
| docs/MARKET_AWARENESS_DESIGN.md | split | v0.2 capability + provider contract |
| docs/DATA_SOURCE_ROADMAP.md | split | provider contract + asset universe ADR |
| docs/INTRADAY_WATCH_DESIGN.md | archive_reference | docs/archive_reference/ |
| docs/ACCOUNT_ANALYSIS_DESIGN.md | archive_reference | docs/archive_reference/ |
| docs/IMPLEMENTATION_GAP_REGISTER.md | translate | CAPABILITY_REGISTER.md |
| docs/LONG_STRUCTURE_FACTORS.md | translate/split | docs/FACTOR_CORE_INVENTORY.md + FACTOR_GOLDEN_MANIFEST |
| Open-core/private-extension boundary | carry_forward | ADR-0011 + CAPABILITY_REGISTER |
| Factor detector port v0.3 | carry_forward | ADR-0012 + lucerna_core.factors |
| docs/DECISIONS/* | carry_forward | docs/decisions/ADR-0001..0012 |
| docs/archive/* | drop | not copied |
| docs/RUNBOOK_DAILY_WORKFLOW.md | archive_reference | operator note only |

Promotion rule inherited: implementation + tests + docs must agree before a capability changes status.

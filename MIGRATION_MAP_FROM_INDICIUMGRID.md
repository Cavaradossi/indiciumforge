# Migration Map From IndiciumGrid

IndiciumGrid is frozen at `indiciumgrid-golden-v1`. This map records what Lucerna v0.1 implements, defers, or treats as reference-only.

| IndiciumGrid Source | Lucerna Target | v0.1 Scope | Golden Scenario |
| --- | --- | --- | --- |
| `workflow.apply_market_gate` | `lucerna_workflow.market_gate.kernel` | implement | `strict_pass_mixed` |
| `workflow._market_gate_row` | market-gate row evaluation | implement | `strict_pass_mixed` |
| active-watch helpers | `lucerna_workflow.market_gate.active_watch` | implement | `empty_strict_c_grade` |
| calibration audit helper | `lucerna_workflow.market_gate.calibration` | implement | all market-gate scenarios |
| market-gate review path resolver | `lucerna_workflow.market_gate.resolver` | implement | `fallback_post_close` |
| `workflow.run_market_gate_workflow` | `lucerna_workflow.market_gate.runner` | implement | all market-gate scenarios |
| `REVIEW_COLUMNS` / `MARKET_GATE_COLUMNS` | `lucerna_core.labels` | implement compat labels | all market-gate scenarios |
| `THEME_STATE_RULES` | `lucerna_core.market.theme_rules` | metadata only | state/summary artifacts |
| provider registry | `lucerna_core.ports.DataProviderPort` | contract only | contract tests |
| intraday watch | future watch capability | not in v0.1 | none |
| factor tracking | future research/evidence audit capability | not in v0.1 | none |
| account analysis | future account evidence capability | not in v0.1 | none |
| catalyst/research experimental branch | future capture/evidence capability | not in v0.1 | none |

Do not use line numbers as migration anchors. Use symbol names, scenario ids, and artifact names.

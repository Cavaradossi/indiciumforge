# Golden Artifact Test Plan

Golden tests compare Lucerna outputs with artifacts generated from frozen IndiciumGrid reference scenarios.

Reference:

```yaml
reference: indiciumgrid@indiciumgrid-golden-v1
```

## Scenario Set

- `strict_pass_mixed`: strict, observation, rejected, active-watch, and calibration all present.
- `empty_strict_c_grade`: strict is empty but active-watch and calibration remain meaningful.
- `fallback_post_close`: preopen review is missing and post-close review is used with warning.
- `missing_theme_fail`: missing `theme_state_ranking.csv` fails explicitly.
- `catalyst_ignored`: catalyst files do not affect strict gate outputs.

## Comparison Levels

- Schema equality: files, columns, JSON keys, required fields.
- Semantic equality: counts, code sets, gate reasons, rejected reasons, active-watch reasons, calibration fields, warnings.
- Byte equality: only small stable JSON fixtures without paths, timestamps, or unstable ordering.

Differences must be classified as `match`, `intentional_change`, or `unsupported_gap`.

## Factor core scenarios (planned)

Factor-core golden scenarios are defined in [FACTOR_GOLDEN_MANIFEST.yaml](FACTOR_GOLDEN_MANIFEST.yaml).
Planning details: [docs/FACTOR_GOLDEN_SCENARIO_PLAN.md](docs/FACTOR_GOLDEN_SCENARIO_PLAN.md).

IG scenarios in FACTOR_GOLDEN_MANIFEST.yaml are `private_reference` (require private factor pack).
Open-source demo scenarios: [FACTOR_DEMO_MANIFEST.yaml](FACTOR_DEMO_MANIFEST.yaml).

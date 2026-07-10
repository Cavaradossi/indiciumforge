# Accounting-Risk Anomaly Detection — Research Plan

**Status:** planning stub only. **No completed experiments.** Do not cite as published research or submit to arXiv until the reproducibility package exists.

## Terminology

Use **accounting-risk anomaly detection** — not "fraud conviction" or legal findings.

Lucerna and related research aim to surface **disclosure and accounting-signal anomalies** for human review. Outputs are audit hypotheses, not investment recommendations or legal conclusions.

## Problem statement (draft)

Detect statistically unusual patterns in point-in-time financial disclosures and derived accounting-risk features that may indicate elevated reporting risk — subject to false positives and domain shift.

Primary open-research direction: **point-in-time disclosure drift** — measuring how filing revisions, restatement flags, and feature trajectories diverge from peer and historical baselines at each disclosure date.

## Conceptual reuse (no private data)

IndiciumGrid explored accounting-risk **signal design** conceptually (feature families, labeling guardrails, audit-first presentation). This open repo:

- Does **not** ship private datasets, labels, or calibrated models.
- May reuse **public methodological ideas** in future Lucerna extensions or research modules.
- Must keep all experiments on public or synthetic data committed to OSS.

## Data and labels (future work)

| Topic | Plan |
| --- | --- |
| Data sources | Public filings APIs, synthetic generators for unit tests only in OSS |
| Labels | Weak labels from disclosure events; avoid hindsight conviction labels |
| Point-in-time | Strict as-of dates for every feature; no future filing leakage |
| Holdout | Time-based splits, not random ticker splits |

## Evaluation risks

Document and mitigate explicitly:

1. **Look-ahead bias** — features using post-event information
2. **Survivorship bias** — universe restricted to currently listed issuers
3. **Label leakage** — training labels derived from outcomes used at inference time
4. **Multiple testing** — uncontrolled factor mining across many thresholds
5. **Domain shift** — regime changes across accounting standards and markets

## Baselines (planned)

- Rule-based disclosure change flags
- Univariate z-score drift per feature
- Simple peer-group median absolute deviation
- Gradient boosting on point-in-time tabular features (only after PIT pipeline verified)

No baseline results are claimed in this document.

## Method sketch (planned)

1. Build point-in-time feature store aligned to Lucerna artifact audit timestamps.
2. Define anomaly score as robust multivariate drift vs peer cohort.
3. Emit **research artifacts** (scores, explanations, provenance) — same evidence-first pattern as workflow outputs.
4. Human-in-the-loop review; no automated trade linkage.

## Future arXiv / technical report outline

When experiments exist, a paper should include:

1. Problem definition and threat model (audit vs trading)
2. Dataset description and label construction
3. Point-in-time protocol diagram
4. Baselines and proposed method
5. Primary metrics (precision at k, event recall, calibration)
6. Error analysis and failure modes
7. Reproducibility package (code, configs, synthetic fixtures — no private data)

**Until then:** treat this file as an internal roadmap stub only.

## Relationship to Lucerna OSS

- No new runtime code required for v1.0 publication.
- Future work may add optional research ports or example notebooks under `docs/research/`.
- Private calibrated models remain outside OSS per [EXTENSION_AUTHOR_GUIDE.md](../EXTENSION_AUTHOR_GUIDE.md).

## Next steps

See [NEXT_ACTIONS.md](../NEXT_ACTIONS.md) — research section.

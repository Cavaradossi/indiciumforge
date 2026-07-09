# Lucerna v1.0 Definition of Done (Draft)

Planning document — not a release commitment. v1.0 means Lucerna can replace IndiciumGrid
for **core A-share daily research workflow** without importing IG Python runtime.

## Criteria

1. **Local A-share daily recipe** runs end-to-end via Lucerna CLI + private packs (provider,
   factor, recipe extension) without `import indiciumgrid`.
2. **Core artifacts** pass `lucerna artifact audit` for daily_review, post_close, preopen,
   market_gate stages.
3. **Parity gate:** private golden reference comparison for market_gate (existing) plus
   post_close/preopen review shape and strict-count semantics.
4. **Private extensions** live outside the public repository.
5. **No IG private detector logic** in OSS (slugs, thresholds, calibrated parameters).
6. **No TDX/local path defaults** in OSS code or committed fixtures.
7. **Market-gate boundary preserved** — gate inputs are review artifact +
   `theme_state_ranking.csv` only.
8. **Empty strict / empty universe** produce explicit `empty_result_reason` in stage state JSON.
9. **Provider provenance** attached to evidence-stage outputs where data was fetched.
10. **Documented command sequence** in README/runbook:
    sync → daily-review → post-close → preopen → market-gate → audit.

## Not required for v1.0

- intraday-watch, midday/late quote refresh, factor_tracking, account analysis
- ETF workflow, crypto/perp domains
- ResearchDossier production runtime
- Full IG bundle parity (xlsx/md/txt sidecars, accounting risk sidecars)

## Roadmap alignment

| Version | Delivers toward v1.0 |
| --- | --- |
| v0.10 | Recipe wiring + fake private recipe (OSS) |
| v0.11 | Private production review builder + private golden reference |
| v0.12+ | Optional midday refresh, extended parity |

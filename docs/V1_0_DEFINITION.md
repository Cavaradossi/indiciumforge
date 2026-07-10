# Lucerna v1.0 Definition of Done (Draft)

Planning document — not a release commitment.

## v1.0 meaning

v1.0 means the **Lucerna open-core + private extension** migration path for **core A-share daily
research workflow** is validated: operators can run `lucerna parity run` with a private recipe pack
against a local reference without `import indiciumgrid`.

v1.0 **does not** mean Lucerna fully replaces IndiciumGrid for all domains or artifact bundles.

## v1.0-rc1 (readiness milestone)

v1.0-rc1 is a **readiness tag** on open-core v0.11.0 plus documented private parity evidence
(`lucerna-private` readiness report). It confirms:

- v0.11 parity harness and recipe chain operate end-to-end with a real private A-share adapter.
- At least one frozen trade date achieves `all_match: true` on all five parity dimensions.
- Remaining gaps (incomplete frozen layouts, `strict_count>0` absence) are classified and non-blocking.

v1.0-rc1 is **not** a feature release and does not bump open-core semantics beyond v0.11.0.

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

## Not required for v1.0 (explicit non-scope)

- **Real TDX sync in OSS** — private adapter only
- **Proprietary factor detectors in OSS** — private factor packs only
- **Account / watchlist / research dossier / intraday** runtime in OSS
- intraday-watch, midday/late quote refresh, factor_tracking, account analysis
- ETF workflow, crypto/perp domains
- ResearchDossier production runtime
- Full IG bundle parity (xlsx/md/txt sidecars, accounting risk sidecars)

## Roadmap alignment

| Version | Delivers toward v1.0 |
| --- | --- |
| v0.10 | Recipe wiring + fake private recipe (OSS) |
| v0.11 | Private local parity harness (OSS) + local reference compare |
| v0.12 | Private parity pilot evidence (external `lucerna-private`) |
| v1.0-rc1 | Readiness tag + documented multi-date parity summary |
| v1.0 | Production private review builder + repeatable operator sign-off |

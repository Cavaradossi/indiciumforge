# Lucerna v1.0 Definition of Done

Signed scope for Lucerna **v1.0.0** (open-core semantics frozen at v0.11.0; private path evidenced externally).

## v1.0 meaning

v1.0 means the **Lucerna open-core + private extension** migration path for **core A-share daily
research workflow** is validated: operators can run `lucerna parity run` with a private recipe pack
against a local reference without `import indiciumgrid`.

v1.0 **does not** mean Lucerna fully replaces IndiciumGrid for all domains, artifact bundles, or
operator surfaces (account, watchlist, intraday, research dossier).

## v1.0-rc1 (readiness milestone — completed)

v1.0-rc1 (`838f018`) documented private parity evidence before final sign-off. See private repo
`V1_0_RC1_READINESS_REPORT.md`.

## v1.0 signed (final)

v1.0.0 adds formal sign-off documentation and accepted gap register. Open-core code semantics are
unchanged from v0.11.0; version label reflects migration-path maturity.

Evidence layers:

| Layer | What it proves |
| ----- | -------------- |
| L1 OSS golden | Market-gate strict semantics including `strict_count >= 1` scenarios |
| L2 OSS parity demo | Harness + comparator against synthetic reference (`strict_count: 1`) |
| L3 Private real-path | End-to-end IG-output adapter on golden date `2026-07-03`, `all_match: true` |

See private repo `V1_0_SIGNOFF_REPORT.md` and `V1_0_SIGNOFF_GAP_REGISTER.md` (no paths in Lucerna Git).

## Criteria

1. **Local A-share daily recipe** runs end-to-end via Lucerna CLI + private packs without `import indiciumgrid`. — **met** (L3)
2. **Core artifacts** pass `lucerna artifact audit` for workflow stages. — **partial**: `market_gate` ok on golden run; IG-shaped `daily_review` fails Lucerna skeleton manifest (accepted gap GAP-07)
3. **Parity gate:** private golden reference comparison for market_gate plus post_close/preopen shape. — **met** (L3); strict-pass semantics also covered by L1+L2
4. **Private extensions** live outside the public repository. — **met**
5. **No IG private detector logic** in OSS. — **met**
6. **No TDX/local path defaults** in OSS. — **met**
7. **Market-gate boundary preserved.** — **met**
8. **Empty strict / empty universe** produce explicit `empty_result_reason`. — **met** (ADR-0016)
9. **Provider provenance** on evidence-stage outputs where fetched. — **met** (contract v2)
10. **Documented operator runbook** in private repo. — **met**

## Accepted limitations (v1.0)

Documented in private `V1_0_SIGNOFF_GAP_REGISTER.md`:

- Incomplete frozen layouts (`2026-06-24`, `2026-06-23`) not runnable without adapter expansion
- No real frozen `strict_count > 0` date (L1+L2 suffice for open-core)
- IG-output replay adapter; production review builder deferred to v1.1
- IG-shaped daily_review vs Lucerna manifest column set (parity structure still matches reference)

## Not in v1.0 scope

- **Real TDX sync in OSS** — private adapter only
- **Proprietary factor detectors in OSS** — private factor packs only
- **Account / watchlist / research dossier / intraday** runtime in OSS
- Full IG bundle parity (xlsx/md/txt sidecars, accounting risk sidecars)
- Full IndiciumGrid replacement claim

## Roadmap alignment

| Version | Delivers toward v1.0 |
| --- | --- |
| v0.10 | Recipe wiring + fake private recipe (OSS) |
| v0.11 | Private local parity harness (OSS) |
| v0.12 / rc1 | Private pilot evidence + readiness tag |
| **v1.0** | **Signed migration path + gap register** |
| v1.1+ | Production private review builder; partial frozen layouts |

# Current Status

Snapshot for open-source readers and agents. Last aligned with **Lucerna v1.0.0** sign-off.

## Release state

| Item | Value |
| --- | --- |
| Open-core version label | `1.0.0` (`signed_v1.0`) |
| Code semantics baseline | v0.11.0 parity harness (frozen) |
| License | Apache-2.0 |
| Reference pin | `indiciumgrid @ indiciumgrid-golden-v1` (external, frozen) |

v1.0.0 is a **documentation and sign-off milestone**. No new open-core features beyond v0.11.0 semantics.

## Evidence boundary

| Evidence type | Where it lives | In OSS Git? |
| --- | --- | --- |
| Golden market-gate scenarios | `tests/golden/` | Yes (synthetic exports) |
| OSS parity demo | `tests/fixtures/parity_reference_demo/` | Yes |
| Private golden parity | External private sign-off repo | No |
| Accepted gap register | External private sign-off repo | No |
| Legacy `output/` trees | Operator-local | No |

OSS readers should treat private sign-off reports as **operator evidence**, not as files in this repository.

## Known accepted gaps (summary)

Private sign-off documents gaps such as:

- IG-shaped `daily_review` manifest vs Lucerna manifest (informational audit mismatch)
- Blocked frozen trade dates where reference layout is incomplete
- `strict_count > 0` not available in frozen reference for some dates

All gaps are **accepted for v1.0** in the private gap register. Lucerna does not claim full legacy replacement.

Details: [V1_0_DEFINITION.md](V1_0_DEFINITION.md), [RELEASE_NOTES.md](../RELEASE_NOTES.md).

## Public release security scan

Pre-publish scan (competition terms, hardcoded operator paths, secrets, run artifacts):

| Check | Result |
| --- | --- |
| Competition / trading leak terms | Clean in tracked files |
| Hardcoded `D:\project\` paths in examples | Remediated (generic `<repo-root>`, `%TEMP%`) |
| Secrets / API keys | Clean |
| Private config committed | Only `.example` templates |

Re-scan before each release with patterns in [EXTENSION_AUTHOR_GUIDE.md](EXTENSION_AUTHOR_GUIDE.md#security-checklist).

## What works in OSS without private packs

- `lucerna workflow synthetic-e2e`, `chain`, `market-gate`, `daily-review`
- `lucerna artifact list/audit`
- `lucerna factor scan` with demo pack
- `lucerna provider inspect/fetch` with fixtures
- `lucerna parity run` with `parity_reference_demo`

## What requires private extensions

- Live market data (TDX, network providers)
- Production A-share review generation
- Proprietary factor detectors and calibrated policies
- Parity against operator legacy `output/` trees

Start: [EXTENSION_AUTHOR_GUIDE.md](EXTENSION_AUTHOR_GUIDE.md).

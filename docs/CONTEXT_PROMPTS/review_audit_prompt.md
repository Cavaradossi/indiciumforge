# Review Audit Prompt

Use this prompt for pre-merge audit of Lucerna pull requests or local patches.

---

Audit this Lucerna change set before merge. Lucerna is **alpha research software** — not investment advice, not a trading system.

## Security and leakage

- [ ] No API keys, tokens, passwords, or `sk-` / `AKIA` patterns
- [ ] No hardcoded operator paths (`D:\project\...`, home dirs, `vipdoc`)
- [ ] No committed `parity_local.yaml` (only `.example` templates)
- [ ] No `run_artifacts/`, real `output/` trees, or account/watchlist data
- [ ] No competition names or broker execution references

Allowed: governance docs saying "do not commit output/.indiciumgrid" as guardrails.

## Architecture

- [ ] Changes use ports and pack loaders, not private imports
- [ ] ADR and CAPABILITY_REGISTER status consistent
- [ ] No strict-gate coupling to catalyst/KOL/news
- [ ] Parity verdicts remain research-audit semantics

## Tests and quality

- [ ] `ruff check .` clean
- [ ] `pytest -q` green (note skip count if any)
- [ ] Golden tests run for market-gate touches
- [ ] New fixtures are synthetic and documented

## Documentation

- [ ] README not bloated with version changelog (belongs in RELEASE_NOTES)
- [ ] Public paths use `<repo-root>` or `/tmp` / `%TEMP%` — not operator machines
- [ ] Extension/private boundaries still accurate

## Output

| Section | Content |
| --- | --- |
| Summary | One paragraph |
| Blockers | Must-fix before merge |
| Warnings | Should-fix |
| Nits | Optional |
| Scan commands | `rg` patterns you ran |

Reference: [AGENT_REVIEW_CHECKLIST.md](../AGENT_REVIEW_CHECKLIST.md), [EXTENSION_AUTHOR_GUIDE.md](../EXTENSION_AUTHOR_GUIDE.md).

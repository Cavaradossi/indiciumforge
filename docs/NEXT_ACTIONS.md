# Next Actions

Post-open-source backlog. Not committed to a release date.

## GitHub publication (operator)

1. Apply public polish patch and run quality gates.
2. Push to a **private** GitHub repo first; verify README Mermaid and CI.
3. Switch visibility to **public**.
4. Publish GitHub Release for `v1.0.0` from polished HEAD (retag locally if tag predates polish).

## Documentation

- [ ] Keep [CURRENT_STATUS.md](CURRENT_STATUS.md) updated per release.
- [ ] Expand [EXTENSION_AUTHOR_GUIDE.md](EXTENSION_AUTHOR_GUIDE.md) with community FAQ as issues arrive.
- [ ] Optional: `docs/MIGRATION_ROADMAP.md` v1.1 slice when scope is agreed.

## Extension ecosystem

- [ ] Publish minimal [examples/private_extension_template/](../examples/private_extension_template/) as canonical starter.
- [ ] Document pack versioning and compatibility matrix (provider v2, recipe v1, parity config v1).
- [ ] Community template for private parity config (operator-local only).

## Research

- [ ] Execute [research/ACCOUNTING_RISK_ANOMALY_RESEARCH_PLAN.md](research/ACCOUNTING_RISK_ANOMALY_RESEARCH_PLAN.md) — **no arXiv until experiments exist**.
- [ ] Point-in-time disclosure drift prototype on public/synthetic datasets only.

## v1.1 candidates (open core)

Per [MIGRATION_ROADMAP.md](MIGRATION_ROADMAP.md) — requires ADR before implementation:

- Manifest audit extensions for post_close/preopen stages
- Stricter OSS parity fixtures where `strict_count > 0` can be demonstrated synthetically
- Provider/workflow integration hooks (still no live network in OSS CI)

## Explicit non-goals (near term)

- Trading, broker execution, or competition integrations
- Committing private `output/`, reference trees, or operator configs
- Claiming completed accounting-risk experiments without reproducibility package

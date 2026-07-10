# Agent Quickstart

Five-minute onboarding for AI agents working in the IndiciumForge open-core repository.

## What you are editing

IndiciumForge is a **contract-first open core** for evidence-first financial research workflows. Your job is to preserve ports, artifact contracts, and golden parity — not to add trading, live brokers, or competition features.

## Repository layout

```text
packages/indiciumforge_core/     # ports, artifacts, recipes, parity, providers
packages/indiciumforge_workflow/ # market_gate, daily_review, chain runners
packages/indiciumforge_cli/      # Typer CLI
tests/golden/              # semantic parity vs reference artifacts
tests/fixtures/            # synthetic demo data only
docs/                      # ADRs, templates, agent docs
```

## Hard rules (read first)

1. **Frozen reference** — `indiciumgrid @ indiciumgrid-golden-v1` is read-only. Do not modify IndiciumGrid source, tests, or docs from this repo.
2. **Migration principle** — preserve behavior where golden-covered, not implementation shape.
3. **No scope creep** — do not connect KOL/news/catalyst inputs to strict gate logic.
4. **Ports, not vendors** — workflows consume `DataProviderPort`, `FactorDetectorPort`, recipe extensions; never import private runtime modules into OSS.
5. **No private data in Git** — never commit `parity_local.yaml`, `reference/`, `run_artifacts/`, `output/`, `.indiciumgrid/`, credentials, or operator paths.

Full rules: [AGENTS.md](../AGENTS.md).

## Allowed agent files

- [AGENTS.md](../AGENTS.md)
- [docs/AGENT_WORKFLOW.md](AGENT_WORKFLOW.md)
- [docs/AGENT_REVIEW_CHECKLIST.md](AGENT_REVIEW_CHECKLIST.md)
- [docs/CONTEXT_PROMPTS/](CONTEXT_PROMPTS/) — reusable prompts for Codex/Cursor/review

## Quality gates (run before proposing merge)

```bash
cd <repo-root>
python -m ruff check .
python -m pytest -q
```

For market-gate changes:

```bash
python -m pytest tests/golden -k market_gate
```

On Windows with temp permission issues:

```powershell
python -m pytest -p no:cacheprovider -q --basetemp "$env:TEMP\indiciumforge_pytest\pytest-basetemp-<unique>"
```

## Typical implementer flow

1. Read [INDICIUMFORGE_CONSTITUTION.md](../INDICIUMFORGE_CONSTITUTION.md), relevant ADR, and [CAPABILITY_REGISTER.md](../CAPABILITY_REGISTER.md).
2. Implement only the requested capability slice.
3. Update [MIGRATION_MAP_FROM_INDICIUMGRID.md](../MIGRATION_MAP_FROM_INDICIUMGRID.md) when a mapping completes.
4. Run quality gates.
5. For golden changes, update `GOLDEN_MANIFEST.yaml` with `intentional_change` or `unsupported_gap`.

Details: [AGENT_WORKFLOW.md](AGENT_WORKFLOW.md).

## Typical reviewer flow

1. Verify behavior against golden expected artifacts, not legacy module shape.
2. Check ADR and capability status consistency.
3. Reject scope creep into `not_in_v0.1` / frozen v1.0 items.
4. Confirm no private paths, secrets, or competition references in tracked files.

Checklist: [AGENT_REVIEW_CHECKLIST.md](AGENT_REVIEW_CHECKLIST.md). Prompt: [CONTEXT_PROMPTS/review_audit_prompt.md](CONTEXT_PROMPTS/review_audit_prompt.md).

## Context documents

| Doc | When to read |
| --- | --- |
| [SYSTEM_MAP.md](SYSTEM_MAP.md) | Package boundaries, ports, artifact stages |
| [CURRENT_STATUS.md](CURRENT_STATUS.md) | v1.0.0 sign-off state and accepted gaps |
| [NEXT_ACTIONS.md](NEXT_ACTIONS.md) | Post-open-source backlog |
| [EXTENSION_AUTHOR_GUIDE.md](EXTENSION_AUTHOR_GUIDE.md) | Private pack boundaries |

## Encoding policy

- Repository is UTF-8.
- CLI flags, schema IDs, config keys, artifact filenames, and operational logs stay ASCII-stable.
- Documentation may use Unicode (including Chinese labels) where appropriate.
- Do not mass-normalize unrelated files; fix only surfaces you touch.

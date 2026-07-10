# OpenBB Public Demo Plan (v2.1.0)

**Status:** planning only — **not implemented in v2.0.0**.

This document defines a low-friction public demo for IndiciumForge v2.1.0. It is a scope and acceptance plan, not a runtime deliverable.

## Motivation

IndiciumForge v2.0.0 is contract-first and evidence-oriented. That strength comes with a cost:

- The open core is engineering-heavy (ports, schemas, parity harness, recipe model).
- The default quickstart uses synthetic fixtures and assumes familiarity with artifact audit concepts.
- There is no **3-minute public demo** that shows a newcomer how IndiciumForge produces auditable workflow output from familiar market data.

A v2.1 public demo should lower the adoption barrier without weakening the non-trading, non-broker boundary.

## Goal (v2.1.0)

Ship **v2.1.0** with a public-data demo where a new user can:

1. Install from the OSS repo or PyPI workspace.
2. Run **one documented CLI smoke command**.
3. Produce a **small, deterministic artifact tree** plus an **artifact audit report** (or equivalent workflow summary).
4. Complete the flow in roughly **3 minutes**, with **no private files**, **no operator paths**, and **no API keys in Git**.

The demo illustrates IndiciumForge as a **research audit workflow**, not as a trading system.

## Why OpenBB first

[OpenBB Open Data Platform](https://github.com/OpenBB-finance/OpenBB) is the preferred candidate for the v2.1 data-provider adapter example:

- It is a **public** financial data integration layer (`pip install openbb`).
- It aligns with existing provider-contract direction ([ADR-0009](decisions/ADR-0009-provider-contract-v1.md), [ADR-0020](decisions/ADR-0020-session-aware-data-provider-v2-v0.9.md)).
- It demonstrates the **open-core + adapter** pattern without committing proprietary A-share paths or TDX vipdoc roots.
- It is widely recognized as a data platform for analysts and AI agents, not as a broker execution gateway.

OpenBB is an **adapter example** for OSS documentation and CI smoke — not a claim that IndiciumForge replaces OpenBB Workspace or any commercial terminal.

## Why not vn.py (deferred)

**vn.py is out of scope for v2.1.**

vn.py is oriented toward live trading, broker connectivity, and execution gateways. That conflicts with IndiciumForge's published boundary:

- Not a trading system or broker execution platform.
- Not investment advice or order routing.

vn.py may be discussed in future ADRs only if a strict **execution-adapter boundary** is maintained ([ADR-0006](decisions/ADR-0006-execution-adapter-boundary.md)). It is not a v2.1 public-demo priority.

## TDX boundary

**No TDX production adapter or real vipdoc paths in OSS.**

- TDX integration remains **operator-local** via [PRIVATE_DATA_ADAPTER_TEMPLATE.md](PRIVATE_DATA_ADAPTER_TEMPLATE.md).
- OSS may ship **fake fixtures**, **adapter templates**, and **contract tests** only.
- The v2.1 demo must not require `D:\...` paths, `.indiciumgrid/`, or local `output/` trees.

## Proposed scope (v2.1.0 implementation)

| Item | Description |
| --- | --- |
| `examples/openbb_daily_chain/` | Example layout: minimal recipe/config, fixture notes, expected artifact paths |
| Public fixture or generated small dataset | Checked-in CSV/JSON slice or CI-generated deterministic sample; no live network required in default CI |
| One CLI smoke command | e.g. documented variant of `indiciumforge workflow synthetic-e2e` or a dedicated `openbb-demo` entry (TBD at implementation) |
| Artifact audit output | `indiciumforge artifact audit` (or chain summary) on the demo artifact root |
| README quickstart snippet | Copy-paste block under a "Public demo (OpenBB)" section |
| Documentation | Link from README and optionally [NEXT_ACTIONS.md](NEXT_ACTIONS.md) |

**Tone:** research workflow and audit evidence only — **no trading advice, no strategy claims, no P&L promises**.

## Non-goals

- No live trading or order placement.
- No broker or execution gateway integration (including vn.py).
- No private A-share detector packs or IG `output/` adapters in OSS.
- No API keys, tokens, or cookies committed to Git.
- No competition or contest-specific material.
- No expansion of the arXiv paper body in the v2.1 implementation slice (see Paper impact).

## Acceptance criteria

Before tagging **v2.1.0**:

- [ ] Clean install from documented steps (`pip install -e ...` or PyPI smoke path).
- [ ] Demo command runs on a fresh clone **without** private files or operator-local YAML.
- [ ] Output is **small and deterministic** (fixed trade date, fixture-backed or pinned sample).
- [ ] `python -m ruff check .` passes.
- [ ] `python -m pytest -q` passes (demo covered by contract or golden smoke test).
- [ ] README includes an updated **Public demo** section with the smoke command and expected artifacts.
- [ ] Forbidden-term and secrets scan clean per [EXTENSION_AUTHOR_GUIDE.md](EXTENSION_AUTHOR_GUIDE.md).

## Paper impact

| Phase | Action |
| --- | --- |
| **Current arXiv MVP (v2.0)** | **Not blocked.** Author metadata and `paper/main.bbl` can ship independently of the OpenBB demo. |
| **After v2.1 demo exists** | Cite the public demo as a **reproducibility example** in a revised paper version (e.g. "Public OpenBB-backed smoke workflow, fixture-backed, deterministic audit output"). |
| **This plan commit** | Does not expand `paper/main.tex` body or add new claims requiring experimental evidence. |

## Related docs

- [FUTURE_SURFACES.md](FUTURE_SURFACES.md) — naming and surface registry
- [EXTENSION_AUTHOR_GUIDE.md](EXTENSION_AUTHOR_GUIDE.md) — private pack boundaries
- [MIGRATION_ROADMAP.md](MIGRATION_ROADMAP.md) — live provider adapter timeline
- [PRIVATE_DATA_ADAPTER_TEMPLATE.md](PRIVATE_DATA_ADAPTER_TEMPLATE.md) — operator-local data packs

## Implementation note

When v2.1 work starts, open an ADR for the OpenBB adapter boundary (network opt-in, fixture fallback, CI policy) before merging runtime code.

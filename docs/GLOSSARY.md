# Glossary

Plain-language definitions for IndiciumForge terms. **Start here** if README jargon feels heavy.

## What to learn first

If you are new, read these four in order:

1. **workflow** — the end-to-end research process you run
2. **recipe** — the ordered list of stages inside that process
3. **artifact** — the files each stage writes (your auditable outputs)
4. **extension pack** — how you plug in private data, factors, or stage logic

Add **artifact audit** and **reference output** when you start validating runs. Add **parity** when you compare a new run against saved expected results.

---

## workflow

A repeatable research process from inputs (data, fixtures, prior stage outputs) to staged outputs.

In IndiciumForge, workflows are run via the CLI (`indiciumforge workflow ...`) and produce a dated folder tree under your chosen output root.

**You need this when:** you want one command to reproduce “what we run every research day” instead of a pile of ad-hoc scripts.

---

## recipe

A named, ordered set of stages (for example: awareness → post-close review → preopen handoff → market gate).

Recipes are configuration (YAML), not hard-coded monoliths. Different asset domains can reuse the same session contracts with different recipes.

**You need this when:** your team thinks in “stages” and handoffs, not a single notebook cell.

---

## artifact

A versioned output file (JSON state, CSV review table, chain summary) produced by a workflow stage.

Artifacts carry a schema identifier so tools—and humans—know what shape to expect.

**Plain name:** *output artifact* (输出工件).

**You need this when:** you want outputs that are inspectable, diffable, and machine-checkable.

---

## artifact audit

A structural check that required files exist, parse correctly, use expected schema IDs, and agree on trade date.

Command: `indiciumforge artifact audit`.

**Plain name:** *output completeness check* (输出完整性检查).

**You need this when:** you want a fast “did the run produce a complete bundle?” gate before deeper comparison.

**Not:** proof that signals are economically correct—only that the output bundle is structurally valid.

---

## reference output

A saved set of expected artifacts used as the baseline for “did we get the same shape and semantics?”

In OSS demos this is often a small checked-in tree under `tests/fixtures/`. In production you may keep reference trees locally (not in the public repo).

**Plain name:** *reference output* (参考输出).

**You need this when:** you refactor a stage and need a trustworthy before/after comparison.

---

## golden test

An automated test that runs a stage (or chain) and compares results against checked-in reference output using semantic rules—not just byte equality.

OSS includes golden scenarios for core market-gate semantics.

**You need this when:** you maintain the open core and want CI to catch regressions in output meaning.

**Ordinary users:** know that golden tests exist in CI; you rarely author them unless you contribute to core.

---

## parity

A configurable comparison of actual run outputs against a reference root, dimension by dimension, producing a report (match, mismatch, intentional change, unsupported gap).

Command: `indiciumforge parity run` (demo config ships in fixtures).

**Plain name:** *output comparison* / *对答案*.

**You need this when:** you upgrade recipes or extensions and need a structured diff story for reviewers.

**Not:** production sign-off or live-trading certification.

---

## extension pack

A YAML manifest plus Python entry points that register a private **data provider**, **factor detector**, or **recipe extension** behind stable core ports.

Starter layout: [examples/private_extension_template/](../examples/private_extension_template/).

**You need this when:** your proprietary logic should stay out of the public repo but still plug into the same CLI and artifact contracts.

---

## private extension

Any implementation you keep operator-local: live data adapters, proprietary factors, production recipe bodies, local reference trees.

The open core defines *how* to load extensions, not *your* proprietary algorithms.

**You need this when:** you open-source the framework but not your alpha, paths, or credentials.

---

## ADR

*Architecture Decision Record* (设计决策记录)—a short doc capturing why a boundary or contract was chosen.

ADRs live under [docs/decisions/](decisions/). They are valuable for maintainers and contributors, not required reading for a first quickstart.

**You need this when:** you change core contracts or wonder “why is execution out of scope?”

---

## output root (`--output-root` / `--artifact-root`)

The directory where a run writes its dated workflow tree (for example `workflows/20260623/...`).

CLI flags may say `--artifact-root` in some commands; treat it as **your run output folder**.

**You need this when:** every command—you pick a writable path per run or per environment.

**Tip:** use a temp directory for demos; keep production roots on operator machines, not in Git.

---

## Related reading

- [EXTENSION_AUTHOR_GUIDE.md](EXTENSION_AUTHOR_GUIDE.md) — build private packs
- [WORKFLOW_SESSION_MODEL.md](WORKFLOW_SESSION_MODEL.md) — sessions, checkpoints, handoffs
- [OPENBB_PUBLIC_DEMO_PLAN.md](OPENBB_PUBLIC_DEMO_PLAN.md) — planned public-data quick demo

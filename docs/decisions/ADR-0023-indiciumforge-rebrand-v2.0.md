# ADR-0023: IndiciumForge rebrand (v2.0.0)

## Status

Accepted (2026-07-10)

## Context

PyPI package name `lucerna` is occupied by an unrelated AI agent orchestration project. The Lucerna open-core repository was public on GitHub but had not published to PyPI, arXiv, MCP, or agent skills. Continuing under `lucerna` would cause install and search confusion.

## Decision

1. **Brand:** Lucerna → **IndiciumForge**
2. **Version:** First post-rebrand release is **v2.0.0** (breaking)
3. **Historical tag:** `v1.0.0` remains the Lucerna sign-off tag (do not move)
4. **Namespace map:**

| Layer | v1 (Lucerna) | v2 (IndiciumForge) |
| --- | --- | --- |
| PyPI workspace | `lucerna-workspace` | `indiciumforge-workspace` |
| PyPI packages | `lucerna-core`, `-workflow`, `-cli` | `indiciumforge-core`, `-workflow`, `-cli` |
| Imports | `lucerna_core`, `lucerna_workflow`, `lucerna_cli` | `indiciumforge_core`, `indiciumforge_workflow`, `indiciumforge_cli` |
| CLI | `lucerna` | `indiciumforge` |
| Entry points | `lucerna.data_providers`, `lucerna.factor_detectors`, `lucerna.recipe_extensions` | `indiciumforge.*` |
| Artifact schemas | `lucerna.*` | `indiciumforge.*` |
| Constitution | `LUCERNA_CONSTITUTION.md` | `INDICIUMFORGE_CONSTITUTION.md` |
| Private workspace | `lucerna-private` | `indiciumforge-private` |

5. **Compat shim (one release):** Config and manifest parsers accept `lucerna.*` schema IDs, normalize to `indiciumforge.*`, emit deprecation warning. Removed v2.1.0.

6. **Frozen reference unchanged:** `indiciumgrid.*` schemas in golden market-gate artifacts are not renamed.

7. **Contest/trading repos:** Not renamed; no IndiciumForge branding in frozen `indiciumgrid` tracked files.

## Consequences

- Private extension packs must update pack YAML `schema:` lines and entry point groups.
- Operator `parity_local.yaml` must use `indiciumforge.parity_local_config.v1` (or deprecated `lucerna.*` during v2.0.0).
- GitHub repository renamed `Lucerna` → `indiciumforge` (redirect preserved).
- Safe rollback SHA: Lucerna `v1.0.0` @ `1ca42fd`, CI fix `45cd163`.

## Alternatives considered

- **ArtifexGrid**, **Sigline** — viable backups; weaker IndiciumGrid lineage signal.
- **Keep `lucerna` PyPI with prefixed packages** — rejected; `pip install lucerna` still wrong product.

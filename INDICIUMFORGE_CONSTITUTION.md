# IndiciumForge Constitution

## Core Invariants

- Migration preserves behavior, not implementation.
- Structured evidence is computed and persisted; interpretation and decisions are downstream.
- Ports define authority. Adapters only implement ports. Workflows consume ports, never vendors.
- The frozen IndiciumGrid reference is read-only after `indiciumgrid-golden-v1`.
- KOL, news, catalyst, and Agent outputs may form hypotheses or review enrichment; they must not feed strict execution gates.
- IndiciumForge does not self-develop broker order placement.
- IndiciumForge does not self-develop a complete portfolio backtest engine; external engines may consume preserved signals through governed adapters.
- Differences from IndiciumGrid golden behavior must be recorded as `match`, `intentional_change`, or `unsupported_gap`.

## Text encoding

- Repository text encoding is **UTF-8**.
- Source identifiers, schema IDs, CLI option names, config keys, artifact filenames, command examples, and other machine-parsed operational surfaces should use **ASCII-stable** syntax.
- Human-facing documentation may use Unicode, including Chinese text.
- Domain labels and artifact payloads may use UTF-8 when the domain requires it.
- Avoid decorative Unicode punctuation or symbols in CLI output, logs, config keys, schema IDs, and file paths unless there is a concrete domain reason.
- This is not an ASCII-only project.

## License

License: **Apache License 2.0** (Apache-2.0). See [LICENSE](LICENSE) and [ADR-0007](docs/decisions/ADR-0007-license-strategy.md).

# Lucerna Constitution

## Core Invariants

- Migration preserves behavior, not implementation.
- Structured evidence is computed and persisted; interpretation and decisions are downstream.
- Ports define authority. Adapters only implement ports. Workflows consume ports, never vendors.
- The frozen IndiciumGrid reference is read-only after `indiciumgrid-golden-v1`.
- KOL, news, catalyst, and Agent outputs may form hypotheses or review enrichment; they must not feed strict execution gates.
- Lucerna does not self-develop broker order placement.
- Lucerna does not self-develop a complete portfolio backtest engine; external engines may consume preserved signals through governed adapters.
- Differences from IndiciumGrid golden behavior must be recorded as `match`, `intentional_change`, or `unsupported_gap`.

## License

License: **Apache License 2.0** (Apache-2.0). See [LICENSE](LICENSE) and [ADR-0007](docs/decisions/ADR-0007-license-strategy.md).

# ADR-0007: License Strategy

Status: accepted

## Context

- IndiciumForge began as a private scaffold extracted from the frozen IndiciumGrid reference.
- Public open-source alpha requires an explicit, SPDX-identifiable license.
- ADR-0011 separates open-core from private-extension packs; the open-source repository
  needs a permissive license compatible with ports, schemas, and demo implementations.

## Decision

IndiciumForge open-source repository is licensed under **Apache License 2.0** (Apache-2.0).

- Root `LICENSE` file carries the standard Apache-2.0 text.
- `INDICIUMFORGE_CONSTITUTION.md` records Apache-2.0 as the project license.
- Private extension packs may use separate licenses; they are not part of this repository.

## Rationale

- Permissive license suitable for research tooling, ports, and reference implementations.
- Clear patent grant and contribution norms for future public collaboration.
- Widely recognized by GitHub, SPDX, and package ecosystems.

## Consequences

- First public alpha may ship without a separate license ADR blocker.
- Contributors should assume Apache-2.0 applies to files in this repository unless marked otherwise.
- IndiciumGrid remains a frozen external reference; its license is not modified by this ADR.

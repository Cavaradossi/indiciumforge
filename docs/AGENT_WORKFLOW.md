# Agent Workflow

## Cursor implementer flow

1. Read `LUCERNA_CONSTITUTION.md`, relevant ADR, and `CAPABILITY_REGISTER.md`.
2. Implement only the requested capability slice.
3. Update `MIGRATION_MAP_FROM_INDICIUMGRID.md` checkboxes when a mapping is complete.
4. Run `ruff check .` and `pytest -q`.
5. For market-gate changes, run `pytest tests/golden -k market_gate`.

## Codex reviewer flow

1. Verify behavior against golden expected artifacts, not IndiciumGrid module shape.
2. Check ADR and capability status consistency.
3. Reject scope creep into `not_in_v0.1` capabilities.
4. Record accepted differences in `GOLDEN_MANIFEST.yaml`.

## Golden export flow

```powershell
# Requires a local frozen reference checkout (indiciumgrid-golden-v1) — not part of Lucerna OSS.
pip install -e <path-to-frozen-reference-checkout>
python scripts/export_golden_market_gate.py
```

Golden fixtures are the reference for semantic parity. Lucerna must not depend on IndiciumGrid at runtime.

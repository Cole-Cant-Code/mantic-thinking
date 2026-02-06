# Release Notes — 2026-02-06 (v1.1.3)

## Summary

This release tightens input validation across all tools, rejects non-finite
override values, and allows contrarian flow to qualify in the finance confluence
engine. The immutable core kernel remains unchanged.

## Highlights

- **Strict input validation**
  - All tool entrypoints now require finite inputs (no None/NaN/inf).
- **Override safety**
  - NaN/inf threshold and temporal overrides are rejected and fall back to defaults.
- **Finance confluence refinement**
  - Contrarian flow can qualify for a window when other layers are favorable.

## Compatibility

- Core formula (`core/mantic_kernel.py`) unchanged.

## Tests

- `python3 -m pytest -q` → 99 passed

## Files Changed (High-Level)

- `core/validators.py` — finite input/override validation
- `tools/**` — enforce finite required inputs; finance confluence gate update
- `tests/test_cross_model.py` — missing input, contrarian flow, NaN override tests

## Notes

- No changes to domain weights or kernel implementation.

# Release Notes — 2026-02-06 (v1.1.4)

## Summary

This release removes import-time `sys.path` mutation from adapters and limits
path adjustments to direct script execution. The immutable core kernel remains
unchanged.

## Highlights

- **Adapter import hygiene**
  - Adapters no longer mutate `sys.path` on import; path adjustments only occur
    for direct script execution.

## Compatibility

- Core formula (`core/mantic_kernel.py`) unchanged.

## Tests

- `python3 -m pytest -q` → 99 passed

## Files Changed (High-Level)

- `adapters/*.py` — guard `sys.path` modification behind `__main__`
- `README.md` — version line updated
- `pyproject.toml` — version bump

## Notes

- No functional changes to tool behavior or kernel math.

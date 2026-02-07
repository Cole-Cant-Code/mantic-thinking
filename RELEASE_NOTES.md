# Release Notes — 2026-02-06 (v1.1.5)

## Summary

This release adds `.pytest_cache/` to `.gitignore` to keep working trees clean
after running tests. The immutable core kernel remains unchanged.

## Highlights

- **Git hygiene**
  - Ignore pytest cache artifacts by default.

## Compatibility

- Core formula (`core/mantic_kernel.py`) unchanged.

## Tests

- Not required for this change.

## Files Changed (High-Level)

- `.gitignore` — ignore `.pytest_cache/`
- `README.md` — version line updated
- `pyproject.toml` — version bump

## Notes

- No functional code changes in this release.

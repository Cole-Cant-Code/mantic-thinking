# Release Notes — 2026-02-06 (v1.1.6)

## Summary

This release applies a safe kernel wrapper (keeping the core kernel file
unchanged), fixes override edge cases, improves adapter/tool robustness, and
makes emergence outputs consistent. No changes to the immutable core formula.

## Highlights

- **Safe kernel wrapper**
  - New `core/safe_kernel.py` enforces `k_n > 0` without modifying
    `core/mantic_kernel.py`.
  - Tools now call the safe wrapper.
- **Override correctness**
  - Clamp bounds fixed when defaults are near 0; unknown domain now fails closed
    for temporal allowlists.
- **Tool output consistency**
  - Emergence tools always include `layer_attribution` (even on no-window).
  - Climate maladaptation uses override thresholds (no hardcoded comparisons).
- **Adapter robustness**
  - Claude/Gemini adapters filter extra kwargs before calling tools.
- **Import hygiene**
  - Tool modules only adjust `sys.path` when run as scripts.

## Compatibility

- Core formula (`core/mantic_kernel.py`) unchanged.

## Tests

- `python3 -m pytest tests/test_cross_model.py tests/test_schema_alignment.py -q`

## Files Changed (High-Level)

- `core/safe_kernel.py` — safe wrapper with k_n guard
- `core/validators.py` — clamp edge-case + unknown domain allowlist handling
- `tools/**` — safe kernel import + output consistency + import hygiene
- `adapters/claude_adapter.py`, `adapters/gemini_adapter.py` — kwargs filtering
- `README.md`, `pyproject.toml` — version bump

## Notes

- No changes to domain weights or kernel implementation.

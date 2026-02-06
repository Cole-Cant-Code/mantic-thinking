# Release Notes — 2026-02-06

## Summary

This release adds a bounded override system for thresholds and temporal kernels,
and introduces an internal, domain-agnostic planning tool with a supporting
reasoning scaffold. The immutable core kernel remains unchanged.

## Highlights

- **Bounded overrides across all 14 tools**
  - Threshold overrides are clamped to ±20% of defaults with hard bounds.
  - Temporal configs are validated by domain allowlists and require both
    `kernel_type` and `t` to apply.
  - `f_time` is clamped to prevent runaway scores.
  - All overrides are audited in `overrides_applied`.

- **Planning domain support (internal)**
  - Added `configs/mantic_plan.md` planning scaffold.
  - Added `tools/emergence/plan_alignment_window.py` (internal-only, not in
    adapters or public tool exports).
  - Added tests for the plan tool in `tests/test_cross_model.py`.

- **Domain kernel allowlist updated**
  - Added `planning` to `DOMAIN_KERNEL_ALLOWLIST`.

- **Public schemas/adapters updated**
  - `temporal_config` and `threshold_override` are now exposed as optional
    parameters in OpenAI/Claude/Kimi/Gemini schemas.

## Compatibility

- Core formula (`core/mantic_kernel.py`) unchanged.
- All existing outputs preserved; additional fields include:
  - `overrides_applied` (all tools)
  - `thresholds` (all tools)
- `threshold` remains present where previously returned (e.g., cyber tool).

## Tests

- `python3 -m pytest -q` → 83 passed

## Files Changed (High-Level)

- `core/validators.py` — bounded override system + planning allowlist
- `tools/friction/*` — override support + audit blocks
- `tools/emergence/*` — override support + audit blocks + new plan tool
- `configs/mantic_plan.md` — new planning scaffold
- `tests/test_cross_model.py` — internal plan tool tests
- `configs/README.md` — added planning scaffold entry

## Notes

- The planning tool is internal-only and not exposed via adapters or schemas.
- Adapters and schemas now include optional override parameters.

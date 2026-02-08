# Release Notes — 2026-02-08 (v1.2.4)

## Summary

Documentation and schema alignment for `layer_coupling` (v1.2.3) and
`layer_visibility` (v1.2.0). No functional code changes.

## Highlights

- **SKILL.md**: Added `layer_coupling` section with reasoning guidance.
- **schemas/openapi.json**: Added `layer_visibility` and `layer_coupling` to
  all 14 response schemas; set `additionalProperties: true`.
- **schemas/kimi-tools.json**: Added `response_includes` under `_mantic_meta`
  for all 14 tools.
- **README.md**: Fixed misleading threshold pseudocode, added `layer_coupling`
  to "How It Works" overview, restored Contributing link.

## Compatibility

- No runtime changes. Documentation only.
- Core formula unchanged.

## Tests

- `python3 -m pytest -q`

---

# Release Notes — 2026-02-08 (v1.2.3)

## Summary

This release adds `layer_coupling` to all 14 tools, providing a read-only view
of inter-layer agreement (coherence, per-layer agreement, and tension pairs).
No changes to the public tool set or immutable core formula.

## Highlights

- Added `compute_layer_coupling()` helper in `core/validators.py`.
- All tools now include `layer_coupling` alongside `layer_visibility`.

## Compatibility

- Public adapters still expose **14 tools** (7 friction + 7 emergence).
- Core formula unchanged.
- Additive output only (new `layer_coupling` field).

## Tests

- `python3 -m pytest -q`

---

# Release Notes — 2026-02-08 (v1.2.2)

## Summary

This release removes non-public internal tools and self-analysis artifacts that
were never part of the documented 14-tool surface area. No changes to the
public tool set or immutable core formula.

## Highlights

- Removed internal/unwired modules:
  - `tools/friction/codebase_layer_conflict.py`
  - `tools/emergence/codebase_alignment_window.py`
  - `tools/emergence/plan_alignment_window.py`
- Removed internal self-analysis docs/scripts:
  - `configs/mantic_codebase.md`
  - `configs/mantic_self_analysis_results.md`

## Compatibility

- Public adapters still expose **14 tools** (7 friction + 7 emergence).
- Core formula unchanged.

## Tests

- `python3 -m pytest -q`

---

# Release Notes — 2026-02-08 (v1.2.1)

## Summary

This release improves README clarity around purpose, value, and novelty. No
functional code changes.

## Highlights

- **README purpose/value framing**
  - Added a concise "Why Mantic" section.

## Compatibility

- Core formula unchanged.

## Tests

- Not required for this change.

---

# Release Notes — 2026-02-07 (v1.2.0)

## Summary

This release adds layer visibility to all tools, enabling LLMs and humans to
understand which hierarchical layer (Micro/Meso/Macro/Meta) drives detection.
Dominance is input-driven using W*L*I contributions. All changes are
backward-compatible and additive.

## Highlights

- **Layer Visibility (All 14 Tools)**
  - New `layer_visibility` field in all tool responses
  - Dominant layer computed from actual contributions (W*L*I)
  - Includes weights by layer, optional contributions, and rationale
  - Interpretive aid for reasoning; does not affect M-score calculation

- **Introspection Module**
  - New `mantic/introspection/` module with layer hierarchy mappings
  - `get_layer_visibility()` function for programmatic access
  - `LAYER_DEFINITIONS` for canonical layer descriptions
  - `mantic/__init__.py` added for reliable packaging

- **Adapter Helpers**
  - New `explain_result()` function in all adapters (Kimi/Claude/OpenAI/Gemini)
  - Returns reasoning hints based on dominant layer
  - Helps LLMs provide context-appropriate guidance

## Compatibility

- **100% Backward Compatible**: All changes are additive
- Core formula (`core/mantic_kernel.py`) unchanged
- All existing fields preserved
- No breaking changes

## Usage Example

```python
result = detect(phenotypic=0.3, genomic=0.9, ...)
print(result["layer_visibility"]["dominant"])  # "Micro"
print(result["layer_visibility"]["rationale"])  # Why Micro dominates

from adapters.kimi_adapter import explain_result
explanation = explain_result("healthcare_phenotype_genotype", result)
print(explanation["reasoning_hints"])
# ["Trust immediate signals but check for noise/outliers", ...]
```

---

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

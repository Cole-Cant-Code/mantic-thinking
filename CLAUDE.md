# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mantic Thinking is a cross-domain anomaly and opportunity detection framework using deterministic hierarchical analysis. One detection tool -- the LLM defines layer names, weights, and values. The kernel handles the math. 16 built-in domain configurations serve as reference presets.

**Core formula (immutable):** `M = (sum(W * L * I)) * f(t) / k_n`

**LLM controls:** layer names, weights, values, interactions, temporal kernel, mode.

**Immutable:** formula, 7 temporal kernels, Micro/Meso/Macro/Meta hierarchy, governance bounds.

## Commands

```bash
# Run all tests (654 tests, ~1s)
python3 -m pytest -q

# Run a single test file
python3 -m pytest tests/test_kernel_properties.py

# Run a single test by name
python3 -m pytest -k "test_kernel_determinism"

# Run with coverage
python3 -m pytest --cov=mantic_thinking

# Build wheel
python3 -m build

# Run MCP server
python -m mantic_thinking
```

No linter is configured. No Makefile exists. Tests are the primary validation mechanism.

## Architecture

### Immutable Kernel (`core/`)

The mathematical core is **never modified** -- this is a fundamental design constraint.

- `mantic_kernel.py` -- The core formula + 7 temporal kernel modes. `mantic_kernel()` returns `(M, S, attribution)`. `compute_temporal_kernel()` pre-computes `f_time`.
- `safe_kernel.py` -- Wraps the kernel with input validation, NaN handling, and weight renormalization before calling the raw kernel.
- `validators.py` -- All input validation: clamping (0-1), weight normalization, threshold bounds (+/-20%), interaction coefficients (0.1-2.0), temporal config restrictions, layer coupling computation.

### Tools (`tools/`)

- `tools/generic_detect.py` -- **THE detect function.** Accepts caller-defined domains with 3-6 layers and custom weights. This is the product.
- `tools/friction/` -- 8 reference preset tools (divergence/risk detection). Each defines `WEIGHTS`, `LAYER_NAMES`, and a `detect()` function. These are reference implementations, not the primary interface.
- `tools/emergence/` -- 8 reference preset tools (convergence/opportunity detection). Same structure.
- Each preset tool has a paired `.yaml` file providing LLM calibration guidance.

### MCP Server (`server.py`)

FastMCP server exposing the single-detect architecture:
- **7 tools:** health_check, detect, detect_friction, detect_emergence, visualize_gauge, visualize_attribution, visualize_kernels
- **9 resources:** system-prompt, presets, scaffold, tech-spec, config/{domain}, guidance, guidance/{tool}, context/{domain}, domains
- **3 prompts:** warmup, analyze_domain, compare_friction_emergence

### Adapters (`adapters/`)

Expose ONE detect tool in model-specific function-calling formats. The LLM supplies layer names, weights, and values. Legacy tool names still work via backward-compatible dispatch.

- `openai_adapter.py` -- OpenAI/Ollama format. Central adapter with context loading helpers.
- `claude_adapter.py` -- Claude tool-use format.
- `kimi_adapter.py` -- Kimi native format.
- `gemini_adapter.py` -- Gemini FunctionDeclaration format.

`TOOL_MAP` is an internal registry of all 17 tool functions (16 presets + generic_detect). Used for backward-compatible dispatch and preset extraction. Not exposed to LLMs.

### Introspection (`mantic/introspection/`)

`hierarchy.py` maps tool inputs to hierarchical layers (Micro/Meso/Macro/Meta) and computes `layer_visibility` (dominant layer + rationale) for each detection result.

### Configs (`configs/`)

Markdown files: framework docs (`mantic_scaffold.md`, `mantic_tech_spec.md`, `mantic_explicit_framework.md`, `mantic_reasoning_guidelines.md`, `mantic_system_prompt.md`) + domain configs. Loaded by adapters and MCP resources as LLM system-prompt context.

### Visualization (`visualization/`)

`ascii_charts.py` -- ASCII gauge, treemap, matrix, and cascade visualizations for detection results.

## Key Constraints

- **Formula is immutable** -- M = (sum(W * L * I)) * f(t) / k_n. Never changes.
- **LLM defines layers and weights** -- not hardcoded per domain.
- **Thresholds shift +/-20% max** -- enforced by `clamp_threshold_override()`.
- **Interaction coefficients bounded [0.1, 2.0]** -- enforced by `resolve_interaction_coefficients()`.
- **f_time bounded [0.1, 3.0]** -- enforced by `clamp_f_time()`.
- **NaN graceful degradation** -- requires >=2 valid layers; weights renormalize around missing data.
- **Deterministic** -- same inputs always produce identical outputs. No randomness.

## Tool Output Schema

Every `detect()` returns: `m_score`, `spatial_component`, `layer_attribution`, `layer_visibility`, `layer_coupling`, `overrides_applied`, `calibration`, `thresholds`, plus mode-specific fields (`alert`/`severity` for friction, `window_detected`/`window_type`/`confidence` for emergence).

## Dependencies

Runtime: `numpy>=1.20.0`, `pyyaml>=6.0`. MCP: `fastmcp>=2.0.0` (optional). No external APIs or network calls.

## License

Elastic License 2.0. Contributions require DCO sign-off (`git commit -s`). Individual contributors only.

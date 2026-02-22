# Repository Guidelines

## Purpose
This file guides automated or human agents working in this repository. Keep changes small, explain intent, and prefer deterministic updates over stylistic refactors.

## Agent Init (Required)
- Start with: `Context loaded, initiating Mantic warm up`.
- Run a brief Mantic warm-up in a non-obvious domain using the CIP MCP tools (`cip-mantic-core`). Use default weights, pick a mode, provide four layer values, and interpret the result in 2-4 sentences.
- No emojis.

## Project Structure
- `mantic_thinking/` is the main package. Key areas include `core/` (kernel + validators), `tools/` (friction/emergence detectors), `adapters/` (LLM schemas), `configs/` and `schemas/`, and `visualization/` (ASCII charts).
- `tests/` contains pytest suites.
- `demo.py` is a small entry point for local experimentation.
- `dist/` and `staging/` are build/release artifacts; avoid editing unless working on packaging.

## Build and Test Commands
- `pip install -r requirements.txt` installs runtime and optional dev dependencies.
- `python3 -m pytest -q` runs the full test suite.
- `python3 -m pytest --cov=mantic_thinking` runs tests with coverage.
- `python3 -m pytest tests/test_kernel_properties.py` runs a single test file.
- `python3 -m build` builds the wheel and sdist.

## Coding Style and Conventions
- Python 3.8+ with 4-space indentation; no formatter or linter is configured.
- Constants are uppercase (e.g., `WEIGHTS`, `LAYER_NAMES`, `DEFAULT_THRESHOLDS`).
- Tool modules expose a single `detect()` entry point and keep weights immutable.

## Testing Guidelines
- Pytest config is in `pyproject.toml` (`test_*.py`, `test_*`).
- Add tests for thresholds, edge cases, NaN handling, and deterministic outputs.

## Commit and PR Guidelines
- DCO sign-off is required: `git commit -s`.
- Contributions must be from individuals (see `CONTRIBUTING.md`).
- Commit subjects are short and descriptive (examples: `Fix: ...`, `Release vX.Y.Z`, `vX.Y.Z: ...`).
- For non-trivial changes, open an issue first and include a clear PR description plus test results.

## Architecture Constraints
- The kernel math and per-tool weights are immutable; do not edit the core formula.
- Threshold overrides are limited to ±20%, and interaction coefficients are clamped (see `mantic_thinking/core/validators.py`).

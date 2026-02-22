"""FastMCP server for the Mantic Thinking detection engine.

One detection tool. The LLM defines layer names, weights, and values.
The kernel provides the math, governance, and audit trail.

Surface:
    Tools (7):
        health_check            — Server status
        detect                  — Run detection (LLM supplies layers, weights, values)
        detect_friction         — Shortcut: friction mode
        detect_emergence        — Shortcut: emergence mode
        visualize_gauge         — ASCII M-score gauge
        visualize_attribution   — ASCII layer contribution treemap
        visualize_kernels       — ASCII temporal kernel comparison

    Resources (9):
        mantic://system-prompt      — Full system prompt
        mantic://presets            — Reference presets (layer names + weights from 16 built-in tools)
        mantic://scaffold           — Reasoning scaffold
        mantic://tech-spec          — Technical specification
        mantic://config/{domain}    — Domain-specific config
        mantic://guidance           — All tool calibration guidance
        mantic://guidance/{tool}    — Per-tool calibration guidance
        mantic://context/{domain}   — Full LLM context
        mantic://domains            — Domain registry with kernel allowlists

    Prompts (3):
        warmup                      — Onboarding warmup protocol
        analyze_domain              — Structured detection workflow
        compare_friction_emergence  — Side-by-side mode comparison
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from mantic_thinking.adapters.openai_adapter import (
    TOOL_MAP,
    _DOMAIN_TOOLS,
    _DOMAIN_ALIASES,
    get_domain_config,
    get_full_context,
    get_scaffold,
    get_tool_guidance,
)
from mantic_thinking.core.validators import DOMAIN_KERNEL_ALLOWLIST
from mantic_thinking.visualization.ascii_charts import (
    draw_attribution_treemap,
    draw_kernel_comparison,
    draw_m_gauge,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Build preset registry from the 16 built-in tools at import time
# ---------------------------------------------------------------------------
_PRESETS: dict[str, dict[str, Any]] = {}

import importlib as _importlib

for _tool_name, _func in TOOL_MAP.items():
    if _tool_name == "generic_detect":
        continue
    # Every built-in tool module has WEIGHTS and LAYER_NAMES at module level
    _module = _importlib.import_module(_func.__module__)
    _raw_weights = getattr(_module, "WEIGHTS", {})
    _layer_names = list(getattr(_module, "LAYER_NAMES", []))
    _default_thresholds = getattr(_module, "DEFAULT_THRESHOLDS", {})

    # Friction tools store WEIGHTS as dict, emergence tools as list — normalize
    if isinstance(_raw_weights, dict):
        _weights_dict = dict(_raw_weights)
    else:
        _weights_dict = dict(zip(_layer_names, _raw_weights))

    _PRESETS[_tool_name] = {
        "layer_names": _layer_names,
        "weights": _weights_dict,
        "default_thresholds": dict(_default_thresholds) if isinstance(_default_thresholds, dict) else {},
    }


def _error(message: str, *, code: str = "validation_error") -> dict[str, Any]:
    return {"status": "error", "error": {"code": code, "message": message}}


# ---------------------------------------------------------------------------
# FastMCP server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "Mantic Thinking",
    instructions=(
        "Deterministic cross-domain detection engine. "
        "Immutable kernel: M = (sum(W * L * I)) * f(t) / k_n. "
        "You define the layers, weights, and values. The kernel handles the math. "
        "Read mantic://presets for reference examples. "
        "Read mantic://system-prompt for full onboarding."
    ),
)


# ---------------------------------------------------------------------------
# Detection tools
# ---------------------------------------------------------------------------

_generic = TOOL_MAP["generic_detect"]


def _run_detect(
    *,
    layer_names: list[str],
    weights: list[float],
    layer_values: list[float],
    mode: str,
    f_time: float = 1.0,
    detection_threshold: float = 0.4,
    layer_hierarchy: dict[str, str] | None = None,
    threshold_override: dict[str, float] | None = None,
    temporal_config: dict[str, Any] | None = None,
    interaction_mode: str = "dynamic",
    interaction_override: dict[str, float] | list[float] | None = None,
    interaction_override_mode: str = "scale",
) -> dict[str, Any]:
    """Dispatch to generic_detect with caller-supplied layers and weights."""
    kwargs: dict[str, Any] = {
        "domain_name": "mcp_detect",
        "layer_names": layer_names,
        "weights": weights,
        "layer_values": layer_values,
        "mode": mode,
        "f_time": f_time,
        "detection_threshold": detection_threshold,
        "interaction_mode": interaction_mode,
        "interaction_override_mode": interaction_override_mode,
    }
    if layer_hierarchy is not None:
        kwargs["layer_hierarchy"] = layer_hierarchy
    if threshold_override is not None:
        kwargs["threshold_override"] = threshold_override
    if temporal_config is not None:
        kwargs["temporal_config"] = temporal_config
    if interaction_override is not None:
        kwargs["interaction_override"] = interaction_override

    try:
        return _generic(**kwargs)
    except Exception as exc:
        logger.exception("detect failed")
        return _error(str(exc), code="runtime_error")


@mcp.tool
def health_check() -> dict[str, Any]:
    """Check server status."""
    return {
        "status": "ok",
        "server": "Mantic Thinking",
        "version": "2.1.0",
        "presets": len(_PRESETS),
    }


@mcp.tool
def detect(
    layer_names: list[str],
    weights: list[float],
    layer_values: list[float],
    mode: str = "friction",
    f_time: float = 1.0,
    detection_threshold: float = 0.4,
    layer_hierarchy: dict[str, str] | None = None,
    threshold_override: dict[str, float] | None = None,
    temporal_config: dict[str, Any] | None = None,
    interaction_mode: str = "dynamic",
    interaction_override: dict[str, float] | list[float] | None = None,
    interaction_override_mode: str = "scale",
) -> dict[str, Any]:
    """Run detection with your own layers and weights.

    You define what the layers mean and how much each one matters.
    The kernel handles the math: M = (sum(W * L * I)) * f(t) / k_n.
    Read mantic://presets for reference starting points.

    Args:
        layer_names: 3-6 layer name strings you define.
        weights: Layer weights summing to 1.0 (one per layer). You decide importance.
        layer_values: Layer input values (0-1, one per layer). Your situational assessment.
        mode: "friction" (divergence/risk) or "emergence" (alignment/opportunity).
        f_time: Temporal multiplier (0.1-3.0). Default 1.0.
        detection_threshold: Threshold for detection (default 0.4).
        layer_hierarchy: Optional mapping of layer names to Micro/Meso/Macro/Meta.
        threshold_override: Optional threshold overrides (bounded +/-20%).
        temporal_config: Optional temporal kernel config (kernel_type + t required).
        interaction_mode: "dynamic" or "base".
        interaction_override: Per-layer interaction coefficient overrides (0.1-2.0).
        interaction_override_mode: "scale" (multiply) or "replace".
    """
    if mode not in ("friction", "emergence"):
        return _error("mode must be 'friction' or 'emergence'")
    return _run_detect(
        layer_names=layer_names,
        weights=weights,
        layer_values=layer_values,
        mode=mode,
        f_time=f_time,
        detection_threshold=detection_threshold,
        layer_hierarchy=layer_hierarchy,
        threshold_override=threshold_override,
        temporal_config=temporal_config,
        interaction_mode=interaction_mode,
        interaction_override=interaction_override,
        interaction_override_mode=interaction_override_mode,
    )


@mcp.tool
def detect_friction(
    layer_names: list[str],
    weights: list[float],
    layer_values: list[float],
    f_time: float = 1.0,
    detection_threshold: float = 0.4,
    layer_hierarchy: dict[str, str] | None = None,
    threshold_override: dict[str, float] | None = None,
    temporal_config: dict[str, Any] | None = None,
    interaction_mode: str = "dynamic",
    interaction_override: dict[str, float] | list[float] | None = None,
    interaction_override_mode: str = "scale",
) -> dict[str, Any]:
    """Run friction (divergence/risk) detection. Shortcut for detect with mode='friction'.

    Args:
        layer_names: 3-6 layer name strings you define.
        weights: Layer weights summing to 1.0.
        layer_values: Layer input values (0-1).
        f_time: Temporal multiplier (0.1-3.0). Default 1.0.
        detection_threshold: Threshold for detection (default 0.4).
        layer_hierarchy: Optional mapping of layer names to Micro/Meso/Macro/Meta.
        threshold_override: Optional threshold overrides (bounded +/-20%).
        temporal_config: Optional temporal kernel config.
        interaction_mode: "dynamic" or "base".
        interaction_override: Per-layer interaction coefficient overrides (0.1-2.0).
        interaction_override_mode: "scale" or "replace".
    """
    return _run_detect(
        layer_names=layer_names,
        weights=weights,
        layer_values=layer_values,
        mode="friction",
        f_time=f_time,
        detection_threshold=detection_threshold,
        layer_hierarchy=layer_hierarchy,
        threshold_override=threshold_override,
        temporal_config=temporal_config,
        interaction_mode=interaction_mode,
        interaction_override=interaction_override,
        interaction_override_mode=interaction_override_mode,
    )


@mcp.tool
def detect_emergence(
    layer_names: list[str],
    weights: list[float],
    layer_values: list[float],
    f_time: float = 1.0,
    detection_threshold: float = 0.4,
    layer_hierarchy: dict[str, str] | None = None,
    threshold_override: dict[str, float] | None = None,
    temporal_config: dict[str, Any] | None = None,
    interaction_mode: str = "dynamic",
    interaction_override: dict[str, float] | list[float] | None = None,
    interaction_override_mode: str = "scale",
) -> dict[str, Any]:
    """Run emergence (alignment/opportunity) detection. Shortcut for detect with mode='emergence'.

    Args:
        layer_names: 3-6 layer name strings you define.
        weights: Layer weights summing to 1.0.
        layer_values: Layer input values (0-1).
        f_time: Temporal multiplier (0.1-3.0). Default 1.0.
        detection_threshold: Threshold for detection (default 0.4).
        layer_hierarchy: Optional mapping of layer names to Micro/Meso/Macro/Meta.
        threshold_override: Optional threshold overrides (bounded +/-20%).
        temporal_config: Optional temporal kernel config.
        interaction_mode: "dynamic" or "base".
        interaction_override: Per-layer interaction coefficient overrides (0.1-2.0).
        interaction_override_mode: "scale" or "replace".
    """
    return _run_detect(
        layer_names=layer_names,
        weights=weights,
        layer_values=layer_values,
        mode="emergence",
        f_time=f_time,
        detection_threshold=detection_threshold,
        layer_hierarchy=layer_hierarchy,
        threshold_override=threshold_override,
        temporal_config=temporal_config,
        interaction_mode=interaction_mode,
        interaction_override=interaction_override,
        interaction_override_mode=interaction_override_mode,
    )


# ---------------------------------------------------------------------------
# Visualization tools
# ---------------------------------------------------------------------------


@mcp.tool
def visualize_gauge(
    m_score: float,
    spatial_component: float,
    width: int = 50,
) -> str:
    """Render an ASCII M-score gauge from detection results.

    Args:
        m_score: The M-score from a detection result.
        spatial_component: The spatial component (S) from a detection result.
        width: Gauge width in characters (default 50).
    """
    return draw_m_gauge(m_score, spatial_component, width)


@mcp.tool
def visualize_attribution(
    layer_attribution: dict[str, float],
    width: int = 60,
) -> str:
    """Render an ASCII treemap of layer contributions from detection results.

    Args:
        layer_attribution: The layer_attribution dict from a detection result.
        width: Chart width in characters (default 60).
    """
    labels = list(layer_attribution.keys())
    values = list(layer_attribution.values())
    return draw_attribution_treemap(values, labels, width)


@mcp.tool
def visualize_kernels(
    t: float,
    n: float = 1.0,
    alpha: float = 0.1,
    width: int = 50,
) -> str:
    """Compare all 7 temporal kernel modes side by side.

    Args:
        t: Time value for kernel evaluation.
        n: Novelty parameter (default 1.0).
        alpha: Sensitivity parameter (default 0.1).
        width: Chart width in characters (default 50).
    """
    return draw_kernel_comparison(t, n, alpha, width)


# ---------------------------------------------------------------------------
# MCP Resources
# ---------------------------------------------------------------------------

_CONFIGS_DIR = Path(__file__).resolve().parent / "configs"


@mcp.resource("mantic://system-prompt")
def resource_system_prompt() -> str:
    """Mantic Thinking system prompt — full onboarding, formula, tools, workflow."""
    path = _CONFIGS_DIR / "mantic_system_prompt.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


@mcp.resource("mantic://presets")
def resource_presets() -> str:
    """Reference presets from 16 built-in domain tools — layer names, weights, thresholds.

    These are starting points, not requirements. Use them as-is, modify them,
    or ignore them and define your own layers and weights.
    """
    return json.dumps(_PRESETS, indent=2)


@mcp.resource("mantic://scaffold")
def resource_scaffold() -> str:
    """Universal Mantic reasoning scaffold — Stage 1 of the LLM load order."""
    return get_scaffold()


@mcp.resource("mantic://tech-spec")
def resource_tech_spec() -> str:
    """Mantic framework technical specification."""
    path = _CONFIGS_DIR / "mantic_tech_spec.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


@mcp.resource("mantic://config/{domain}")
def resource_domain_config(domain: str) -> str:
    """Domain-specific config (healthcare, finance, cyber, climate, legal, military, social, system_lock)."""
    content = get_domain_config(domain)
    if not content:
        return f"No config found for domain: {domain}"
    return content


@mcp.resource("mantic://guidance")
def resource_all_guidance() -> str:
    """YAML calibration guidance for all built-in tools."""
    return get_tool_guidance()


@mcp.resource("mantic://guidance/{tool_name}")
def resource_tool_guidance(tool_name: str) -> str:
    """YAML calibration guidance for a specific tool."""
    return get_tool_guidance([tool_name])


@mcp.resource("mantic://context/{domain}")
def resource_full_context(domain: str) -> str:
    """Complete LLM context for system prompt injection (Scaffold + Domain Config + Tool Guidance)."""
    return get_full_context(domain)


@mcp.resource("mantic://domains")
def resource_domains() -> str:
    """Available domains, their tool mappings, and temporal kernel allowlists."""
    registry = {}
    for domain, tools in _DOMAIN_TOOLS.items():
        registry[domain] = {
            "tools": tools,
            "temporal_kernels": DOMAIN_KERNEL_ALLOWLIST.get(domain, []),
        }
    registry["_aliases"] = _DOMAIN_ALIASES
    return json.dumps(registry, indent=2)


# ---------------------------------------------------------------------------
# MCP Prompts
# ---------------------------------------------------------------------------


@mcp.prompt
def warmup() -> str:
    """Mantic onboarding warmup — build hands-on intuition before real use."""
    return (
        "You have access to the Mantic detection engine. Before using it on "
        "real problems, run this warmup to build intuition:\n\n"
        "1. Define 4 layers for any domain you find interesting. Name them yourself. "
        "Assign weights that reflect your theory of what matters most.\n"
        "2. Run friction detection with one layer high (0.85) and the rest moderate (0.5).\n"
        "3. Run emergence detection with the SAME inputs. Compare M-scores — "
        "the same score means different things in each mode.\n"
        "4. Equalize all layers to 0.7. Run both modes again. Watch coupling "
        "increase and attribution spread evenly.\n"
        "5. Try a temporal kernel: run with temporal_config={\"kernel_type\": \"s_curve\", "
        "\"alpha\": 0.15, \"t\": 5.0}. Compare the score with and without.\n"
        "6. Read the layer_coupling coherence value. Push layers apart, then pull "
        "them together. That number is the most honest signal in the output.\n"
        "7. Read mantic://presets to see how the built-in domain tools define their "
        "layers and weights. Try one as a starting point, then modify it.\n\n"
        "After warmup, summarize what you learned about coupling, attribution, "
        "and temporal scaling."
    )


@mcp.prompt
def analyze_domain(domain: str, situation: str) -> str:
    """Structured detection workflow for a specific domain.

    Args:
        domain: Domain name or any label for the area you're analyzing.
        situation: Description of the situation to analyze.
    """
    return (
        f"Analyze this {domain} situation using Mantic detection:\n\n"
        f"Situation: {situation}\n\n"
        f"Workflow:\n"
        f"1. Read mantic://presets to see if a built-in preset fits. Adapt or define your own.\n"
        f"2. Define 4 layer names and weights that capture the key dimensions of this situation.\n"
        f"3. Translate the situation into layer values (0-1). Approximate boldly.\n"
        f"4. Run friction detection to identify divergence/risk.\n"
        f"5. Run emergence detection on the SAME inputs to check for opportunity windows.\n"
        f"6. Compare: Which mode produced a stronger signal? What does coupling tell you?\n"
        f"7. If the signal is ambiguous, add temporal config or interaction overrides and re-run.\n"
        f"8. Narrate the findings: which layers matter, what the dominant layer means, "
        f"and what action the coupling pattern suggests."
    )


@mcp.prompt
def compare_friction_emergence(domain: str) -> str:
    """Compare friction and emergence detection on the same situation.

    Args:
        domain: Domain or situation label.
    """
    return (
        f"Run a friction/emergence comparison for {domain}.\n\n"
        f"1. Define 4 layers and weights for this domain (or read mantic://presets for ideas).\n"
        f"2. Choose realistic layer values for a current scenario.\n"
        f"3. Run friction detection. Record M-score, coupling, dominant layer.\n"
        f"4. Run emergence detection with the SAME layer values.\n"
        f"5. Compare the results side-by-side:\n"
        f"   - Are both signals strong, or does one dominate?\n"
        f"   - Does coupling differ? (It shouldn't — coupling reflects inputs, not mode.)\n"
        f"   - What does the dominant layer tell you about risk vs. opportunity?\n"
        f"6. Summarize: Is this situation primarily a risk, an opportunity, or both?"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """Run the Mantic Thinking MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

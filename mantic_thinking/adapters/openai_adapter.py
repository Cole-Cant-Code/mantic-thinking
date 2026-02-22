"""
OpenAI/Codex Adapter for Mantic Tools

Exposes ONE detection tool where the LLM supplies layer names, weights,
and values. The 16 built-in domain tools are available as presets (data),
not locked functions.

Compatible with GPT-4, GPT-4o, Codex, and any OpenAI-compatible endpoint.
"""

import sys
import os
from pathlib import Path
import inspect

import yaml

# Avoid mutating sys.path on import; only adjust for direct script execution.
if __name__ == "__main__":
    # adapters/ -> mantic_thinking/ -> repo root
    _repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

_TOOLS_DIR = Path(__file__).parent.parent / "tools"
_CONFIGS_DIR = Path(__file__).parent.parent / "configs"

# Friction tools (divergence detection)
from mantic_thinking.tools import (
    healthcare_phenotype_genotype,
    finance_regime_conflict,
    cyber_attribution_resolver,
    climate_maladaptation,
    legal_precedent_drift,
    military_friction_forecast,
    social_narrative_rupture,
    system_lock_recursive_control,
)

# Emergence tools (confluence detection)
from mantic_thinking.tools import (
    healthcare_precision_therapeutic,
    finance_confluence_alpha,
    cyber_adversary_overreach,
    climate_resilience_multiplier,
    legal_precedent_seeding,
    military_strategic_initiative,
    social_catalytic_alignment,
    system_lock_dissolution_window,
)

# Generic tool (caller-defined domains) — this IS the product
from mantic_thinking.tools import generic_detect


# Internal registry — used for preset extraction and backward-compatible dispatch
TOOL_MAP = {
    # Friction tools (8)
    "healthcare_phenotype_genotype": healthcare_phenotype_genotype.detect,
    "finance_regime_conflict": finance_regime_conflict.detect,
    "cyber_attribution_resolver": cyber_attribution_resolver.detect,
    "climate_maladaptation": climate_maladaptation.detect,
    "legal_precedent_drift": legal_precedent_drift.detect,
    "military_friction_forecast": military_friction_forecast.detect,
    "social_narrative_rupture": social_narrative_rupture.detect,
    "system_lock_recursive_control": system_lock_recursive_control.detect,
    # Emergence tools (8)
    "healthcare_precision_therapeutic": healthcare_precision_therapeutic.detect,
    "finance_confluence_alpha": finance_confluence_alpha.detect,
    "cyber_adversary_overreach": cyber_adversary_overreach.detect,
    "climate_resilience_multiplier": climate_resilience_multiplier.detect,
    "legal_precedent_seeding": legal_precedent_seeding.detect,
    "military_strategic_initiative": military_strategic_initiative.detect,
    "social_catalytic_alignment": social_catalytic_alignment.detect,
    "system_lock_dissolution_window": system_lock_dissolution_window.detect,
    # Generic (caller-defined domains)
    "generic_detect": generic_detect.detect,
}


# ---- Presets ---------------------------------------------------------------

def get_presets():
    """
    Return the 16 built-in domain tools as preset data.

    These are reference starting points — the LLM can use them as-is,
    modify them, or ignore them and define its own layers and weights.

    Returns:
        dict: {preset_name: {layer_names, weights, default_thresholds}}
    """
    import importlib
    presets = {}
    for tool_name, func in TOOL_MAP.items():
        if tool_name == "generic_detect":
            continue
        module = importlib.import_module(func.__module__)
        raw_weights = getattr(module, "WEIGHTS", {})
        layer_names = list(getattr(module, "LAYER_NAMES", []))
        default_thresholds = getattr(module, "DEFAULT_THRESHOLDS", {})

        # Friction tools store WEIGHTS as dict, emergence tools as list
        if isinstance(raw_weights, dict):
            weights_dict = dict(raw_weights)
        else:
            weights_dict = dict(zip(layer_names, raw_weights))

        presets[tool_name] = {
            "layer_names": layer_names,
            "weights": weights_dict,
            "default_thresholds": dict(default_thresholds) if isinstance(default_thresholds, dict) else {},
        }
    return presets


# ---- Override schema (shared) ----------------------------------------------

OVERRIDE_PROPERTIES = {
    "threshold_override": {
        "type": "object",
        "description": "Optional per-threshold overrides (bounded +/-20% internally).",
        "additionalProperties": {"type": "number"}
    },
    "temporal_config": {
        "type": "object",
        "description": "Optional temporal kernel config (bounded internally). Requires kernel_type and t.",
        "properties": {
            "kernel_type": {"type": "string", "description": "Temporal kernel type"},
            "alpha": {"type": "number", "description": "Sensitivity (bounded)"},
            "n": {"type": "number", "description": "Novelty (bounded)"},
            "t": {"type": "number", "description": "Time delta"},
            "t0": {"type": "number", "description": "S-curve inflection point"},
            "exponent": {"type": "number", "description": "Power-law exponent"},
            "frequency": {"type": "number", "description": "Oscillation frequency"},
            "memory_strength": {"type": "number", "description": "Memory strength"}
        }
    },
    "interaction_mode": {
        "type": "string",
        "description": "Which interaction coefficients (I) to start from.",
        "enum": ["dynamic", "base"],
        "default": "dynamic"
    },
    "interaction_override": {
        "description": "Optional interaction coefficient overrides (per-layer I). Either a list of floats or a dict keyed by layer name. Values bounded to [0.1, 2.0].",
        "anyOf": [
            {"type": "array", "items": {"type": "number"}},
            {"type": "object", "additionalProperties": {"type": "number"}}
        ]
    },
    "interaction_override_mode": {
        "type": "string",
        "description": "How to apply interaction_override: scale (multiply) or replace (use as-is).",
        "enum": ["scale", "replace"],
        "default": "scale"
    }
}


# ---- Tool schema -----------------------------------------------------------

def get_openai_tools():
    """
    Return OpenAI function calling schema for Mantic detection.

    Returns a single detect tool where the LLM defines layer names,
    weights, and values. The 16 built-in domains are reference presets,
    not locked functions.

    Returns:
        list: OpenAI function definitions (1 tool)
    """
    detect_tool = {
        "type": "function",
        "function": {
            "name": "detect",
            "description": (
                "Run Mantic detection on any domain. You define the layers, weights, "
                "and values. The kernel provides the math: M = (sum(W * L * I)) * f(t) / k_n. "
                "Use mode='friction' for risk/divergence or mode='emergence' for opportunity/alignment."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "domain_name": {
                        "type": "string",
                        "description": "Label for the domain you're analyzing"
                    },
                    "layer_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 3, "maxItems": 6,
                        "description": "3-6 layer name strings you define"
                    },
                    "weights": {
                        "type": "array",
                        "items": {"type": "number", "minimum": 0, "maximum": 1},
                        "minItems": 3, "maxItems": 6,
                        "description": "Layer weights summing to 1.0. You decide importance."
                    },
                    "layer_values": {
                        "type": "array",
                        "items": {"type": "number", "minimum": 0, "maximum": 1},
                        "minItems": 3, "maxItems": 6,
                        "description": "Layer input values (0-1). Your situational assessment."
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["friction", "emergence"],
                        "description": "Detection mode: friction (divergence/risk) or emergence (alignment/opportunity)"
                    },
                    "detection_threshold": {
                        "type": "number",
                        "default": 0.4,
                        "description": "Threshold for detection (default 0.4)"
                    },
                    "layer_hierarchy": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "string",
                            "enum": ["Micro", "Meso", "Macro", "Meta"]
                        },
                        "description": "Optional mapping of layer names to hierarchy levels"
                    },
                    "f_time": {"type": "number", "default": 1.0},
                    **OVERRIDE_PROPERTIES,
                },
                "required": ["domain_name", "layer_names", "weights", "layer_values", "mode"]
            }
        }
    }

    return [detect_tool]


def execute_tool(tool_name, arguments):
    """
    Execute a Mantic tool by name with given arguments.

    For 'detect', routes to generic_detect with caller-supplied parameters.
    Legacy tool names (e.g. 'healthcare_phenotype_genotype') still work
    for backward compatibility.

    Args:
        tool_name: Name of the tool to execute
        arguments: Dict of arguments to pass to the tool

    Returns:
        dict: Tool execution result

    Raises:
        ValueError: If tool_name is not recognized
    """
    if tool_name == "detect":
        return generic_detect.detect(**arguments)

    if tool_name not in TOOL_MAP:
        raise ValueError(f"Unknown tool: {tool_name}. Use 'detect' with your own layers and weights.")

    # Legacy dispatch — filter arguments to function signature
    func = TOOL_MAP[tool_name]
    sig = inspect.signature(func)
    valid_params = set(sig.parameters.keys())
    filtered_args = {k: v for k, v in arguments.items() if k in valid_params}
    return func(**filtered_args)


def get_tool_descriptions():
    """
    Get human-readable descriptions of available tools.

    Returns:
        dict: {tool_name: description}
    """
    tools = get_openai_tools()
    return {
        t["function"]["name"]: t["function"]["description"]
        for t in tools
    }


def get_tools_by_type(tool_type="all"):
    """
    Get tools filtered by type.

    With the single-detect architecture, this always returns
    the detect tool. Kept for backward compatibility.

    Args:
        tool_type: "friction", "emergence", or "all"

    Returns:
        list: Tool definitions
    """
    return get_openai_tools()


def explain_result(tool_name, result):
    """
    Get human-friendly explanation of tool result.

    Returns reasoning guidance based on layer visibility.

    Args:
        tool_name: Name of the tool
        result: Tool result dict (must include 'layer_visibility')

    Returns:
        Dict with explanation or None if layer_visibility not available
    """
    layer_vis = result.get("layer_visibility")
    if not layer_vis:
        return None

    dominant = layer_vis.get("dominant")
    rationale = layer_vis.get("rationale")

    hints = {
        "Micro": [
            "Trust immediate signals but check for noise/outliers",
            "Individual-level factors are primary driver",
            "Short-term volatility expected"
        ],
        "Meso": [
            "Local context matters most - verify environmental factors",
            "Pattern is contextual/domain-specific",
            "Medium-term patterns dominant"
        ],
        "Macro": [
            "Systemic trend; slower to change but more persistent",
            "Check institutional/contextual constraints",
            "Structural level pattern"
        ],
        "Meta": [
            "Long-term adaptation signal",
            "Consider if baseline has shifted",
            "May indicate regime change"
        ]
    }

    return {
        "tool": tool_name,
        "m_score": result.get("m_score"),
        "dominant_layer": dominant,
        "layer_rationale": rationale,
        "reasoning_hints": hints.get(dominant, []),
    }


# ---- YAML guidance loading -------------------------------------------------

def _load_tool_yaml(tool_name):
    """Load YAML guidance for a tool. Returns dict or None."""
    for suite in ("friction", "emergence"):
        path = _TOOLS_DIR / suite / f"{tool_name}.yaml"
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except yaml.YAMLError:
                return None
    return None


def get_tool_guidance(tool_names=None):
    """
    Load YAML calibration guidance for tools, formatted for system prompt.

    Args:
        tool_names: List of tool names, or None for all tools.

    Returns:
        str: Formatted guidance text for system prompt injection.
    """
    if tool_names is None:
        tool_names = [n for n in TOOL_MAP.keys() if n != "generic_detect"]
    else:
        tool_names = [n for n in tool_names if n in TOOL_MAP]

    sections = []
    for name in tool_names:
        data = _load_tool_yaml(name)
        if not data:
            continue

        lines = [f"### {name} ({data.get('type', '?')} | {data.get('domain', '?')})"]

        sel = data.get("selection", {})
        if sel.get("use_when"):
            lines.append("**Use when:**")
            for item in sel["use_when"]:
                lines.append(f"  - {item}")
        if sel.get("not_for"):
            lines.append("**Not for:**")
            for item in sel["not_for"]:
                lines.append(f"  - {item}")

        params = data.get("parameters", {})
        if params:
            lines.append("**Parameters:**")
            for pname, pdata in params.items():
                layer = pdata.get("layer", "?")
                low = pdata.get("low", "")
                high = pdata.get("high", "")
                lines.append(f"  - `{pname}` ({layer}): {low} \u2192 {high}")

        ig = data.get("interaction_guidance", {})
        dampen = ig.get("dampen_when", {})
        amplify = ig.get("amplify_when", {})
        if dampen or amplify:
            lines.append("**Tuning:**")
            for p, reason in dampen.items():
                lines.append(f"  - Dampen `{p}`: {reason}")
            for p, reason in amplify.items():
                lines.append(f"  - Amplify `{p}`: {reason}")

        interp = data.get("interpretation", {})
        if interp:
            lines.append(f"**High M:** {interp.get('high_m', '')}")
            lines.append(f"**Low M:** {interp.get('low_m', '')}")

        sections.append("\n".join(lines))

    header = "## Tool Calibration Guidance\n"
    return header + "\n\n".join(sections)


# ---- Context loading -------------------------------------------------------

# Domain name -> tool name mapping for context loading
_DOMAIN_TOOLS = {
    "healthcare": ["healthcare_phenotype_genotype", "healthcare_precision_therapeutic"],
    "finance": ["finance_regime_conflict", "finance_confluence_alpha"],
    "cyber": ["cyber_attribution_resolver", "cyber_adversary_overreach"],
    "climate": ["climate_maladaptation", "climate_resilience_multiplier"],
    "legal": ["legal_precedent_drift", "legal_precedent_seeding"],
    "military": ["military_friction_forecast", "military_strategic_initiative"],
    "social": ["social_narrative_rupture", "social_catalytic_alignment"],
    "system_lock": ["system_lock_recursive_control", "system_lock_dissolution_window"],
}

# Aliases for domain names
_DOMAIN_ALIASES = {
    "cybersecurity": "cyber",
    "security": "cyber",
    "health": "healthcare",
    "command": "military",
}


def get_scaffold():
    """
    Load the universal reasoning scaffold.

    Returns:
        str: Scaffold content, or empty string if file not found.
    """
    path = _CONFIGS_DIR / "mantic_scaffold.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def get_domain_config(domain):
    """
    Load a domain-specific config file.

    Args:
        domain: Domain name (healthcare, finance, cyber, climate,
                legal, military, social, system_lock, plan, current).

    Returns:
        str: Domain config content, or empty string if not found.
    """
    aliases = {
        "healthcare": "health",
        "cybersecurity": "security",
        "cyber": "security",
        "military": "command",
    }
    config_name = aliases.get(domain, domain)
    path = _CONFIGS_DIR / f"mantic_{config_name}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def get_full_context(domain=None):
    """
    Load the complete LLM context in the correct order.

    Chains: Scaffold -> Domain Config (optional) -> Tool Guidance.

    Args:
        domain: Optional domain name.

    Returns:
        str: Complete context string for system prompt injection.
    """
    parts = []

    scaffold = get_scaffold()
    if scaffold:
        parts.append(scaffold)

    if domain:
        config = get_domain_config(domain)
        if config:
            parts.append(config)

    canonical = _DOMAIN_ALIASES.get(domain, domain) if domain else None
    if canonical and canonical in _DOMAIN_TOOLS:
        guidance = get_tool_guidance(_DOMAIN_TOOLS[canonical])
    else:
        guidance = get_tool_guidance()
    parts.append(guidance)

    return "\n\n---\n\n".join(parts)


if __name__ == "__main__":
    print("=== OpenAI Adapter ===\n")

    tools = get_openai_tools()
    print(f"Tools exposed to LLM: {len(tools)}")
    for t in tools:
        print(f"  - {t['function']['name']}: {t['function']['description'][:80]}...")

    presets = get_presets()
    print(f"\nPresets available: {len(presets)}")
    for name in presets:
        print(f"  - {name}")

    print("\n--- Testing detect ---")
    result = execute_tool("detect", {
        "domain_name": "test_healthcare",
        "layer_names": ["phenotypic", "genomic", "environmental", "psychosocial"],
        "weights": [0.35, 0.30, 0.20, 0.15],
        "layer_values": [0.3, 0.9, 0.4, 0.8],
        "mode": "friction"
    })
    print(f"Alert: {result.get('alert')}")
    print(f"M-Score: {result['m_score']:.3f}")

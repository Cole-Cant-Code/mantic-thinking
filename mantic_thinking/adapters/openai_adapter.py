"""
OpenAI/Codex Adapter for Mantic Tools

Converts Mantic tools to OpenAI function calling format.
Compatible with GPT-4, GPT-4o, and Codex.

Includes Friction tools (7), Emergence tools (7), and Generic (1) = 15 total.
"""

import sys
import os
from pathlib import Path

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
)

# Generic tool (caller-defined domains)
from mantic_thinking.tools import generic_detect

# Optional override inputs (bounded internally by tools)
OVERRIDE_PROPERTIES = {
    "threshold_override": {
        "type": "object",
        "description": "Optional per-threshold overrides (bounded internally). Keys vary by tool.",
        "additionalProperties": {"type": "number"}
    },
    "temporal_config": {
        "type": "object",
        "description": "Optional temporal kernel config (bounded internally). Requires kernel_type and t.",
        "properties": {
            "kernel_type": {"type": "string", "description": "Temporal kernel type (domain-allowed)"},
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
        "description": "Which interaction coefficients (I) to start from: tool base or tool dynamic.",
        "enum": ["dynamic", "base"],
        "default": "dynamic"
    },
    "interaction_override": {
        "description": "Optional interaction coefficient overrides (per-layer I). Either a list of 4 floats (tool layer order) or a dict keyed by layer name. Values are bounded internally to [0.1, 2.0].",
        "anyOf": [
            {"type": "array", "items": {"type": "number"}, "minItems": 4, "maxItems": 4},
            {"type": "object", "additionalProperties": {"type": "number"}}
        ]
    },
    "interaction_override_mode": {
        "type": "string",
        "description": "How to apply interaction_override: scale (elementwise multiply) or replace (use override as-is).",
        "enum": ["scale", "replace"],
        "default": "scale"
    }
}


# Map tool IDs to detection functions (15 tools total)
TOOL_MAP = {
    # Friction tools (7)
    "healthcare_phenotype_genotype": healthcare_phenotype_genotype.detect,
    "finance_regime_conflict": finance_regime_conflict.detect,
    "cyber_attribution_resolver": cyber_attribution_resolver.detect,
    "climate_maladaptation": climate_maladaptation.detect,
    "legal_precedent_drift": legal_precedent_drift.detect,
    "military_friction_forecast": military_friction_forecast.detect,
    "social_narrative_rupture": social_narrative_rupture.detect,
    # Emergence tools (7)
    "healthcare_precision_therapeutic": healthcare_precision_therapeutic.detect,
    "finance_confluence_alpha": finance_confluence_alpha.detect,
    "cyber_adversary_overreach": cyber_adversary_overreach.detect,
    "climate_resilience_multiplier": climate_resilience_multiplier.detect,
    "legal_precedent_seeding": legal_precedent_seeding.detect,
    "military_strategic_initiative": military_strategic_initiative.detect,
    "social_catalytic_alignment": social_catalytic_alignment.detect,
    # Generic (caller-defined domains)
    "generic_detect": generic_detect.detect,
}


def get_openai_tools():
    """
    Return OpenAI function calling schema for all Mantic tools.

    Returns:
        list: OpenAI function definitions (15 tools)
    """
    friction_tools = [
        {
            "type": "function",
            "function": {
                "name": "healthcare_phenotype_genotype",
                "description": "FRICTION: Detects when genomic risk doesn't match phenotypic presentation, indicating environmental buffering or psychosocial resilience.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phenotypic": {"type": "number", "description": "Current symptoms/vitals (0-1)"},
                        "genomic": {"type": "number", "description": "Genetic risk score (0-1)"},
                        "environmental": {"type": "number", "description": "Exposure load (0-1)"},
                        "psychosocial": {"type": "number", "description": "Stress/resilience (0-1)"},
                        "f_time": {"type": "number", "default": 1.0}
                    },
                    "required": ["phenotypic", "genomic", "environmental", "psychosocial"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "finance_regime_conflict",
                "description": "FRICTION: Spots when technical price action contradicts fundamentals, flow, or risk signals.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "technical": {"type": "number", "description": "Price action signals (0-1)"},
                        "macro": {"type": "number", "description": "Fundamental indicators (0-1)"},
                        "flow": {"type": "number", "description": "Capital flow direction (-1 to 1)"},
                        "risk": {"type": "number", "description": "Risk appetite metrics (0-1)"},
                        "f_time": {"type": "number", "default": 1.0}
                    },
                    "required": ["technical", "macro", "flow", "risk"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "cyber_attribution_resolver",
                "description": "FRICTION: Scores confidence when technical sophistication doesn't align with geopolitical context.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "technical": {"type": "number", "description": "Technical sophistication (0-1)"},
                        "threat_intel": {"type": "number", "description": "Threat intel confidence (0-1)"},
                        "operational_impact": {"type": "number", "description": "Operational impact severity (0-1)"},
                        "geopolitical": {"type": "number", "description": "Geopolitical context alignment (0-1)"},
                        "f_time": {"type": "number", "default": 1.0}
                    },
                    "required": ["technical", "threat_intel", "operational_impact", "geopolitical"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "climate_maladaptation",
                "description": "FRICTION: Blocks solutions that solve immediate micro problems but create macro/meta harms.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "atmospheric": {"type": "number", "description": "Atmospheric metrics (0-1)"},
                        "ecological": {"type": "number", "description": "Ecosystem health (0-1)"},
                        "infrastructure": {"type": "number", "description": "Infrastructure resilience (0-1)"},
                        "policy": {"type": "number", "description": "Policy coherence (0-1)"},
                        "f_time": {"type": "number", "default": 1.0}
                    },
                    "required": ["atmospheric", "ecological", "infrastructure", "policy"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "legal_precedent_drift",
                "description": "FRICTION: Warns when judicial philosophy shifts threaten current precedent-based strategies.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "black_letter": {"type": "number", "description": "Statutory text alignment (0-1)"},
                        "precedent": {"type": "number", "description": "Precedent consistency (0-1)"},
                        "operational": {"type": "number", "description": "Implementation feasibility (0-1)"},
                        "socio_political": {"type": "number", "description": "Social/political context (-1 to 1)"},
                        "f_time": {"type": "number", "default": 1.0}
                    },
                    "required": ["black_letter", "precedent", "operational", "socio_political"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "military_friction_forecast",
                "description": "FRICTION: Identifies where tactical plans hit logistics or political constraints.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "maneuver": {"type": "number", "description": "Tactical maneuver feasibility (0-1)"},
                        "intelligence": {"type": "number", "description": "Intelligence confidence (0-1)"},
                        "sustainment": {"type": "number", "description": "Logistics sustainability (0-1)"},
                        "political": {"type": "number", "description": "Political authorization (0-1)"},
                        "f_time": {"type": "number", "default": 1.0}
                    },
                    "required": ["maneuver", "intelligence", "sustainment", "political"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "social_narrative_rupture",
                "description": "FRICTION: Catches virality that outpaces institutional sense-making capacity.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "individual": {"type": "number", "description": "Sentiment velocity (0-1)"},
                        "network": {"type": "number", "description": "Propagation speed (0-1)"},
                        "institutional": {"type": "number", "description": "Response lag (0-1)"},
                        "cultural": {"type": "number", "description": "Archetype alignment (-1 to 1)"},
                        "f_time": {"type": "number", "default": 1.0}
                    },
                    "required": ["individual", "network", "institutional", "cultural"]
                }
            }
        }
    ]

    emergence_tools = [
        {
            "type": "function",
            "function": {
                "name": "healthcare_precision_therapeutic",
                "description": "CONFLUENCE: Identifies rare alignment of genomic predisposition, environmental readiness, phenotypic timing, and psychosocial engagement for maximum treatment efficacy.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "genomic_predisposition": {"type": "number", "description": "Genetic readiness for treatment (0-1)"},
                        "environmental_readiness": {"type": "number", "description": "Exposure/toxin levels favorable (0-1)"},
                        "phenotypic_timing": {"type": "number", "description": "Disease progression stage optimal (0-1)"},
                        "psychosocial_engagement": {"type": "number", "description": "Patient motivation/support high (0-1)"},
                        "f_time": {"type": "number", "default": 1.0}
                    },
                    "required": ["genomic_predisposition", "environmental_readiness", "phenotypic_timing", "psychosocial_engagement"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "finance_confluence_alpha",
                "description": "CONFLUENCE: Detects asymmetric opportunity when technical setup, macro tailwind, flow positioning, and risk compression achieve directional harmony.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "technical_setup": {"type": "number", "description": "Technical indicators favorable (0-1)"},
                        "macro_tailwind": {"type": "number", "description": "Fundamental/macro support (0-1)"},
                        "flow_positioning": {"type": "number", "description": "Crowd positioning (-1 to 1, extreme = contrarian signal)"},
                        "risk_compression": {"type": "number", "description": "Risk appetite favorable (0-1)"},
                        "f_time": {"type": "number", "default": 1.0}
                    },
                    "required": ["technical_setup", "macro_tailwind", "flow_positioning", "risk_compression"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "cyber_adversary_overreach",
                "description": "CONFLUENCE: Identifies defensive advantage windows when attacker TTPs are stretched, geopolitically pressured, and operationally fatigued.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "threat_intel_stretch": {"type": "number", "description": "Attacker TTPs overextended/visible (0-1)"},
                        "geopolitical_pressure": {"type": "number", "description": "External pressure on attacker (0-1)"},
                        "operational_hardening": {"type": "number", "description": "Defender readiness/hardening (0-1)"},
                        "tool_reuse_fatigue": {"type": "number", "description": "Attacker tool reuse/indicators (0-1)"},
                        "f_time": {"type": "number", "default": 1.0}
                    },
                    "required": ["threat_intel_stretch", "geopolitical_pressure", "operational_hardening", "tool_reuse_fatigue"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "climate_resilience_multiplier",
                "description": "CONFLUENCE: Surfaces interventions with positive cross-domain coupling solving multiple layer problems simultaneously.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "atmospheric_benefit": {"type": "number", "description": "Atmospheric/climate benefit (0-1)"},
                        "ecological_benefit": {"type": "number", "description": "Ecosystem benefit (0-1)"},
                        "infrastructure_benefit": {"type": "number", "description": "Infrastructure resilience benefit (0-1)"},
                        "policy_alignment": {"type": "number", "description": "Policy coherence/support (0-1)"},
                        "f_time": {"type": "number", "default": 1.0}
                    },
                    "required": ["atmospheric_benefit", "ecological_benefit", "infrastructure_benefit", "policy_alignment"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "legal_precedent_seeding",
                "description": "CONFLUENCE: Spots windows when socio-political climate, institutional capacity, statutory ambiguity, and circuit splits align for favorable case law establishment.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "socio_political_climate": {"type": "number", "description": "Receptiveness to legal change (0-1)"},
                        "institutional_capacity": {"type": "number", "description": "Courts/resources to handle case (0-1)"},
                        "statutory_ambiguity": {"type": "number", "description": "Statutory text ambiguity/openness (0-1)"},
                        "circuit_split": {"type": "number", "description": "Degree of circuit split (0-1)"},
                        "f_time": {"type": "number", "default": 1.0}
                    },
                    "required": ["socio_political_climate", "institutional_capacity", "statutory_ambiguity", "circuit_split"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "military_strategic_initiative",
                "description": "CONFLUENCE: Identifies decisive action opportunities when intelligence ambiguity, positional advantage, logistic readiness, and political authorization synchronize.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "enemy_ambiguity": {"type": "number", "description": "Intelligence gaps favoring surprise (0-1)"},
                        "positional_advantage": {"type": "number", "description": "Geographical/tactical position (0-1)"},
                        "logistic_readiness": {"type": "number", "description": "Sustainment capability ready (0-1)"},
                        "authorization_clarity": {"type": "number", "description": "Political authority clear (0-1)"},
                        "f_time": {"type": "number", "default": 1.0}
                    },
                    "required": ["enemy_ambiguity", "positional_advantage", "logistic_readiness", "authorization_clarity"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "social_catalytic_alignment",
                "description": "CONFLUENCE: Spots transformative potential when individual readiness, network bridges, policy windows, and paradigm momentum converge.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "individual_readiness": {"type": "number", "description": "Population psychological readiness (0-1)"},
                        "network_bridges": {"type": "number", "description": "Cross-cutting network connections (0-1)"},
                        "policy_window": {"type": "number", "description": "Policy opportunity open (0-1)"},
                        "paradigm_momentum": {"type": "number", "description": "Cultural paradigm shift underway (0-1)"},
                        "f_time": {"type": "number", "default": 1.0}
                    },
                    "required": ["individual_readiness", "network_bridges", "policy_window", "paradigm_momentum"]
                }
            }
        }
    ]

    generic_tools = [
        {
            "type": "function",
            "function": {
                "name": "generic_detect",
                "description": "GENERIC: Run Mantic detection on a caller-defined domain. Supports 3-6 layers with caller-specified weights and layer names. Same kernel and governance as built-in tools.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain_name": {"type": "string", "description": "Unique domain label (cannot shadow built-in domains)"},
                        "layer_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 3, "maxItems": 6,
                            "description": "Layer name strings (3-6)"
                        },
                        "weights": {
                            "type": "array",
                            "items": {"type": "number", "minimum": 0, "maximum": 1},
                            "minItems": 3, "maxItems": 6,
                            "description": "Layer weights summing to 1.0"
                        },
                        "layer_values": {
                            "type": "array",
                            "items": {"type": "number", "minimum": 0, "maximum": 1},
                            "minItems": 3, "maxItems": 6,
                            "description": "Layer input values (0-1)"
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["friction", "emergence"],
                            "description": "Detection mode: friction (divergence) or emergence (alignment)"
                        },
                        "detection_threshold": {
                            "type": "number",
                            "default": 0.4,
                            "description": "Threshold for friction range / emergence alignment floor"
                        },
                        "layer_hierarchy": {
                            "type": "object",
                            "additionalProperties": {
                                "type": "string",
                                "enum": ["Micro", "Meso", "Macro", "Meta"]
                            },
                            "description": "Optional mapping of layer names to hierarchy levels for layer visibility"
                        },
                        "f_time": {"type": "number", "default": 1.0}
                    },
                    "required": ["domain_name", "layer_names", "weights", "layer_values", "mode"]
                }
            }
        }
    ]

    # Add bounded override params to all tools (optional)
    for tool in friction_tools + emergence_tools + generic_tools:
        tool["function"]["parameters"]["properties"].update(OVERRIDE_PROPERTIES)

    return friction_tools + emergence_tools + generic_tools


def execute_tool(tool_name, arguments):
    """
    Execute a Mantic tool by name with given arguments.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Dict of arguments to pass to the tool
    
    Returns:
        dict: Tool execution result
    
    Raises:
        ValueError: If tool_name is not recognized
    """
    if tool_name not in TOOL_MAP:
        raise ValueError(f"Unknown tool: {tool_name}. Available: {list(TOOL_MAP.keys())}")
    
    # Filter arguments to only those expected by the function
    func = TOOL_MAP[tool_name]
    import inspect
    sig = inspect.signature(func)
    valid_params = set(sig.parameters.keys())
    
    filtered_args = {k: v for k, v in arguments.items() if k in valid_params}
    
    return func(**filtered_args)


def get_tool_descriptions():
    """
    Get human-readable descriptions of all tools.
    
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
    
    Args:
        tool_type: "friction", "emergence", or "all"
    
    Returns:
        list: Filtered tool definitions
    """
    all_tools = get_openai_tools()
    
    if tool_type == "friction":
        return [t for t in all_tools if t["function"]["description"].startswith("FRICTION:")]
    elif tool_type == "emergence":
        return [t for t in all_tools if t["function"]["description"].startswith("CONFLUENCE:")]
    else:
        return all_tools


def explain_result(tool_name, result):
    """
    [v1.2.0] Get human-friendly explanation of tool result.
    
    Returns reasoning guidance based on layer visibility, helping LLMs
    and humans understand which hierarchical layer drove the detection.
    
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
        "_api_version": "1.2.0"
    }


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

    Reads the per-tool YAML files at runtime so edits to YAML are
    immediately reflected without code changes.

    Args:
        tool_names: List of tool names, or None for all tools.

    Returns:
        str: Formatted guidance text for system prompt injection.
    """
    if tool_names is None:
        tool_names = list(TOOL_MAP.keys())
    else:
        # Filter to known tools only (prevents path traversal)
        tool_names = [n for n in tool_names if n in TOOL_MAP]

    sections = []
    for name in tool_names:
        data = _load_tool_yaml(name)
        if not data:
            continue

        lines = [f"### {name} ({data.get('type', '?')} | {data.get('domain', '?')})"]

        # Selection criteria
        sel = data.get("selection", {})
        if sel.get("use_when"):
            lines.append("**Use when:**")
            for item in sel["use_when"]:
                lines.append(f"  - {item}")
        if sel.get("not_for"):
            lines.append("**Not for:**")
            for item in sel["not_for"]:
                lines.append(f"  - {item}")

        # Parameters with calibration anchors
        params = data.get("parameters", {})
        if params:
            lines.append("**Parameters:**")
            for pname, pdata in params.items():
                layer = pdata.get("layer", "?")
                low = pdata.get("low", "")
                high = pdata.get("high", "")
                lines.append(f"  - `{pname}` ({layer}): {low} \u2192 {high}")

        # Interaction guidance (condensed)
        ig = data.get("interaction_guidance", {})
        dampen = ig.get("dampen_when", {})
        amplify = ig.get("amplify_when", {})
        if dampen or amplify:
            lines.append("**Tuning:**")
            for p, reason in dampen.items():
                lines.append(f"  - Dampen `{p}`: {reason}")
            for p, reason in amplify.items():
                lines.append(f"  - Amplify `{p}`: {reason}")

        # Interpretation
        interp = data.get("interpretation", {})
        if interp:
            lines.append(f"**High M:** {interp.get('high_m', '')}")
            lines.append(f"**Low M:** {interp.get('low_m', '')}")

        sections.append("\n".join(lines))

    header = "## Tool Calibration Guidance\n"
    return header + "\n\n".join(sections)


# Domain name → tool name mapping for context loading
_DOMAIN_TOOLS = {
    "healthcare": ["healthcare_phenotype_genotype", "healthcare_precision_therapeutic"],
    "finance": ["finance_regime_conflict", "finance_confluence_alpha"],
    "cyber": ["cyber_attribution_resolver", "cyber_adversary_overreach"],
    "climate": ["climate_maladaptation", "climate_resilience_multiplier"],
    "legal": ["legal_precedent_drift", "legal_precedent_seeding"],
    "military": ["military_friction_forecast", "military_strategic_initiative"],
    "social": ["social_narrative_rupture", "social_catalytic_alignment"],
}

# Aliases for domain names → canonical _DOMAIN_TOOLS key
_DOMAIN_ALIASES = {
    "cybersecurity": "cyber",
    "security": "cyber",
    "health": "healthcare",
    "command": "military",
}


def get_scaffold():
    """
    Load the universal reasoning scaffold.

    This is Stage 1 of the load order: the domain-agnostic framework
    that teaches an LLM how to think with Mantic (formula, layer
    hierarchy, design philosophy, translation rules).

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

    This is Stage 2 of the load order: the domain-specific layer
    mappings, multi-column architecture, and reasoning protocols.

    Args:
        domain: Domain name (healthcare, finance, cyber, climate,
                legal, military, social, plan, current).

    Returns:
        str: Domain config content, or empty string if not found.
    """
    # Map domain names to config filenames
    # Files are named mantic_{name}.md in configs/
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

    Chains: Scaffold → Domain Config (optional) → Tool Guidance.

    Args:
        domain: Optional domain name. If provided, includes the
                domain-specific config and only that domain's tool
                guidance. If None, includes all tool guidance.

    Returns:
        str: Complete context string for system prompt injection.
    """
    parts = []

    # Stage 1: Scaffold (always)
    scaffold = get_scaffold()
    if scaffold:
        parts.append(scaffold)

    # Stage 2: Domain config (if domain specified)
    if domain:
        config = get_domain_config(domain)
        if config:
            parts.append(config)

    # Stage 3: Tool guidance (normalize aliases before lookup)
    canonical = _DOMAIN_ALIASES.get(domain, domain) if domain else None
    if canonical and canonical in _DOMAIN_TOOLS:
        guidance = get_tool_guidance(_DOMAIN_TOOLS[canonical])
    else:
        guidance = get_tool_guidance()
    parts.append(guidance)

    return "\n\n---\n\n".join(parts)


if __name__ == "__main__":
    # Test the adapter
    print("=== OpenAI Adapter Test (14 Tools) ===\n")
    
    tools = get_openai_tools()
    print(f"Total available tools: {len(tools)}")
    
    friction = get_tools_by_type("friction")
    emergence = get_tools_by_type("emergence")
    print(f"  Friction tools: {len(friction)}")
    print(f"  Emergence tools: {len(emergence)}")
    
    print("\n--- Testing Friction Tool ---")
    result = execute_tool("healthcare_phenotype_genotype", {
        "phenotypic": 0.3, "genomic": 0.9, "environmental": 0.4, "psychosocial": 0.8
    })
    print(f"Alert: {result['alert']}")
    print(f"M-Score: {result['m_score']:.3f}")
    
    print("\n--- Testing Emergence Tool ---")
    result = execute_tool("healthcare_precision_therapeutic", {
        "genomic_predisposition": 0.85, "environmental_readiness": 0.82,
        "phenotypic_timing": 0.88, "psychosocial_engagement": 0.90
    })
    print(f"Window Detected: {result['window_detected']}")
    print(f"Window Type: {result.get('window_type', 'N/A')}")
    print(f"M-Score: {result['m_score']:.3f}")

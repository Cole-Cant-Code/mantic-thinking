"""
Layer Hierarchy Definitions and Visibility

Maps tool inputs to hierarchical layers (Micro/Meso/Macro/Meta) for reasoning.

NOTE: These are interpretive aids derived from tool weight structures.
They help LLMs explain results but do not affect the core M-score calculation.
"""

from typing import Dict, List, Literal, Optional, Any

LayerType = Literal["Micro", "Meso", "Macro", "Meta"]

# Layer definitions from mantic framework
LAYER_DEFINITIONS = {
    "Micro": {
        "symbol": "L₁",
        "description": "Granular signal. Individual data points, atomic facts.",
        "timescale": "Immediate",
        "examples": ["cellular", "token-level", "individual sensor"]
    },
    "Meso": {
        "symbol": "L₂",
        "description": "Local coupling. Pattern detection within domain boundaries.",
        "timescale": "Short-term",
        "examples": ["ward", "team", "local context"]
    },
    "Macro": {
        "symbol": "L₃",
        "description": "System structure. Domain-wide constraints.",
        "timescale": "Medium-term",
        "examples": ["hospital system", "market regime", "organization"]
    },
    "Meta": {
        "symbol": "L₄",
        "description": "Adaptive weights. Long-term drift, learning, memory.",
        "timescale": "Long-term",
        "examples": ["epidemiological trends", "baseline evolution"]
    }
}

# Tool layer mappings - interpretive aids for reasoning
_TOOL_LAYER_MAP: Dict[str, Dict[str, LayerType]] = {
    # Healthcare Friction
    "healthcare_phenotype_genotype": {
        "phenotypic": "Micro",
        "genomic": "Micro",
        "environmental": "Meso",
        "psychosocial": "Meso"
    },
    # Healthcare Emergence
    "healthcare_precision_therapeutic": {
        "genomic_predisposition": "Micro",
        "environmental_readiness": "Meso",
        "phenotypic_timing": "Micro",
        "psychosocial_engagement": "Meso"
    },
    # Finance Friction
    "finance_regime_conflict": {
        "technical": "Micro",
        "macro": "Macro",
        "flow": "Meso",
        "risk": "Meso"
    },
    # Finance Emergence
    "finance_confluence_alpha": {
        "technical_setup": "Micro",
        "macro_tailwind": "Macro",
        "flow_positioning": "Meso",
        "risk_compression": "Meso"
    },
    # Cyber Friction
    "cyber_attribution_resolver": {
        "technical": "Micro",
        "threat_intel": "Meso",
        "operational_impact": "Meso",
        "geopolitical": "Macro"
    },
    # Cyber Emergence
    "cyber_adversary_overreach": {
        "threat_intel_stretch": "Meso",
        "geopolitical_pressure": "Macro",
        "operational_hardening": "Meso",
        "tool_reuse_fatigue": "Micro"
    },
    # Climate Friction
    "climate_maladaptation": {
        "atmospheric": "Micro",
        "ecological": "Meso",
        "infrastructure": "Macro",
        "policy": "Meta"
    },
    # Climate Emergence
    "climate_resilience_multiplier": {
        "atmospheric_benefit": "Micro",
        "ecological_benefit": "Meso",
        "infrastructure_benefit": "Macro",
        "policy_alignment": "Meta"
    },
    # Legal Friction
    "legal_precedent_drift": {
        "black_letter": "Micro",
        "precedent": "Meso",
        "operational": "Macro",
        "socio_political": "Meta"
    },
    # Legal Emergence
    "legal_precedent_seeding": {
        "socio_political_climate": "Meta",
        "institutional_capacity": "Macro",
        "statutory_ambiguity": "Meso",
        "circuit_split": "Meso"
    },
    # Military Friction
    "military_friction_forecast": {
        "maneuver": "Micro",
        "intelligence": "Meso",
        "sustainment": "Macro",
        "political": "Meta"
    },
    # Military Emergence
    "military_strategic_initiative": {
        "enemy_ambiguity": "Meso",
        "positional_advantage": "Micro",
        "logistic_readiness": "Macro",
        "authorization_clarity": "Meta"
    },
    # Social Friction
    "social_narrative_rupture": {
        "individual": "Micro",
        "network": "Meso",
        "institutional": "Macro",
        "cultural": "Meta"
    },
    # Social Emergence
    "social_catalytic_alignment": {
        "individual_readiness": "Micro",
        "network_bridges": "Meso",
        "policy_window": "Macro",
        "paradigm_momentum": "Meta"
    },
    # System Lock Friction
    "system_lock_recursive_control": {
        "agent_autonomy": "Micro",
        "collective_capacity": "Meso",
        "concentration_control": "Macro",
        "recursive_depth": "Meta"
    },
    # System Lock Emergence
    "system_lock_dissolution_window": {
        "autonomy_momentum": "Micro",
        "alternative_readiness": "Meso",
        "control_vulnerability": "Macro",
        "pattern_flexibility": "Meta"
    }
}

# Rationale for dominant layer by tool
_DOMINANT_RATIONALE: Dict[str, Dict[str, str]] = {
    "healthcare_phenotype_genotype": {
        "Micro": "Phenotypic/genomic mismatch manifests at individual/cellular level",
        "Meso": "Environmental or psychosocial factors dominate presentation"
    },
    "healthcare_precision_therapeutic": {
        "Micro": "Genomic readiness and phenotypic timing are primary",
        "Meso": "Environmental readiness or psychosocial engagement is limiting factor"
    },
    "finance_regime_conflict": {
        "Micro": "Technical price action driving regime detection",
        "Meso": "Flow positioning or risk appetite divergence dominant",
        "Macro": "Fundamental macro indicators contradict technical signals"
    },
    "finance_confluence_alpha": {
        "Micro": "Technical setup is primary signal",
        "Meso": "Flow positioning or risk compression dominant",
        "Macro": "Macro tailwind driving opportunity"
    },
    "cyber_attribution_resolver": {
        "Micro": "Technical sophistication mismatch primary",
        "Meso": "Threat intel or operational impact misalignment dominant",
        "Macro": "Geopolitical context contradicts technical assessment"
    },
    "cyber_adversary_overreach": {
        "Micro": "Tool reuse patterns indicate fatigue",
        "Meso": "Threat intel stretch or operational hardening dominant",
        "Macro": "Geopolitical pressure creating window"
    },
    "climate_maladaptation": {
        "Micro": "Atmospheric conditions driving maladaptation risk",
        "Meso": "Ecological factors create cross-layer tension",
        "Macro": "Infrastructure resilience mismatch dominant",
        "Meta": "Policy incoherence creating meta-level harm"
    },
    "climate_resilience_multiplier": {
        "Micro": "Atmospheric benefits drive intervention value",
        "Meso": "Ecological benefits primary",
        "Macro": "Infrastructure resilience dominant",
        "Meta": "Policy alignment creates multiplicative effect"
    },
    "legal_precedent_drift": {
        "Micro": "Statutory text interpretation shifting",
        "Meso": "Precedent consistency eroding",
        "Macro": "Operational feasibility creating tension",
        "Meta": "Socio-political climate driving drift"
    },
    "legal_precedent_seeding": {
        "Micro": "Statutory ambiguity creating opportunity",
        "Meso": "Circuit split or institutional capacity dominant",
        "Macro": "Institutional readiness driving window",
        "Meta": "Socio-political climate favorable for precedent"
    },
    "military_friction_forecast": {
        "Micro": "Maneuver feasibility constraint dominant",
        "Meso": "Intelligence confidence gap creating friction",
        "Macro": "Sustainment/logistics bottleneck",
        "Meta": "Political authorization mismatch"
    },
    "military_strategic_initiative": {
        "Micro": "Positional advantage creating opportunity",
        "Meso": "Enemy ambiguity dominant factor",
        "Macro": "Logistic readiness enabling initiative",
        "Meta": "Clear political authorization"
    },
    "social_narrative_rupture": {
        "Micro": "Individual sentiment velocity driving rupture",
        "Meso": "Network propagation speed dominant",
        "Macro": "Institutional response lag critical",
        "Meta": "Cultural archetype misalignment"
    },
    "social_catalytic_alignment": {
        "Micro": "Individual readiness primary",
        "Meso": "Network bridges enabling alignment",
        "Macro": "Policy window open",
        "Meta": "Cultural paradigm momentum"
    },
    "system_lock_recursive_control": {
        "Micro": "Agent autonomy deficit driving lock-in",
        "Meso": "Collective capacity insufficient for viable alternatives",
        "Macro": "Concentration control is dominating system behavior",
        "Meta": "Recursive reinforcement is absorbing interventions"
    },
    "system_lock_dissolution_window": {
        "Micro": "Autonomy momentum is building at the individual layer",
        "Meso": "Alternative readiness is driving transition potential",
        "Macro": "Control vulnerability is creating an opening",
        "Meta": "Pattern flexibility is enabling sustainable dissolution"
    }
}


def _get_layer_weights(tool_name: str, tool_weights: Dict[str, float]) -> Dict[LayerType, float]:
    """Aggregate tool weights by hierarchical layer."""
    hierarchy = _TOOL_LAYER_MAP.get(tool_name, {})
    layer_weights = {"Micro": 0.0, "Meso": 0.0, "Macro": 0.0, "Meta": 0.0}
    
    for input_name, weight in tool_weights.items():
        layer = hierarchy.get(input_name)
        if layer:
            layer_weights[layer] += weight
    
    return layer_weights


def _get_dominant_layer(layer_weights: Dict[LayerType, float]) -> LayerType:
    """Return layer with highest weight."""
    return max(layer_weights, key=layer_weights.get)


def _get_rationale(tool_name: str, dominant_layer: LayerType, 
                   tool_weights: Dict[str, float]) -> str:
    """Get rationale for dominant layer."""
    # Check if there's a specific rationale for this tool/layer combo
    tool_rationales = _DOMINANT_RATIONALE.get(tool_name, {})
    if dominant_layer in tool_rationales:
        return tool_rationales[dominant_layer]
    
    # Default rationale based on weight distribution
    return f"{dominant_layer} layer has highest aggregated weight ({tool_weights:.2f})"


def _get_layer_contributions(tool_name: str, tool_weights: Dict[str, float],
                             layer_values: Dict[str, float],
                             layer_interactions: Optional[Dict[str, float]] = None) -> Dict[LayerType, float]:
    """
    Compute actual layer contributions for this detection (W * L per layer).
    
    This reflects which layer drove the detection based on actual inputs,
    not just static weight distribution.
    """
    hierarchy = _TOOL_LAYER_MAP.get(tool_name, {})
    contributions = {"Micro": 0.0, "Meso": 0.0, "Macro": 0.0, "Meta": 0.0}
    
    for input_name, weight in tool_weights.items():
        value = layer_values.get(input_name, 0)
        if value != value:  # NaN check
            continue
        interaction = 1.0
        if layer_interactions is not None:
            interaction = layer_interactions.get(input_name, 1.0)
        layer = hierarchy.get(input_name)
        if layer:
            contributions[layer] += weight * value * interaction
    
    return contributions


def get_layer_visibility(tool_name: str, tool_weights: Dict[str, float],
                         layer_values: Optional[Dict[str, float]] = None,
                         layer_interactions: Optional[Dict[str, float]] = None) -> Optional[Dict[str, Any]]:
    """
    Get layer visibility info for a tool result.
    
    Returns interpretive aids for understanding which hierarchical layer
    drives the tool's detection logic.
    
    Args:
        tool_name: Name of the tool
        tool_weights: The tool's WEIGHTS dict
        layer_values: Optional dict of input values {param_name: value}.
                      If provided, dominance is computed from actual contribution (W * L * I).
                      If None, falls back to static weight distribution.
        layer_interactions: Optional dict of interaction values {param_name: value}.
                      If provided, used in contribution calculation.
    
    Returns:
        Dict with dominant layer, weights by layer, and rationale.
        None if tool not mapped.
    
    Note:
        This is an interpretive aid for reasoning. It does not affect
        the M-score calculation in any way.
    """
    if tool_name not in _TOOL_LAYER_MAP:
        return None
    
    layer_weights = _get_layer_weights(tool_name, tool_weights)
    
    # Determine dominance: input-driven if values provided, else weight-only
    if layer_values:
        contributions = _get_layer_contributions(tool_name, tool_weights, layer_values, layer_interactions)
        dominant = _get_dominant_layer(contributions)
        contribution_value = contributions[dominant]
        is_input_driven = True
    else:
        dominant = _get_dominant_layer(layer_weights)
        contribution_value = layer_weights[dominant]
        contributions = None
        is_input_driven = False
    
    result = {
        "dominant": dominant,
        "weights_by_layer": layer_weights,
        "rationale": _get_rationale(tool_name, dominant, contribution_value),
        "_note": "Interpretive aid for reasoning; does not affect M-score calculation"
    }
    
    if contributions:
        result["contributions_by_layer"] = contributions
        result["input_driven"] = True
    else:
        result["input_driven"] = False
    
    return result

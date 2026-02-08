"""
Military: Strategic Initiative Window

Identifies decisive action opportunities when intelligence ambiguity,
positional advantage, logistic readiness, and political authorization synchronize.

Confluence Logic: Fog helps us + we're ready + authorized = initiative window

Optional Overrides (Bounded):
    threshold_override: Dict of threshold overrides
        e.g., {"initiative": 0.75, "minimum_floor": 0.65}
    temporal_config: Dict for temporal kernel tuning (domain-restricted)
    
    NOTE: Domain weights (W) are IMMUTABLE.

Output:
    window_detected, maneuver_type, advantage, m_score, overrides_applied
"""

import sys
import os

# Avoid mutating sys.path on import; only adjust for direct script execution.
if __name__ == "__main__":
    _repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

import numpy as np
from mantic_thinking.core.safe_kernel import safe_mantic_kernel as mantic_kernel
from mantic_thinking.core.mantic_kernel import compute_temporal_kernel
from mantic_thinking.core.validators import (
    clamp_input, require_finite_inputs, format_attribution,
    clamp_threshold_override, validate_temporal_config,
    clamp_f_time, build_overrides_audit, compute_layer_coupling,
    resolve_interaction_coefficients
)
from mantic_thinking.mantic.introspection import get_layer_visibility


WEIGHTS = [0.25, 0.25, 0.25, 0.25]
LAYER_NAMES = ['enemy_ambiguity', 'positional_advantage', 'logistic_readiness', 'authorization_clarity']

DEFAULT_THRESHOLDS = {
    'initiative': 0.70,     # Initiative window threshold
    'minimum_floor': 0.60   # Minimum floor for all layers
}

DOMAIN = "military"


def detect(enemy_ambiguity, positional_advantage, logistic_readiness, authorization_clarity,
           f_time=1.0, threshold_override=None, temporal_config=None,
           interaction_mode="dynamic", interaction_override=None,
           interaction_override_mode="scale"):
    """Identify decisive action windows (offensive leverage)."""
    
    # INPUT VALIDATION
    require_finite_inputs({
        "enemy_ambiguity": enemy_ambiguity,
        "positional_advantage": positional_advantage,
        "logistic_readiness": logistic_readiness,
        "authorization_clarity": authorization_clarity,
    })

    # OVERRIDES PROCESSING
    threshold_info = {}
    active_thresholds = DEFAULT_THRESHOLDS.copy()
    ignored_threshold_keys = []
    
    if threshold_override and isinstance(threshold_override, dict):
        for key, requested in threshold_override.items():
            if key in DEFAULT_THRESHOLDS:
                clamped_val, was_clamped, info = clamp_threshold_override(
                    requested, DEFAULT_THRESHOLDS[key]
                )
                active_thresholds[key] = clamped_val
                threshold_info[key] = info
            else:
                ignored_threshold_keys.append(key)
    
    temporal_validated, temporal_rejected, temporal_clamped = None, {}, {}
    temporal_applied = None
    if temporal_config and isinstance(temporal_config, dict):
        temporal_validated, temporal_rejected, temporal_clamped = validate_temporal_config(
            temporal_config, domain=DOMAIN
        )
        if "kernel_type" not in temporal_validated:
            if "kernel_type" not in temporal_rejected:
                temporal_rejected["kernel_type"] = {
                    "requested": temporal_config.get("kernel_type"),
                    "reason": "kernel_type required and must be allowed for domain"
                }
        if "t" not in temporal_validated:
            if "t" not in temporal_rejected:
                temporal_rejected["t"] = {
                    "requested": temporal_config.get("t"),
                    "reason": "t required for temporal_config"
                }
        if "kernel_type" in temporal_validated and "t" in temporal_validated:
            f_time = compute_temporal_kernel(**temporal_validated)
            temporal_applied = temporal_validated
    
    f_time_clamped, _, f_time_info = clamp_f_time(f_time)
    
    # CORE DETECTION
    L = [
        clamp_input(enemy_ambiguity, name="enemy_ambiguity"),
        clamp_input(positional_advantage, name="positional_advantage"),
        clamp_input(logistic_readiness, name="logistic_readiness"),
        clamp_input(authorization_clarity, name="authorization_clarity")
    ]
    
    # Interaction coefficients: base, optional tool-dynamic, optional caller override.
    I_base = [1.0, 1.0, 1.0, 1.0]
    I_dynamic = I_base
    I, interaction_audit = resolve_interaction_coefficients(
        LAYER_NAMES,
        I_base=I_base,
        I_dynamic=I_dynamic,
        interaction_mode=interaction_mode,
        interaction_override=interaction_override,
        interaction_override_mode=interaction_override_mode,
    )
    
    M, S, attr = mantic_kernel(WEIGHTS, L, I, f_time_clamped)
    
    initiative_threshold = active_thresholds['initiative']
    minimum_floor = active_thresholds['minimum_floor']
    
    critical_factors = [L[0], L[2], L[3]]
    initiative_floor = min(critical_factors)
    initiative_score = initiative_floor * L[1]
    
    window_detected = False
    maneuver_type = None
    advantage_description = None
    recommended_action = None
    execution_window = None
    risk_assessment = None
    
    if initiative_score > initiative_threshold and min(L) > minimum_floor:
        window_detected = True
        
        if initiative_score > 0.85 and all(l > 0.75 for l in L):
            maneuver_type = "DECISIVE_ACTION"
            advantage_description = ("Synchronized ambiguity/readiness/authorization with "
                                    "strong positional edge - rare convergence")
            recommended_action = "Execute within 24-48 hours before fog lifts or enemy adapts"
            execution_window = "24-48 hours (highly perishable)"
            risk_assessment = "LOW - All factors favorable"
        elif initiative_score > 0.75:
            maneuver_type = "OFFENSIVE_OPERATION"
            advantage_description = "Strong initiative conditions across multiple factors"
            recommended_action = "Prepare for execution within 72 hours"
            execution_window = "48-72 hours"
            risk_assessment = "MODERATE - Monitor for enemy counter-moves"
        else:
            maneuver_type = "TACTICAL_INITIATIVE"
            advantage_description = "Favorable but not exceptional initiative window"
            recommended_action = "Develop courses of action, prepare for exploitation"
            execution_window = "72-96 hours"
            risk_assessment = "MODERATE-HIGH - Contingency plans required"
    
    # Build audit
    threshold_clamped_any = any(
        info.get("was_clamped", False) 
        for info in threshold_info.values()
    ) if threshold_info else False
    
    threshold_audit_info = None
    if threshold_info:
        threshold_audit_info = {
            "overrides": {
                key: {
                    "requested": info.get("requested"),
                    "used": info.get("used"),
                    "was_clamped": info.get("was_clamped", False)
                }
                for key, info in threshold_info.items()
            },
            "was_clamped": threshold_clamped_any,
            "ignored_keys": ignored_threshold_keys if ignored_threshold_keys else None
        }
    
    overrides_applied = build_overrides_audit(
        threshold_overrides=threshold_override if threshold_override else None,
        temporal_config=temporal_config if temporal_config else None,
        threshold_info=threshold_audit_info,
        temporal_validated=temporal_applied,
        temporal_rejected=temporal_rejected if temporal_rejected else None,
        temporal_clamped=temporal_clamped if temporal_clamped else None,
        f_time_info=f_time_info,
        interaction=interaction_audit
    )
    
    _weights_dict = dict(zip(LAYER_NAMES, WEIGHTS))
    _layer_values_dict = dict(zip(LAYER_NAMES, L))
    _layer_interactions = dict(zip(LAYER_NAMES, I))
    layer_visibility = get_layer_visibility(
        "military_strategic_initiative",
        _weights_dict,
        _layer_values_dict,
        _layer_interactions
    )
    layer_coupling = compute_layer_coupling(L, LAYER_NAMES)
    
    if window_detected:
        return {
            "window_detected": True,
            "maneuver_type": maneuver_type,
            "initiative_score": float(initiative_score),
            "advantage": advantage_description,
            "recommended_action": recommended_action,
            "execution_window": execution_window,
            "risk_assessment": risk_assessment,
            "m_score": float(M),
            "spatial_component": float(S),
            "layer_attribution": format_attribution(attr, LAYER_NAMES),
            "thresholds": active_thresholds,
            "overrides_applied": overrides_applied,
            "synchronization_status": {
                "enemy_ambiguity": float(L[0]),
                "positional_advantage": float(L[1]),
                "logistic_readiness": float(L[2]),
                "authorization_clarity": float(L[3])
            },
            "layer_visibility": layer_visibility,
            "layer_coupling": layer_coupling
        }
    
    limiting_factors = []
    if L[0] <= minimum_floor:
        limiting_factors.append("insufficient enemy ambiguity (too clear)")
    if L[1] <= minimum_floor:
        limiting_factors.append("weak positional advantage")
    if L[2] <= minimum_floor:
        limiting_factors.append("logistics not ready")
    if L[3] <= minimum_floor:
        limiting_factors.append("authorization unclear")
    
    return {
        "window_detected": False,
        "initiative_score": float(initiative_score),
        "maneuver_type": "DEFENSIVE_POSTURE",
        "limiting_factors": limiting_factors,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "status": f"Initiative window closed. {', '.join(limiting_factors) if limiting_factors else 'Conditions unfavorable'}.",
        "recommendation": "Maintain readiness, seek to improve positional advantage or wait for authorization.",
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied,
        "layer_visibility": layer_visibility,
        "layer_coupling": layer_coupling
    }


if __name__ == "__main__":
    print("=== Military Strategic Initiative Window ===\n")
    
    print("Test 1: Decisive action window")
    result = detect(
        enemy_ambiguity=0.85,
        positional_advantage=0.88,
        logistic_readiness=0.82,
        authorization_clarity=0.90
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Maneuver Type: {result['maneuver_type']}\n")
    
    print("Test 2: Offensive operation")
    result = detect(
        enemy_ambiguity=0.75,
        positional_advantage=0.78,
        logistic_readiness=0.72,
        authorization_clarity=0.80
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Maneuver Type: {result['maneuver_type']}\n")
    
    print("Test 3: No window")
    result = detect(
        enemy_ambiguity=0.80,
        positional_advantage=0.75,
        logistic_readiness=0.45,
        authorization_clarity=0.85
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Limiting Factors: {result['limiting_factors']}")

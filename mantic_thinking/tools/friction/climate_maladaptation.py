"""
Climate: Maladaptation Preventer

Blocks solutions that solve immediate micro problems but create macro/meta harms.

Input Layers:
    atmospheric: Atmospheric condition metrics (0-1)
    ecological: Ecosystem health indicators (0-1)
    infrastructure: Infrastructure resilience (0-1)
    policy: Policy coherence score (0-1)

Optional Overrides (Bounded):
    threshold_override: Dict of threshold overrides
        e.g., {"block": 0.65, "caution": 0.45}
    temporal_config: Dict for temporal kernel tuning (domain-restricted)
    
    NOTE: Domain weights (W) are IMMUTABLE.

Output:
    alert, decision, alternative_suggestion, m_score, overrides_applied
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


WEIGHTS = {
    'atmospheric': 0.25,
    'ecological': 0.30,
    'infrastructure': 0.25,
    'policy': 0.20
}

LAYER_NAMES = ['atmospheric', 'ecological', 'infrastructure', 'policy']

DEFAULT_THRESHOLDS = {
    'block': 0.6,     # Block threshold for severe maladaptation
    'caution': 0.4    # Caution threshold for warnings
}

DOMAIN = "climate"


def detect(atmospheric, ecological, infrastructure, policy, f_time=1.0,
           threshold_override=None, temporal_config=None,
           interaction_mode="dynamic", interaction_override=None,
           interaction_override_mode="scale"):
    """Detect maladaptation risks in climate interventions."""
    
    # INPUT VALIDATION
    require_finite_inputs({
        "atmospheric": atmospheric,
        "ecological": ecological,
        "infrastructure": infrastructure,
        "policy": policy,
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
        clamp_input(atmospheric, name="atmospheric"),
        clamp_input(ecological, name="ecological"),
        clamp_input(infrastructure, name="infrastructure"),
        clamp_input(policy, name="policy")
    ]
    
    W = list(WEIGHTS.values())
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
    
    M, S, attr = mantic_kernel(W, L, I, f_time_clamped)
    
    alert = None
    decision = "proceed"
    alternative_suggestion = None
    maladaptation_score = 0.0
    
    block_threshold = active_thresholds['block']
    caution_threshold = active_thresholds['caution']
    
    infra_eco_gap = L[2] - L[1]
    low_policy = L[3] < 0.3
    short_term_focus = L[0] > 0.6 and L[1] < 0.4
    
    if infra_eco_gap > block_threshold:
        maladaptation_score = infra_eco_gap
        if L[1] < caution_threshold:
            decision = "block"
            alert = "MALADAPTATION RISK: Infrastructure solution threatens ecosystem collapse"
            alternative_suggestion = (
                "Integrate nature-based solutions. Current plan prioritizes infrastructure "
                "(resilience: {:.1f}) over ecological health ({:.1f}). Consider green infrastructure alternatives."
                .format(L[2], L[1])
            )
        else:
            decision = "caution"
            alert = "MALADAPTATION WARNING: Infrastructure-heavy solution may have ecological side effects"
            alternative_suggestion = "Add ecological safeguards. Monitor ecosystem indicators during implementation."
    elif short_term_focus:
        maladaptation_score = L[0] - L[1]
        if L[3] < caution_threshold:
            decision = "block"
            alert = "MALADAPTATION RISK: Short-term atmospheric fix without policy framework or ecological consideration"
            alternative_suggestion = (
                "Develop integrated approach with policy coherence and ecological monitoring. "
                "Avoid atmospheric-only interventions."
            )
        else:
            decision = "caution"
            alert = "MALADAPTATION WARNING: Atmospheric intervention may have downstream ecological impacts"
            alternative_suggestion = "Strengthen ecological monitoring and adaptive management protocols."
    elif low_policy and (L[0] > block_threshold or L[2] > block_threshold):
        decision = "caution"
        maladaptation_score = 0.4
        alert = "POLICY GAP: Technical solution lacks policy coherence - may face implementation barriers"
        alternative_suggestion = "Develop supporting policy framework before proceeding with technical implementation."
    
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
    
    layer_values_dict = {"atmospheric": float(L[0]), "ecological": float(L[1]), "infrastructure": float(L[2]), "policy": float(L[3])}
    layer_interactions = {
        "atmospheric": float(I[0]),
        "ecological": float(I[1]),
        "infrastructure": float(I[2]),
        "policy": float(I[3]),
    }
    layer_visibility = get_layer_visibility("climate_maladaptation", WEIGHTS, layer_values_dict, layer_interactions)
    layer_coupling = compute_layer_coupling(L, LAYER_NAMES)
    
    return {
        "alert": alert,
        "decision": decision,
        "alternative_suggestion": alternative_suggestion,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "maladaptation_score": float(maladaptation_score),
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied,
        "layer_visibility": layer_visibility,
        "layer_coupling": layer_coupling
    }


if __name__ == "__main__":
    print("=== Climate Maladaptation Preventer ===\n")
    
    print("Test 1: Infrastructure solution threatening ecosystem")
    result = detect(atmospheric=0.7, ecological=0.2, infrastructure=0.8, policy=0.3)
    print(f"  Decision: {result['decision']}")
    print(f"  Alert: {result['alert']}\n")
    
    print("Test 2: Balanced approach")
    result = detect(atmospheric=0.6, ecological=0.7, infrastructure=0.6, policy=0.7)
    print(f"  Decision: {result['decision']}")
    print(f"  Alert: {result['alert']}\n")
    
    print("Test 3: Short-term atmospheric fix without policy")
    result = detect(atmospheric=0.8, ecological=0.3, infrastructure=0.6, policy=0.2)
    print(f"  Decision: {result['decision']}")
    print(f"  Alert: {result['alert']}")

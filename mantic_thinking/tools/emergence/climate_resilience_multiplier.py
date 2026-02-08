"""
Climate: Resilience Multiplier

Surfaces interventions with positive cross-domain coupling
solving multiple layer problems simultaneously.

Confluence Logic: Strong positive coupling across all 4 domains = multiplier effect

Optional Overrides (Bounded):
    threshold_override: Dict of threshold overrides
        e.g., {"coupling": 0.55, "min_layer": 0.55, "multiplier": 0.75}
    temporal_config: Dict for temporal kernel tuning (domain-restricted)
    
    NOTE: Domain weights (W) are IMMUTABLE.

Output:
    window_detected, intervention_type, cross_domain_coupling, m_score, overrides_applied
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
    clamp_f_time, build_overrides_audit, compute_layer_coupling
)
from mantic_thinking.mantic.introspection import get_layer_visibility


WEIGHTS = [0.25, 0.25, 0.25, 0.25]
LAYER_NAMES = ['atmospheric', 'ecological', 'infrastructure', 'policy']

DEFAULT_THRESHOLDS = {
    'coupling': 0.50,      # Coupling threshold
    'min_layer': 0.50,     # Minimum layer threshold
    'multiplier': 0.70     # High multiplier threshold
}

DOMAIN = "climate"


def detect(atmospheric_benefit, ecological_benefit, infrastructure_benefit, policy_alignment,
           f_time=1.0, threshold_override=None, temporal_config=None):
    """Identify interventions that solve multiple layer problems simultaneously."""
    
    # INPUT VALIDATION
    require_finite_inputs({
        "atmospheric_benefit": atmospheric_benefit,
        "ecological_benefit": ecological_benefit,
        "infrastructure_benefit": infrastructure_benefit,
        "policy_alignment": policy_alignment,
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
        clamp_input(atmospheric_benefit, name="atmospheric_benefit"),
        clamp_input(ecological_benefit, name="ecological_benefit"),
        clamp_input(infrastructure_benefit, name="infrastructure_benefit"),
        clamp_input(policy_alignment, name="policy_alignment")
    ]
    
    I = [1.0, 1.0, 1.0, 1.0]
    
    M, S, attr = mantic_kernel(WEIGHTS, L, I, f_time_clamped)
    
    coupling_threshold = active_thresholds['coupling']
    min_layer_threshold = active_thresholds['min_layer']
    multiplier_threshold = active_thresholds['multiplier']
    
    pairwise_products = [
        L[0]*L[1], L[0]*L[2], L[0]*L[3],
        L[1]*L[2], L[1]*L[3],
        L[2]*L[3]
    ]
    coupling = sum(pairwise_products) / len(pairwise_products)
    high_benefit_count = sum(1 for l in L if l > 0.7)
    
    window_detected = False
    intervention_type = None
    example_intervention = None
    recommended_action = None
    funding_priority = None
    
    if coupling > coupling_threshold and min(L) > min_layer_threshold:
        window_detected = True
        
        if coupling > multiplier_threshold and high_benefit_count >= 3:
            intervention_type = "HIGH_MULTIPLIER"
            funding_priority = "URGENT - High leverage across 4 domain columns"
            example_intervention = "Urban forestry with green infrastructure: heat reduction + biodiversity + stormwater + equity"
            recommended_action = "Prioritize immediate funding. Every dollar creates compounding benefits across atmospheric, ecological, infrastructure, and policy domains."
        elif coupling > 0.60 or high_benefit_count >= 3:
            intervention_type = "MULTIPLIER"
            funding_priority = "HIGH - Cross-domain benefits"
            example_intervention = "Wetland restoration: carbon sequestration + flood control + habitat + recreation"
            recommended_action = "Fast-track approval. Strong positive externalities across multiple systems."
        else:
            intervention_type = "MODERATE_MULTIPLIER"
            funding_priority = "MODERATE - Dual benefits"
            example_intervention = "Solar canopy parking: renewable energy + heat reduction"
            recommended_action = "Include in funding round. Good but not exceptional cross-domain coupling."
    
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
        f_time_info=f_time_info
    )
    
    _weights_dict = dict(zip(LAYER_NAMES, WEIGHTS))
    _layer_values_dict = dict(zip(LAYER_NAMES, L))
    layer_visibility = get_layer_visibility("climate_resilience_multiplier", _weights_dict, _layer_values_dict)
    layer_coupling = compute_layer_coupling(L, LAYER_NAMES)
    
    if window_detected:
        return {
            "window_detected": True,
            "intervention_type": intervention_type,
            "cross_domain_coupling": float(coupling),
            "benefit_layers_above_70": high_benefit_count,
            "example_intervention": example_intervention,
            "recommended_action": recommended_action,
            "funding_priority": funding_priority,
            "m_score": float(M),
            "spatial_component": float(S),
            "layer_attribution": format_attribution(attr, LAYER_NAMES),
            "thresholds": active_thresholds,
            "overrides_applied": overrides_applied,
            "benefit_profile": {
                "atmospheric": float(L[0]),
                "ecological": float(L[1]),
                "infrastructure": float(L[2]),
                "policy": float(L[3])
            },
            "layer_visibility": layer_visibility,
            "layer_coupling": layer_coupling
        }
    
    below_threshold = [LAYER_NAMES[i] for i, l in enumerate(L) if l <= min_layer_threshold]
    
    return {
        "window_detected": False,
        "cross_domain_coupling": float(coupling),
        "coupling_status": "Insufficient coupling for multiplier effect",
        "benefit_layers_above_70": high_benefit_count,
        "limiting_factors": below_threshold,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "status": f"Intervention benefits limited to {high_benefit_count} domains. Seek solutions with broader coupling.",
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied,
        "layer_visibility": layer_visibility,
        "layer_coupling": layer_coupling
    }


if __name__ == "__main__":
    print("=== Climate Resilience Multiplier ===\n")
    
    print("Test 1: High multiplier")
    result = detect(
        atmospheric_benefit=0.75,
        ecological_benefit=0.80,
        infrastructure_benefit=0.78,
        policy_alignment=0.82
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Intervention Type: {result.get('intervention_type', 'N/A')}\n")
    
    print("Test 2: Moderate multiplier")
    result = detect(
        atmospheric_benefit=0.70,
        ecological_benefit=0.72,
        infrastructure_benefit=0.65,
        policy_alignment=0.68
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Intervention Type: {result.get('intervention_type', 'N/A')}\n")
    
    print("Test 3: No multiplier")
    result = detect(
        atmospheric_benefit=0.30,
        ecological_benefit=0.25,
        infrastructure_benefit=0.85,
        policy_alignment=0.40
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Status: {result['status']}")

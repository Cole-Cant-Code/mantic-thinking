"""
Social/Cultural: Catalytic Alignment Detector

Spots transformative potential when individual readiness, network bridges,
policy windows, and paradigm momentum converge.

Confluence Logic: Readiness + Bridges + Policy + Momentum = Movement Ready

Optional Overrides (Bounded):
    threshold_override: Dict of threshold overrides
        e.g., {"catalyst": 0.70, "transformative": 0.85}
    temporal_config: Dict for temporal kernel tuning (domain-restricted)
    
    NOTE: Domain weights (W) are IMMUTABLE.

Output:
    window_detected, movement_potential, recommended_action, m_score, overrides_applied
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
from core.mantic_kernel import mantic_kernel, compute_temporal_kernel
from core.validators import (
    clamp_input, format_attribution,
    clamp_threshold_override, validate_temporal_config,
    clamp_f_time, build_overrides_audit
)


WEIGHTS = [0.20, 0.30, 0.30, 0.20]
LAYER_NAMES = ['individual_readiness', 'network_bridges', 'policy_window', 'paradigm_momentum']

DEFAULT_THRESHOLDS = {
    'catalyst': 0.65,       # Catalyst threshold for movement window
    'transformative': 0.80  # Transformative potential threshold
}

DOMAIN = "social"


def detect(individual_readiness, network_bridges, policy_window, paradigm_momentum,
           f_time=1.0, threshold_override=None, temporal_config=None):
    """Detect transformative potential for movement-building."""
    
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
        clamp_input(individual_readiness, name="individual_readiness"),
        clamp_input(network_bridges, name="network_bridges"),
        clamp_input(policy_window, name="policy_window"),
        clamp_input(paradigm_momentum, name="paradigm_momentum")
    ]
    
    I = [1.0, min(1.0, 0.9 + L[1]*0.1), 1.0, 1.0]
    
    M, S, attr = mantic_kernel(WEIGHTS, L, I, f_time_clamped)
    
    catalyst_threshold = active_thresholds['catalyst']
    transformative_threshold = active_thresholds['transformative']
    
    critical_factors = [L[0], L[1], L[2]]
    catalyst = min(critical_factors)
    transformative_potential = catalyst * (1 + L[3]*0.5)
    
    window_detected = False
    movement_potential = None
    critical_mass_risk = None
    recommended_action = None
    duration_estimate = None
    mobilization_urgency = None
    
    if catalyst > catalyst_threshold:
        window_detected = True
        
        if transformative_potential > transformative_threshold and all(l > 0.75 for l in L):
            movement_potential = "TRANSFORMATIVE"
            critical_mass_risk = "Network bridges activated but window is narrow - act before policy closes"
            recommended_action = ("Mobilize immediately across all channels. Policy window + Network topology + "
                                 "Individual readiness creates rare transformative potential. Deploy resources fully.")
            duration_estimate = "Policy window typically 6-18 months; peak mobilization window 3-6 months"
            mobilization_urgency = "CRITICAL - Peak convergence now"
        elif transformative_potential > 0.70:
            movement_potential = "HIGH"
            critical_mass_risk = "Network and policy favorable but paradigm momentum still building"
            recommended_action = ("Accelerate mobilization. Prepare for rapid scaling. Window is open but "
                                 "will not remain indefinitely.")
            duration_estimate = "12-24 months sustained effort"
            mobilization_urgency = "HIGH - Mobilize within 30 days"
        else:
            movement_potential = "MODERATE"
            critical_mass_risk = "Some factors present but transformational potential limited"
            recommended_action = ("Build infrastructure. Current alignment is favorable but not exceptional. "
                                 "Prepare for future convergence.")
            duration_estimate = "2-3 years for major shift"
            mobilization_urgency = "MODERATE - Build capacity"
    
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
    
    if window_detected:
        return {
            "window_detected": True,
            "movement_potential": movement_potential,
            "catalyst_score": float(catalyst),
            "transformative_potential": float(transformative_potential),
            "critical_mass_risk": critical_mass_risk,
            "recommended_action": recommended_action,
            "duration_estimate": duration_estimate,
            "mobilization_urgency": mobilization_urgency,
            "m_score": float(M),
            "spatial_component": float(S),
            "layer_attribution": format_attribution(attr, LAYER_NAMES),
            "thresholds": active_thresholds,
            "overrides_applied": overrides_applied,
            "alignment_status": {
                "individual_readiness": float(L[0]),
                "network_bridges": float(L[1]),
                "policy_window": float(L[2]),
                "paradigm_momentum": float(L[3])
            }
        }
    
    below_threshold = [LAYER_NAMES[i] for i, l in enumerate(L) if l <= catalyst_threshold]
    
    return {
        "window_detected": False,
        "catalyst_score": float(catalyst),
        "movement_potential": "LOW",
        "limiting_factors": below_threshold,
        "m_score": float(M),
        "spatial_component": float(S),
        "status": f"Catalytic alignment not achieved. {', '.join(below_threshold)} below threshold.",
        "recommendation": "Continue base-building. Focus on strengthening network bridges and individual readiness.",
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied
    }


if __name__ == "__main__":
    print("=== Social Catalytic Alignment Detector ===\n")
    
    print("Test 1: Transformative potential")
    result = detect(
        individual_readiness=0.82,
        network_bridges=0.85,
        policy_window=0.80,
        paradigm_momentum=0.88
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Movement Potential: {result['movement_potential']}\n")
    
    print("Test 2: High potential")
    result = detect(
        individual_readiness=0.75,
        network_bridges=0.78,
        policy_window=0.72,
        paradigm_momentum=0.70
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Movement Potential: {result['movement_potential']}\n")
    
    print("Test 3: No window")
    result = detect(
        individual_readiness=0.80,
        network_bridges=0.75,
        policy_window=0.40,
        paradigm_momentum=0.70
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Limiting Factors: {result['limiting_factors']}")

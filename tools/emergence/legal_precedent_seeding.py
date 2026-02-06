"""
Legal: Precedent Seeding Optimizer

Spots windows when socio-political climate, institutional capacity,
statutory ambiguity, and circuit splits align for favorable case law establishment.

Confluence Logic: Receptive climate + ambiguity + capacity + split = ripe for precedent

Optional Overrides (Bounded):
    threshold_override: Dict of threshold overrides
        e.g., {"ripeness": 0.65, "split": 0.55}
    temporal_config: Dict for temporal kernel tuning (domain-restricted)
    
    NOTE: Domain weights (W) are IMMUTABLE.

Output:
    window_detected, precedent_opportunity, strategy, m_score, overrides_applied
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
from core.mantic_kernel import mantic_kernel, compute_temporal_kernel
from core.validators import (
    clamp_input, require_finite_inputs, format_attribution,
    clamp_threshold_override, validate_temporal_config,
    clamp_f_time, build_overrides_audit
)


WEIGHTS = [0.30, 0.20, 0.30, 0.20]
LAYER_NAMES = ['socio_political', 'institutional_capacity', 'statutory_ambiguity', 'circuit_split']

DEFAULT_THRESHOLDS = {
    'ripeness': 0.60,  # Ripeness threshold for precedent window
    'split': 0.50      # Circuit split threshold
}

DOMAIN = "legal"


def detect(socio_political_climate, institutional_capacity, statutory_ambiguity, circuit_split,
           f_time=1.0, threshold_override=None, temporal_config=None):
    """Spot windows for favorable precedent establishment."""
    
    # INPUT VALIDATION
    require_finite_inputs({
        "socio_political_climate": socio_political_climate,
        "institutional_capacity": institutional_capacity,
        "statutory_ambiguity": statutory_ambiguity,
        "circuit_split": circuit_split,
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
        clamp_input(socio_political_climate, name="socio_political_climate"),
        clamp_input(institutional_capacity, name="institutional_capacity"),
        clamp_input(statutory_ambiguity, name="statutory_ambiguity"),
        clamp_input(circuit_split, name="circuit_split")
    ]
    
    I = [1.0, 1.0, 1.0, 1.0]
    
    M, S, attr = mantic_kernel(WEIGHTS, L, I, f_time_clamped)
    
    ripeness_threshold = active_thresholds['ripeness']
    split_threshold = active_thresholds['split']
    
    climate_ambiguity_floor = min(L[0], L[2])
    ripeness = climate_ambiguity_floor * L[1]
    
    window_detected = False
    precedent_opportunity = None
    circuit_split_exploitable = None
    strategy = None
    forum_recommendation = None
    timeline = None
    
    if ripeness > ripeness_threshold and circuit_split > split_threshold:
        window_detected = True
        circuit_split_exploitable = True
        
        if ripeness > 0.80 and L[3] > 0.75:
            precedent_opportunity = "EXCEPTIONAL"
            strategy = ("File test case in most favorable circuit immediately. "
                       "Exceptional convergence of socio-political tailwinds, statutory ambiguity, "
                       "and circuit split creates Supreme Court grant likelihood. "
                       "Maximize ripple effects through amicus coordination.")
            forum_recommendation = "File in 9th or DC Circuit (depending on issue) with expedited briefing"
            timeline = "6-12 months to circuit decision, 18-24 months to potential SCOTUS"
        elif ripeness > 0.70:
            precedent_opportunity = "HIGH"
            strategy = ("Pursue test case aggressively. Socio-political climate favorable, "
                       "statutory ambiguity provides doctrinal opening, circuit split creates urgency. "
                       "Monitor parallel cases in other circuits.")
            forum_recommendation = "Forum shop for most favorable circuit with active split"
            timeline = "12-18 months to circuit decision"
        else:
            precedent_opportunity = "MODERATE"
            strategy = ("Begin test case development. Window is open but not exceptional. "
                       "Build record and coalition while conditions favorable.")
            forum_recommendation = "Select circuit with favorable precedent + active split"
            timeline = "18-24 months to decision"
    
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
            "precedent_opportunity": precedent_opportunity,
            "ripeness_score": float(ripeness),
            "circuit_split_exploitable": circuit_split_exploitable,
            "strategy": strategy,
            "forum_recommendation": forum_recommendation,
            "timeline": timeline,
            "m_score": float(M),
            "spatial_component": float(S),
            "layer_attribution": format_attribution(attr, LAYER_NAMES),
            "thresholds": active_thresholds,
            "overrides_applied": overrides_applied,
            "favorable_conditions": {
                "socio_political_receptiveness": float(L[0]),
                "statutory_ambiguity": float(L[2]),
                "institutional_capacity": float(L[1]),
                "circuit_split_strength": float(L[3])
            }
        }
    
    if L[3] <= split_threshold:
        limiting_factor = "No exploitable circuit split"
    elif L[0] <= ripeness_threshold:
        limiting_factor = "Socio-political climate not receptive"
    elif L[2] <= ripeness_threshold:
        limiting_factor = "Statutory text too clear/ambiguous"
    else:
        limiting_factor = "Insufficient institutional capacity"
    
    return {
        "window_detected": False,
        "ripeness_score": float(ripeness),
        "precedent_opportunity": "LOW",
        "circuit_split_exploitable": L[3] > split_threshold,
        "limiting_factor": limiting_factor,
        "m_score": float(M),
        "spatial_component": float(S),
        "status": f"Precedent window not yet ripe. {limiting_factor}.",
        "recommendation": "Monitor for circuit split development or socio-political shift.",
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied
    }


if __name__ == "__main__":
    print("=== Legal Precedent Seeding Optimizer ===\n")
    
    print("Test 1: Exceptional opportunity")
    result = detect(
        socio_political_climate=0.85,
        institutional_capacity=0.80,
        statutory_ambiguity=0.88,
        circuit_split=0.82
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Opportunity Level: {result['precedent_opportunity']}\n")
    
    print("Test 2: High opportunity")
    result = detect(
        socio_political_climate=0.75,
        institutional_capacity=0.70,
        statutory_ambiguity=0.78,
        circuit_split=0.72
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Opportunity Level: {result['precedent_opportunity']}\n")
    
    print("Test 3: No window")
    result = detect(
        socio_political_climate=0.80,
        institutional_capacity=0.75,
        statutory_ambiguity=0.82,
        circuit_split=0.30
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Limiting Factor: {result['limiting_factor']}")
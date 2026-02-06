"""
Healthcare: Precision Therapeutic Window Detector

Identifies rare alignment of genomic predisposition, environmental readiness,
phenotypic timing, and psychosocial engagement for maximum treatment efficacy.

Confluence Logic: All 4 layers must be favorable simultaneously (not just average)

Optional Overrides (Bounded):
    threshold_override: Dict of threshold overrides
        e.g., {"alignment": 0.70, "optimal": 0.85}
    temporal_config: Dict for temporal kernel tuning (domain-restricted)
    
    NOTE: Domain weights (W) are IMMUTABLE.

Output:
    window_detected, window_type, confidence, m_score, overrides_applied
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


WEIGHTS = [0.25, 0.25, 0.25, 0.25]
LAYER_NAMES = ['genomic', 'environmental', 'phenotypic', 'psychosocial']

DEFAULT_THRESHOLDS = {
    'alignment': 0.65,  # Confluence threshold for favorable window
    'optimal': 0.80     # Optimal window threshold
}

DOMAIN = "healthcare"


def detect(genomic_predisposition, environmental_readiness, phenotypic_timing, psychosocial_engagement, 
           f_time=1.0, threshold_override=None, temporal_config=None):
    """Detect rare alignment window for maximum therapeutic efficacy."""
    
    # INPUT VALIDATION
    require_finite_inputs({
        "genomic_predisposition": genomic_predisposition,
        "environmental_readiness": environmental_readiness,
        "phenotypic_timing": phenotypic_timing,
        "psychosocial_engagement": psychosocial_engagement,
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
        clamp_input(genomic_predisposition, name="genomic_predisposition"),
        clamp_input(environmental_readiness, name="environmental_readiness"),
        clamp_input(phenotypic_timing, name="phenotypic_timing"),
        clamp_input(psychosocial_engagement, name="psychosocial_engagement")
    ]
    
    I = [1.0, 1.0, 1.0, 1.0]
    
    M, S, attr = mantic_kernel(WEIGHTS, L, I, f_time_clamped)
    
    alignment_floor = min(L)
    alignment_threshold = active_thresholds['alignment']
    optimal_threshold = active_thresholds['optimal']
    
    window_detected = False
    window_type = None
    confidence = 0.0
    recommended_action = None
    duration_estimate = None
    limiting_factor = None
    
    # Build audit (once, before branching)
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
    
    if alignment_floor > alignment_threshold:
        window_detected = True
        
        if all(l > optimal_threshold for l in L):
            window_type = "OPTIMAL: All systems aligned for maximum efficacy"
            confidence = 0.95
            recommended_action = "Initiate treatment protocol immediately - peak window"
            duration_estimate = "48-72 hour optimal window"
        else:
            window_type = "FAVORABLE: Strong alignment across all factors"
            confidence = 0.75
            recommended_action = "Good therapeutic window - proceed with treatment"
            duration_estimate = "5-7 day favorable window"
        
        weakest_idx = int(np.argmin(L))
        limiting_factor = LAYER_NAMES[weakest_idx]
        
        return {
            "window_detected": True,
            "window_type": window_type,
            "confidence": float(confidence),
            "m_score": float(M),
            "spatial_component": float(S),
            "layer_attribution": format_attribution(attr, LAYER_NAMES),
            "alignment_floor": float(alignment_floor),
            "limiting_factor": limiting_factor,
            "recommended_action": recommended_action,
            "duration_estimate": duration_estimate,
            "thresholds": active_thresholds,
            "overrides_applied": overrides_applied,
            "layer_values": {
                "genomic": float(L[0]),
                "environmental": float(L[1]),
                "phenotypic": float(L[2]),
                "psychosocial": float(L[3])
            }
        }
    
    below_threshold = [LAYER_NAMES[i] for i, l in enumerate(L) if l <= alignment_threshold]
    
    return {
        "window_detected": False,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "alignment_floor": float(alignment_floor),
        "status": f"Layers not aligned. {', '.join(below_threshold)} below threshold.",
        "improvement_needed": below_threshold,
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied
    }


if __name__ == "__main__":
    print("=== Healthcare Precision Therapeutic Window Detector ===\n")
    
    print("Test 1: Optimal alignment (all > 0.8)")
    result = detect(
        genomic_predisposition=0.85,
        environmental_readiness=0.82,
        phenotypic_timing=0.88,
        psychosocial_engagement=0.90
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Type: {result['window_type']}")
    print(f"  Confidence: {result['confidence']}\n")
    
    print("Test 2: Favorable alignment (all > 0.65)")
    result = detect(
        genomic_predisposition=0.70,
        environmental_readiness=0.72,
        phenotypic_timing=0.68,
        psychosocial_engagement=0.75
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Type: {result['window_type']}\n")
    
    print("Test 3: Not aligned (psychosocial low)")
    result = detect(
        genomic_predisposition=0.75,
        environmental_readiness=0.80,
        phenotypic_timing=0.70,
        psychosocial_engagement=0.45
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Status: {result['status']}")
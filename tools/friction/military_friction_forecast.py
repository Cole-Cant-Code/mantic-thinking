"""
Military: Friction Forecast Engine

Identifies where tactical plans hit logistics or political constraints.

Input Layers:
    maneuver: Tactical maneuver feasibility (0-1)
    intelligence: Intelligence confidence (0-1)
    sustainment: Logistics sustainability (0-1)
    political: Political authorization level (0-1)

Optional Overrides (Bounded):
    threshold_override: Dict of threshold overrides
        e.g., {"bottleneck": 0.45, "risk_high": 0.65, "risk_medium": 0.45}
    temporal_config: Dict for temporal kernel tuning (domain-restricted)
    
    NOTE: Domain weights (W) are IMMUTABLE.

Output:
    alert, bottleneck, risk_rating, m_score, overrides_applied
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


WEIGHTS = {
    'maneuver': 0.30,
    'intelligence': 0.25,
    'sustainment': 0.25,
    'political': 0.20
}

LAYER_NAMES = ['maneuver', 'intelligence', 'sustainment', 'political']

DEFAULT_THRESHOLDS = {
    'bottleneck': 0.4,      # Bottleneck detection threshold
    'risk_high': 0.6,       # High risk threshold
    'risk_medium': 0.4      # Medium risk threshold
}

DOMAIN = "military"


def detect(maneuver, intelligence, sustainment, political, f_time=1.0,
           threshold_override=None, temporal_config=None):
    """Detect friction points in military operations."""
    
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
        clamp_input(maneuver, name="maneuver"),
        clamp_input(intelligence, name="intelligence"),
        clamp_input(sustainment, name="sustainment"),
        clamp_input(political, name="political")
    ]
    
    W = list(WEIGHTS.values())
    I = [1.0, 1.0, 1.0, 1.0]
    
    M, S, attr = mantic_kernel(W, L, I, f_time_clamped)
    
    alert = None
    bottleneck = None
    risk_rating = "low"
    
    bottleneck_threshold = active_thresholds['bottleneck']
    risk_high = active_thresholds['risk_high']
    risk_medium = active_thresholds['risk_medium']
    
    min_value = min(L)
    min_index = L.index(min_value)
    bottleneck = LAYER_NAMES[min_index]
    
    tactical_avg = (L[0] + L[1]) / 2
    support_avg = (L[2] + L[3]) / 2
    friction_gap = abs(tactical_avg - support_avg)
    
    if friction_gap > risk_high or min_value < 0.3:
        risk_rating = "high"
    elif friction_gap > risk_medium or min_value < 0.5:
        risk_rating = "medium"
    
    if bottleneck == "sustainment" and L[2] < bottleneck_threshold:
        alert = "LOGISTICS BOTTLENECK: Tactical plan viable but sustainment insufficient"
    elif bottleneck == "political" and L[3] < bottleneck_threshold:
        alert = "POLITICAL CONSTRAINT: Operation feasible but lacks political authorization/flexibility"
    elif bottleneck == "intelligence" and L[1] < bottleneck_threshold:
        alert = "INTELLIGENCE GAP: Significant unknowns in operational environment"
    elif bottleneck == "maneuver":
        alert = "TACTICAL LIMITATION: Maneuver space constrained by terrain or enemy disposition"
    elif friction_gap > risk_medium:
        alert = f"FRICTION FORECAST: {tactical_avg:.0%} tactical readiness vs {support_avg:.0%} support capability"
    
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
    
    return {
        "alert": alert,
        "bottleneck": bottleneck,
        "risk_rating": risk_rating,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "tactical_readiness": float(tactical_avg),
        "support_capability": float(support_avg),
        "friction_gap": float(friction_gap),
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied
    }


if __name__ == "__main__":
    print("=== Military Friction Forecast Engine ===\n")
    
    print("Test 1: Logistics bottleneck")
    result = detect(maneuver=0.8, intelligence=0.7, sustainment=0.3, political=0.6)
    print(f"  Alert: {result['alert']}")
    print(f"  Bottleneck: {result['bottleneck']}\n")
    
    print("Test 2: Balanced capability")
    result = detect(maneuver=0.75, intelligence=0.8, sustainment=0.7, political=0.8)
    print(f"  Alert: {result['alert']}")
    print(f"  Bottleneck: {result['bottleneck']}\n")
    
    print("Test 3: Political constraint")
    result = detect(maneuver=0.8, intelligence=0.75, sustainment=0.7, political=0.25)
    print(f"  Alert: {result['alert']}")
    print(f"  Bottleneck: {result['bottleneck']}")

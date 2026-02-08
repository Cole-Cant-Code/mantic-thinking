"""
Social/Cultural: Narrative Rupture Detector

Catches virality that outpaces institutional sense-making capacity.

Input Layers:
    individual: Individual sentiment velocity (0-1)
    network: Network propagation speed (0-1)
    institutional: Institutional response lag (0-1, higher = slower)
    cultural: Cultural archetype alignment (-1 to 1)

Optional Overrides (Bounded):
    threshold_override: Dict of threshold overrides
        e.g., {"rapid_propagation": 0.75, "institutional_lag": 0.65, "rupture": 0.55}
    temporal_config: Dict for temporal kernel tuning (domain-restricted)
    
    NOTE: Domain weights (W) are IMMUTABLE.

Output:
    alert, rupture_timing, recommended_adjustment, m_score, overrides_applied
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
    'individual': 0.25,
    'network': 0.30,
    'institutional': 0.25,
    'cultural': 0.20
}

LAYER_NAMES = ['individual', 'network', 'institutional', 'cultural']

DEFAULT_THRESHOLDS = {
    'rapid_propagation': 0.7,  # Rapid propagation threshold
    'institutional_lag': 0.6,  # Institutional lag threshold
    'rupture': 0.5             # Rupture detection threshold
}

DOMAIN = "social"


def detect(individual, network, institutional, cultural, f_time=1.0,
           threshold_override=None, temporal_config=None,
           interaction_mode="dynamic", interaction_override=None,
           interaction_override_mode="scale"):
    """Detect narrative ruptures in social/cultural systems."""
    
    # INPUT VALIDATION
    require_finite_inputs({
        "individual": individual,
        "network": network,
        "institutional": institutional,
        "cultural": cultural,
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
        clamp_input(individual, name="individual"),
        clamp_input(network, name="network"),
        clamp_input(institutional, name="institutional"),
        clamp_input(cultural, min_val=-1, max_val=1, name="cultural")
    ]
    
    L_normalized = [
        L[0],
        L[1],
        L[2],
        (L[3] + 1) / 2  # Convert -1,1 to 0,1
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
    
    M, S, attr = mantic_kernel(W, L_normalized, I, f_time_clamped)
    
    alert = None
    rupture_timing = "contained"
    recommended_adjustment = None
    
    rapid_threshold = active_thresholds['rapid_propagation']
    lag_threshold = active_thresholds['institutional_lag']
    rupture_threshold = active_thresholds['rupture']
    
    propagation_speed = (L[0] + L[1]) / 2
    institutional_capacity = 1 - L[2]
    velocity_gap = propagation_speed - institutional_capacity
    cultural_stress = abs(L[3])
    is_counter_narrative = L[3] < -0.3
    
    if velocity_gap > rupture_threshold and propagation_speed > rapid_threshold:
        rupture_timing = "imminent"
        if is_counter_narrative:
            alert = "NARRATIVE RUPTURE IMMINENT: Counter-cultural narrative spreading faster than institutional response"
            recommended_adjustment = (
                "Deploy rapid response team. Narrative is counter to cultural archetypes "
                "and spreading at {:.0%} velocity with {:.0%} institutional lag. "
                "Consider reframing rather than direct counter-messaging."
                .format(propagation_speed, L[2])
            )
        else:
            alert = "VIRALITY CRISIS: Aligned narrative outpacing institutional capacity"
            recommended_adjustment = (
                "Scale institutional response mechanisms. Positive narrative becoming "
                "uncontrollable. Establish narrative ownership before external actors co-opt."
            )
    elif velocity_gap > 0.3:
        rupture_timing = "ongoing"
        if L[2] > lag_threshold:
            alert = "SENSE-MAKING GAP: Institutional response significantly lagging narrative spread"
            recommended_adjustment = (
                "Accelerate decision cycles. Current lag of {:.0%} exceeds safe threshold. "
                "Consider delegating authority to lower levels for faster response."
                .format(L[2])
            )
        else:
            alert = "VELOCITY MISMATCH: Narrative propagation exceeding normal institutional pace"
            recommended_adjustment = "Monitor closely and prepare rapid response protocols."
    elif is_counter_narrative and L[1] > 0.6:
        rupture_timing = "ongoing"
        alert = "CULTURAL FRICTION: Counter-archetype narrative gaining network traction"
        recommended_adjustment = (
            "Assess cultural resonance. May indicate deeper cultural shift requiring "
            "narrative strategy revision rather than tactical response."
        )
    else:
        recommended_adjustment = "Current narrative management approach sufficient."
    
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
    
    layer_values_dict = {"individual": float(L[0]), "network": float(L[1]), "institutional": float(L[2]), "cultural": float(L[3])}
    layer_interactions = {
        "individual": float(I[0]),
        "network": float(I[1]),
        "institutional": float(I[2]),
        "cultural": float(I[3]),
    }
    layer_visibility = get_layer_visibility("social_narrative_rupture", WEIGHTS, layer_values_dict, layer_interactions)
    layer_coupling = compute_layer_coupling(L_normalized, LAYER_NAMES)
    
    return {
        "alert": alert,
        "rupture_timing": rupture_timing,
        "recommended_adjustment": recommended_adjustment,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "propagation_speed": float(propagation_speed),
        "institutional_capacity": float(institutional_capacity),
        "velocity_gap": float(velocity_gap),
        "cultural_alignment": float(L[3]),
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied,
        "layer_visibility": layer_visibility,
        "layer_coupling": layer_coupling
    }


if __name__ == "__main__":
    print("=== Social Narrative Rupture Detector ===\n")
    
    print("Test 1: Counter-cultural narrative spreading fast")
    result = detect(individual=0.8, network=0.9, institutional=0.7, cultural=-0.6)
    print(f"  Alert: {result['alert']}")
    print(f"  Rupture Timing: {result['rupture_timing']}\n")
    
    print("Test 2: Contained narrative")
    result = detect(individual=0.4, network=0.3, institutional=0.3, cultural=0.5)
    print(f"  Alert: {result['alert']}")
    print(f"  Rupture Timing: {result['rupture_timing']}\n")
    
    print("Test 3: Institutional lag")
    result = detect(individual=0.7, network=0.75, institutional=0.8, cultural=0.2)
    print(f"  Alert: {result['alert']}")
    print(f"  Rupture Timing: {result['rupture_timing']}")

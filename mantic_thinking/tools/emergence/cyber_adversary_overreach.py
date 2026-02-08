"""
Cybersecurity: Adversary Overreach Detector

Identifies defensive advantage windows when attacker TTPs are stretched,
geopolitically pressured, and operationally fatigued.

Confluence Logic: Attacker strained + defender hardened = counter-attack window

Optional Overrides (Bounded):
    threshold_override: Dict of threshold overrides
        e.g., {"overreach": 0.75, "hardening": 0.65}
    temporal_config: Dict for temporal kernel tuning (domain-restricted)
    
    NOTE: Domain weights (W) are IMMUTABLE.

Output:
    window_detected, attacker_state, defender_advantage, m_score, overrides_applied
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


WEIGHTS = [0.30, 0.20, 0.30, 0.20]
LAYER_NAMES = ['threat_stretch', 'geopolitical_pressure', 'operational_hardening', 'tool_reuse_fatigue']

DEFAULT_THRESHOLDS = {
    'overreach': 0.70,  # Overreach detection threshold
    'hardening': 0.60   # Defender hardening threshold
}

DOMAIN = "cyber"


def detect(threat_intel_stretch, geopolitical_pressure, operational_hardening, tool_reuse_fatigue,
           f_time=1.0, threshold_override=None, temporal_config=None):
    """Detect when attacker is vulnerable due to overextension."""
    
    # INPUT VALIDATION
    require_finite_inputs({
        "threat_intel_stretch": threat_intel_stretch,
        "geopolitical_pressure": geopolitical_pressure,
        "operational_hardening": operational_hardening,
        "tool_reuse_fatigue": tool_reuse_fatigue,
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
        clamp_input(threat_intel_stretch, name="threat_intel_stretch"),
        clamp_input(geopolitical_pressure, name="geopolitical_pressure"),
        clamp_input(operational_hardening, name="operational_hardening"),
        clamp_input(tool_reuse_fatigue, name="tool_reuse_fatigue")
    ]
    
    I = [1.0, 1.0, 1.0, 1.0]
    
    M, S, attr = mantic_kernel(WEIGHTS, L, I, f_time_clamped)
    
    overreach_threshold = active_thresholds['overreach']
    hardening_threshold = active_thresholds['hardening']
    
    attacker_strain = (L[0] + L[1] + L[3]) / 3
    
    window_detected = False
    attacker_state = "RESILIENT"
    defender_advantage = "LOW"
    recommended_action = "Continue monitoring"
    duration_estimate = None
    counter_attack_viability = None
    
    if attacker_strain > overreach_threshold and L[2] > hardening_threshold:
        window_detected = True
        
        if attacker_strain > 0.85 and L[2] > 0.75:
            defender_advantage = "CRITICAL"
            attacker_state = "SEVERELY_OVEREXTENDED"
            recommended_action = "Deploy active defense / deception / takedown. Attacker TTPs are brittle and exposed."
            duration_estimate = "24-48 hours before attacker rotates tools"
            counter_attack_viability = "High - consider attribution publication or infrastructure seizure"
        elif attacker_strain > 0.75:
            defender_advantage = "HIGH"
            attacker_state = "OVEREXTENDED"
            recommended_action = "Deploy deception and enhanced monitoring. Prepare for rapid response."
            duration_estimate = "48-72 hour window"
            counter_attack_viability = "Moderate - gather intelligence before acting"
        else:
            defender_advantage = "MODERATE"
            attacker_state = "STRESSED"
            recommended_action = "Increase monitoring. Prepare countermeasures."
            duration_estimate = "72-96 hour window"
            counter_attack_viability = "Low - maintain defensive posture"
    
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
    layer_visibility = get_layer_visibility("cyber_adversary_overreach", _weights_dict, _layer_values_dict)
    layer_coupling = compute_layer_coupling(L, LAYER_NAMES)
    
    if window_detected:
        return {
            "window_detected": True,
            "attacker_state": attacker_state,
            "defender_advantage": defender_advantage,
            "attacker_strain_score": float(attacker_strain),
            "recommended_action": recommended_action,
            "duration_estimate": duration_estimate,
            "counter_attack_viability": counter_attack_viability,
            "m_score": float(M),
            "spatial_component": float(S),
            "layer_attribution": format_attribution(attr, LAYER_NAMES),
            "thresholds": active_thresholds,
            "overrides_applied": overrides_applied,
            "strain_indicators": {
                "ttp_stretch": float(L[0]),
                "geopolitical_pressure": float(L[1]),
                "tool_fatigue": float(L[3])
            },
            "layer_visibility": layer_visibility,
            "layer_coupling": layer_coupling
        }
    
    if L[2] <= hardening_threshold:
        limiting_factor = "Defender not sufficiently hardened"
    elif attacker_strain <= overreach_threshold:
        limiting_factor = "Attacker not showing strain indicators"
    else:
        limiting_factor = "Confluence not achieved"
    
    return {
        "window_detected": False,
        "attacker_state": attacker_state,
        "defender_advantage": defender_advantage,
        "attacker_strain_score": float(attacker_strain),
        "defender_readiness": float(L[2]),
        "limiting_factor": limiting_factor,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "status": "Defensive window not yet open",
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied,
        "layer_visibility": layer_visibility,
        "layer_coupling": layer_coupling
    }


if __name__ == "__main__":
    print("=== Cyber Adversary Overreach Detector ===\n")
    
    print("Test 1: Critical overreach")
    result = detect(
        threat_intel_stretch=0.90,
        geopolitical_pressure=0.85,
        operational_hardening=0.80,
        tool_reuse_fatigue=0.88
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Attacker State: {result['attacker_state']}\n")
    
    print("Test 2: Moderate overreach")
    result = detect(
        threat_intel_stretch=0.75,
        geopolitical_pressure=0.70,
        operational_hardening=0.75,
        tool_reuse_fatigue=0.72
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Attacker State: {result['attacker_state']}\n")
    
    print("Test 3: No window")
    result = detect(
        threat_intel_stretch=0.85,
        geopolitical_pressure=0.80,
        operational_hardening=0.45,
        tool_reuse_fatigue=0.75
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Limiting Factor: {result['limiting_factor']}")

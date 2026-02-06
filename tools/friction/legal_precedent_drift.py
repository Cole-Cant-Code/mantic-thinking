"""
Legal: Precedent Drift Alert

Warns when judicial philosophy shifts threaten current precedent-based strategies.

Input Layers:
    black_letter: Statutory text alignment (0-1)
    precedent: Precedent consistency (0-1)
    operational: Practical implementation feasibility (0-1)
    socio_political: Social/political context (-1 to 1)

Optional Overrides (Bounded):
    threshold_override: Dict of threshold overrides
        e.g., {"drift": 0.45, "precedent_weak": 0.35}
    temporal_config: Dict for temporal kernel tuning (domain-restricted)
    
    NOTE: Domain weights (W) are IMMUTABLE.

Output:
    alert, drift_direction, strategy_pivot, m_score, overrides_applied
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


WEIGHTS = {
    'black_letter': 0.30,
    'precedent': 0.35,
    'operational': 0.20,
    'socio_political': 0.15
}

LAYER_NAMES = ['black_letter', 'precedent', 'operational', 'socio_political']

DEFAULT_THRESHOLDS = {
    'drift': 0.4,          # Drift detection threshold
    'precedent_weak': 0.3  # Weak precedent threshold
}

DOMAIN = "legal"


def detect(black_letter, precedent, operational, socio_political, f_time=1.0,
           threshold_override=None, temporal_config=None):
    """Detect precedent drift and judicial philosophy shifts."""
    
    # INPUT VALIDATION
    require_finite_inputs({
        "black_letter": black_letter,
        "precedent": precedent,
        "operational": operational,
        "socio_political": socio_political,
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
        clamp_input(black_letter, name="black_letter"),
        clamp_input(precedent, name="precedent"),
        clamp_input(operational, name="operational"),
        clamp_input(socio_political, min_val=-1, max_val=1, name="socio_political")
    ]
    
    L_normalized = [
        L[0],
        L[1],
        L[2],
        (L[3] + 1) / 2  # Convert -1,1 to 0,1
    ]
    
    W = list(WEIGHTS.values())
    I = [1.0, 1.0, 1.0, 1.0]
    
    M, S, attr = mantic_kernel(W, L_normalized, I, f_time_clamped)
    
    alert = None
    drift_direction = "stable"
    strategy_pivot = None
    
    drift_threshold = active_thresholds['drift']
    precedent_weak = active_thresholds['precedent_weak']
    
    weak_precedent = L[1] < precedent_weak
    statutory_precedent_gap = abs(L[0] - L[1])
    
    if L[3] > 0.5:
        drift_direction = "right"
    elif L[3] < -0.5:
        drift_direction = "left"
    elif abs(L[3]) > 0.3:
        drift_direction = "fragmenting"
    
    if weak_precedent and statutory_precedent_gap > drift_threshold:
        alert = "PRECEDENT CRISIS: Statutory interpretation diverging from established precedent"
        if drift_direction == "right":
            strategy_pivot = (
                "Shift to textualist/originalist arguments. Precedent-based strategy vulnerable. "
                "Emphasize black letter law over case law."
            )
        elif drift_direction == "left":
            strategy_pivot = (
                "Emphasize purposive interpretation and policy outcomes. Traditional precedent "
                "analysis may be overridden by equity considerations."
            )
        else:
            strategy_pivot = (
                "Judicial instability detected. Consider settlement or alternative dispute resolution. "
                "Precedent value diminished."
            )
    elif weak_precedent:
        alert = "PRECEDENT DRIFT: Established case law losing persuasive authority"
        strategy_pivot = (
            "Strengthen statutory arguments. Have backup theories not dependent on contested precedents. "
            "Monitor appellate trends."
        )
    elif statutory_precedent_gap > drift_threshold:
        alert = "INTERPRETIVE CONFLICT: Statutory text and precedent on diverging paths"
        strategy_pivot = (
            "Prepare for certiorari. Circuit split likely. Develop arguments for both textualist "
            "and purposive frameworks."
        )
    elif drift_direction != "stable" and L[1] < 0.5:
        alert = f"PHILOSOPHICAL SHIFT: {drift_direction.capitalize()}ward drift threatening precedent stability"
        strategy_pivot = (
            "Reassess forum selection. Some jurisdictions becoming less favorable to precedent-based arguments. "
            "Consider legislative solution if judicial path uncertain."
        )
    else:
        strategy_pivot = "Current precedent-based strategy remains sound."
    
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
        "drift_direction": drift_direction,
        "strategy_pivot": strategy_pivot,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "socio_political_raw": float(L[3]),
        "precedent_strength": float(L[1]),
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied
    }


if __name__ == "__main__":
    print("=== Legal Precedent Drift Alert ===\n")
    
    print("Test 1: Precedent crisis + rightward drift")
    result = detect(black_letter=0.8, precedent=0.3, operational=0.7, socio_political=0.6)
    print(f"  Alert: {result['alert']}")
    print(f"  Drift Direction: {result['drift_direction']}\n")
    
    print("Test 2: Stable precedent")
    result = detect(black_letter=0.75, precedent=0.8, operational=0.7, socio_political=0.1)
    print(f"  Alert: {result['alert']}")
    print(f"  Drift Direction: {result['drift_direction']}\n")
    
    print("Test 3: Leftward drift")
    result = detect(black_letter=0.3, precedent=0.7, operational=0.6, socio_political=-0.6)
    print(f"  Alert: {result['alert']}")
    print(f"  Drift Direction: {result['drift_direction']}")
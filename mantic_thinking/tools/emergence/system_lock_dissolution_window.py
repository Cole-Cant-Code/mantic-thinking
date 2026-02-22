"""
System Lock: Dissolution Window Detector (Emergence)

Detects opportunity windows where autonomy momentum, alternative readiness,
and control vulnerability converge to break lock-in patterns.

Input Layers:
    autonomy_momentum: Individual agency growth (0-1)
    alternative_readiness: Viability of alternatives (0-1)
    control_vulnerability: Fragility in concentrated control (0-1)
    pattern_flexibility: Structural adaptability / recursion weakening (0-1)

Optional Overrides (Bounded):
    threshold_override: Dict of threshold overrides
        e.g., {"dissolution_forming": 0.55, "dissolution_window": 0.75}
    temporal_config: Dict for temporal kernel tuning (domain-restricted)

Output:
    window_detected, window_type, catalyst_score, m_score, overrides_applied
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
    clamp_input,
    require_finite_inputs,
    format_attribution,
    clamp_threshold_override,
    validate_temporal_config,
    clamp_f_time,
    build_overrides_audit,
    compute_layer_coupling,
    resolve_interaction_coefficients,
)
from mantic_thinking.mantic.introspection import get_layer_visibility


WEIGHTS = [0.20, 0.30, 0.30, 0.20]
LAYER_NAMES = [
    "autonomy_momentum",
    "alternative_readiness",
    "control_vulnerability",
    "pattern_flexibility",
]

DEFAULT_THRESHOLDS = {
    "dissolution_forming": 0.50,
    "dissolution_window": 0.70,
}

DOMAIN = "system_lock"


def _sustainability_assessment(pattern_flexibility):
    if pattern_flexibility >= 0.75:
        return "Durable: pattern flexibility is high; gains are likely to persist."
    if pattern_flexibility >= 0.50:
        return "Moderate: gains are possible but require reinforcement to hold."
    return "Fragile: low flexibility means lock patterns may reassert quickly."


def detect(
    autonomy_momentum,
    alternative_readiness,
    control_vulnerability,
    pattern_flexibility,
    f_time=1.0,
    threshold_override=None,
    temporal_config=None,
    interaction_mode="dynamic",
    interaction_override=None,
    interaction_override_mode="scale",
):
    """Detect system-lock dissolution windows."""

    # INPUT VALIDATION
    require_finite_inputs(
        {
            "autonomy_momentum": autonomy_momentum,
            "alternative_readiness": alternative_readiness,
            "control_vulnerability": control_vulnerability,
            "pattern_flexibility": pattern_flexibility,
        }
    )

    # OVERRIDES PROCESSING
    threshold_info = {}
    active_thresholds = DEFAULT_THRESHOLDS.copy()
    ignored_threshold_keys = []

    if threshold_override and isinstance(threshold_override, dict):
        for key, requested in threshold_override.items():
            if key in DEFAULT_THRESHOLDS:
                clamped_val, _, info = clamp_threshold_override(
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
                    "reason": "kernel_type required and must be allowed for domain",
                }
        if "t" not in temporal_validated:
            if "t" not in temporal_rejected:
                temporal_rejected["t"] = {
                    "requested": temporal_config.get("t"),
                    "reason": "t required for temporal_config",
                }
        if "kernel_type" in temporal_validated and "t" in temporal_validated:
            f_time = compute_temporal_kernel(**temporal_validated)
            temporal_applied = temporal_validated

    f_time_clamped, _, f_time_info = clamp_f_time(f_time)

    # CORE DETECTION
    L = [
        clamp_input(autonomy_momentum, name="autonomy_momentum"),
        clamp_input(alternative_readiness, name="alternative_readiness"),
        clamp_input(control_vulnerability, name="control_vulnerability"),
        clamp_input(pattern_flexibility, name="pattern_flexibility"),
    ]

    # Dynamic readiness boost when control vulnerability is high.
    readiness_boost = L[2] * 0.3
    I_base = [1.0, 1.0, 1.0, 1.0]
    I_dynamic = [1.0, min(1.5, 1.0 + readiness_boost), 1.0, 1.0]

    I, interaction_audit = resolve_interaction_coefficients(
        LAYER_NAMES,
        I_base=I_base,
        I_dynamic=I_dynamic,
        interaction_mode=interaction_mode,
        interaction_override=interaction_override,
        interaction_override_mode=interaction_override_mode,
    )

    M, S, attr = mantic_kernel(WEIGHTS, L, I, f_time_clamped)

    dissolution_forming = active_thresholds["dissolution_forming"]
    dissolution_window = active_thresholds["dissolution_window"]

    catalyst = min(L[0], L[1], L[2])

    window_detected = False
    window_type = None
    recommended_action = None

    if catalyst > dissolution_forming:
        window_detected = True

        if all(v > dissolution_window for v in [L[0], L[1], L[2]]) and L[3] > 0.6:
            window_type = "STRUCTURAL_DISSOLUTION"
            recommended_action = (
                "Execute structural transition now: accelerate migration pathways, open interoperability, "
                "and lock in governance changes before coherence decays."
            )
        elif L[1] > dissolution_window and L[2] > dissolution_forming:
            window_type = "COMPETITIVE_DISPLACEMENT"
            recommended_action = (
                "Scale alternatives aggressively while concentrated control is vulnerable. "
                "Focus on switching costs, distribution, and reliability proofs."
            )
        else:
            window_type = "EARLY_DISSOLUTION"
            recommended_action = (
                "Build transition infrastructure now. Momentum is forming but still reversible without coordinated execution."
            )

    # Build audit
    threshold_clamped_any = any(
        info.get("was_clamped", False) for info in threshold_info.values()
    ) if threshold_info else False

    threshold_audit_info = None
    if threshold_info:
        threshold_audit_info = {
            "overrides": {
                key: {
                    "requested": info.get("requested"),
                    "used": info.get("used"),
                    "was_clamped": info.get("was_clamped", False),
                }
                for key, info in threshold_info.items()
            },
            "was_clamped": threshold_clamped_any,
            "ignored_keys": ignored_threshold_keys if ignored_threshold_keys else None,
        }

    overrides_applied = build_overrides_audit(
        threshold_overrides=threshold_override if threshold_override else None,
        temporal_config=temporal_config if temporal_config else None,
        threshold_info=threshold_audit_info,
        temporal_validated=temporal_applied,
        temporal_rejected=temporal_rejected if temporal_rejected else None,
        temporal_clamped=temporal_clamped if temporal_clamped else None,
        f_time_info=f_time_info,
        interaction=interaction_audit,
    )

    _weights_dict = dict(zip(LAYER_NAMES, WEIGHTS))
    _layer_values_dict = dict(zip(LAYER_NAMES, L))
    _layer_interactions = dict(zip(LAYER_NAMES, I))
    layer_visibility = get_layer_visibility(
        "system_lock_dissolution_window",
        _weights_dict,
        _layer_values_dict,
        _layer_interactions,
    )
    layer_coupling = compute_layer_coupling(L, LAYER_NAMES)

    if window_detected:
        return {
            "window_detected": True,
            "window_type": window_type,
            "dissolution_sustainability": _sustainability_assessment(L[3]),
            "recommended_action": recommended_action,
            "catalyst_score": float(catalyst),
            "m_score": float(M),
            "spatial_component": float(S),
            "layer_attribution": format_attribution(attr, LAYER_NAMES),
            "thresholds": active_thresholds,
            "overrides_applied": overrides_applied,
            "layer_visibility": layer_visibility,
            "layer_coupling": layer_coupling,
        }

    below_threshold = [
        LAYER_NAMES[i] for i, value in enumerate([L[0], L[1], L[2]]) if value <= dissolution_forming
    ]

    return {
        "window_detected": False,
        "catalyst_score": float(catalyst),
        "limiting_factors": below_threshold,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "status": "Dissolution window not yet formed.",
        "recommendation": "Increase autonomy momentum, alternative readiness, and control vulnerability alignment.",
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied,
        "layer_visibility": layer_visibility,
        "layer_coupling": layer_coupling,
    }


if __name__ == "__main__":
    print("=== System Lock Dissolution Window Detector ===\\n")
    result = detect(
        autonomy_momentum=0.6,
        alternative_readiness=0.7,
        control_vulnerability=0.65,
        pattern_flexibility=0.6,
    )
    print(f"Window detected: {result['window_detected']}")
    print(f"M-score: {result['m_score']:.3f}")

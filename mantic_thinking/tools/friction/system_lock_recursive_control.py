"""
System Lock: Recursive Control Detector (Friction)

Detects value-asymmetry lock states where concentrated control and recursive
reinforcement outpace individual and collective agency.

Input Layers:
    agent_autonomy: Individual agency and choice diversity (0-1)
    collective_capacity: Alternative system viability (0-1)
    concentration_control: Dominance/concentration pressure (0-1)
    recursive_depth: Intervention absorption / recursion depth (0-1)

Optional Overrides (Bounded):
    threshold_override: Dict of threshold overrides
        e.g., {"asymmetry_warning": 0.42, "lock_active": 0.55}
    temporal_config: Dict for temporal kernel tuning (domain-restricted)

Output:
    alert, lock_phase, severity, m_score, overrides_applied
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


WEIGHTS = {
    "agent_autonomy": 0.30,
    "collective_capacity": 0.25,
    "concentration_control": 0.25,
    "recursive_depth": 0.20,
}

LAYER_NAMES = [
    "agent_autonomy",
    "collective_capacity",
    "concentration_control",
    "recursive_depth",
]

DEFAULT_THRESHOLDS = {
    "asymmetry_warning": 0.40,
    "lock_active": 0.52,
    "lock_irreversible": 0.72,
}

DOMAIN = "system_lock"


def _severity_band(score):
    if score < 0.25:
        return "low"
    if score < 0.50:
        return "moderate"
    if score < 0.75:
        return "high"
    return "critical"


def detect(
    agent_autonomy,
    collective_capacity,
    concentration_control,
    recursive_depth,
    f_time=1.0,
    threshold_override=None,
    temporal_config=None,
    interaction_mode="dynamic",
    interaction_override=None,
    interaction_override_mode="scale",
):
    """Detect recursive control lock states in socio-technical systems."""

    # INPUT VALIDATION
    require_finite_inputs(
        {
            "agent_autonomy": agent_autonomy,
            "collective_capacity": collective_capacity,
            "concentration_control": concentration_control,
            "recursive_depth": recursive_depth,
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
        clamp_input(agent_autonomy, name="agent_autonomy"),
        clamp_input(collective_capacity, name="collective_capacity"),
        clamp_input(concentration_control, name="concentration_control"),
        clamp_input(recursive_depth, name="recursive_depth"),
    ]

    W = list(WEIGHTS.values())

    # Dynamic lock amplification: when concentration exceeds autonomy,
    # recursive reinforcement gets stronger.
    lock_amplification = max(0.0, L[2] - L[0])
    I_base = [1.0, 1.0, 1.0, 1.0]
    I_dynamic = [1.0, 1.0, 1.0, min(1.5, 1.0 + lock_amplification)]

    I, interaction_audit = resolve_interaction_coefficients(
        LAYER_NAMES,
        I_base=I_base,
        I_dynamic=I_dynamic,
        interaction_mode=interaction_mode,
        interaction_override=interaction_override,
        interaction_override_mode=interaction_override_mode,
    )

    M, S, attr = mantic_kernel(W, L, I, f_time_clamped)

    asymmetry_ratio = L[2] / max(L[0], 0.01)
    lock_signal = ((L[2] + L[3]) / 2.0) - ((L[0] + L[1]) / 2.0)

    asymmetry_warning = active_thresholds["asymmetry_warning"]
    lock_active = active_thresholds["lock_active"]
    lock_irreversible = active_thresholds["lock_irreversible"]

    if M < asymmetry_warning:
        lock_phase = "pre_rigidity"
    elif M < lock_active:
        lock_phase = "rigidity"
    elif M < lock_irreversible:
        if lock_signal > 0 and asymmetry_ratio >= 1.5:
            lock_phase = "lock_active"
        else:
            lock_phase = "rigidity"
    else:
        if lock_signal > 0.2 and asymmetry_ratio >= 2.0:
            lock_phase = "lock_critical"
        else:
            lock_phase = "lock_active"

    base_severity = float(np.clip((M - asymmetry_warning) / (1.0 - asymmetry_warning), 0.0, 1.0))
    structure_boost = max(0.0, lock_signal) * 0.25 + max(0.0, asymmetry_ratio - 1.0) * 0.10
    severity = float(np.clip(base_severity + structure_boost, 0.0, 1.0))
    severity_band = _severity_band(severity)

    if recursive_depth >= 0.75 and lock_signal > 0.2:
        recursion_assessment = "Deep recursion likely absorbing interventions into self-reinforcing control loops."
    elif recursive_depth >= 0.55:
        recursion_assessment = "Recursive reinforcement present; interventions may be partially absorbed."
    else:
        recursion_assessment = "Recursion remains shallow enough for direct interventions to hold."

    alert = None
    recommended_adjustment = "Monitor lock signals and maintain alternative capacity."

    if lock_phase == "lock_critical":
        alert = "LOCK CRITICAL: Concentration and recursion are reinforcing at system-preserving depth."
        recommended_adjustment = (
            "Shift to structural levers (distribution defaults, policy constraints, interoperability mandates) "
            "instead of messaging-only interventions."
        )
    elif lock_phase == "lock_active":
        alert = "LOCK ACTIVE: Value asymmetry and recursive control are now self-reinforcing."
        recommended_adjustment = (
            "Prioritize migration pathways and collective alternatives before recursion deepens."
        )
    elif lock_phase == "rigidity" and (asymmetry_ratio >= 1.2 or lock_signal > 0):
        alert = "RIGIDITY RISING: Control concentration is outpacing autonomy and collective adaptation."
        recommended_adjustment = (
            "Intervene early by strengthening collective capacity and reducing concentration bottlenecks."
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

    layer_values_dict = {
        "agent_autonomy": float(L[0]),
        "collective_capacity": float(L[1]),
        "concentration_control": float(L[2]),
        "recursive_depth": float(L[3]),
    }
    layer_interactions = {
        "agent_autonomy": float(I[0]),
        "collective_capacity": float(I[1]),
        "concentration_control": float(I[2]),
        "recursive_depth": float(I[3]),
    }

    layer_visibility = get_layer_visibility(
        "system_lock_recursive_control", WEIGHTS, layer_values_dict, layer_interactions
    )
    layer_coupling = compute_layer_coupling(L, LAYER_NAMES)

    return {
        "alert": alert,
        "severity": severity,
        "severity_band": severity_band,
        "lock_phase": lock_phase,
        "asymmetry_ratio": float(asymmetry_ratio),
        "lock_signal": float(lock_signal),
        "recursion_assessment": recursion_assessment,
        "recommended_adjustment": recommended_adjustment,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied,
        "layer_visibility": layer_visibility,
        "layer_coupling": layer_coupling,
    }


if __name__ == "__main__":
    print("=== System Lock Recursive Control Detector ===\\n")
    result = detect(
        agent_autonomy=0.2,
        collective_capacity=0.3,
        concentration_control=0.8,
        recursive_depth=0.7,
    )
    print(f"Phase: {result['lock_phase']}")
    print(f"Alert: {result['alert']}")
    print(f"M-score: {result['m_score']:.3f}")

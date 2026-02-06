"""
Plan: Alignment Window Detector

Identifies when all four planning layers achieve sufficient readiness
for plan execution — domain-agnostic planning alignment detection.

Layers (Planning Translation):
    immediate_actions: Micro — concrete next steps, resources, blockers (0-1)
    coordination:      Meso — dependencies, sequencing, team alignment (0-1)
    constraints:       Macro — system constraints, strategic alignment (0-1)
    adaptation:        Meta — lessons learned, pivot readiness, assumptions (0-1)

Confluence Logic: All 4 layers must be favorable simultaneously

Optional Overrides (Bounded):
    threshold_override: Dict of threshold overrides
        e.g., {"readiness": 0.55, "optimal": 0.75, "critical_gap": 0.35}
    temporal_config: Dict for temporal kernel tuning (domain-restricted)

    NOTE: Domain weights (W) are IMMUTABLE.

Output:
    plan_ready, readiness_tier, m_score, alignment_floor, balance_score,
    limiting_factor, critical_gaps, recommended_action, overrides_applied
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
LAYER_NAMES = ['immediate_actions', 'coordination', 'constraints', 'adaptation']

DEFAULT_THRESHOLDS = {
    'readiness': 0.60,       # Minimum per-layer value for plan readiness
    'optimal': 0.80,         # All layers above this = optimal plan
    'critical_gap': 0.40,    # Layer below this = critical weakness
}

DOMAIN = "planning"


def detect(immediate_actions, coordination, constraints, adaptation,
           f_time=1.0, threshold_override=None, temporal_config=None):
    """Detect plan alignment windows across four planning layers."""

    # INPUT VALIDATION
    require_finite_inputs({
        "immediate_actions": immediate_actions,
        "coordination": coordination,
        "constraints": constraints,
        "adaptation": adaptation,
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
        clamp_input(immediate_actions, name="immediate_actions"),
        clamp_input(coordination, name="coordination"),
        clamp_input(constraints, name="constraints"),
        clamp_input(adaptation, name="adaptation")
    ]

    I = [1.0, 1.0, 1.0, 1.0]

    M, S, attr = mantic_kernel(WEIGHTS, L, I, f_time_clamped)

    # PLAN-SPECIFIC DETECTION LOGIC
    readiness_threshold = active_thresholds['readiness']
    optimal_threshold = active_thresholds['optimal']
    critical_gap_threshold = active_thresholds['critical_gap']

    alignment_floor = min(L)
    weakest_idx = int(np.argmin(L))
    limiting_factor = LAYER_NAMES[weakest_idx]

    critical_gaps = [LAYER_NAMES[i] for i, l in enumerate(L) if l < critical_gap_threshold]

    valid_L = [l for l in L if not np.isnan(l)]
    balance_score = float(1.0 - np.std(valid_L)) if len(valid_L) > 1 else 0.0

    plan_ready = False
    readiness_tier = "NOT_READY"
    recommended_action = None

    if all(l > optimal_threshold for l in L):
        plan_ready = True
        readiness_tier = "OPTIMAL"
        recommended_action = (
            "Execute with full confidence. All planning dimensions are strongly aligned. "
            f"Monitor '{limiting_factor}' for drift."
        )
    elif alignment_floor > readiness_threshold:
        plan_ready = True
        readiness_tier = "READY"
        recommended_action = (
            f"Execute with active monitoring. Limiting factor is '{limiting_factor}' "
            f"at {L[weakest_idx]:.2f}. Establish checkpoints to detect degradation."
        )
    elif alignment_floor > critical_gap_threshold:
        plan_ready = False
        readiness_tier = "CONDITIONAL"
        below_ready = [LAYER_NAMES[i] for i, l in enumerate(L) if l <= readiness_threshold]
        recommended_action = (
            f"Address gaps before full execution: {', '.join(below_ready)}. "
            "Consider phased rollout starting with strongest layers."
        )
    else:
        plan_ready = False
        readiness_tier = "NOT_READY"
        recommended_action = (
            f"Critical gaps in: {', '.join(critical_gaps)}. "
            "Plan requires significant strengthening before execution. "
            "Prioritize the weakest layer first."
        )

    # BUILD AUDIT
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

    # RETURN
    result = {
        "plan_ready": plan_ready,
        "readiness_tier": readiness_tier,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "alignment_floor": float(alignment_floor),
        "balance_score": balance_score,
        "limiting_factor": limiting_factor,
        "critical_gaps": critical_gaps,
        "recommended_action": recommended_action,
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied,
        "layer_values": {
            "immediate_actions": float(L[0]),
            "coordination": float(L[1]),
            "constraints": float(L[2]),
            "adaptation": float(L[3])
        }
    }

    if not plan_ready:
        below_threshold = [LAYER_NAMES[i] for i, l in enumerate(L) if l <= readiness_threshold]
        result["improvement_needed"] = below_threshold

    return result


if __name__ == "__main__":
    print("=== Plan Alignment Window Detector ===\n")

    print("Test 1: Optimal plan (all layers > 0.80)")
    result = detect(
        immediate_actions=0.85,
        coordination=0.82,
        constraints=0.88,
        adaptation=0.81
    )
    print(f"  Plan Ready: {result['plan_ready']}")
    print(f"  Tier: {result['readiness_tier']}")
    print(f"  M-Score: {result['m_score']:.3f}")
    print(f"  Balance: {result['balance_score']:.3f}")
    print(f"  Limiting Factor: {result['limiting_factor']}\n")

    print("Test 2: Ready plan (all layers > 0.60)")
    result = detect(
        immediate_actions=0.75,
        coordination=0.65,
        constraints=0.70,
        adaptation=0.62
    )
    print(f"  Plan Ready: {result['plan_ready']}")
    print(f"  Tier: {result['readiness_tier']}")
    print(f"  M-Score: {result['m_score']:.3f}")
    print(f"  Limiting Factor: {result['limiting_factor']}\n")

    print("Test 3: Conditional plan (gaps but no critical)")
    result = detect(
        immediate_actions=0.80,
        coordination=0.70,
        constraints=0.45,
        adaptation=0.55
    )
    print(f"  Plan Ready: {result['plan_ready']}")
    print(f"  Tier: {result['readiness_tier']}")
    print(f"  Improvement Needed: {result.get('improvement_needed', 'N/A')}\n")

    print("Test 4: Not ready (critical gaps)")
    result = detect(
        immediate_actions=0.85,
        coordination=0.75,
        constraints=0.30,
        adaptation=0.20
    )
    print(f"  Plan Ready: {result['plan_ready']}")
    print(f"  Tier: {result['readiness_tier']}")
    print(f"  Critical Gaps: {result['critical_gaps']}")
    print(f"  Recommended: {result['recommended_action']}")
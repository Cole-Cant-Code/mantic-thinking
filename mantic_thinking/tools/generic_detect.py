"""
Generic Mantic Detector

Exposes the Mantic kernel for arbitrary caller-defined domains.
The caller specifies layer names, weights, and values — the kernel,
governance (bounded overrides, interaction clamping, f_time limits),
and audit trail remain identical to the 14 hardcoded domain tools.

Domain Registration (Option D):
    The caller "registers" a novel domain by declaring:
    - domain_name: A unique identifier (cannot collide with existing 7 domains)
    - layer_names: 3-6 layer labels
    - weights: Must sum to 1.0
    - layer_values: One value per layer (0-1)
    - mode: "friction" or "emergence"

    These are validated before the kernel runs.  Output includes a
    calibration block documenting that this is a user-defined domain.

Temporal Config:
    The generic tool is registered in DOMAIN_KERNEL_ALLOWLIST with all 7
    valid kernel types.  Unknown kernel types are properly rejected.
    The rest of the temporal governance (alpha bounds, f_time clamp) still
    applies.

Layer Hierarchy:
    Caller can optionally provide layer_hierarchy (dict mapping layer
    names to Micro/Meso/Macro/Meta).  If omitted, layer visibility
    is skipped (returns None) — same behavior as an unmapped tool in
    the existing hierarchy module.
"""

import sys
import os

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

# Existing hardcoded domains — generic tool cannot shadow these
_RESERVED_DOMAINS = frozenset([
    "healthcare", "finance", "cyber", "climate", "legal", "military", "social"
])

# Layer count bounds
_MIN_LAYERS = 3
_MAX_LAYERS = 6

# Generic domain uses full kernel allowlist (all types permitted)
_GENERIC_DOMAIN_KEY = "generic"


def _validate_registration(domain_name, layer_names, weights, layer_values, mode):
    """
    Validate domain registration inputs.

    Raises:
        ValueError: On any validation failure with a clear message.
    """
    # Domain name
    if not domain_name or not isinstance(domain_name, str):
        raise ValueError("domain_name must be a non-empty string")
    if domain_name.lower() in _RESERVED_DOMAINS:
        raise ValueError(
            f"domain_name '{domain_name}' collides with a built-in domain. "
            f"Reserved: {sorted(_RESERVED_DOMAINS)}"
        )

    # Mode
    if mode not in ("friction", "emergence"):
        raise ValueError(f"mode must be 'friction' or 'emergence', got '{mode}'")

    # Layer names
    if not isinstance(layer_names, (list, tuple)):
        raise ValueError("layer_names must be a list of strings")
    if not (_MIN_LAYERS <= len(layer_names) <= _MAX_LAYERS):
        raise ValueError(
            f"layer_names must have {_MIN_LAYERS}-{_MAX_LAYERS} entries, got {len(layer_names)}"
        )
    if len(set(layer_names)) != len(layer_names):
        raise ValueError("layer_names must be unique")
    for name in layer_names:
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Each layer name must be a non-empty string, got {name!r}")

    # Weights
    if not isinstance(weights, (list, tuple)):
        raise ValueError("weights must be a list of numbers")
    if len(weights) != len(layer_names):
        raise ValueError(
            f"weights length ({len(weights)}) must match layer_names length ({len(layer_names)})"
        )
    for i, w in enumerate(weights):
        try:
            wf = float(w)
        except (TypeError, ValueError):
            raise ValueError(f"weights[{i}] must be a number, got {type(w).__name__}")
        if not np.isfinite(wf) or wf < 0:
            raise ValueError(f"weights[{i}] must be a non-negative finite number, got {wf}")
    weight_sum = sum(float(w) for w in weights)
    if not (0.95 <= weight_sum <= 1.05):
        raise ValueError(f"weights must sum to 1.0 (got {weight_sum:.4f})")

    # Layer values
    if not isinstance(layer_values, (list, tuple)):
        raise ValueError("layer_values must be a list of numbers")
    if len(layer_values) != len(layer_names):
        raise ValueError(
            f"layer_values length ({len(layer_values)}) must match layer_names length ({len(layer_names)})"
        )


def detect(domain_name, layer_names, weights, layer_values, mode="friction",
           f_time=1.0, threshold_override=None, temporal_config=None,
           interaction_mode="dynamic", interaction_override=None,
           interaction_override_mode="scale",
           layer_hierarchy=None,
           detection_threshold=0.4):
    """
    Run Mantic detection on a caller-defined domain.

    Args:
        domain_name: Unique domain label (cannot shadow built-in 7 domains)
        layer_names: List of 3-6 layer name strings
        weights: List of floats summing to 1.0 (one per layer)
        layer_values: List of floats 0-1 (one per layer)
        mode: "friction" (divergence detection) or "emergence" (alignment detection)
        f_time: Temporal kernel multiplier (default 1.0)
        threshold_override: Dict of threshold overrides (bounded internally)
        temporal_config: Dict for temporal kernel (bounded internally)
        interaction_mode: "dynamic" or "base"
        interaction_override: Per-layer I overrides (list or dict)
        interaction_override_mode: "scale" or "replace"
        layer_hierarchy: Optional dict mapping layer names to Micro/Meso/Macro/Meta
        detection_threshold: Threshold for friction range / emergence alignment floor (default 0.4)

    Returns:
        dict with m_score, layer_attribution, overrides_applied, calibration, etc.
    """
    # =========================================================================
    # DOMAIN REGISTRATION VALIDATION
    # =========================================================================
    _validate_registration(domain_name, layer_names, weights, layer_values, mode)

    n_layers = len(layer_names)

    # Validate layer values are finite
    value_dict = {layer_names[i]: layer_values[i] for i in range(n_layers)}
    require_finite_inputs(value_dict)

    # =========================================================================
    # OVERRIDE PROCESSING (same governance as hardcoded tools)
    # =========================================================================
    DEFAULT_THRESHOLDS = {"detection": detection_threshold}

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

    # Temporal config — generic domain allows ALL kernel types
    temporal_validated, temporal_rejected, temporal_clamped = None, {}, {}
    temporal_applied = None
    if temporal_config and isinstance(temporal_config, dict):
        temporal_validated, temporal_rejected, temporal_clamped = validate_temporal_config(
            temporal_config, domain=_GENERIC_DOMAIN_KEY  # "generic" — allowlist includes all 7 kernel types
        )
        if "kernel_type" not in temporal_validated:
            if "kernel_type" not in temporal_rejected:
                temporal_rejected["kernel_type"] = {
                    "requested": temporal_config.get("kernel_type"),
                    "reason": "kernel_type required and must be a valid kernel type"
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

    # =========================================================================
    # CORE DETECTION (same kernel, same governance)
    # =========================================================================
    L = [clamp_input(layer_values[i], name=layer_names[i]) for i in range(n_layers)]
    W_raw = [float(w) for w in weights]
    # Normalize to exactly 1.0 — closes the gap between registration tolerance
    # (0.95-1.05) and kernel precision (atol=1e-6).
    w_sum = sum(W_raw)
    W = [w / w_sum for w in W_raw]

    I_base = [1.0] * n_layers
    I_dynamic = I_base

    # Validate list-based interaction_override length matches n_layers.
    # The hardcoded validator expects exactly 4; for generic domains with
    # N≠4 layers we convert list→dict so the named-key path handles it.
    if interaction_override is not None and isinstance(interaction_override, (list, tuple)):
        if len(interaction_override) != n_layers:
            raise ValueError(
                f"interaction_override list length ({len(interaction_override)}) "
                f"must match layer count ({n_layers})"
            )
        # Convert positional list to named dict for N-layer compatibility
        if n_layers != 4:
            interaction_override = {
                layer_names[i]: interaction_override[i]
                for i in range(n_layers)
            }

    I, interaction_audit = resolve_interaction_coefficients(
        layer_names,
        I_base=I_base,
        I_dynamic=I_dynamic,
        interaction_mode=interaction_mode,
        interaction_override=interaction_override,
        interaction_override_mode=interaction_override_mode,
    )

    M, S, attr = mantic_kernel(W, L, I, f_time_clamped)

    # =========================================================================
    # MODE-SPECIFIC DETECTION LOGIC
    # =========================================================================
    detection_thresh = active_thresholds["detection"]

    if mode == "friction":
        # Friction: detect cross-layer divergence via range (max - min)
        valid_L = [v for v in L if not np.isnan(v)]
        range_val = float(max(valid_L) - min(valid_L)) if len(valid_L) >= 2 else 0.0
        has_mismatch = range_val > detection_thresh

        alert = None
        severity = 0.0
        if has_mismatch:
            severity = min(range_val, 1.0)
            max_idx = int(np.argmax(L))
            min_idx = int(np.argmin(L))
            alert = (
                f"DIVERGENCE: {layer_names[max_idx]} ({L[max_idx]:.2f}) vs "
                f"{layer_names[min_idx]} ({L[min_idx]:.2f}) — "
                f"cross-layer conflict detected (range={range_val:.3f})"
            )

        domain_result = {
            "alert": alert,
            "severity": float(severity),
            "mismatch_score": float(range_val),
        }

    else:  # emergence
        # Emergence: detect cross-layer alignment
        alignment_floor = min(L)
        window_detected = alignment_floor > detection_thresh

        window_type = None
        confidence = 0.0
        recommended_action = None

        if window_detected:
            if alignment_floor > 0.8:
                window_type = "OPTIMAL: All layers strongly aligned"
                confidence = 0.95
                recommended_action = "High-confidence window — act now"
            else:
                window_type = "FAVORABLE: Layers aligned above threshold"
                confidence = 0.75
                recommended_action = "Good alignment — proceed with awareness"

            weakest_idx = int(np.argmin(L))
            domain_result = {
                "window_detected": True,
                "window_type": window_type,
                "confidence": float(confidence),
                "alignment_floor": float(alignment_floor),
                "limiting_factor": layer_names[weakest_idx],
                "recommended_action": recommended_action,
            }
        else:
            below = [layer_names[i] for i, l in enumerate(L) if l <= detection_thresh]
            domain_result = {
                "window_detected": False,
                "alignment_floor": float(alignment_floor),
                "status": f"Layers not aligned. {', '.join(below)} below threshold.",
                "improvement_needed": below,
            }

    # =========================================================================
    # AUDIT
    # =========================================================================
    threshold_clamped_any = any(
        info.get("was_clamped", False)
        for info in threshold_info.values()
    ) if threshold_info else False

    threshold_audit_info = None
    if threshold_info or ignored_threshold_keys:
        threshold_audit_info = {
            "overrides": {
                key: {
                    "requested": info.get("requested"),
                    "used": info.get("used"),
                    "was_clamped": info.get("was_clamped", False)
                }
                for key, info in threshold_info.items()
            } if threshold_info else {},
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

    # =========================================================================
    # LAYER VISIBILITY (optional — caller provides hierarchy)
    # =========================================================================
    layer_visibility = None
    if layer_hierarchy and isinstance(layer_hierarchy, dict):
        valid_levels = {"Micro", "Meso", "Macro", "Meta"}
        # Build weights_dict and values_dict
        weights_dict = {layer_names[i]: W[i] for i in range(n_layers)}
        values_dict = {layer_names[i]: float(L[i]) for i in range(n_layers)}
        interactions_dict = {layer_names[i]: float(I[i]) for i in range(n_layers)}

        # Compute contributions by hierarchy level
        level_contributions = {"Micro": 0.0, "Meso": 0.0, "Macro": 0.0, "Meta": 0.0}
        level_weights = {"Micro": 0.0, "Meso": 0.0, "Macro": 0.0, "Meta": 0.0}
        for name in layer_names:
            level = layer_hierarchy.get(name)
            if level in valid_levels:
                level_weights[level] += weights_dict[name]
                level_contributions[level] += (
                    weights_dict[name] * values_dict[name] * interactions_dict[name]
                )

        dominant = max(level_contributions, key=level_contributions.get)
        layer_visibility = {
            "dominant": dominant,
            "weights_by_layer": level_weights,
            "contributions_by_layer": level_contributions,
            "rationale": f"{dominant} layer has highest contribution in user-defined domain '{domain_name}'",
            "input_driven": True,
            "_note": "Interpretive aid for reasoning; does not affect M-score calculation"
        }

    layer_coupling = compute_layer_coupling(L, layer_names)

    # =========================================================================
    # CALIBRATION BLOCK (Option D + C flavor)
    # =========================================================================
    calibration = {
        "domain_type": "user_defined",
        "domain_name": domain_name,
        "mode": mode,
        "layer_count": n_layers,
        "weight_distribution": {layer_names[i]: W[i] for i in range(n_layers)},
        "note": (
            "This domain was defined by the caller, not a hardcoded Mantic tool. "
            "The kernel, governance bounds, and audit trail are identical to built-in tools. "
            "Weights and layer semantics are caller-specified."
        )
    }

    # =========================================================================
    # RESULT
    # =========================================================================
    return {
        **domain_result,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, layer_names),
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied,
        "layer_visibility": layer_visibility,
        "layer_coupling": layer_coupling,
        "calibration": calibration,
        "layer_values": {layer_names[i]: float(L[i]) for i in range(n_layers)},
    }


if __name__ == "__main__":
    print("=== Generic Mantic Detector ===\n")

    print("Test 1: Friction mode — supply chain divergence")
    result = detect(
        domain_name="supply_chain",
        layer_names=["supply", "demand", "logistics", "regulatory"],
        weights=[0.3, 0.3, 0.2, 0.2],
        layer_values=[0.8, 0.3, 0.6, 0.7],
        mode="friction",
        layer_hierarchy={"supply": "Micro", "demand": "Micro", "logistics": "Meso", "regulatory": "Macro"}
    )
    print(f"  Alert: {result['alert']}")
    print(f"  M-Score: {result['m_score']:.3f}")
    print(f"  Calibration: {result['calibration']['domain_type']}")
    print(f"  Layer Visibility: {result.get('layer_visibility', {}).get('dominant')}\n")

    print("Test 2: Emergence mode — education alignment")
    result = detect(
        domain_name="education",
        layer_names=["student_readiness", "curriculum_fit", "instructor_capacity", "institutional_support"],
        weights=[0.25, 0.25, 0.25, 0.25],
        layer_values=[0.85, 0.80, 0.78, 0.82],
        mode="emergence"
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  M-Score: {result['m_score']:.3f}")
    print(f"  Calibration: {result['calibration']['domain_type']}\n")

    print("Test 3: 5-layer domain")
    result = detect(
        domain_name="product_launch",
        layer_names=["market", "engineering", "design", "operations", "finance"],
        weights=[0.25, 0.25, 0.2, 0.15, 0.15],
        layer_values=[0.9, 0.7, 0.8, 0.5, 0.6],
        mode="friction"
    )
    print(f"  Alert: {result['alert']}")
    print(f"  M-Score: {result['m_score']:.3f}")
    print(f"  Layers: {result['calibration']['layer_count']}")

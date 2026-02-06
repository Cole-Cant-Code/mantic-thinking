"""
Input Validation Utilities for Mantic Tools

Provides consistent input validation across all domain tools:
- Input clamping to valid ranges
- Weight normalization
- Layer validation and NaN handling
"""

import numpy as np


def clamp_input(value, min_val=0.0, max_val=1.0, name="input"):
    """
    Clamp a single input value to valid range.
    
    Args:
        value: Input value (float or None)
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        name: Name of the input for error messages
    
    Returns:
        float: Clamped value, or NaN if input is None
    
    Raises:
        TypeError: If value is not a number (and not None)
    """
    if value is None:
        return np.nan
    
    try:
        val = float(value)
    except (TypeError, ValueError):
        raise TypeError(f"{name} must be a number, got {type(value).__name__}")
    
    if np.isnan(val):
        return val
    
    clamped = np.clip(val, min_val, max_val)
    return float(clamped)


def normalize_weights(weights):
    """
    Normalize weights to sum to 1.0.
    
    Args:
        weights: List or array of weight values
    
    Returns:
        numpy array: Normalized weights summing to 1.0
    
    Raises:
        ValueError: If all weights are zero
    """
    w = np.array(weights, dtype=float)
    w = np.clip(w, 0, 1)  # Ensure all weights are valid
    
    total = w.sum()
    if total < 1e-10:
        raise ValueError("Cannot normalize: all weights are zero or negative")
    
    return w / total


def validate_layers(layer_values, layer_names=None):
    """
    Validate and prepare layer values for mantic kernel.
    
    Args:
        layer_values: List of 4 layer values (may contain None/NaN)
        layer_names: Optional list of layer names for error messages
    
    Returns:
        list: Validated layer values (NaN for missing, clamped for present)
    
    Raises:
        ValueError: If fewer than 2 layers have valid data
    """
    if len(layer_values) != 4:
        raise ValueError(f"Expected 4 layer values, got {len(layer_values)}")
    
    if layer_names is None:
        layer_names = [f"layer_{i}" for i in range(4)]
    
    validated = []
    valid_count = 0
    
    for i, val in enumerate(layer_values):
        clamped = clamp_input(val, name=layer_names[i])
        validated.append(clamped)
        if not np.isnan(clamped):
            valid_count += 1
    
    if valid_count < 2:
        raise ValueError(
            f"At least 2 layers must have valid data, only {valid_count} provided"
        )
    
    return validated


def require_finite_inputs(values):
    """
    Ensure required inputs are present and finite numbers.

    Args:
        values: Dict or iterable of (name, value) pairs

    Raises:
        ValueError: If any value is None or not finite
        TypeError: If any value is not a number
    """
    items = values.items() if isinstance(values, dict) else values
    for name, value in items:
        if value is None:
            raise ValueError(f"{name} is required and cannot be None")
        try:
            val = float(value)
        except (TypeError, ValueError):
            raise TypeError(f"{name} must be a number, got {type(value).__name__}")
        if not np.isfinite(val):
            raise ValueError(f"{name} must be a finite number")


def check_mismatch(layer_values, threshold=0.4, comparison_mode="variance"):
    """
    Check for mismatches between layer values.
    
    Args:
        layer_values: List of 4 validated layer values
        threshold: Mismatch detection threshold (default 0.4)
        comparison_mode: "variance", "range", or "pairwise"
    
    Returns:
        tuple: (has_mismatch, mismatch_score, mismatch_description)
    """
    # Filter out NaN values
    valid_values = [v for v in layer_values if not np.isnan(v)]
    
    if len(valid_values) < 2:
        return False, 0.0, "Insufficient data for mismatch detection"
    
    valid_array = np.array(valid_values)
    
    if comparison_mode == "variance":
        # Use standard deviation as mismatch indicator
        mean_val = valid_array.mean()
        std_val = valid_array.std()
        mismatch_score = std_val
        has_mismatch = std_val > threshold
        description = f"StdDev={std_val:.3f} vs threshold={threshold}"
    
    elif comparison_mode == "range":
        # Use range (max - min) as mismatch indicator
        range_val = valid_array.max() - valid_array.min()
        mismatch_score = range_val
        has_mismatch = range_val > threshold
        description = f"Range={range_val:.3f} vs threshold={threshold}"
    
    elif comparison_mode == "pairwise":
        # Compare first two layers (domain-specific interpretation)
        if len(valid_values) >= 2:
            diff = abs(valid_values[0] - valid_values[1])
            mismatch_score = diff
            has_mismatch = diff > threshold
            description = f"Pairwise diff={diff:.3f} vs threshold={threshold}"
        else:
            return False, 0.0, "Need 2+ layers for pairwise comparison"
    
    else:
        raise ValueError(f"Unknown comparison mode: {comparison_mode}")
    
    return has_mismatch, float(mismatch_score), description


def format_attribution(attribution_array, layer_names):
    """
    Format attribution array into a dictionary with named layers.
    
    Args:
        attribution_array: List of attribution percentages from mantic_kernel
        layer_names: List of layer names
    
    Returns:
        dict: {layer_name: attribution_percentage}
    """
    return {
        name: float(pct)
        for name, pct in zip(layer_names, attribution_array)
    }


# =============================================================================
# BOUNDED OVERRIDE SYSTEM
# Allows runtime tuning of tempo (kernel) and sensitivity (thresholds) while
# keeping domain weights immutable. All overrides are clamped to safe ranges.
# =============================================================================

# Domain-specific allowed temporal kernels
# Prevents nonsensical combinations (e.g., oscillatory for climate)
DOMAIN_KERNEL_ALLOWLIST = {
    "healthcare": ["exponential", "s_curve", "linear", "memory"],
    "finance": ["oscillatory", "exponential", "memory", "linear"],
    "cyber": ["exponential", "memory", "linear"],
    "climate": ["power_law", "exponential", "logistic", "linear"],
    "legal": ["logistic", "s_curve", "linear", "memory"],
    "military": ["memory", "exponential", "linear"],
    "social": ["exponential", "oscillatory", "s_curve", "linear"],
    "planning": ["logistic", "s_curve", "linear", "memory"],
}

# Global hard bounds for any threshold override
THRESHOLD_HARD_BOUNDS = (0.05, 0.95)

# Maximum percent drift from default threshold (±20%)
THRESHOLD_MAX_DRIFT_PCT = 0.20

# f_time clamp bounds (prevent runaway growth)
F_TIME_BOUNDS = (0.1, 3.0)

# Temporal parameter bounds
ALPHA_BOUNDS = (0.01, 0.5)
NOVELTY_BOUNDS = (-2.0, 2.0)


def clamp_threshold_override(requested, default, 
                              max_drift_pct=THRESHOLD_MAX_DRIFT_PCT,
                              hard_bounds=THRESHOLD_HARD_BOUNDS):
    """
    Clamp a threshold override using dual bounds (percent + absolute).
    
    Args:
        requested: The requested threshold value
        default: The default threshold for this tool/rule
        max_drift_pct: Max percent change allowed from default (e.g., 0.20 = ±20%)
        hard_bounds: Absolute (min, max) bounds regardless of default
    
    Returns:
        tuple: (clamped_value, was_clamped, clamp_info)
            - clamped_value: The final threshold to use
            - was_clamped: True if the value was constrained
            - clamp_info: Dict explaining what happened
    """
    if requested is None:
        return default, False, {"used": "default", "value": default}
    
    # Calculate percent-based bounds (independent of requested value)
    min_pct = default * (1 - max_drift_pct)
    max_pct = default * (1 + max_drift_pct)
    
    # Combine with hard bounds (most restrictive wins)
    effective_min = max(hard_bounds[0], min_pct)
    effective_max = min(hard_bounds[1], max_pct)

    try:
        val = float(requested)
    except (TypeError, ValueError):
        return default, True, {
            "requested": requested,
            "used": float(default),
            "default": default,
            "bounds": {"min": effective_min, "max": effective_max},
            "was_clamped": True,
            "reason": f"Invalid type: {type(requested).__name__}"
        }
    if not np.isfinite(val):
        return default, True, {
            "requested": requested,
            "used": float(default),
            "default": default,
            "bounds": {"min": effective_min, "max": effective_max},
            "was_clamped": True,
            "reason": "Not a finite number"
        }
    
    # Apply clamping
    clamped = np.clip(val, effective_min, effective_max)
    was_clamped = not np.isclose(clamped, val, atol=1e-10)
    
    clamp_info = {
        "requested": val,
        "used": float(clamped),
        "default": default,
        "bounds": {"min": effective_min, "max": effective_max},
        "was_clamped": was_clamped
    }
    
    if was_clamped:
        if val < effective_min:
            clamp_info["reason"] = f"Below minimum ({effective_min:.3f})"
        else:
            clamp_info["reason"] = f"Above maximum ({effective_max:.3f})"
    
    return float(clamped), was_clamped, clamp_info


def validate_temporal_config(config, domain=None):
    """
    Validate and clamp temporal configuration parameters.
    
    Args:
        config: Dict with keys like 'kernel_type', 'alpha', 'n', 't', etc.
        domain: Optional domain name to check kernel allowlist
    
    Returns:
        tuple: (validated_config, rejected_params, clamp_info)
            - validated_config: Clean dict ready for compute_temporal_kernel
            - rejected_params: Dict of params that were rejected and why
            - clamp_info: Dict of params that were clamped and to what
    """
    if config is None:
        return None, {}, {}
    
    validated = {}
    rejected = {}
    clamped = {}
    
    # Validate kernel_type against domain allowlist
    kernel_type = config.get("kernel_type")
    if kernel_type is not None:
        allowed = DOMAIN_KERNEL_ALLOWLIST.get(domain, [])
        if allowed and kernel_type not in allowed:
            rejected["kernel_type"] = {
                "requested": kernel_type,
                "reason": f"Not allowed for domain '{domain}'",
                "allowed": allowed
            }
            # Don't include kernel_type in validated
        else:
            validated["kernel_type"] = kernel_type
    
    # Clamp alpha
    alpha = config.get("alpha")
    if alpha is not None:
        try:
            val = float(alpha)
            if not np.isfinite(val):
                raise ValueError("Not a finite number")
            clamped_val = np.clip(val, ALPHA_BOUNDS[0], ALPHA_BOUNDS[1])
            validated["alpha"] = float(clamped_val)
            if not np.isclose(clamped_val, val, atol=1e-10):
                clamped["alpha"] = {"requested": val, "used": clamped_val, "bounds": ALPHA_BOUNDS}
        except (TypeError, ValueError):
            rejected["alpha"] = {"requested": alpha, "reason": "Not a finite number"}
    
    # Clamp n (novelty)
    n = config.get("n")
    if n is not None:
        try:
            val = float(n)
            if not np.isfinite(val):
                raise ValueError("Not a finite number")
            clamped_val = np.clip(val, NOVELTY_BOUNDS[0], NOVELTY_BOUNDS[1])
            validated["n"] = float(clamped_val)
            if not np.isclose(clamped_val, val, atol=1e-10):
                clamped["n"] = {"requested": val, "used": clamped_val, "bounds": NOVELTY_BOUNDS}
        except (TypeError, ValueError):
            rejected["n"] = {"requested": n, "reason": "Not a finite number"}
    
    # Pass through other params (t, t0, exponent, frequency, etc.) with basic validation
    for key in ["t", "t0", "exponent", "frequency", "memory_strength"]:
        if key in config:
            try:
                val = float(config[key])
                if not np.isfinite(val):
                    raise ValueError("Not a finite number")
                validated[key] = val
            except (TypeError, ValueError):
                rejected[key] = {"requested": config[key], "reason": "Not a finite number"}
    
    return validated, rejected, clamped


def clamp_f_time(f_time):
    """
    Clamp f_time to prevent runaway growth from extreme temporal kernels.
    
    Args:
        f_time: Raw temporal kernel multiplier
    
    Returns:
        tuple: (clamped_f_time, was_clamped, clamp_info)
    """
    if f_time is None:
        return 1.0, False, {"used": 1.0, "reason": "None provided"}
    
    try:
        val = float(f_time)
    except (TypeError, ValueError):
        return 1.0, True, {
            "used": 1.0,
            "was_clamped": True,
            "reason": f"Invalid type: {type(f_time).__name__}"
        }
    if not np.isfinite(val):
        return 1.0, True, {
            "used": 1.0,
            "was_clamped": True,
            "reason": "Not a finite number"
        }
    
    clamped = np.clip(val, F_TIME_BOUNDS[0], F_TIME_BOUNDS[1])
    was_clamped = not np.isclose(clamped, val, atol=1e-10)
    
    clamp_info = {
        "requested": float(val), 
        "used": float(clamped), 
        "bounds": F_TIME_BOUNDS,
        "was_clamped": was_clamped
    }
    if was_clamped:
        clamp_info["reason"] = f"Outside bounds [{F_TIME_BOUNDS[0]}, {F_TIME_BOUNDS[1]}]"
    
    return float(clamped), was_clamped, clamp_info


def build_overrides_audit(threshold_overrides=None, temporal_config=None, 
                          threshold_info=None, temporal_validated=None, 
                          temporal_rejected=None, temporal_clamped=None,
                          f_time_info=None):
    """
    Build the overrides_applied audit block for tool responses.
    
    Args:
        threshold_overrides: Original threshold override request dict
        temporal_config: Original temporal config request
        threshold_info: Dict with 'overrides' (per-threshold details) and 'was_clamped'
        temporal_validated: Validated temporal config
        temporal_rejected: Rejected temporal params
        temporal_clamped: Clamped temporal params
        f_time_info: Dict from clamp_f_time
    
    Returns:
        dict: Audit block showing what was tuned and what was constrained
    """
    audit = {}
    
    # Threshold overrides audit - new structure with per-threshold details
    if threshold_overrides:
        audit["threshold_overrides"] = {
            "requested": threshold_overrides,
            "applied": threshold_info.get("overrides") if threshold_info else None,
            "clamped": threshold_info.get("was_clamped", False) if threshold_info else False,
            "ignored_keys": threshold_info.get("ignored_keys") if threshold_info else None
        }
    
    # Temporal config audit
    if temporal_config:
        audit["temporal_config"] = {
            "requested": temporal_config,
            "applied": temporal_validated,
            "rejected": temporal_rejected if temporal_rejected else None,
            "clamped": temporal_clamped if temporal_clamped else None
        }
    
    # f_time audit (always include if computed)
    if f_time_info:
        f_time_used = f_time_info.get("used")
        f_time_requested = f_time_info.get("requested")
        audit["f_time"] = {
            "requested": float(f_time_requested) if f_time_requested is not None else None,
            "used": float(f_time_used) if f_time_used is not None else None,
            "clamped": f_time_info.get("was_clamped", False)
        }
    
    return audit

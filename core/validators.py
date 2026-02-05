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

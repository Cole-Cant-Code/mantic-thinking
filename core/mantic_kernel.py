"""
Mantic Kernel - IMMUTABLE CORE FORMULA

This file contains the immutable mathematical foundation of the Mantic Framework.
It must not be modified by any tool or adapter.

Formula: M = (sum(W * L * I)) * f(t) / k_n

Where:
    M: Final mantic score (anomaly intensity)
    W: Array of weights (must sum to 1)
    L: Array of layer values (0-1 range)
    I: Array of interaction coefficients (0-1)
    f_time: Temporal kernel value (default 1.0)
    k_n: Normalization constant (default 1.0)
"""

import numpy as np


def mantic_kernel(W, L, I, f_time=1.0, k_n=1.0):
    """
    Immutable core formula: M = (sum(W * L * I)) * f(t) / k_n
    
    This function implements the mathematical foundation of the Mantic Framework.
    It is intentionally simple, deterministic, and strictly validated.
    
    Args:
        W: array of 4 weights (must sum to 1, each 0-1)
        L: array of 4 layer values (0-1, NaN allowed for missing data)
        I: array of 4 interaction coefficients (0-1)
        f_time: temporal kernel value (default 1.0)
        k_n: normalization constant (default 1.0)
    
    Returns:
        tuple: (M, S, attribution)
            M: final mantic score (float)
            S: spatial component = sum(W*L*I) (float)
            attribution: layer contribution percentages (list of 4 floats)
    
    Raises:
        ValueError: If weights don't sum to ~1 after NaN handling
    
    Example:
        >>> W = [0.25, 0.25, 0.25, 0.25]
        >>> L = [0.8, 0.6, 0.9, 0.4]
        >>> I = [1.0, 1.0, 1.0, 1.0]
        >>> M, S, attr = mantic_kernel(W, L, I)
        >>> print(f"M-score: {M:.3f}")
        M-score: 0.675
    """
    W = np.array(W, dtype=float)
    L = np.array(L, dtype=float)
    I = np.array(I, dtype=float)
    
    # Validate array lengths
    if not (len(W) == len(L) == len(I)):
        raise ValueError(f"Array length mismatch: W={len(W)}, L={len(L)}, I={len(I)}")
    
    # Handle missing data via graceful degradation
    # If any L value is NaN, redistribute weights among available layers
    available = ~np.isnan(L)
    if not np.all(available):
        if not np.any(available):
            raise ValueError("All layer values are NaN - cannot compute mantic score")
        W = W[available]
        L = L[available]
        I = I[available]
        W = W / W.sum()  # Renormalize to sum to 1
    
    # Validate normalized weights
    weight_sum = W.sum()
    if not np.isclose(weight_sum, 1.0, atol=1e-6):
        raise ValueError(f"Weights must sum to 1.0, got {weight_sum}")
    
    # Validate value ranges
    if np.any((L < 0) | (L > 1)):
        raise ValueError("Layer values (L) must be in range [0, 1]")
    if np.any((W < 0) | (W > 1)):
        raise ValueError("Weights (W) must be in range [0, 1]")
    if np.any((I < 0) | (I > 1)):
        raise ValueError("Interaction coefficients (I) must be in range [0, 1]")
    
    # Core formula calculation
    S = np.sum(W * L * I)  # Spatial component
    M = (S * f_time) / k_n  # Final mantic score
    
    # Calculate attribution (percentage contribution per layer)
    if S > 1e-10:
        attribution = (W * L * I) / S
    else:
        attribution = np.zeros_like(W)
    
    return float(M), float(S), attribution.tolist()


def compute_temporal_kernel(t, decay_rate=0.1, kernel_type="exponential"):
    """
    Compute temporal kernel value f(t) for time-based adjustments.
    
    Args:
        t: time delta (0 = current, positive = future, negative = past)
        decay_rate: rate of temporal decay (default 0.1)
        kernel_type: "exponential" or "linear" (default "exponential")
    
    Returns:
        float: temporal kernel multiplier
    
    Note:
        This is a utility function - the core mantic_kernel expects
        f_time to be pre-computed. Use this to generate f_time values.
    """
    if kernel_type == "exponential":
        return np.exp(-decay_rate * abs(t))
    elif kernel_type == "linear":
        return max(0, 1 - decay_rate * abs(t))
    else:
        raise ValueError(f"Unknown kernel type: {kernel_type}")


# Version marker for cross-model compatibility verification
KERNEL_VERSION = "1.0.0"
KERNEL_HASH = "immutable_core_v1"


def verify_kernel_integrity():
    """
    Verify the kernel implementation hasn't been tampered with.
    Returns True if core formula is intact.
    """
    # Test case: known input/output pair
    # W * L * I = 0.25 * 0.5 * 1.0 = 0.125 per layer
    # Sum over 4 layers = 0.125 * 4 = 0.5
    W = [0.25, 0.25, 0.25, 0.25]
    L = [0.5, 0.5, 0.5, 0.5]
    I = [1.0, 1.0, 1.0, 1.0]
    
    M, S, attr = mantic_kernel(W, L, I)
    
    # Expected: S = 0.5 (sum of 4 * 0.125), M = 0.5 (with f_time=1, k_n=1)
    expected_M = 0.5
    expected_S = 0.5
    
    return (
        np.isclose(M, expected_M, atol=1e-10) and
        np.isclose(S, expected_S, atol=1e-10) and
        len(attr) == 4 and
        all(np.isclose(a, 0.25, atol=1e-10) for a in attr)
    )

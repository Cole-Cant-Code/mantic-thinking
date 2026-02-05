"""
Codebase: Alignment Window Detector

Identifies rare alignment when architecture, implementation, testing,
and documentation all achieve favorable levels simultaneously —
optimal window for major refactoring, feature addition, or release.

Confluence Logic: All 4 layers must be favorable simultaneously (not just average)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
from core.mantic_kernel import mantic_kernel
from core.validators import clamp_input, format_attribution


# Equal weight for alignment detection
WEIGHTS = [0.25, 0.25, 0.25, 0.25]
LAYER_NAMES = ['architecture', 'implementation', 'testing', 'documentation']

# Confluence thresholds
ALIGNMENT_THRESHOLD = 0.65
OPTIMAL_THRESHOLD = 0.80


def detect(architecture, implementation, testing, documentation, f_time=1.0):
    """
    Detect alignment windows in a codebase for optimal action timing.

    Args:
        architecture: Structural soundness (0-1)
        implementation: Code quality and correctness (0-1)
        testing: Validation coverage and rigor (0-1)
        documentation: Specification completeness (0-1)
        f_time: Temporal kernel multiplier (default 1.0)

    Returns:
        dict with window_detected, window_type, confidence, m_score, etc.

    Example:
        >>> result = detect(
        ...     architecture=0.85,
        ...     implementation=0.82,
        ...     testing=0.78,
        ...     documentation=0.80
        ... )
        >>> print(result['window_detected'])
        True
    """
    # Clamp inputs
    L = [
        clamp_input(architecture, name="architecture"),
        clamp_input(implementation, name="implementation"),
        clamp_input(testing, name="testing"),
        clamp_input(documentation, name="documentation")
    ]

    # Use equal interactions for baseline
    I = [1.0, 1.0, 1.0, 1.0]

    # Calculate Mantic score
    M, S, attr = mantic_kernel(WEIGHTS, L, I, f_time)

    # CONFLUENCE LOGIC: Check if ALL layers are above threshold (alignment)
    alignment_floor = min(L)

    window_detected = False
    window_type = None
    confidence = 0.0
    recommended_action = None
    limiting_factor = None

    if alignment_floor > ALIGNMENT_THRESHOLD:
        window_detected = True

        # Check for optimal vs favorable
        if all(l > OPTIMAL_THRESHOLD for l in L):
            window_type = "OPTIMAL: All engineering dimensions aligned for maximum impact"
            confidence = 0.95
            recommended_action = "Major feature addition, architectural evolution, or release — peak window"
        else:
            window_type = "FAVORABLE: Strong alignment across all dimensions"
            confidence = 0.75
            recommended_action = "Good window for moderate changes, refactoring, or dependency updates"

        # Identify weakest link for monitoring
        weakest_idx = int(np.argmin(L))
        limiting_factor = LAYER_NAMES[weakest_idx]

        return {
            "window_detected": True,
            "window_type": window_type,
            "confidence": float(confidence),
            "m_score": float(M),
            "spatial_component": float(S),
            "layer_attribution": format_attribution(attr, LAYER_NAMES),
            "alignment_floor": float(alignment_floor),
            "limiting_factor": limiting_factor,
            "recommended_action": recommended_action,
            "layer_values": {
                "architecture": float(L[0]),
                "implementation": float(L[1]),
                "testing": float(L[2]),
                "documentation": float(L[3])
            }
        }

    # Window not detected - identify what's missing
    below_threshold = [LAYER_NAMES[i] for i, l in enumerate(L) if l <= ALIGNMENT_THRESHOLD]

    return {
        "window_detected": False,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "alignment_floor": float(alignment_floor),
        "status": f"Dimensions not aligned. {', '.join(below_threshold)} below threshold.",
        "improvement_needed": below_threshold
    }


if __name__ == "__main__":
    print("=== Codebase Alignment Window Detector ===\n")

    # Test 1: Optimal alignment
    print("Test 1: Optimal alignment (all > 0.8)")
    result = detect(
        architecture=0.85,
        implementation=0.82,
        testing=0.88,
        documentation=0.80
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Type: {result['window_type']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Limiting Factor: {result.get('limiting_factor', 'N/A')}")
    print(f"  M-Score: {result['m_score']:.3f}\n")

    # Test 2: Favorable alignment
    print("Test 2: Favorable alignment (all > 0.65)")
    result = detect(
        architecture=0.75,
        implementation=0.72,
        testing=0.68,
        documentation=0.70
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Type: {result['window_type']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  M-Score: {result['m_score']:.3f}\n")

    # Test 3: Not aligned (testing below threshold)
    print("Test 3: Not aligned (testing low)")
    result = detect(
        architecture=0.80,
        implementation=0.75,
        testing=0.45,
        documentation=0.70
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Status: {result['status']}")
    print(f"  Alignment Floor: {result['alignment_floor']:.3f}")

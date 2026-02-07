"""
Codebase: Layer Conflict Detector

Detects when codebase engineering dimensions diverge — e.g., implementation
quality is high but testing coverage is low, or documentation is excellent
but architecture has structural debt.

Input Layers:
    architecture: Structural soundness (0-1)
    implementation: Code quality and correctness (0-1)
    testing: Validation coverage and rigor (0-1)
    documentation: Specification completeness (0-1)

Output:
    alert: Detection message or None
    conflict_type: Type of codebase conflict detected
    bottleneck: Which layer is the constraint
    m_score: Final mantic anomaly score
    spatial_component: Raw S value
    layer_attribution: Percentage contribution per layer
"""

import sys
import os

# Avoid mutating sys.path on import; only adjust for direct script execution.
if __name__ == "__main__":
    _repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

import numpy as np
from core.safe_kernel import safe_mantic_kernel as mantic_kernel
from core.validators import clamp_input, require_finite_inputs, format_attribution


# Domain weights (must sum to 1)
WEIGHTS = {
    'architecture': 0.30,
    'implementation': 0.25,
    'testing': 0.25,
    'documentation': 0.20
}

LAYER_NAMES = ['architecture', 'implementation', 'testing', 'documentation']

# Detection thresholds
THRESHOLD = 0.35
HIGH_QUALITY_THRESHOLD = 0.75


def detect(architecture, implementation, testing, documentation, f_time=1.0):
    """
    Detect layer conflicts in a codebase analysis.

    Args:
        architecture: Structural soundness (0-1)
        implementation: Code quality and correctness (0-1)
        testing: Validation coverage and rigor (0-1)
        documentation: Specification completeness (0-1)
        f_time: Temporal kernel multiplier (default 1.0)

    Returns:
        dict with alert, conflict_type, bottleneck, m_score, etc.

    Example:
        >>> result = detect(
        ...     architecture=0.85,
        ...     implementation=0.80,
        ...     testing=0.40,
        ...     documentation=0.75
        ... )
        >>> print(result['conflict_type'])
        'confidence_debt'
    """
    # INPUT VALIDATION
    require_finite_inputs({
        "architecture": architecture,
        "implementation": implementation,
        "testing": testing,
        "documentation": documentation,
    })

    # Clamp inputs
    L = [
        clamp_input(architecture, name="architecture"),
        clamp_input(implementation, name="implementation"),
        clamp_input(testing, name="testing"),
        clamp_input(documentation, name="documentation")
    ]

    W = list(WEIGHTS.values())
    I = [1.0, 1.0, 1.0, 1.0]

    # Calculate Mantic score
    M, S, attr = mantic_kernel(W, L, I, f_time)

    # Detection logic
    alert = None
    conflict_type = None
    bottleneck = None

    # Compute pairwise gaps
    arch_impl_gap = abs(L[0] - L[1])
    impl_test_gap = L[1] - L[2]  # Signed: positive means impl > testing
    doc_impl_gap = abs(L[3] - L[1])
    arch_test_gap = L[0] - L[2]  # Signed: positive means arch > testing

    # Find the weakest layer
    weakest_idx = int(np.argmin(L))
    bottleneck = LAYER_NAMES[weakest_idx]

    # Check for specific conflict patterns
    if impl_test_gap > THRESHOLD and L[1] > HIGH_QUALITY_THRESHOLD:
        conflict_type = "confidence_debt"
        alert = (
            f"CONFIDENCE DEBT: Strong implementation ({L[1]:.2f}) "
            f"but weak testing ({L[2]:.2f}). "
            "Correctness is asserted structurally, not empirically."
        )
    elif arch_test_gap > THRESHOLD and L[0] > HIGH_QUALITY_THRESHOLD:
        conflict_type = "brittleness_risk"
        alert = (
            f"BRITTLENESS RISK: Clean architecture ({L[0]:.2f}) "
            f"with insufficient test coverage ({L[2]:.2f}). "
            "Structure looks sound but changes may break silently."
        )
    elif doc_impl_gap > THRESHOLD:
        if L[3] > L[1]:
            conflict_type = "specification_drift"
            alert = (
                f"SPECIFICATION DRIFT: Documentation ({L[3]:.2f}) "
                f"exceeds implementation ({L[1]:.2f}). "
                "Docs describe capabilities the code doesn't deliver."
            )
        else:
            conflict_type = "documentation_lag"
            alert = (
                f"DOCUMENTATION LAG: Implementation ({L[1]:.2f}) "
                f"outpaces documentation ({L[3]:.2f}). "
                "Code has evolved beyond what the docs describe."
            )
    elif arch_impl_gap > THRESHOLD:
        if L[0] > L[1]:
            conflict_type = "tech_debt_accumulation"
            alert = (
                f"TECH DEBT: Architecture design ({L[0]:.2f}) "
                f"ahead of implementation quality ({L[1]:.2f}). "
                "The blueprint is good but the build is rough."
            )
        else:
            conflict_type = "architecture_erosion"
            alert = (
                f"ARCHITECTURE EROSION: Implementation ({L[1]:.2f}) "
                f"outgrew the architecture ({L[0]:.2f}). "
                "Good code is fighting a weak structure."
            )
    else:
        conflict_type = "aligned"

    return {
        "alert": alert,
        "conflict_type": conflict_type,
        "bottleneck": bottleneck,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "layer_values": {
            "architecture": float(L[0]),
            "implementation": float(L[1]),
            "testing": float(L[2]),
            "documentation": float(L[3])
        },
        "max_gap": float(max(L) - min(L)),
        "threshold": THRESHOLD
    }


if __name__ == "__main__":
    print("=== Codebase Layer Conflict Detector ===\n")

    # Test 1: Confidence debt (high impl, low testing)
    print("Test 1: Strong implementation, weak testing")
    result = detect(architecture=0.85, implementation=0.80, testing=0.40, documentation=0.75)
    print(f"  Alert: {result['alert']}")
    print(f"  Conflict: {result['conflict_type']}")
    print(f"  Bottleneck: {result['bottleneck']}")
    print(f"  M-Score: {result['m_score']:.3f}\n")

    # Test 2: Aligned codebase (no conflict)
    print("Test 2: Well-aligned codebase")
    result = detect(architecture=0.75, implementation=0.72, testing=0.70, documentation=0.68)
    print(f"  Alert: {result['alert']}")
    print(f"  Conflict: {result['conflict_type']}")
    print(f"  M-Score: {result['m_score']:.3f}\n")

    # Test 3: Specification drift (docs exceed implementation)
    print("Test 3: Specification drift")
    result = detect(architecture=0.70, implementation=0.45, testing=0.50, documentation=0.85)
    print(f"  Alert: {result['alert']}")
    print(f"  Conflict: {result['conflict_type']}")
    print(f"  Bottleneck: {result['bottleneck']}")

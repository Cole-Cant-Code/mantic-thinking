"""
Legal: Precedent Drift Alert

Warns when judicial philosophy shifts threaten current precedent-based strategies.

Input Layers:
    black_letter: Statutory text alignment (0-1)
    precedent: Precedent consistency (0-1)
    operational: Practical implementation feasibility (0-1)
    socio_political: Social/political context (-1 to 1, where -1 = left shift, 1 = right shift)

Output:
    alert: Detection message or None
    drift_direction: left/right/fragmenting/stable
    strategy_pivot: Recommended strategy adjustment
    m_score: Final mantic anomaly score
    spatial_component: Raw S value
    layer_attribution: Percentage contribution per layer
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
from core.mantic_kernel import mantic_kernel
from core.validators import clamp_input, format_attribution


# Domain weights (must sum to 1)
WEIGHTS = {
    'black_letter': 0.30,
    'precedent': 0.35,
    'operational': 0.20,
    'socio_political': 0.15
}

LAYER_NAMES = ['black_letter', 'precedent', 'operational', 'socio_political']

# Detection thresholds
DRIFT_THRESHOLD = 0.4
PRECEDENT_THRESHOLD = 0.3


def detect(black_letter, precedent, operational, socio_political, f_time=1.0):
    """
    Detect precedent drift and judicial philosophy shifts.
    
    Args:
        black_letter: Statutory text alignment (0-1)
        precedent: Precedent consistency (0-1)
        operational: Practical implementation (0-1)
        socio_political: Social/political context (-1 to 1)
        f_time: Temporal kernel multiplier (default 1.0)
    
    Returns:
        dict with alert, drift_direction, strategy_pivot, m_score, etc.
    
    Example:
        >>> result = detect(
        ...     black_letter=0.8,
        ...     precedent=0.3,
        ...     operational=0.7,
        ...     socio_political=0.6
        ... )
        >>> print(result['drift_direction'])
        'right'
    """
    # Clamp inputs
    L = [
        clamp_input(black_letter, name="black_letter"),
        clamp_input(precedent, name="precedent"),
        clamp_input(operational, name="operational"),
        clamp_input(socio_political, min_val=-1, max_val=1, name="socio_political")
    ]
    
    # Normalize socio_political to 0-1 for kernel
    L_normalized = [
        L[0],
        L[1],
        L[2],
        (L[3] + 1) / 2  # Convert -1,1 to 0,1
    ]
    
    W = list(WEIGHTS.values())
    I = [1.0, 1.0, 1.0, 1.0]
    
    # Calculate Mantic score
    M, S, attr = mantic_kernel(W, L_normalized, I, f_time)
    
    # Detection logic
    alert = None
    drift_direction = "stable"
    strategy_pivot = None
    
    # Check precedent strength
    weak_precedent = L[1] < PRECEDENT_THRESHOLD
    
    # Check alignment between black letter and precedent
    statutory_precedent_gap = abs(L[0] - L[1])
    
    # Interpret socio_political drift
    if L[3] > 0.5:
        drift_direction = "right"
    elif L[3] < -0.5:
        drift_direction = "left"
    elif abs(L[3]) > 0.3:
        drift_direction = "fragmenting"
    
    if weak_precedent and statutory_precedent_gap > DRIFT_THRESHOLD:
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
    elif statutory_precedent_gap > DRIFT_THRESHOLD:
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
    
    return {
        "alert": alert,
        "drift_direction": drift_direction,
        "strategy_pivot": strategy_pivot,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "socio_political_raw": float(L[3]),
        "precedent_strength": float(L[1])
    }


if __name__ == "__main__":
    print("=== Legal Precedent Drift Alert ===\n")
    
    # Test 1: Precedent crisis with rightward drift
    print("Test 1: Precedent crisis + rightward drift")
    result = detect(black_letter=0.8, precedent=0.3, operational=0.7, socio_political=0.6)
    print(f"  Alert: {result['alert']}")
    print(f"  Drift Direction: {result['drift_direction']}")
    print(f"  Strategy Pivot: {result['strategy_pivot']}\n")
    
    # Test 2: Stable precedent
    print("Test 2: Stable precedent")
    result = detect(black_letter=0.75, precedent=0.8, operational=0.7, socio_political=0.1)
    print(f"  Alert: {result['alert']}")
    print(f"  Drift Direction: {result['drift_direction']}")
    print(f"  Strategy Pivot: {result['strategy_pivot']}\n")
    
    # Test 3: Leftward drift
    print("Test 3: Interpretive conflict + leftward drift")
    result = detect(black_letter=0.3, precedent=0.7, operational=0.6, socio_political=-0.6)
    print(f"  Alert: {result['alert']}")
    print(f"  Drift Direction: {result['drift_direction']}")

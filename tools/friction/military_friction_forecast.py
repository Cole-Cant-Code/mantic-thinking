"""
Military: Friction Forecast Engine

Identifies where tactical plans hit logistics or political constraints.

Input Layers:
    maneuver: Tactical maneuver feasibility (0-1)
    intelligence: Intelligence confidence (0-1)
    sustainment: Logistics sustainability (0-1)
    political: Political authorization level (0-1)

Output:
    alert: Detection message or None
    bottleneck: Which layer is the primary constraint
    risk_rating: high/medium/low
    m_score: Final mantic anomaly score
    spatial_component: Raw S value
    layer_attribution: Percentage contribution per layer
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from core.mantic_kernel import mantic_kernel
from core.validators import clamp_input, format_attribution


# Domain weights (must sum to 1)
WEIGHTS = {
    'maneuver': 0.30,
    'intelligence': 0.25,
    'sustainment': 0.25,
    'political': 0.20
}

LAYER_NAMES = ['maneuver', 'intelligence', 'sustainment', 'political']

# Detection thresholds
BOTTLENECK_THRESHOLD = 0.4
RISK_THRESHOLD_HIGH = 0.6
RISK_THRESHOLD_MEDIUM = 0.4


def detect(maneuver, intelligence, sustainment, political, f_time=1.0):
    """
    Detect friction points in military operations.
    
    Args:
        maneuver: Tactical maneuver feasibility (0-1)
        intelligence: Intelligence confidence (0-1)
        sustainment: Logistics sustainability (0-1)
        political: Political authorization level (0-1)
        f_time: Temporal kernel multiplier (default 1.0)
    
    Returns:
        dict with alert, bottleneck, risk_rating, m_score, etc.
    
    Example:
        >>> result = detect(
        ...     maneuver=0.8,
        ...     intelligence=0.7,
        ...     sustainment=0.3,
        ...     political=0.6
        ... )
        >>> print(result['bottleneck'])
        'sustainment'
    """
    # Clamp inputs
    L = [
        clamp_input(maneuver, name="maneuver"),
        clamp_input(intelligence, name="intelligence"),
        clamp_input(sustainment, name="sustainment"),
        clamp_input(political, name="political")
    ]
    
    W = list(WEIGHTS.values())
    I = [1.0, 1.0, 1.0, 1.0]
    
    # Calculate Mantic score
    M, S, attr = mantic_kernel(W, L, I, f_time)
    
    # Detection logic
    alert = None
    bottleneck = None
    risk_rating = "low"
    
    # Find the lowest layer (primary bottleneck)
    min_value = min(L)
    min_index = L.index(min_value)
    bottleneck = LAYER_NAMES[min_index]
    
    # Calculate gap between tactical (maneuver+intel) and support (sustainment+political)
    tactical_avg = (L[0] + L[1]) / 2
    support_avg = (L[2] + L[3]) / 2
    friction_gap = abs(tactical_avg - support_avg)
    
    # Determine risk rating
    if friction_gap > RISK_THRESHOLD_HIGH or min_value < 0.3:
        risk_rating = "high"
    elif friction_gap > RISK_THRESHOLD_MEDIUM or min_value < 0.5:
        risk_rating = "medium"
    
    # Generate alerts based on bottleneck type
    if bottleneck == "sustainment" and L[2] < BOTTLENECK_THRESHOLD:
        alert = "LOGISTICS BOTTLENECK: Tactical plan viable but sustainment insufficient"
    elif bottleneck == "political" and L[3] < BOTTLENECK_THRESHOLD:
        alert = "POLITICAL CONSTRAINT: Operation feasible but lacks political authorization/flexibility"
    elif bottleneck == "intelligence" and L[1] < BOTTLENECK_THRESHOLD:
        alert = "INTELLIGENCE GAP: Significant unknowns in operational environment"
    elif bottleneck == "maneuver":
        alert = "TACTICAL LIMITATION: Maneuver space constrained by terrain or enemy disposition"
    elif friction_gap > RISK_THRESHOLD_MEDIUM:
        alert = f"FRICTION FORECAST: {tactical_avg:.0%} tactical readiness vs {support_avg:.0%} support capability"
    
    return {
        "alert": alert,
        "bottleneck": bottleneck,
        "risk_rating": risk_rating,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "tactical_readiness": float(tactical_avg),
        "support_capability": float(support_avg),
        "friction_gap": float(friction_gap)
    }


if __name__ == "__main__":
    print("=== Military Friction Forecast Engine ===\n")
    
    # Test 1: Logistics bottleneck
    print("Test 1: Logistics bottleneck (sustainment low)")
    result = detect(maneuver=0.8, intelligence=0.7, sustainment=0.3, political=0.6)
    print(f"  Alert: {result['alert']}")
    print(f"  Bottleneck: {result['bottleneck']}")
    print(f"  Risk Rating: {result['risk_rating']}\n")
    
    # Test 2: Balanced capability
    print("Test 2: Balanced capability")
    result = detect(maneuver=0.75, intelligence=0.8, sustainment=0.7, political=0.8)
    print(f"  Alert: {result['alert']}")
    print(f"  Bottleneck: {result['bottleneck']}")
    print(f"  Risk Rating: {result['risk_rating']}\n")
    
    # Test 3: Political constraint
    print("Test 3: Political constraint")
    result = detect(maneuver=0.8, intelligence=0.75, sustainment=0.7, political=0.25)
    print(f"  Alert: {result['alert']}")
    print(f"  Bottleneck: {result['bottleneck']}")
    print(f"  Risk Rating: {result['risk_rating']}")

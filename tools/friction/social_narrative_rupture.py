"""
Social/Cultural: Narrative Rupture Detector

Catches virality that outpaces institutional sense-making capacity.

Input Layers:
    individual: Individual sentiment velocity (0-1)
    network: Network propagation speed (0-1)
    institutional: Institutional response lag (0-1, higher = slower response)
    cultural: Cultural archetype alignment (-1 to 1, where -1 = counter-narrative, 1 = aligned)

Output:
    alert: Detection message or None
    rupture_timing: imminent/ongoing/contained
    recommended_adjustment: Strategy recommendation
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
    'individual': 0.25,
    'network': 0.30,
    'institutional': 0.25,
    'cultural': 0.20
}

LAYER_NAMES = ['individual', 'network', 'institutional', 'cultural']

# Detection thresholds
RAPID_PROPAGATION = 0.7
INSTITUTIONAL_LAG = 0.6
Rupture_THRESHOLD = 0.5


def detect(individual, network, institutional, cultural, f_time=1.0):
    """
    Detect narrative ruptures in social/cultural systems.
    
    Args:
        individual: Individual sentiment velocity (0-1)
        network: Network propagation speed (0-1)
        institutional: Institutional response lag (0-1, higher = slower)
        cultural: Cultural archetype alignment (-1 to 1)
        f_time: Temporal kernel multiplier (default 1.0)
    
    Returns:
        dict with alert, rupture_timing, recommended_adjustment, m_score, etc.
    
    Example:
        >>> result = detect(
        ...     individual=0.8,
        ...     network=0.9,
        ...     institutional=0.7,
        ...     cultural=-0.4
        ... )
        >>> print(result['rupture_timing'])
        'imminent'
    """
    # Clamp inputs
    L = [
        clamp_input(individual, name="individual"),
        clamp_input(network, name="network"),
        clamp_input(institutional, name="institutional"),
        clamp_input(cultural, min_val=-1, max_val=1, name="cultural")
    ]
    
    # Normalize cultural to 0-1 for kernel
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
    rupture_timing = "contained"
    recommended_adjustment = None
    
    # Calculate propagation vs response gap
    propagation_speed = (L[0] + L[1]) / 2
    institutional_capacity = 1 - L[2]  # Invert: higher institutional = lower capacity
    
    velocity_gap = propagation_speed - institutional_capacity
    
    # Cultural counter-alignment magnitude
    cultural_stress = abs(L[3])
    is_counter_narrative = L[3] < -0.3
    
    # Determine rupture timing
    if velocity_gap > Rupture_THRESHOLD and propagation_speed > RAPID_PROPAGATION:
        rupture_timing = "imminent"
        if is_counter_narrative:
            alert = "NARRATIVE RUPTURE IMMINENT: Counter-cultural narrative spreading faster than institutional response"
            recommended_adjustment = (
                "Deploy rapid response team. Narrative is counter to cultural archetypes "
                "and spreading at {:.0%} velocity with {:.0%} institutional lag. "
                "Consider reframing rather than direct counter-messaging."
                .format(propagation_speed, L[2])
            )
        else:
            alert = "VIRALITY CRISIS: Aligned narrative outpacing institutional capacity"
            recommended_adjustment = (
                "Scale institutional response mechanisms. Positive narrative becoming "
                "uncontrollable. Establish narrative ownership before external actors co-opt."
            )
    elif velocity_gap > 0.3:
        rupture_timing = "ongoing"
        if L[2] > INSTITUTIONAL_LAG:
            alert = "SENSE-MAKING GAP: Institutional response significantly lagging narrative spread"
            recommended_adjustment = (
                "Accelerate decision cycles. Current lag of {:.0%} exceeds safe threshold. "
                "Consider delegating authority to lower levels for faster response."
                .format(L[2])
            )
        else:
            alert = "VELOCITY MISMATCH: Narrative propagation exceeding normal institutional pace"
            recommended_adjustment = "Monitor closely and prepare rapid response protocols."
    elif is_counter_narrative and L[1] > 0.6:
        rupture_timing = "ongoing"
        alert = "CULTURAL FRICTION: Counter-archetype narrative gaining network traction"
        recommended_adjustment = (
            "Assess cultural resonance. May indicate deeper cultural shift requiring "
            "narrative strategy revision rather than tactical response."
        )
    else:
        recommended_adjustment = "Current narrative management approach sufficient."
    
    return {
        "alert": alert,
        "rupture_timing": rupture_timing,
        "recommended_adjustment": recommended_adjustment,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "propagation_speed": float(propagation_speed),
        "institutional_capacity": float(institutional_capacity),
        "velocity_gap": float(velocity_gap),
        "cultural_alignment": float(L[3])
    }


if __name__ == "__main__":
    print("=== Social Narrative Rupture Detector ===\n")
    
    # Test 1: Imminent rupture (counter-cultural + fast spread)
    print("Test 1: Counter-cultural narrative spreading fast")
    result = detect(individual=0.8, network=0.9, institutional=0.7, cultural=-0.6)
    print(f"  Alert: {result['alert']}")
    print(f"  Rupture Timing: {result['rupture_timing']}")
    print(f"  Recommended Adjustment: {result['recommended_adjustment']}\n")
    
    # Test 2: Contained narrative
    print("Test 2: Contained narrative")
    result = detect(individual=0.4, network=0.3, institutional=0.3, cultural=0.5)
    print(f"  Alert: {result['alert']}")
    print(f"  Rupture Timing: {result['rupture_timing']}")
    print(f"  Adjustment: {result['recommended_adjustment']}\n")
    
    # Test 3: Sense-making gap
    print("Test 3: Institutional lag (slow response)")
    result = detect(individual=0.7, network=0.75, institutional=0.8, cultural=0.2)
    print(f"  Alert: {result['alert']}")
    print(f"  Rupture Timing: {result['rupture_timing']}")

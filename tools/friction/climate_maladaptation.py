"""
Climate: Maladaptation Preventer

Blocks solutions that solve immediate micro problems but create macro/meta harms.

Input Layers:
    atmospheric: Atmospheric condition metrics (0-1)
    ecological: Ecosystem health indicators (0-1)
    infrastructure: Infrastructure resilience (0-1)
    policy: Policy coherence score (0-1)

Output:
    alert: Detection message or None
    decision: proceed/caution/block
    alternative_suggestion: Recommended alternative approach
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
    'atmospheric': 0.25,
    'ecological': 0.30,
    'infrastructure': 0.25,
    'policy': 0.20
}

LAYER_NAMES = ['atmospheric', 'ecological', 'infrastructure', 'policy']

# Detection thresholds
BLOCK_THRESHOLD = 0.6
CAUTION_THRESHOLD = 0.4


def detect(atmospheric, ecological, infrastructure, policy, f_time=1.0):
    """
    Detect maladaptation risks in climate interventions.
    
    Args:
        atmospheric: Atmospheric condition metrics (0-1)
        ecological: Ecosystem health indicators (0-1)
        infrastructure: Infrastructure resilience (0-1)
        policy: Policy coherence score (0-1)
        f_time: Temporal kernel multiplier (default 1.0)
    
    Returns:
        dict with alert, decision, alternative_suggestion, m_score, etc.
    
    Example:
        >>> result = detect(
        ...     atmospheric=0.7,
        ...     ecological=0.2,
        ...     infrastructure=0.8,
        ...     policy=0.3
        ... )
        >>> print(result['decision'])
        'block'
    """
    # Clamp inputs
    L = [
        clamp_input(atmospheric, name="atmospheric"),
        clamp_input(ecological, name="ecological"),
        clamp_input(infrastructure, name="infrastructure"),
        clamp_input(policy, name="policy")
    ]
    
    W = list(WEIGHTS.values())
    I = [1.0, 1.0, 1.0, 1.0]
    
    # Calculate Mantic score
    M, S, attr = mantic_kernel(W, L, I, f_time)
    
    # Detection logic
    alert = None
    decision = "proceed"
    alternative_suggestion = None
    
    # Check for infrastructure-heavy, ecology-light solutions
    infra_eco_gap = L[2] - L[1]
    
    # Check for policy coherence
    low_policy = L[3] < 0.3
    
    # Check for atmospheric short-term focus
    short_term_focus = L[0] > 0.6 and L[1] < 0.4
    
    maladaptation_score = 0.0
    
    if infra_eco_gap > 0.5:
        maladaptation_score = infra_eco_gap
        if L[1] < 0.3:
            decision = "block"
            alert = "MALADAPTATION RISK: Infrastructure solution threatens ecosystem collapse"
            alternative_suggestion = (
                "Integrate nature-based solutions. Current plan prioritizes infrastructure "
                "(resilience: {:.1f}) over ecological health ({:.1f}). Consider green infrastructure alternatives."
                .format(L[2], L[1])
            )
        else:
            decision = "caution"
            alert = "MALADAPTATION WARNING: Infrastructure-heavy solution may have ecological side effects"
            alternative_suggestion = (
                "Add ecological safeguards. Monitor ecosystem indicators during implementation."
            )
    elif short_term_focus:
        maladaptation_score = L[0] - L[1]
        if L[3] < 0.4:
            decision = "block"
            alert = "MALADAPTATION RISK: Short-term atmospheric fix without policy framework or ecological consideration"
            alternative_suggestion = (
                "Develop integrated approach with policy coherence and ecological monitoring. "
                "Avoid atmospheric-only interventions."
            )
        else:
            decision = "caution"
            alert = "MALADAPTATION WARNING: Atmospheric intervention may have downstream ecological impacts"
            alternative_suggestion = "Strengthen ecological monitoring and adaptive management protocols."
    elif low_policy and (L[0] > 0.5 or L[2] > 0.5):
        decision = "caution"
        maladaptation_score = 0.4
        alert = "POLICY GAP: Technical solution lacks policy coherence - may face implementation barriers"
        alternative_suggestion = "Develop supporting policy framework before proceeding with technical implementation."
    
    return {
        "alert": alert,
        "decision": decision,
        "alternative_suggestion": alternative_suggestion,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "maladaptation_score": float(maladaptation_score)
    }


if __name__ == "__main__":
    print("=== Climate Maladaptation Preventer ===\n")
    
    # Test 1: Infrastructure-heavy, ecological damage (BLOCK)
    print("Test 1: Infrastructure solution threatening ecosystem")
    result = detect(atmospheric=0.7, ecological=0.2, infrastructure=0.8, policy=0.3)
    print(f"  Decision: {result['decision']}")
    print(f"  Alert: {result['alert']}")
    print(f"  Alternative: {result['alternative_suggestion']}\n")
    
    # Test 2: Normal balanced approach (PROCEED)
    print("Test 2: Balanced approach")
    result = detect(atmospheric=0.6, ecological=0.7, infrastructure=0.6, policy=0.7)
    print(f"  Decision: {result['decision']}")
    print(f"  Alert: {result['alert']}\n")
    
    # Test 3: Short-term focus without policy (BLOCK)
    print("Test 3: Short-term atmospheric fix without policy")
    result = detect(atmospheric=0.8, ecological=0.3, infrastructure=0.6, policy=0.2)
    print(f"  Decision: {result['decision']}")
    print(f"  Alert: {result['alert']}")

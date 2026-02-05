"""
Legal: Precedent Seeding Optimizer

Spots windows when socio-political climate, institutional capacity,
statutory ambiguity, and circuit splits align for favorable case law establishment.

Confluence Logic: Receptive climate + ambiguity + capacity + split = ripe for precedent
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
from core.mantic_kernel import mantic_kernel
from core.validators import clamp_input, format_attribution


# Climate and ambiguity weighted higher
WEIGHTS = [0.30, 0.20, 0.30, 0.20]
LAYER_NAMES = ['socio_political', 'institutional_capacity', 'statutory_ambiguity', 'circuit_split']

# Thresholds
RIPENESS_THRESHOLD = 0.60
SPLIT_THRESHOLD = 0.50


def detect(socio_political_climate, institutional_capacity, statutory_ambiguity, circuit_split, f_time=1.0):
    """
    Spot windows for favorable precedent establishment.
    
    Args:
        socio_political_climate: Receptiveness to legal change (0-1)
        institutional_capacity: Courts/resources to handle case (0-1)
        statutory_ambiguity: Statutory text ambiguity/openness (0-1)
        circuit_split: Degree of circuit split (0-1)
        f_time: Temporal kernel multiplier (default 1.0)
    
    Returns:
        dict with window_detected, precedent_opportunity, strategy, etc.
    """
    # Clamp inputs
    L = [
        clamp_input(socio_political_climate, name="socio_political_climate"),
        clamp_input(institutional_capacity, name="institutional_capacity"),
        clamp_input(statutory_ambiguity, name="statutory_ambiguity"),
        clamp_input(circuit_split, name="circuit_split")
    ]
    
    # Interactions: Climate + Ambiguity compound, Capacity + Split enable action
    I = [1.0, 1.0, 1.0, 1.0]
    
    # Calculate Mantic score
    M, S, attr = mantic_kernel(WEIGHTS, L, I, f_time)
    
    # CONFLUENCE LOGIC: Ripeness for precedent setting
    # Ripeness = receptive climate + ambiguity floor, boosted by capacity
    # Must have circuit split to create urgency
    climate_ambiguity_floor = min(L[0], L[2])
    ripeness = climate_ambiguity_floor * L[1]  # Floor is climate+ambiguity, scaled by capacity
    
    window_detected = False
    precedent_opportunity = None
    circuit_split_exploitable = None
    strategy = None
    forum_recommendation = None
    timeline = None
    
    if ripeness > RIPENESS_THRESHOLD and circuit_split > SPLIT_THRESHOLD:
        window_detected = True
        circuit_split_exploitable = True
        
        # Determine opportunity level
        if ripeness > 0.80 and L[3] > 0.75:
            precedent_opportunity = "EXCEPTIONAL"
            strategy = ("File test case in most favorable circuit immediately. "
                       "Exceptional convergence of socio-political tailwinds, statutory ambiguity, "
                       "and circuit split creates Supreme Court grant likelihood. "
                       "Maximize ripple effects through amicus coordination.")
            forum_recommendation = "File in 9th or DC Circuit (depending on issue) with expedited briefing"
            timeline = "6-12 months to circuit decision, 18-24 months to potential SCOTUS"
        elif ripeness > 0.70:
            precedent_opportunity = "HIGH"
            strategy = ("Pursue test case aggressively. Socio-political climate favorable, "
                       "statutory ambiguity provides doctrinal opening, circuit split creates urgency. "
                       "Monitor parallel cases in other circuits.")
            forum_recommendation = "Forum shop for most favorable circuit with active split"
            timeline = "12-18 months to circuit decision"
        else:
            precedent_opportunity = "MODERATE"
            strategy = ("Begin test case development. Window is open but not exceptional. "
                       "Build record and coalition while conditions favorable.")
            forum_recommendation = "Select circuit with favorable precedent + active split"
            timeline = "18-24 months to decision"
        
        return {
            "window_detected": True,
            "precedent_opportunity": precedent_opportunity,
            "ripeness_score": float(ripeness),
            "circuit_split_exploitable": circuit_split_exploitable,
            "strategy": strategy,
            "forum_recommendation": forum_recommendation,
            "timeline": timeline,
            "m_score": float(M),
            "spatial_component": float(S),
            "layer_attribution": format_attribution(attr, LAYER_NAMES),
            "favorable_conditions": {
                "socio_political_receptiveness": float(L[0]),
                "statutory_ambiguity": float(L[2]),
                "institutional_capacity": float(L[1]),
                "circuit_split_strength": float(L[3])
            }
        }
    
    # No window - explain why
    if L[3] <= SPLIT_THRESHOLD:
        limiting_factor = "No exploitable circuit split"
    elif L[0] <= RIPENESS_THRESHOLD:
        limiting_factor = "Socio-political climate not receptive"
    elif L[2] <= RIPENESS_THRESHOLD:
        limiting_factor = "Statutory text too clear/ambiguous"
    else:
        limiting_factor = "Insufficient institutional capacity"
    
    return {
        "window_detected": False,
        "ripeness_score": float(ripeness),
        "precedent_opportunity": "LOW",
        "circuit_split_exploitable": L[3] > SPLIT_THRESHOLD,
        "limiting_factor": limiting_factor,
        "m_score": float(M),
        "spatial_component": float(S),
        "status": f"Precedent window not yet ripe. {limiting_factor}.",
        "recommendation": "Monitor for circuit split development or socio-political shift."
    }


if __name__ == "__main__":
    print("=== Legal Precedent Seeding Optimizer ===\n")
    
    # Test 1: Exceptional opportunity
    print("Test 1: Exceptional precedent opportunity")
    result = detect(
        socio_political_climate=0.85,
        institutional_capacity=0.80,
        statutory_ambiguity=0.88,
        circuit_split=0.82
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Opportunity Level: {result.get('precedent_opportunity', 'N/A')}")
    print(f"  Ripeness Score: {result.get('ripeness_score', 0):.3f}")
    print(f"  Timeline: {result.get('timeline', 'N/A')}")
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
    # Test 2: High opportunity
    print("Test 2: High opportunity")
    result = detect(
        socio_political_climate=0.75,
        institutional_capacity=0.70,
        statutory_ambiguity=0.78,
        circuit_split=0.72
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Opportunity Level: {result.get('precedent_opportunity', 'N/A')}")
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
    # Test 3: No window (no circuit split)
    print("Test 3: No window (no circuit split)")
    result = detect(
        socio_political_climate=0.80,
        institutional_capacity=0.75,
        statutory_ambiguity=0.82,
        circuit_split=0.30  # No split
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Limiting Factor: {result.get('limiting_factor', 'N/A')}")

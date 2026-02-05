"""
Social/Cultural: Catalytic Alignment Detector

Spots transformative potential when individual readiness, network bridges,
policy windows, and paradigm momentum converge.

Confluence Logic: Readiness + Bridges + Policy + Momentum = Movement Ready
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
from core.mantic_kernel import mantic_kernel
from core.validators import clamp_input, format_attribution


# Network and Policy weighted higher for catalysis
WEIGHTS = [0.20, 0.30, 0.30, 0.20]
LAYER_NAMES = ['individual_readiness', 'network_bridges', 'policy_window', 'paradigm_momentum']

# Thresholds
CATALYST_THRESHOLD = 0.65
TRANSFORMATIVE_THRESHOLD = 0.80


def detect(individual_readiness, network_bridges, policy_window, paradigm_momentum, f_time=1.0):
    """
    Detect transformative potential for movement-building.
    
    Args:
        individual_readiness: Population psychological readiness (0-1)
        network_bridges: Cross-cutting network connections (0-1)
        policy_window: Policy opportunity open (0-1)
        paradigm_momentum: Cultural paradigm shift underway (0-1)
        f_time: Temporal kernel multiplier (default 1.0)
    
    Returns:
        dict with window_detected, movement_potential, recommended_action, etc.
    """
    # Clamp inputs
    L = [
        clamp_input(individual_readiness, name="individual_readiness"),
        clamp_input(network_bridges, name="network_bridges"),
        clamp_input(policy_window, name="policy_window"),
        clamp_input(paradigm_momentum, name="paradigm_momentum")
    ]
    
    # Interactions: Network bridges amplify other factors (capped at 1.0)
    I = [1.0, min(1.0, 0.9 + L[1]*0.1), 1.0, 1.0]
    
    # Calculate Mantic score
    M, S, attr = mantic_kernel(WEIGHTS, L, I, f_time)
    
    # CONFLUENCE LOGIC: Catalysis calculation
    # Catalyst = floor of readiness/bridges/policy (these must all be present)
    # Transformative potential boosted by paradigm momentum
    critical_factors = [L[0], L[1], L[2]]  # Readiness, Bridges, Policy
    catalyst = min(critical_factors)
    transformative_potential = catalyst * (1 + L[3]*0.5)  # Boosted by paradigm shift
    
    window_detected = False
    movement_potential = None
    critical_mass_risk = None
    recommended_action = None
    duration_estimate = None
    mobilization_urgency = None
    
    if catalyst > CATALYST_THRESHOLD:
        window_detected = True
        
        # Determine movement potential
        if transformative_potential > TRANSFORMATIVE_THRESHOLD and all(l > 0.75 for l in L):
            movement_potential = "TRANSFORMATIVE"
            critical_mass_risk = "Network bridges activated but window is narrow - act before policy closes"
            recommended_action = ("Mobilize immediately across all channels. Policy window + Network topology + "
                                 "Individual readiness creates rare transformative potential. Deploy resources fully.")
            duration_estimate = "Policy window typically 6-18 months; peak mobilization window 3-6 months"
            mobilization_urgency = "CRITICAL - Peak convergence now"
        elif transformative_potential > 0.70:
            movement_potential = "HIGH"
            critical_mass_risk = "Network and policy favorable but paradigm momentum still building"
            recommended_action = ("Accelerate mobilization. Prepare for rapid scaling. Window is open but "
                                 "will not remain indefinitely.")
            duration_estimate = "12-24 months sustained effort"
            mobilization_urgency = "HIGH - Mobilize within 30 days"
        else:
            movement_potential = "MODERATE"
            critical_mass_risk = "Some factors present but transformational potential limited"
            recommended_action = ("Build infrastructure. Current alignment is favorable but not exceptional. "
                                 "Prepare for future convergence.")
            duration_estimate = "2-3 years for major shift"
            mobilization_urgency = "MODERATE - Build capacity"
        
        return {
            "window_detected": True,
            "movement_potential": movement_potential,
            "catalyst_score": float(catalyst),
            "transformative_potential": float(transformative_potential),
            "critical_mass_risk": critical_mass_risk,
            "recommended_action": recommended_action,
            "duration_estimate": duration_estimate,
            "mobilization_urgency": mobilization_urgency,
            "m_score": float(M),
            "spatial_component": float(S),
            "layer_attribution": format_attribution(attr, LAYER_NAMES),
            "alignment_status": {
                "individual_readiness": float(L[0]),
                "network_bridges": float(L[1]),
                "policy_window": float(L[2]),
                "paradigm_momentum": float(L[3])
            }
        }
    
    # No catalytic window
    below_threshold = [LAYER_NAMES[i] for i, l in enumerate(L) if l <= CATALYST_THRESHOLD]
    
    return {
        "window_detected": False,
        "catalyst_score": float(catalyst),
        "movement_potential": "LOW",
        "limiting_factors": below_threshold,
        "m_score": float(M),
        "spatial_component": float(S),
        "status": f"Catalytic alignment not achieved. {', '.join(below_threshold)} below threshold.",
        "recommendation": "Continue base-building. Focus on strengthening network bridges and individual readiness."
    }


if __name__ == "__main__":
    print("=== Social Catalytic Alignment Detector ===\n")
    
    # Test 1: Transformative potential
    print("Test 1: Transformative potential (all > 0.75)")
    result = detect(
        individual_readiness=0.82,
        network_bridges=0.85,
        policy_window=0.80,
        paradigm_momentum=0.88
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Movement Potential: {result.get('movement_potential', 'N/A')}")
    print(f"  Catalyst Score: {result.get('catalyst_score', 0):.3f}")
    print(f"  Transformative Potential: {result.get('transformative_potential', 0):.3f}")
    print(f"  Mobilization Urgency: {result.get('mobilization_urgency', 'N/A')}")
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
    # Test 2: High potential
    print("Test 2: High potential")
    result = detect(
        individual_readiness=0.75,
        network_bridges=0.78,
        policy_window=0.72,
        paradigm_momentum=0.70
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Movement Potential: {result.get('movement_potential', 'N/A')}")
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
    # Test 3: No window (policy window closed)
    print("Test 3: No window (policy window closed)")
    result = detect(
        individual_readiness=0.80,
        network_bridges=0.75,
        policy_window=0.40,  # Closed
        paradigm_momentum=0.70
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Limiting Factors: {result.get('limiting_factors', [])}")

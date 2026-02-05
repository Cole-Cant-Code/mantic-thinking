"""
Military: Strategic Initiative Window

Identifies decisive action opportunities when intelligence ambiguity,
positional advantage, logistic readiness, and political authorization synchronize.

Confluence Logic: Fog helps us + we're ready + authorized = initiative window
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
from core.mantic_kernel import mantic_kernel
from core.validators import clamp_input, format_attribution


# Equal weight for initiative requirements
WEIGHTS = [0.25, 0.25, 0.25, 0.25]
LAYER_NAMES = ['enemy_ambiguity', 'positional_advantage', 'logistic_readiness', 'authorization_clarity']

# Thresholds
INITIATIVE_THRESHOLD = 0.70
MINIMUM_FLOOR = 0.60


def detect(enemy_ambiguity, positional_advantage, logistic_readiness, authorization_clarity, f_time=1.0):
    """
    Identify decisive action windows (offensive leverage).
    
    Args:
        enemy_ambiguity: Intelligence gaps favoring surprise (0-1)
        positional_advantage: Geographical/tactical position (0-1)
        logistic_readiness: Sustainment capability ready (0-1)
        authorization_clarity: Political authority clear (0-1)
        f_time: Temporal kernel multiplier (default 1.0)
    
    Returns:
        dict with window_detected, maneuver_type, advantage, etc.
    """
    # Clamp inputs
    L = [
        clamp_input(enemy_ambiguity, name="enemy_ambiguity"),
        clamp_input(positional_advantage, name="positional_advantage"),
        clamp_input(logistic_readiness, name="logistic_readiness"),
        clamp_input(authorization_clarity, name="authorization_clarity")
    ]
    
    # Interactions: Ambiguity + Position compound for advantage
    I = [1.0, 1.0, 1.0, 1.0]
    
    # Calculate Mantic score
    M, S, attr = mantic_kernel(WEIGHTS, L, I, f_time)
    
    # CONFLUENCE LOGIC: Initiative window calculation
    # Initiative = min(Ambiguity, Readiness, Auth) * Position
    # Fog helps us, we're ready, we're authorized, AND we have position
    critical_factors = [L[0], L[2], L[3]]  # Ambiguity, Readiness, Authorization
    initiative_floor = min(critical_factors)
    initiative_score = initiative_floor * L[1]  # Scaled by positional advantage
    
    window_detected = False
    maneuver_type = None
    advantage_description = None
    recommended_action = None
    execution_window = None
    risk_assessment = None
    
    if initiative_score > INITIATIVE_THRESHOLD and min(L) > MINIMUM_FLOOR:
        window_detected = True
        
        # Determine initiative quality
        if initiative_score > 0.85 and all(l > 0.75 for l in L):
            maneuver_type = "DECISIVE_ACTION"
            advantage_description = ("Synchronized ambiguity/readiness/authorization with "
                                    "strong positional edge - rare convergence")
            recommended_action = "Execute within 24-48 hours before fog lifts or enemy adapts"
            execution_window = "24-48 hours (highly perishable)"
            risk_assessment = "LOW - All factors favorable"
        elif initiative_score > 0.75:
            maneuver_type = "OFFENSIVE_OPERATION"
            advantage_description = "Strong initiative conditions across multiple factors"
            recommended_action = "Prepare for execution within 72 hours"
            execution_window = "48-72 hours"
            risk_assessment = "MODERATE - Monitor for enemy counter-moves"
        else:
            maneuver_type = "TACTICAL_INITIATIVE"
            advantage_description = "Favorable but not exceptional initiative window"
            recommended_action = "Develop courses of action, prepare for exploitation"
            execution_window = "72-96 hours"
            risk_assessment = "MODERATE-HIGH - Contingency plans required"
        
        return {
            "window_detected": True,
            "maneuver_type": maneuver_type,
            "initiative_score": float(initiative_score),
            "advantage": advantage_description,
            "recommended_action": recommended_action,
            "execution_window": execution_window,
            "risk_assessment": risk_assessment,
            "m_score": float(M),
            "spatial_component": float(S),
            "layer_attribution": format_attribution(attr, LAYER_NAMES),
            "synchronization_status": {
                "enemy_ambiguity": float(L[0]),
                "positional_advantage": float(L[1]),
                "logistic_readiness": float(L[2]),
                "authorization_clarity": float(L[3])
            }
        }
    
    # No initiative window
    limiting_factors = []
    if L[0] <= MINIMUM_FLOOR:
        limiting_factors.append("insufficient enemy ambiguity (too clear)")
    if L[1] <= MINIMUM_FLOOR:
        limiting_factors.append("weak positional advantage")
    if L[2] <= MINIMUM_FLOOR:
        limiting_factors.append("logistics not ready")
    if L[3] <= MINIMUM_FLOOR:
        limiting_factors.append("authorization unclear")
    
    return {
        "window_detected": False,
        "initiative_score": float(initiative_score),
        "maneuver_type": "DEFENSIVE_POSTURE",
        "limiting_factors": limiting_factors,
        "m_score": float(M),
        "spatial_component": float(S),
        "status": f"Initiative window closed. {', '.join(limiting_factors) if limiting_factors else 'Conditions unfavorable'}.",
        "recommendation": "Maintain readiness, seek to improve positional advantage or wait for authorization."
    }


if __name__ == "__main__":
    print("=== Military Strategic Initiative Window ===\n")
    
    # Test 1: Decisive action window
    print("Test 1: Decisive action window")
    result = detect(
        enemy_ambiguity=0.85,      # Fog of war helps us
        positional_advantage=0.88, # Good position
        logistic_readiness=0.82,   # Ready to go
        authorization_clarity=0.90 # Clear to act
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Maneuver Type: {result.get('maneuver_type', 'N/A')}")
    print(f"  Initiative Score: {result.get('initiative_score', 0):.3f}")
    print(f"  Execution Window: {result.get('execution_window', 'N/A')}")
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
    # Test 2: Offensive operation
    print("Test 2: Offensive operation")
    result = detect(
        enemy_ambiguity=0.75,
        positional_advantage=0.78,
        logistic_readiness=0.72,
        authorization_clarity=0.80
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Maneuver Type: {result.get('maneuver_type', 'N/A')}")
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
    # Test 3: No window (logistics not ready)
    print("Test 3: No window (logistics not ready)")
    result = detect(
        enemy_ambiguity=0.80,
        positional_advantage=0.75,
        logistic_readiness=0.45,  # Too low
        authorization_clarity=0.85
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Limiting Factors: {result.get('limiting_factors', [])}")

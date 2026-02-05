"""
Cybersecurity: Adversary Overreach Detector

Identifies defensive advantage windows when attacker TTPs are stretched,
geopolitically pressured, and operationally fatigued.

Confluence Logic: Attacker strained + defender hardened = counter-attack window
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
from core.mantic_kernel import mantic_kernel
from core.validators import clamp_input, format_attribution


# Threat intel and operational hardening weighted higher
WEIGHTS = [0.30, 0.20, 0.30, 0.20]
LAYER_NAMES = ['threat_stretch', 'geopolitical_pressure', 'operational_hardening', 'tool_reuse_fatigue']

# Thresholds
OVERREACH_THRESHOLD = 0.70
HARDENING_THRESHOLD = 0.60


def detect(threat_intel_stretch, geopolitical_pressure, operational_hardening, tool_reuse_fatigue, f_time=1.0):
    """
    Detect when attacker is vulnerable due to overextension.
    High values = defender advantage window.
    
    Args:
        threat_intel_stretch: Attacker TTPs overextended/visible (0-1)
        geopolitical_pressure: External pressure on attacker (0-1)
        operational_hardening: Defender readiness/hardening (0-1)
        tool_reuse_fatigue: Attacker tool reuse/indicators (0-1)
        f_time: Temporal kernel multiplier (default 1.0)
    
    Returns:
        dict with window_detected, attacker_state, defender_advantage, etc.
    """
    # Clamp inputs
    L = [
        clamp_input(threat_intel_stretch, name="threat_intel_stretch"),
        clamp_input(geopolitical_pressure, name="geopolitical_pressure"),
        clamp_input(operational_hardening, name="operational_hardening"),
        clamp_input(tool_reuse_fatigue, name="tool_reuse_fatigue")
    ]
    
    # Interactions: Stretch + Fatigue compound, Pressure + Hardening synergize
    I = [1.0, 1.0, 1.0, 1.0]
    
    # Calculate Mantic score
    M, S, attr = mantic_kernel(WEIGHTS, L, I, f_time)
    
    # CONFLUENCE LOGIC: Attacker overreach indicators
    # Overreach = high stretch + high pressure + high fatigue, but only if we're hardened
    attacker_strain = (L[0] + L[1] + L[3]) / 3  # Stretch, pressure, fatigue average
    
    window_detected = False
    attacker_state = "RESILIENT"
    defender_advantage = "LOW"
    recommended_action = "Continue monitoring"
    duration_estimate = None
    counter_attack_viability = None
    
    if attacker_strain > OVERREACH_THRESHOLD and L[2] > HARDENING_THRESHOLD:
        window_detected = True
        
        # Determine advantage level
        if attacker_strain > 0.85 and L[2] > 0.75:
            defender_advantage = "CRITICAL"
            attacker_state = "SEVERELY_OVEREXTENDED"
            recommended_action = "Deploy active defense / deception / takedown. Attacker TTPs are brittle and exposed."
            duration_estimate = "24-48 hours before attacker rotates tools"
            counter_attack_viability = "High - consider attribution publication or infrastructure seizure"
        elif attacker_strain > 0.75:
            defender_advantage = "HIGH"
            attacker_state = "OVEREXTENDED"
            recommended_action = "Deploy deception and enhanced monitoring. Prepare for rapid response."
            duration_estimate = "48-72 hour window"
            counter_attack_viability = "Moderate - gather intelligence before acting"
        else:
            defender_advantage = "MODERATE"
            attacker_state = "STRESSED"
            recommended_action = "Increase monitoring. Prepare countermeasures."
            duration_estimate = "72-96 hour window"
            counter_attack_viability = "Low - maintain defensive posture"
        
        return {
            "window_detected": True,
            "attacker_state": attacker_state,
            "defender_advantage": defender_advantage,
            "attacker_strain_score": float(attacker_strain),
            "recommended_action": recommended_action,
            "duration_estimate": duration_estimate,
            "counter_attack_viability": counter_attack_viability,
            "m_score": float(M),
            "spatial_component": float(S),
            "layer_attribution": format_attribution(attr, LAYER_NAMES),
            "strain_indicators": {
                "ttp_stretch": float(L[0]),
                "geopolitical_pressure": float(L[1]),
                "tool_fatigue": float(L[3])
            }
        }
    
    # No window - assess why
    if L[2] <= HARDENING_THRESHOLD:
        limiting_factor = "Defender not sufficiently hardened"
    elif attacker_strain <= OVERREACH_THRESHOLD:
        limiting_factor = "Attacker not showing strain indicators"
    else:
        limiting_factor = "Confluence not achieved"
    
    return {
        "window_detected": False,
        "attacker_state": attacker_state,
        "defender_advantage": defender_advantage,
        "attacker_strain_score": float(attacker_strain),
        "defender_readiness": float(L[2]),
        "limiting_factor": limiting_factor,
        "m_score": float(M),
        "spatial_component": float(S),
        "status": "Defensive window not yet open"
    }


if __name__ == "__main__":
    print("=== Cyber Adversary Overreach Detector ===\n")
    
    # Test 1: Critical overreach
    print("Test 1: Critical overreach (high strain + high hardening)")
    result = detect(
        threat_intel_stretch=0.90,
        geopolitical_pressure=0.85,
        operational_hardening=0.80,
        tool_reuse_fatigue=0.88
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Attacker State: {result.get('attacker_state', 'N/A')}")
    print(f"  Defender Advantage: {result.get('defender_advantage', 'N/A')}")
    print(f"  Strain Score: {result.get('attacker_strain_score', 0):.3f}")
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
    # Test 2: Moderate overreach
    print("Test 2: Moderate overreach")
    result = detect(
        threat_intel_stretch=0.75,
        geopolitical_pressure=0.70,
        operational_hardening=0.75,
        tool_reuse_fatigue=0.72
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Attacker State: {result.get('attacker_state', 'N/A')}")
    print(f"  Defender Advantage: {result.get('defender_advantage', 'N/A')}")
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
    # Test 3: No window (defender not ready)
    print("Test 3: No window (defender not hardened)")
    result = detect(
        threat_intel_stretch=0.85,
        geopolitical_pressure=0.80,
        operational_hardening=0.45,  # Too low
        tool_reuse_fatigue=0.75
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Limiting Factor: {result.get('limiting_factor', 'N/A')}")

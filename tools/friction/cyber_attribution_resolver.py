"""
Cybersecurity: Attribution Uncertainty Resolver

Scores confidence when technical sophistication doesn't align with geopolitical context.

Input Layers:
    technical: Technical sophistication indicators (0-1)
    threat_intel: Threat intelligence confidence (0-1)
    operational_impact: Severity of operational impact (0-1)
    geopolitical: Geopolitical context alignment (0-1)

Output:
    alert: Detection message or None
    confidence: high/medium/low string
    mismatch_explanation: Detailed explanation of the mismatch
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
    'technical': 0.30,
    'threat_intel': 0.25,
    'operational_impact': 0.25,
    'geopolitical': 0.20
}

LAYER_NAMES = ['technical', 'threat_intel', 'operational_impact', 'geopolitical']

# Detection thresholds
THRESHOLD = 0.35
HIGH_TECH_THRESHOLD = 0.8


def detect(technical, threat_intel, operational_impact, geopolitical, f_time=1.0):
    """
    Detect attribution uncertainties in cyber incidents.
    
    Args:
        technical: Technical sophistication indicators (0-1)
        threat_intel: Threat intelligence confidence (0-1)
        operational_impact: Severity of operational impact (0-1)
        geopolitical: Geopolitical context alignment (0-1)
        f_time: Temporal kernel multiplier (default 1.0)
    
    Returns:
        dict with alert, confidence, mismatch_explanation, m_score, etc.
    
    Example:
        >>> result = detect(
        ...     technical=0.9,
        ...     threat_intel=0.3,
        ...     operational_impact=0.8,
        ...     geopolitical=0.2
        ... )
        >>> print(result['confidence'])
        'low'
    """
    # Clamp inputs
    L = [
        clamp_input(technical, name="technical"),
        clamp_input(threat_intel, name="threat_intel"),
        clamp_input(operational_impact, name="operational_impact"),
        clamp_input(geopolitical, name="geopolitical")
    ]
    
    W = list(WEIGHTS.values())
    I = [1.0, 1.0, 1.0, 1.0]
    
    # Calculate Mantic score
    M, S, attr = mantic_kernel(W, L, I, f_time)
    
    # Detection logic
    alert = None
    confidence = "high"
    mismatch_explanation = None
    
    # Check for high technical sophistication with low threat intel
    tech_intel_gap = L[0] - L[1]
    
    # Check for geopolitical misalignment
    geo_mismatch = abs(L[0] - L[3])
    
    # Assess overall confidence
    avg_intel = (L[1] + L[3]) / 2
    
    if tech_intel_gap > THRESHOLD and L[0] > HIGH_TECH_THRESHOLD:
        confidence = "low"
        mismatch_explanation = (
            f"High technical sophistication ({L[0]:.2f}) but weak threat intel ({L[1]:.2f}). "
            "Possible false flag or unknown APT group."
        )
        alert = "ATTRIBUTION GAP: Sophisticated attack with unclear origin"
    elif geo_mismatch > THRESHOLD:
        if L[3] < 0.3 and L[0] > 0.7:
            confidence = "low"
            mismatch_explanation = (
                f"Technical indicators suggest nation-state capability ({L[0]:.2f}) "
                f"but no geopolitical motive/context ({L[3]:.2f}). Possible proxy or mercenary group."
            )
            alert = "GEOPOLITICAL MISMATCH: Capability without context"
        elif L[3] > 0.7 and L[0] < 0.4:
            confidence = "medium"
            mismatch_explanation = (
                f"Geopolitical context suggests high capability actor ({L[3]:.2f}) "
                f"but observed techniques are rudimentary ({L[0]:.2f}). Possible deception or training exercise."
            )
            alert = "CAPABILITY GAP: Expected sophistication not observed"
    elif avg_intel < 0.4:
        confidence = "medium"
        mismatch_explanation = "Limited intelligence on both technical and geopolitical fronts."
        alert = "INTELLIGENCE GAP: Insufficient data for reliable attribution"
    else:
        mismatch_explanation = "Attribution factors align reasonably well."
    
    return {
        "alert": alert,
        "confidence": confidence,
        "mismatch_explanation": mismatch_explanation,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "tech_intel_gap": float(tech_intel_gap),
        "threshold": THRESHOLD
    }


if __name__ == "__main__":
    print("=== Cyber Attribution Uncertainty Resolver ===\n")
    
    # Test 1: High tech, low intel (attribution gap)
    print("Test 1: High sophistication + low threat intel")
    result = detect(technical=0.9, threat_intel=0.3, operational_impact=0.8, geopolitical=0.2)
    print(f"  Alert: {result['alert']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Explanation: {result['mismatch_explanation']}\n")
    
    # Test 2: Normal case (high confidence)
    print("Test 2: Normal alignment")
    result = detect(technical=0.8, threat_intel=0.85, operational_impact=0.7, geopolitical=0.75)
    print(f"  Alert: {result['alert']}")
    print(f"  Confidence: {result['confidence']}\n")
    
    # Test 3: Capability gap
    print("Test 3: Capability gap (low tech, high geopolitical context)")
    result = detect(technical=0.3, threat_intel=0.6, operational_impact=0.5, geopolitical=0.85)
    print(f"  Alert: {result['alert']}")
    print(f"  Confidence: {result['confidence']}")

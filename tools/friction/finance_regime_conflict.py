"""
Finance: Regime Conflict Monitor

Spots when technical price action contradicts fundamentals, flow, or risk signals.

Input Layers:
    technical: Price action signals (0-1)
    macro: Fundamental indicators (0-1)
    flow: Capital flow direction (-1 to 1, where -1 = outflow, 1 = inflow)
    risk: Risk appetite metrics (0-1)

Output:
    alert: Detection message or None
    conflict_type: Type of regime conflict detected
    confidence: 0-1 confidence score
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
    'technical': 0.35,
    'macro': 0.30,
    'flow': 0.20,
    'risk': 0.15
}

LAYER_NAMES = ['technical', 'macro', 'flow', 'risk']

# Detection threshold
THRESHOLD = 0.4


def detect(technical, macro, flow, risk, f_time=1.0):
    """
    Detect regime conflicts in financial markets.
    
    Args:
        technical: Price action signals (0-1)
        macro: Fundamental indicators (0-1)
        flow: Capital flow direction (-1 to 1)
        risk: Risk appetite metrics (0-1)
        f_time: Temporal kernel multiplier (default 1.0)
    
    Returns:
        dict with alert, conflict_type, confidence, m_score, etc.
    
    Example:
        >>> result = detect(
        ...     technical=0.8,
        ...     macro=0.3,
        ...     flow=-0.6,
        ...     risk=0.7
        ... )
        >>> print(result['conflict_type'])
        'technical_macro_divergence'
    """
    # Clamp inputs
    L = [
        clamp_input(technical, name="technical"),
        clamp_input(macro, name="macro"),
        clamp_input(flow, min_val=-1, max_val=1, name="flow"),
        clamp_input(risk, name="risk")
    ]
    
    # Normalize flow to 0-1 for kernel calculation
    L_normalized = [
        L[0],
        L[1],
        (L[2] + 1) / 2,  # Convert -1,1 to 0,1
        L[3]
    ]
    
    W = list(WEIGHTS.values())
    I = [1.0, 1.0, 1.0, 1.0]
    
    # Calculate Mantic score
    M, S, attr = mantic_kernel(W, L_normalized, I, f_time)
    
    # Detection logic
    alert = None
    conflict_type = None
    confidence = 0.0
    
    # Check for technical vs macro divergence
    tech_macro_diff = abs(L[0] - L[1])
    
    # Check for flow contradiction (flow opposite to technical)
    flow_aligned = (L[2] > 0 and L[0] > 0.5) or (L[2] < 0 and L[0] < 0.5)
    
    # Risk-off but technical bullish
    risk_conflict = L[3] < 0.3 and L[0] > 0.7
    
    if tech_macro_diff > THRESHOLD or not flow_aligned or risk_conflict:
        confidence = max(tech_macro_diff, 0.5 if not flow_aligned else 0, 0.6 if risk_conflict else 0)
        
        if tech_macro_diff > THRESHOLD and not flow_aligned:
            conflict_type = "multi_factor_breakdown"
            alert = "REGIME CONFLICT: Technical, fundamental, and flow signals all divergent"
        elif tech_macro_diff > THRESHOLD:
            if L[0] > L[1]:
                conflict_type = "technical_macro_divergence"
                alert = "PRICE-FUNDAMENTAL SPLIT: Technical bullishness unsupported by macro data"
            else:
                conflict_type = "technical_macro_divergence"
                alert = "PRICE-FUNDAMENTAL SPLIT: Technical weakness despite strong fundamentals"
        elif not flow_aligned:
            conflict_type = "flow_contradiction"
            if L[2] < 0:
                alert = "CAPITAL FLIGHT: Price holding despite net outflows - investigate artificial support"
            else:
                alert = "STEALTH ACCUMULATION: Price stagnant despite inflows - possible accumulation phase"
        elif risk_conflict:
            conflict_type = "risk_parity_breakdown"
            alert = "RISK MISMATCH: Risk-off environment with bullish technicals - contrarian trap"
    
    return {
        "alert": alert,
        "conflict_type": conflict_type,
        "confidence": float(confidence),
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "flow_raw": float(L[2]),
        "threshold": THRESHOLD
    }


if __name__ == "__main__":
    print("=== Finance Regime Conflict Monitor ===\n")
    
    # Test 1: Technical-macro divergence
    print("Test 1: Technical bullish + macro bearish + outflows")
    result = detect(technical=0.8, macro=0.3, flow=-0.6, risk=0.7)
    print(f"  Alert: {result['alert']}")
    print(f"  Conflict Type: {result['conflict_type']}")
    print(f"  Confidence: {result['confidence']:.3f}\n")
    
    # Test 2: Normal alignment
    print("Test 2: Normal alignment")
    result = detect(technical=0.7, macro=0.75, flow=0.6, risk=0.6)
    print(f"  Alert: {result['alert']}")
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
    # Test 3: Risk-off with bullish technicals
    print("Test 3: Risk-off with bullish technicals")
    result = detect(technical=0.85, macro=0.7, flow=0.3, risk=0.2)
    print(f"  Alert: {result['alert']}")
    print(f"  Conflict Type: {result['conflict_type']}")

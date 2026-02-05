"""
Finance: Confluence Alpha Engine

Detects asymmetric opportunity when technical setup, macro tailwind,
flow positioning, and risk compression achieve directional harmony.

Confluence Logic: Technical/Macro aligned + Flow against crowd + Risk OK
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
from core.mantic_kernel import mantic_kernel
from core.validators import clamp_input, format_attribution


# Technical and Macro weighted higher
WEIGHTS = [0.30, 0.30, 0.20, 0.20]
LAYER_NAMES = ['technical', 'macro', 'flow', 'risk']

# Thresholds
ALIGNMENT_THRESHOLD = 0.60
FLOW_EXTREME = 0.50
RISK_OK = 0.50
TECHNICAL_MACRO_GAP = 0.20


def detect(technical_setup, macro_tailwind, flow_positioning, risk_compression, f_time=1.0):
    """
    Detect asymmetric opportunity when directional harmony achieved.
    
    Args:
        technical_setup: Technical indicators favorable (0-1)
        macro_tailwind: Fundamental/macro support (0-1)
        flow_positioning: Crowd positioning (-1 to 1, -1 = crowded long, 1 = crowded short)
        risk_compression: Risk appetite/safety (0-1, 1 = compressed/favorable)
        f_time: Temporal kernel multiplier (default 1.0)
    
    Returns:
        dict with window_detected, setup_quality, conviction_score, etc.
    """
    # Clamp inputs
    L_raw = [
        clamp_input(technical_setup, name="technical_setup"),
        clamp_input(macro_tailwind, name="macro_tailwind"),
        clamp_input(flow_positioning, min_val=-1, max_val=1, name="flow_positioning"),
        clamp_input(risk_compression, name="risk_compression")
    ]
    
    # Normalize flow to 0-1 for kernel
    L_normalized = [
        L_raw[0],
        L_raw[1],
        (L_raw[2] + 1) / 2,  # Convert -1,1 to 0,1
        L_raw[3]
    ]
    
    # Interaction terms: Flow against crowd amplifies technical setup
    # If flow is extreme (-1 or 1), boost the interaction (capped at 1.0)
    flow_boost = abs(L_raw[2]) * 0.2
    I = [min(1.0, 0.9 + flow_boost), 1.0, min(1.0, 0.9 + flow_boost * 1.5), 1.0]
    
    # Calculate Mantic score
    M, S, attr = mantic_kernel(WEIGHTS, L_normalized, I, f_time)
    
    # CONFLUENCE LOGIC: Check for directional harmony
    # 1. Technical and Macro aligned (similar values, both high)
    technical_macro_gap = abs(L_raw[0] - L_raw[1])
    technical_macro_aligned = technical_macro_gap < TECHNICAL_MACRO_GAP and L_raw[0] > ALIGNMENT_THRESHOLD
    
    # 2. Flow is extreme (crowd positioned opposite to our direction)
    flow_favorable = abs(L_raw[2]) > FLOW_EXTREME
    flow_direction = "long" if L_raw[2] < 0 else "short"  # Crowd is here, we go opposite
    
    # 3. Risk environment is acceptable
    risk_ok = L_raw[3] > RISK_OK
    
    # 4. All layers at minimum threshold
    all_favorable = min(L_normalized) > 0.5
    
    window_detected = False
    setup_quality = None
    conviction_score = 0.0
    edge_source = None
    recommended_action = None
    stop_loss = None
    risk_reward = None
    
    if technical_macro_aligned and flow_favorable and risk_ok and all_favorable:
        window_detected = True
        
        # Calculate conviction
        base_conviction = (L_raw[0] + L_raw[1]) / 2
        flow_boost_factor = 1 + abs(L_raw[2]) * 0.2
        conviction_score = min(base_conviction * flow_boost_factor, 1.0)
        
        # Determine quality tier
        if conviction_score > 0.85 and min(L_raw[0], L_raw[1]) > 0.75:
            setup_quality = "HIGH_CONVICTION"
            edge_source = "Strong Technical/Macro harmony + Extreme flow against crowd"
            recommended_action = f"Enter full position size ({flow_direction})"
            stop_loss = "Technical setup invalidation or flow extreme mean reversion"
            risk_reward = "Asymmetric favorable (3:1 or better)"
        else:
            setup_quality = "MODERATE_CONVICTION"
            edge_source = "Technical/Macro aligned with flow tailwind"
            recommended_action = f"Enter half position size ({flow_direction})"
            stop_loss = "Technical support/resistance break"
            risk_reward = "Favorable (2:1)"
        
        return {
            "window_detected": True,
            "setup_quality": setup_quality,
            "conviction_score": float(conviction_score),
            "edge_source": edge_source,
            "recommended_action": recommended_action,
            "stop_loss": stop_loss,
            "risk_reward": risk_reward,
            "m_score": float(M),
            "spatial_component": float(S),
            "layer_attribution": format_attribution(attr, LAYER_NAMES),
            "flow_raw": float(L_raw[2]),
            "technical_macro_gap": float(technical_macro_gap),
            "position_direction": flow_direction
        }
    
    # No window - explain why
    missing = []
    if not technical_macro_aligned:
        missing.append("Technical/Macro divergence")
    if not flow_favorable:
        missing.append("Flow not extreme enough")
    if not risk_ok:
        missing.append("Risk environment unfavorable")
    
    return {
        "window_detected": False,
        "status": "Confluence not achieved",
        "reason": "; ".join(missing) if missing else "Layers below threshold",
        "m_score": float(M),
        "spatial_component": float(S),
        "technical_macro_aligned": technical_macro_aligned,
        "flow_favorable": flow_favorable,
        "risk_ok": risk_ok
    }


if __name__ == "__main__":
    print("=== Finance Confluence Alpha Engine ===\n")
    
    # Test 1: High conviction setup (crowd short, we're long)
    print("Test 1: High conviction (crowd short, technical/macro bullish)")
    result = detect(
        technical_setup=0.85,
        macro_tailwind=0.80,
        flow_positioning=0.75,  # Crowd is short (positive = short for us going long)
        risk_compression=0.70
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Quality: {result.get('setup_quality', 'N/A')}")
    print(f"  Conviction: {result.get('conviction_score', 0):.3f}")
    print(f"  Direction: {result.get('position_direction', 'N/A')}")
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
    # Test 2: Moderate setup
    print("Test 2: Moderate conviction")
    result = detect(
        technical_setup=0.70,
        macro_tailwind=0.65,
        flow_positioning=-0.60,  # Crowd is long (we go short)
        risk_compression=0.60
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Quality: {result.get('setup_quality', 'N/A')}")
    print(f"  Direction: {result.get('position_direction', 'N/A')}")
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
    # Test 3: No confluence (flow not extreme)
    print("Test 3: No confluence (flow not extreme)")
    result = detect(
        technical_setup=0.75,
        macro_tailwind=0.70,
        flow_positioning=-0.20,  # Not extreme
        risk_compression=0.65
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Reason: {result.get('reason', 'N/A')}")

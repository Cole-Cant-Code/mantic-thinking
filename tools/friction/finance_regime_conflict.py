"""
Finance: Regime Conflict Monitor

Spots when technical price action contradicts fundamentals, flow, or risk signals.

Input Layers:
    technical: Price action signals (0-1)
    macro: Fundamental indicators (0-1)
    flow: Capital flow direction (-1 to 1, where -1 = outflow, 1 = inflow)
    risk: Risk appetite metrics (0-1)

Optional Overrides (Bounded):
    threshold_override: Dict of threshold overrides, clamped to ±20% of defaults
        e.g., {"conflict": 0.45} (clamped to [0.32, 0.48])
    temporal_config: Dict for temporal kernel tuning, domain-restricted
        e.g., {"kernel_type": "oscillatory", "alpha": 0.15, "t": 3}
    
    NOTE: Domain weights (W) are IMMUTABLE and never exposed for override.

Output:
    alert: Detection message or None
    conflict_type: Type of regime conflict detected
    confidence: 0-1 confidence score
    m_score: Final mantic anomaly score
    spatial_component: Raw S value
    layer_attribution: Percentage contribution per layer
    overrides_applied: Audit log of any parameter tuning applied
"""

import sys
import os

# Avoid mutating sys.path on import; only adjust for direct script execution.
if __name__ == "__main__":
    _repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

import numpy as np
from core.safe_kernel import safe_mantic_kernel as mantic_kernel
from core.mantic_kernel import compute_temporal_kernel
from core.validators import (
    clamp_input, require_finite_inputs, format_attribution,
    clamp_threshold_override, validate_temporal_config,
    clamp_f_time, build_overrides_audit
)


# Domain weights (IMMUTABLE - encode finance domain theory)
WEIGHTS = {
    'technical': 0.35,
    'macro': 0.30,
    'flow': 0.20,
    'risk': 0.15
}

LAYER_NAMES = ['technical', 'macro', 'flow', 'risk']

# Detection thresholds (tuneable within bounds)
DEFAULT_THRESHOLDS = {
    'conflict': 0.4  # Primary threshold for regime conflict detection
}

DOMAIN = "finance"


def detect(technical, macro, flow, risk, f_time=1.0,
           threshold_override=None, temporal_config=None):
    """
    Detect regime conflicts in financial markets.
    
    Args:
        technical: Price action signals (0-1)
        macro: Fundamental indicators (0-1)
        flow: Capital flow direction (-1 to 1)
        risk: Risk appetite metrics (0-1)
        f_time: Temporal kernel multiplier (default 1.0)
        threshold_override: Dict of threshold overrides, clamped to safe bounds
        temporal_config: Dict for temporal kernel (kernel_type, alpha, n, t)
    
    Returns:
        dict with alert, conflict_type, confidence, m_score, etc.
        Includes 'overrides_applied' audit block showing any tuning.
    """
    # =======================================================================
    # INPUT VALIDATION
    require_finite_inputs({
        "technical": technical,
        "macro": macro,
        "flow": flow,
        "risk": risk,
    })

    # OVERRIDES PROCESSING (Bounded and Audited)
    # =======================================================================
    
    # Process threshold overrides (clamped to ±20% of defaults, within [0.05, 0.95])
    threshold_info = {}
    active_thresholds = DEFAULT_THRESHOLDS.copy()
    ignored_threshold_keys = []
    
    if threshold_override and isinstance(threshold_override, dict):
        for key, requested in threshold_override.items():
            if key in DEFAULT_THRESHOLDS:
                clamped_val, was_clamped, info = clamp_threshold_override(
                    requested, DEFAULT_THRESHOLDS[key]
                )
                active_thresholds[key] = clamped_val
                threshold_info[key] = info
            else:
                ignored_threshold_keys.append(key)
    
    # Process temporal config (domain-restricted kernel types, clamped params)
    temporal_validated, temporal_rejected, temporal_clamped = None, {}, {}
    temporal_applied = None
    if temporal_config and isinstance(temporal_config, dict):
        temporal_validated, temporal_rejected, temporal_clamped = validate_temporal_config(
            temporal_config, domain=DOMAIN
        )
        
        # Require kernel_type + t to apply temporal_config
        if "kernel_type" not in temporal_validated:
            if "kernel_type" not in temporal_rejected:
                temporal_rejected["kernel_type"] = {
                    "requested": temporal_config.get("kernel_type"),
                    "reason": "kernel_type required and must be allowed for domain"
                }
        if "t" not in temporal_validated:
            if "t" not in temporal_rejected:
                temporal_rejected["t"] = {
                    "requested": temporal_config.get("t"),
                    "reason": "t required for temporal_config"
                }
        
        # Compute f_time only when required fields are valid
        if "kernel_type" in temporal_validated and "t" in temporal_validated:
            f_time = compute_temporal_kernel(**temporal_validated)
            temporal_applied = temporal_validated
    
    # Clamp f_time to prevent runaway growth ([0.1, 3.0])
    f_time_clamped, f_time_was_clamped, f_time_info = clamp_f_time(f_time)
    
    # =======================================================================
    # CORE DETECTION (Formula Unchanged)
    # =======================================================================
    
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
    I = [1.0, 1.0, 1.0, 1.0]  # Default interactions (immutable)
    
    # Calculate Mantic score (IMMUTABLE FORMULA)
    M, S, attr = mantic_kernel(W, L_normalized, I, f_time_clamped)
    
    # Detection logic
    alert = None
    conflict_type = None
    confidence = 0.0
    
    # Use clamped threshold
    threshold = active_thresholds['conflict']
    
    # Check for technical vs macro divergence
    tech_macro_diff = abs(L[0] - L[1])
    
    # Check for flow contradiction (flow opposite to technical)
    flow_aligned = (L[2] > 0 and L[0] > 0.5) or (L[2] < 0 and L[0] < 0.5)
    
    # Risk-off but technical bullish
    risk_conflict = L[3] < 0.3 and L[0] > 0.7
    
    if tech_macro_diff > threshold or not flow_aligned or risk_conflict:
        confidence = max(tech_macro_diff, 0.5 if not flow_aligned else 0, 0.6 if risk_conflict else 0)
        
        if tech_macro_diff > threshold and not flow_aligned:
            conflict_type = "multi_factor_breakdown"
            alert = "REGIME CONFLICT: Technical, fundamental, and flow signals all divergent"
        elif tech_macro_diff > threshold:
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
    
    # Build audit block - collect threshold clamp info
    threshold_clamped_any = any(
        info.get("was_clamped", False) 
        for info in threshold_info.values()
    ) if threshold_info else False
    
    # Convert threshold info to audit format
    threshold_audit_info = None
    if threshold_info:
        threshold_audit_info = {
            "overrides": {
                key: {
                    "requested": info.get("requested"),
                    "used": info.get("used"),
                    "was_clamped": info.get("was_clamped", False)
                }
                for key, info in threshold_info.items()
            },
            "was_clamped": threshold_clamped_any,
            "ignored_keys": ignored_threshold_keys if ignored_threshold_keys else None
        }
    
    overrides_applied = build_overrides_audit(
        threshold_overrides=threshold_override if threshold_override else None,
        temporal_config=temporal_config if temporal_config else None,
        threshold_info=threshold_audit_info,
        temporal_validated=temporal_applied,
        temporal_rejected=temporal_rejected if temporal_rejected else None,
        temporal_clamped=temporal_clamped if temporal_clamped else None,
        f_time_info=f_time_info
    )
    
    return {
        "alert": alert,
        "conflict_type": conflict_type,
        "confidence": float(confidence),
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "flow_raw": float(L[2]),
        "threshold": threshold,
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied
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

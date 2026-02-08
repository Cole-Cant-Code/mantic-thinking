"""
Cybersecurity: Attribution Uncertainty Resolver

Scores confidence when technical sophistication doesn't align with geopolitical context.

Input Layers:
    technical: Technical sophistication indicators (0-1)
    threat_intel: Threat intelligence confidence (0-1)
    operational_impact: Severity of operational impact (0-1)
    geopolitical: Geopolitical context alignment (0-1)

Optional Overrides (Bounded):
    threshold_override: Dict of threshold overrides, clamped to ±20% of defaults
        e.g., {"attribution_gap": 0.40, "high_tech": 0.85}
    temporal_config: Dict for temporal kernel tuning, domain-restricted
        e.g., {"kernel_type": "exponential", "alpha": 0.12, "t": 2}
    
    NOTE: Domain weights (W) are IMMUTABLE and never exposed for override.

Output:
    alert: Detection message or None
    confidence: high/medium/low string
    mismatch_explanation: Detailed explanation of the mismatch
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
from mantic.introspection import get_layer_visibility


# Domain weights (IMMUTABLE)
WEIGHTS = {
    'technical': 0.30,
    'threat_intel': 0.25,
    'operational_impact': 0.25,
    'geopolitical': 0.20
}

LAYER_NAMES = ['technical', 'threat_intel', 'operational_impact', 'geopolitical']

# Detection thresholds (tuneable within bounds)
DEFAULT_THRESHOLDS = {
    'attribution_gap': 0.35,  # Primary gap threshold
    'high_tech': 0.8          # High sophistication threshold
}

DOMAIN = "cyber"


def detect(technical, threat_intel, operational_impact, geopolitical, f_time=1.0,
           threshold_override=None, temporal_config=None):
    """
    Detect attribution uncertainties in cyber incidents.
    
    Args:
        technical: Technical sophistication indicators (0-1)
        threat_intel: Threat intelligence confidence (0-1)
        operational_impact: Severity of operational impact (0-1)
        geopolitical: Geopolitical context alignment (0-1)
        f_time: Temporal kernel multiplier (default 1.0)
        threshold_override: Dict of threshold overrides
        temporal_config: Dict for temporal kernel
    
    Returns:
        dict with alert, confidence, mismatch_explanation, m_score, etc.
    """
    # =======================================================================
    # INPUT VALIDATION
    require_finite_inputs({
        "technical": technical,
        "threat_intel": threat_intel,
        "operational_impact": operational_impact,
        "geopolitical": geopolitical,
    })

    # OVERRIDES PROCESSING
    # =======================================================================
    
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
    
    temporal_validated, temporal_rejected, temporal_clamped = None, {}, {}
    temporal_applied = None
    if temporal_config and isinstance(temporal_config, dict):
        temporal_validated, temporal_rejected, temporal_clamped = validate_temporal_config(
            temporal_config, domain=DOMAIN
        )
        
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
        
        if "kernel_type" in temporal_validated and "t" in temporal_validated:
            f_time = compute_temporal_kernel(**temporal_validated)
            temporal_applied = temporal_validated
    
    f_time_clamped, _, f_time_info = clamp_f_time(f_time)
    
    # =======================================================================
    # CORE DETECTION
    # =======================================================================
    
    L = [
        clamp_input(technical, name="technical"),
        clamp_input(threat_intel, name="threat_intel"),
        clamp_input(operational_impact, name="operational_impact"),
        clamp_input(geopolitical, name="geopolitical")
    ]
    
    W = list(WEIGHTS.values())
    I = [1.0, 1.0, 1.0, 1.0]
    
    M, S, attr = mantic_kernel(W, L, I, f_time_clamped)
    
    alert = None
    confidence = "high"
    mismatch_explanation = None
    
    gap_threshold = active_thresholds['attribution_gap']
    high_tech_threshold = active_thresholds['high_tech']
    
    tech_intel_gap = L[0] - L[1]
    geo_mismatch = abs(L[0] - L[3])
    avg_intel = (L[1] + L[3]) / 2
    
    if tech_intel_gap > gap_threshold and L[0] > high_tech_threshold:
        confidence = "low"
        mismatch_explanation = (
            f"High technical sophistication ({L[0]:.2f}) but weak threat intel ({L[1]:.2f}). "
            "Possible false flag or unknown APT group."
        )
        alert = "ATTRIBUTION GAP: Sophisticated attack with unclear origin"
    elif geo_mismatch > gap_threshold:
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
    
    threshold_clamped_any = any(
        info.get("was_clamped", False) 
        for info in threshold_info.values()
    ) if threshold_info else False
    
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
    
    layer_values_dict = {"technical": float(L[0]), "threat_intel": float(L[1]), "operational_impact": float(L[2]), "geopolitical": float(L[3])}
    layer_interactions = {
        "technical": float(I[0]),
        "threat_intel": float(I[1]),
        "operational_impact": float(I[2]),
        "geopolitical": float(I[3]),
    }
    layer_visibility = get_layer_visibility("cyber_attribution_resolver", WEIGHTS, layer_values_dict, layer_interactions)
    
    return {
        "alert": alert,
        "confidence": confidence,
        "mismatch_explanation": mismatch_explanation,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "tech_intel_gap": float(tech_intel_gap),
        "threshold": active_thresholds["attribution_gap"],
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied,
        "layer_visibility": layer_visibility
    }


if __name__ == "__main__":
    print("=== Cyber Attribution Uncertainty Resolver ===\n")
    
    print("Test 1: High sophistication + low threat intel")
    result = detect(technical=0.9, threat_intel=0.3, operational_impact=0.8, geopolitical=0.2)
    print(f"  Alert: {result['alert']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Explanation: {result['mismatch_explanation']}\n")
    
    print("Test 2: Normal alignment")
    result = detect(technical=0.8, threat_intel=0.85, operational_impact=0.7, geopolitical=0.75)
    print(f"  Alert: {result['alert']}")
    print(f"  Confidence: {result['confidence']}\n")
    
    print("Test 3: Capability gap")
    result = detect(technical=0.3, threat_intel=0.6, operational_impact=0.5, geopolitical=0.85)
    print(f"  Alert: {result['alert']}")
    print(f"  Confidence: {result['confidence']}")

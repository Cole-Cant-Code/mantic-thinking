"""
Healthcare: Phenotype-Genotype Mismatch Detector

Detects when genomic risk doesn't match phenotypic presentation,
indicating environmental buffering or psychosocial resilience.

Input Layers:
    phenotypic: Current symptoms/vitals (0-1)
    genomic: Genetic risk score (0-1)
    environmental: Exposure load (0-1)
    psychosocial: Stress/resilience (0-1)

Optional Overrides (Bounded):
    threshold_override: Dict of threshold overrides, clamped to ±20% of defaults
        e.g., {"buffering": 0.45} (clamped to [0.32, 0.48])
    temporal_config: Dict for temporal kernel tuning, domain-restricted
        e.g., {"kernel_type": "s_curve", "alpha": 0.15}
    
    NOTE: Domain weights (W) are IMMUTABLE and never exposed for override.

Output:
    alert: Detection message or None
    severity: 0-1 severity score
    buffering_layer: Which layer is buffering the risk
    m_score: Final mantic anomaly score
    spatial_component: Raw S value
    layer_attribution: Percentage contribution per layer
    overrides_applied: Audit log of any parameter tuning applied
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
from core.mantic_kernel import mantic_kernel, compute_temporal_kernel
from core.validators import (
    clamp_input, format_attribution,
    clamp_threshold_override, validate_temporal_config,
    clamp_f_time, build_overrides_audit
)


# Domain weights (IMMUTABLE - encode healthcare domain theory)
WEIGHTS = {
    'phenotypic': 0.40,
    'genomic': 0.20,
    'environmental': 0.25,
    'psychosocial': 0.15
}

LAYER_NAMES = ['phenotypic', 'genomic', 'environmental', 'psychosocial']

# Detection thresholds (tuneable within bounds)
DEFAULT_THRESHOLDS = {
    'buffering': 0.4  # Primary threshold for mismatch detection
}

DOMAIN = "healthcare"


def detect(phenotypic, genomic, environmental, psychosocial, f_time=1.0,
           threshold_override=None, temporal_config=None):
    """
    Detect mismatch between genomic risk and phenotypic presentation.
    
    Args:
        phenotypic: Current symptoms/vitals (0-1)
        genomic: Genetic risk score (0-1)
        environmental: Exposure load (0-1)
        psychosocial: Stress/resilience (0-1)
        f_time: Temporal kernel multiplier (default 1.0)
        threshold_override: Dict of threshold overrides, clamped to safe bounds
        temporal_config: Dict for temporal kernel (kernel_type, alpha, n, t)
    
    Returns:
        dict with alert, severity, buffering_layer, m_score, etc.
        Includes 'overrides_applied' audit block showing any tuning.
    
    Example:
        >>> result = detect(
        ...     phenotypic=0.3,
        ...     genomic=0.9,
        ...     environmental=0.4,
        ...     psychosocial=0.8
        ... )
        >>> print(result['alert'])
        'RESILIENCE: High genetic risk buffered by strong psychosocial factors'
        
        >>> # With bounded overrides
        >>> result = detect(
        ...     phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8,
        ...     threshold_override={"buffering": 0.35},
        ...     temporal_config={"kernel_type": "s_curve", "alpha": 0.12, "t": 2}
        ... )
    """
    # =======================================================================
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
    
    # Clamp inputs to valid range
    L = [
        clamp_input(phenotypic, name="phenotypic"),
        clamp_input(genomic, name="genomic"),
        clamp_input(environmental, name="environmental"),
        clamp_input(psychosocial, name="psychosocial")
    ]
    
    W = list(WEIGHTS.values())
    I = [1.0, 1.0, 1.0, 1.0]  # Default interactions (immutable)
    
    # Calculate Mantic score (IMMUTABLE FORMULA)
    M, S, attr = mantic_kernel(W, L, I, f_time_clamped)
    
    # Detection logic: Compare expected vs actual phenotype
    # Expected phenotype = weighted combination of genomic + environmental
    expected_phenotype = (L[1] * 0.6) + (L[2] * 0.4)
    buffering_score = abs(L[0] - expected_phenotype)
    
    alert = None
    buffering_layer = None
    severity = 0.0
    
    # Use clamped threshold
    threshold = active_thresholds['buffering']
    
    if buffering_score > threshold:
        severity = min(buffering_score, 1.0)
        
        if L[0] < expected_phenotype:
            # Phenotype is better than expected - buffering occurring
            if L[3] > 0.7:
                buffering_layer = "psychosocial"
                alert = "RESILIENCE: High genetic risk buffered by strong psychosocial factors"
            elif L[2] < 0.3:
                buffering_layer = "environmental"
                alert = "PROTECTION: Low exposure load buffering genetic predisposition"
            else:
                buffering_layer = "unknown"
                alert = "PHENOTYPE SUPPRESSION: Symptoms below genetic expectation, investigate hidden resilience"
        else:
            # Phenotype is worse than expected - hidden burden
            buffering_layer = "environmental_stress"
            alert = "HIDDEN BURDEN: Symptoms exceed genetic profile, check acute environmental toxic load"
    
    # Build audit block - collect threshold clamp info
    threshold_clamped_any = any(
        info.get("was_clamped", False) 
        for info in threshold_info.values()
    ) if threshold_info else False
    
    # Convert threshold info to audit format
    threshold_audit_info = None
    if threshold_info or ignored_threshold_keys:
        threshold_audit_info = {
            "overrides": {
                key: {
                    "requested": info.get("requested"),
                    "used": info.get("used"),
                    "was_clamped": info.get("was_clamped", False)
                }
                for key, info in threshold_info.items()
            } if threshold_info else {},
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
        "severity": float(severity),
        "buffering_layer": buffering_layer,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "threshold": threshold,
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied
    }


if __name__ == "__main__":
    # Test cases
    print("=== Healthcare Phenotype-Genotype Mismatch Detector ===\n")
    
    # Test 1: High genetic risk, low symptoms, high resilience (mismatch detected)
    print("Test 1: High genetic risk + low symptoms + high resilience")
    result = detect(
        phenotypic=0.3,
        genomic=0.9,
        environmental=0.4,
        psychosocial=0.8
    )
    print(f"  Alert: {result['alert']}")
    print(f"  Buffering Layer: {result['buffering_layer']}")
    print(f"  Severity: {result['severity']:.3f}")
    print(f"  M-Score: {result['m_score']:.3f}")
    print(f"  Overrides Applied: {result.get('overrides_applied', {})}\n")
    
    # Test 2: Normal case (no mismatch)
    print("Test 2: Normal alignment case")
    result = detect(
        phenotypic=0.6,
        genomic=0.7,
        environmental=0.5,
        psychosocial=0.5
    )
    print(f"  Alert: {result['alert']}")
    print(f"  Severity: {result['severity']:.3f}")
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
    # Test 3: Edge case - symptoms exceed genetic expectation
    print("Test 3: Symptoms exceed genetic expectation")
    result = detect(
        phenotypic=0.9,
        genomic=0.4,
        environmental=0.8,
        psychosocial=0.3
    )
    print(f"  Alert: {result['alert']}")
    print(f"  Buffering Layer: {result['buffering_layer']}")
    print(f"  Severity: {result['severity']:.3f}")
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
    # Test 4: Bounded threshold override (valid - within ±20%)
    print("Test 4: Valid threshold override (0.35, within ±20% of 0.4)")
    result = detect(
        phenotypic=0.3,
        genomic=0.9,
        environmental=0.4,
        psychosocial=0.8,
        threshold_override={"buffering": 0.35}
    )
    print(f"  Alert: {result['alert']}")
    print(f"  Threshold Used: {result['threshold']}")
    print(f"  Was Clamped: {result['overrides_applied']['threshold_overrides']['clamped']}\n")
    
    # Test 5: Bounded threshold override (clamped - outside ±20%)
    print("Test 5: Invalid threshold override (0.10, clamped to minimum)")
    result = detect(
        phenotypic=0.3,
        genomic=0.9,
        environmental=0.4,
        psychosocial=0.8,
        threshold_override={"buffering": 0.10}
    )
    print(f"  Alert: {result['alert']}")
    print(f"  Threshold Used: {result['threshold']}")
    print(f"  Was Clamped: {result['overrides_applied']['threshold_overrides']['clamped']}")
    print(f"  Audit: {result['overrides_applied']['threshold_overrides']}\n")
    
    # Test 6: Temporal config with valid healthcare kernel
    print("Test 6: Valid temporal config (s_curve kernel)")
    result = detect(
        phenotypic=0.3,
        genomic=0.9,
        environmental=0.4,
        psychosocial=0.8,
        temporal_config={"kernel_type": "s_curve", "alpha": 0.12, "t": 2.0}
    )
    print(f"  M-Score: {result['m_score']:.3f}")
    print(f"  Temporal Applied: {result['overrides_applied']['temporal_config']['applied']}\n")
    
    # Test 7: Temporal config with invalid kernel for healthcare (rejected)
    print("Test 7: Invalid temporal config (oscillatory rejected for healthcare)")
    result = detect(
        phenotypic=0.3,
        genomic=0.9,
        environmental=0.4,
        psychosocial=0.8,
        temporal_config={"kernel_type": "oscillatory", "alpha": 0.1}
    )
    print(f"  M-Score: {result['m_score']:.3f}")
    print(f"  Rejected: {result['overrides_applied']['temporal_config']['rejected']}\n")

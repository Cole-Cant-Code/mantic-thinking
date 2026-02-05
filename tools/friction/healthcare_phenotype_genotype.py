"""
Healthcare: Phenotype-Genotype Mismatch Detector

Detects when genomic risk doesn't match phenotypic presentation,
indicating environmental buffering or psychosocial resilience.

Input Layers:
    phenotypic: Current symptoms/vitals (0-1)
    genomic: Genetic risk score (0-1)
    environmental: Exposure load (0-1)
    psychosocial: Stress/resilience (0-1)

Output:
    alert: Detection message or None
    severity: 0-1 severity score
    buffering_layer: Which layer is buffering the risk
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
    'phenotypic': 0.40,
    'genomic': 0.20,
    'environmental': 0.25,
    'psychosocial': 0.15
}

LAYER_NAMES = ['phenotypic', 'genomic', 'environmental', 'psychosocial']

# Detection threshold
THRESHOLD = 0.4


def detect(phenotypic, genomic, environmental, psychosocial, f_time=1.0):
    """
    Detect mismatch between genomic risk and phenotypic presentation.
    
    Args:
        phenotypic: Current symptoms/vitals (0-1)
        genomic: Genetic risk score (0-1)
        environmental: Exposure load (0-1)
        psychosocial: Stress/resilience (0-1)
        f_time: Temporal kernel multiplier (default 1.0)
    
    Returns:
        dict with alert, severity, buffering_layer, m_score, etc.
    
    Example:
        >>> result = detect(
        ...     phenotypic=0.3,
        ...     genomic=0.9,
        ...     environmental=0.4,
        ...     psychosocial=0.8
        ... )
        >>> print(result['alert'])
        'RESILIENCE: High genetic risk buffered by strong psychosocial factors'
    """
    # Clamp inputs to valid range
    L = [
        clamp_input(phenotypic, name="phenotypic"),
        clamp_input(genomic, name="genomic"),
        clamp_input(environmental, name="environmental"),
        clamp_input(psychosocial, name="psychosocial")
    ]
    
    W = list(WEIGHTS.values())
    I = [1.0, 1.0, 1.0, 1.0]  # Default interactions
    
    # Calculate Mantic score
    M, S, attr = mantic_kernel(W, L, I, f_time)
    
    # Detection logic: Compare expected vs actual phenotype
    # Expected phenotype = weighted combination of genomic + environmental
    expected_phenotype = (L[1] * 0.6) + (L[2] * 0.4)
    buffering_score = abs(L[0] - expected_phenotype)
    
    alert = None
    buffering_layer = None
    severity = 0.0
    
    if buffering_score > THRESHOLD:
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
    
    return {
        "alert": alert,
        "severity": float(severity),
        "buffering_layer": buffering_layer,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "threshold": THRESHOLD
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
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
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
    print(f"  M-Score: {result['m_score']:.3f}")

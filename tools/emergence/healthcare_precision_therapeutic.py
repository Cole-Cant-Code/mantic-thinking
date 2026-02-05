"""
Healthcare: Precision Therapeutic Window Detector

Identifies rare alignment of genomic predisposition, environmental readiness,
phenotypic timing, and psychosocial engagement for maximum treatment efficacy.

Confluence Logic: All 4 layers must be favorable simultaneously (not just average)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
from core.mantic_kernel import mantic_kernel
from core.validators import clamp_input, format_attribution


# Equal weight for therapeutic alignment
WEIGHTS = [0.25, 0.25, 0.25, 0.25]
LAYER_NAMES = ['genomic', 'environmental', 'phenotypic', 'psychosocial']

# Confluence thresholds
ALIGNMENT_THRESHOLD = 0.65
OPTIMAL_THRESHOLD = 0.80


def detect(genomic_predisposition, environmental_readiness, phenotypic_timing, psychosocial_engagement, f_time=1.0):
    """
    Detect rare alignment window for maximum therapeutic efficacy.
    
    Args:
        genomic_predisposition: Genetic readiness for treatment (0-1)
        environmental_readiness: Exposure/toxin levels favorable (0-1)
        phenotypic_timing: Disease progression stage optimal (0-1)
        psychosocial_engagement: Patient motivation/support high (0-1)
        f_time: Temporal kernel multiplier (default 1.0)
    
    Returns:
        dict with window_detected, window_type, confidence, m_score, etc.
    """
    # Clamp inputs
    L = [
        clamp_input(genomic_predisposition, name="genomic_predisposition"),
        clamp_input(environmental_readiness, name="environmental_readiness"),
        clamp_input(phenotypic_timing, name="phenotypic_timing"),
        clamp_input(psychosocial_engagement, name="psychosocial_engagement")
    ]
    
    # Use equal interactions for baseline
    I = [1.0, 1.0, 1.0, 1.0]
    
    # Calculate Mantic score
    M, S, attr = mantic_kernel(WEIGHTS, L, I, f_time)
    
    # CONFLUENCE LOGIC: Check if ALL layers are above threshold (alignment)
    alignment_floor = min(L)
    
    window_detected = False
    window_type = None
    confidence = 0.0
    recommended_action = None
    duration_estimate = None
    limiting_factor = None
    
    if alignment_floor > ALIGNMENT_THRESHOLD:
        window_detected = True
        
        # Check for optimal vs favorable
        if all(l > OPTIMAL_THRESHOLD for l in L):
            window_type = "OPTIMAL: All systems aligned for maximum efficacy"
            confidence = 0.95
            recommended_action = "Initiate treatment protocol immediately - peak window"
            duration_estimate = "48-72 hour optimal window"
        else:
            window_type = "FAVORABLE: Strong alignment across all factors"
            confidence = 0.75
            recommended_action = "Good therapeutic window - proceed with treatment"
            duration_estimate = "5-7 day favorable window"
        
        # Identify weakest link for monitoring
        weakest_idx = int(np.argmin(L))
        limiting_factor = LAYER_NAMES[weakest_idx]
        
        return {
            "window_detected": True,
            "window_type": window_type,
            "confidence": float(confidence),
            "m_score": float(M),
            "spatial_component": float(S),
            "layer_attribution": format_attribution(attr, LAYER_NAMES),
            "alignment_floor": float(alignment_floor),
            "limiting_factor": limiting_factor,
            "recommended_action": recommended_action,
            "duration_estimate": duration_estimate,
            "layer_values": {
                "genomic": float(L[0]),
                "environmental": float(L[1]),
                "phenotypic": float(L[2]),
                "psychosocial": float(L[3])
            }
        }
    
    # Window not detected - identify what's missing
    below_threshold = [LAYER_NAMES[i] for i, l in enumerate(L) if l <= ALIGNMENT_THRESHOLD]
    
    return {
        "window_detected": False,
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "alignment_floor": float(alignment_floor),
        "status": f"Layers not aligned. {', '.join(below_threshold)} below threshold.",
        "improvement_needed": below_threshold
    }


if __name__ == "__main__":
    print("=== Healthcare Precision Therapeutic Window Detector ===\n")
    
    # Test 1: Optimal alignment
    print("Test 1: Optimal alignment (all > 0.8)")
    result = detect(
        genomic_predisposition=0.85,
        environmental_readiness=0.82,
        phenotypic_timing=0.88,
        psychosocial_engagement=0.90
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Type: {result['window_type']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Limiting Factor: {result.get('limiting_factor', 'N/A')}")
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
    # Test 2: Favorable alignment
    print("Test 2: Favorable alignment (all > 0.65)")
    result = detect(
        genomic_predisposition=0.70,
        environmental_readiness=0.72,
        phenotypic_timing=0.68,
        psychosocial_engagement=0.75
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Type: {result['window_type']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
    # Test 3: Not aligned
    print("Test 3: Not aligned (psychosocial low)")
    result = detect(
        genomic_predisposition=0.75,
        environmental_readiness=0.80,
        phenotypic_timing=0.70,
        psychosocial_engagement=0.45
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Status: {result['status']}")
    print(f"  Alignment Floor: {result['alignment_floor']:.3f}")

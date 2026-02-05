"""
Climate: Resilience Multiplier

Surfaces interventions with positive cross-domain coupling
solving multiple layer problems simultaneously.

Confluence Logic: Strong positive coupling across all 4 domains = multiplier effect
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
from core.mantic_kernel import mantic_kernel
from core.validators import clamp_input, format_attribution


# Equal weight for multi-domain solutions
WEIGHTS = [0.25, 0.25, 0.25, 0.25]
LAYER_NAMES = ['atmospheric', 'ecological', 'infrastructure', 'policy']

# Thresholds
COUPLING_THRESHOLD = 0.50
MIN_LAYER_THRESHOLD = 0.50
MULTIPLIER_THRESHOLD = 0.70


def detect(atmospheric_benefit, ecological_benefit, infrastructure_benefit, policy_alignment, f_time=1.0):
    """
    Identify interventions that solve multiple layer problems simultaneously.
    
    Args:
        atmospheric_benefit: Atmospheric/climate benefit (0-1)
        ecological_benefit: Ecosystem benefit (0-1)
        infrastructure_benefit: Infrastructure resilience benefit (0-1)
        policy_alignment: Policy coherence/support (0-1)
        f_time: Temporal kernel multiplier (default 1.0)
    
    Returns:
        dict with window_detected, intervention_type, cross_domain_coupling, etc.
    """
    # Clamp inputs
    L = [
        clamp_input(atmospheric_benefit, name="atmospheric_benefit"),
        clamp_input(ecological_benefit, name="ecological_benefit"),
        clamp_input(infrastructure_benefit, name="infrastructure_benefit"),
        clamp_input(policy_alignment, name="policy_alignment")
    ]
    
    # Interactions: Positive coupling between layers
    I = [1.0, 1.0, 1.0, 1.0]
    
    # Calculate Mantic score
    M, S, attr = mantic_kernel(WEIGHTS, L, I, f_time)
    
    # CONFLUENCE LOGIC: Positive coupling across all domains
    # Calculate pairwise coupling (all layers benefiting each other)
    pairwise_products = [
        L[0]*L[1], L[0]*L[2], L[0]*L[3],  # Atmospheric with others
        L[1]*L[2], L[1]*L[3],              # Ecological with others
        L[2]*L[3]                          # Infrastructure with policy
    ]
    coupling = sum(pairwise_products) / len(pairwise_products)
    
    # Count high-benefit layers
    high_benefit_count = sum(1 for l in L if l > 0.7)
    
    window_detected = False
    intervention_type = None
    example_intervention = None
    recommended_action = None
    funding_priority = None
    
    if coupling > COUPLING_THRESHOLD and min(L) > MIN_LAYER_THRESHOLD:
        window_detected = True
        
        # Determine multiplier tier
        if coupling > MULTIPLIER_THRESHOLD and high_benefit_count >= 3:
            intervention_type = "HIGH_MULTIPLIER"
            funding_priority = "URGENT - High leverage across 4 domain columns"
            example_intervention = "Urban forestry with green infrastructure: heat reduction + biodiversity + stormwater + equity"
            recommended_action = "Prioritize immediate funding. Every dollar creates compounding benefits across atmospheric, ecological, infrastructure, and policy domains."
        elif coupling > 0.60 or high_benefit_count >= 3:
            intervention_type = "MULTIPLIER"
            funding_priority = "HIGH - Cross-domain benefits"
            example_intervention = "Wetland restoration: carbon sequestration + flood control + habitat + recreation"
            recommended_action = "Fast-track approval. Strong positive externalities across multiple systems."
        else:
            intervention_type = "MODERATE_MULTIPLIER"
            funding_priority = "MODERATE - Dual benefits"
            example_intervention = "Solar canopy parking: renewable energy + heat reduction"
            recommended_action = "Include in funding round. Good but not exceptional cross-domain coupling."
        
        return {
            "window_detected": True,
            "intervention_type": intervention_type,
            "cross_domain_coupling": float(coupling),
            "benefit_layers_above_70": high_benefit_count,
            "example_intervention": example_intervention,
            "recommended_action": recommended_action,
            "funding_priority": funding_priority,
            "m_score": float(M),
            "spatial_component": float(S),
            "layer_attribution": format_attribution(attr, LAYER_NAMES),
            "benefit_profile": {
                "atmospheric": float(L[0]),
                "ecological": float(L[1]),
                "infrastructure": float(L[2]),
                "policy": float(L[3])
            }
        }
    
    # No multiplier window
    below_threshold = [LAYER_NAMES[i] for i, l in enumerate(L) if l <= MIN_LAYER_THRESHOLD]
    
    return {
        "window_detected": False,
        "cross_domain_coupling": float(coupling),
        "coupling_status": "Insufficient coupling for multiplier effect",
        "benefit_layers_above_70": high_benefit_count,
        "limiting_factors": below_threshold,
        "m_score": float(M),
        "spatial_component": float(S),
        "status": f"Intervention benefits limited to {high_benefit_count} domains. Seek solutions with broader coupling."
    }


if __name__ == "__main__":
    print("=== Climate Resilience Multiplier ===\n")
    
    # Test 1: High multiplier (urban forestry)
    print("Test 1: High multiplier (all domains > 0.7)")
    result = detect(
        atmospheric_benefit=0.75,   # Heat reduction
        ecological_benefit=0.80,    # Biodiversity
        infrastructure_benefit=0.78, # Stormwater
        policy_alignment=0.82       # Equity/policy support
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Intervention Type: {result.get('intervention_type', 'N/A')}")
    print(f"  Coupling: {result.get('cross_domain_coupling', 0):.3f}")
    print(f"  Example: {result.get('example_intervention', 'N/A')[:50]}...")
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
    # Test 2: Moderate multiplier
    print("Test 2: Moderate multiplier")
    result = detect(
        atmospheric_benefit=0.70,
        ecological_benefit=0.72,
        infrastructure_benefit=0.65,
        policy_alignment=0.68
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Intervention Type: {result.get('intervention_type', 'N/A')}")
    print(f"  M-Score: {result['m_score']:.3f}\n")
    
    # Test 3: No multiplier (single domain focus)
    print("Test 3: No multiplier (single domain strong)")
    result = detect(
        atmospheric_benefit=0.30,
        ecological_benefit=0.25,
        infrastructure_benefit=0.85,  # Only infrastructure strong
        policy_alignment=0.40
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Status: {result.get('status', 'N/A')}")

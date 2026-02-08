"""
Friction vs Emergence Pair Tests

Tests the relationship between paired friction/emergence tools,
verifying design properties like:
- Same M-score means opposite things
- Weight differences are by design
- Interaction coefficient modifications are tested

Run with: python -m pytest tests/test_friction_emergence_pairs.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np

from mantic_thinking.tools.friction.healthcare_phenotype_genotype import detect as hc_friction
from mantic_thinking.tools.emergence.healthcare_precision_therapeutic import detect as hc_emergence
from mantic_thinking.tools.friction.finance_regime_conflict import detect as fin_friction
from mantic_thinking.tools.emergence.finance_confluence_alpha import detect as fin_emergence
from mantic_thinking.tools.friction.social_narrative_rupture import detect as soc_friction
from mantic_thinking.tools.emergence.social_catalytic_alignment import detect as soc_emergence


# =============================================================================
# Opposite Meaning for Same M-Score Range
# =============================================================================

class TestOppositeMeaning:
    """High M-score means risk in friction, opportunity in emergence."""

    def test_healthcare_opposite_semantics(self):
        """Both can produce high M-scores with opposite interpretations."""
        # Friction: high M → mismatch detected (risk)
        friction_result = hc_friction(
            phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8
        )
        # Emergence: high M → window detected (opportunity)
        emergence_result = hc_emergence(
            genomic_predisposition=0.9, environmental_readiness=0.85,
            phenotypic_timing=0.9, psychosocial_engagement=0.9
        )

        # Both have M-scores > 0 but mean opposite things
        assert friction_result["alert"] is not None, \
            "Friction high M should mean alert"
        assert emergence_result["window_detected"] is True, \
            "Emergence high M should mean window detected"

    def test_finance_opposite_semantics(self):
        """Finance friction alerts vs emergence windows."""
        friction_result = fin_friction(
            technical=0.9, macro=0.3, flow=-0.8, risk=0.2
        )
        emergence_result = fin_emergence(
            technical_setup=0.85, macro_tailwind=0.80,
            flow_positioning=0.75, risk_compression=0.70
        )

        assert friction_result["alert"] is not None
        assert emergence_result["window_detected"] is True


# =============================================================================
# Weight Differences By Design
# =============================================================================

class TestWeightDifferences:
    """Friction and emergence tools use different weights within same domain."""

    def test_healthcare_weight_difference(self):
        """Healthcare friction uses asymmetric weights; emergence uses uniform."""
        from mantic_thinking.tools.friction.healthcare_phenotype_genotype import WEIGHTS as hc_f_w
        from mantic_thinking.tools.emergence.healthcare_precision_therapeutic import WEIGHTS as hc_e_w

        # Friction: {phenotypic: 0.40, genomic: 0.20, environmental: 0.25, psychosocial: 0.15}
        assert isinstance(hc_f_w, dict)
        assert hc_f_w['phenotypic'] != hc_f_w['genomic']  # Asymmetric

        # Emergence: [0.25, 0.25, 0.25, 0.25]
        assert isinstance(hc_e_w, list)
        assert all(w == 0.25 for w in hc_e_w)  # Uniform

    def test_finance_weight_difference(self):
        """Finance friction vs emergence weights differ."""
        from mantic_thinking.tools.friction.finance_regime_conflict import WEIGHTS as fin_f_w
        from mantic_thinking.tools.emergence.finance_confluence_alpha import WEIGHTS as fin_e_w

        # Friction: asymmetric
        assert fin_f_w['technical'] > fin_f_w['risk']
        # Emergence: slightly different distribution
        assert fin_e_w == [0.30, 0.30, 0.20, 0.20]


# =============================================================================
# Interaction Coefficient Modifications
# =============================================================================

class TestInteractionCoefficients:
    """Some emergence tools modify I dynamically (non-standard)."""

    def test_finance_emergence_flow_modifies_interaction(self):
        """Finance emergence modifies I based on flow magnitude."""
        # With flow=0: flow_boost = 0, I = [0.9, 1.0, 0.9, 1.0]
        # With flow=1: flow_boost = 0.2, I = [1.0, 1.0, 1.0, 1.0] (capped)
        result_zero_flow = fin_emergence(
            technical_setup=0.85, macro_tailwind=0.85,
            flow_positioning=0.0, risk_compression=0.70
        )
        result_high_flow = fin_emergence(
            technical_setup=0.85, macro_tailwind=0.85,
            flow_positioning=1.0, risk_compression=0.70
        )

        # Higher flow should produce higher M-score (via I boost)
        # Both normalized: flow=0 → L[2]=0.5, flow=1 → L[2]=1.0
        # Also flow magnitude affects I
        assert result_high_flow["m_score"] > result_zero_flow["m_score"]

    def test_social_emergence_network_modifies_interaction(self):
        """Social emergence modifies I[1] based on network_bridges."""
        # With network=0: I[1] = min(1.0, 0.9 + 0) = 0.9
        # With network=1: I[1] = min(1.0, 0.9 + 0.1) = 1.0
        result_low_net = soc_emergence(
            individual_readiness=0.85, network_bridges=0.0,
            policy_window=0.85, paradigm_momentum=0.85
        )
        result_high_net = soc_emergence(
            individual_readiness=0.85, network_bridges=1.0,
            policy_window=0.85, paradigm_momentum=0.85
        )

        # Higher network bridges should produce higher M-score (via L and I)
        assert result_high_net["m_score"] > result_low_net["m_score"]

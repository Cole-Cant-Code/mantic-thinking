"""
Domain Logic Deep Dive Tests

Tests domain-specific heuristics at exact boundaries, edge cases,
and semantic correctness across all 7 domains.

Run with: python -m pytest tests/test_domain_logic_deep.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np

from tools.friction.healthcare_phenotype_genotype import detect as healthcare_friction
from tools.friction.finance_regime_conflict import detect as finance_friction
from tools.friction.climate_maladaptation import detect as climate_friction
from tools.friction.legal_precedent_drift import detect as legal_friction
from tools.friction.cyber_attribution_resolver import detect as cyber_friction
from tools.friction.military_friction_forecast import detect as military_friction
from tools.friction.social_narrative_rupture import detect as social_friction

from tools.emergence.healthcare_precision_therapeutic import detect as healthcare_emergence
from tools.emergence.finance_confluence_alpha import detect as finance_emergence
from tools.emergence.climate_resilience_multiplier import detect as climate_emergence
from tools.emergence.social_catalytic_alignment import detect as social_emergence


# =============================================================================
# Healthcare Friction: Phenotype-Genotype Mismatch
# =============================================================================

class TestHealthcareFrictionBoundaries:
    """Test buffering_score threshold boundary behavior."""

    def test_buffering_at_exact_threshold_no_alert(self):
        """buffering_score == 0.4 (threshold) does NOT trigger (> not >=)."""
        # expected = genomic*0.6 + environmental*0.4 = 0.5*0.6 + 0.5*0.4 = 0.5
        # buffering_score = |phenotypic - 0.5| = |0.9 - 0.5| = 0.4
        result = healthcare_friction(
            phenotypic=0.9, genomic=0.5, environmental=0.5, psychosocial=0.5
        )
        assert result["alert"] is None, \
            "buffering_score==threshold should NOT trigger alert (strict >)"

    def test_buffering_just_above_threshold_triggers(self):
        """buffering_score > 0.4 triggers alert."""
        # expected = 0.5*0.6 + 0.5*0.4 = 0.5
        # buffering_score = |0.91 - 0.5| = 0.41 > 0.4
        result = healthcare_friction(
            phenotypic=0.91, genomic=0.5, environmental=0.5, psychosocial=0.5
        )
        assert result["alert"] is not None, \
            "buffering_score just above threshold should trigger alert"

    def test_unknown_buffering_path(self):
        """Triggers 'PHENOTYPE SUPPRESSION' when phenotypic < expected,
        psychosocial <= 0.7, environmental >= 0.3."""
        # expected = 0.9*0.6 + 0.5*0.4 = 0.74
        # buffering_score = |0.1 - 0.74| = 0.64 > 0.4 ✓
        # phenotypic(0.1) < expected(0.74) ✓
        # psychosocial(0.5) > 0.7? NO → not "psychosocial"
        # environmental(0.5) < 0.3? NO → not "environmental"
        # → "unknown" path
        result = healthcare_friction(
            phenotypic=0.1, genomic=0.9, environmental=0.5, psychosocial=0.5
        )
        assert result["alert"] is not None
        assert "PHENOTYPE SUPPRESSION" in result["alert"]
        assert result["buffering_layer"] == "unknown"

    def test_hidden_burden_path(self):
        """Triggers 'HIDDEN BURDEN' when phenotypic > expected."""
        # expected = 0.3*0.6 + 0.3*0.4 = 0.30
        # buffering_score = |0.9 - 0.30| = 0.60 > 0.4 ✓
        # phenotypic(0.9) > expected(0.30) → hidden burden
        result = healthcare_friction(
            phenotypic=0.9, genomic=0.3, environmental=0.3, psychosocial=0.3
        )
        assert result["alert"] is not None
        assert "HIDDEN BURDEN" in result["alert"]
        assert result["buffering_layer"] == "environmental_stress"


# =============================================================================
# Climate Friction: Maladaptation Preventer
# =============================================================================

class TestClimateThresholdsDecoupled:
    """Climate tool's block/caution thresholds are defined but NOT used
    in the actual detection logic — threshold_override has no effect."""

    def test_threshold_override_changes_decision(self):
        """Changing block/caution thresholds now affects the decision."""
        base_inputs = dict(
            atmospheric=0.7, ecological=0.2, infrastructure=0.8, policy=0.3
        )

        result_default = climate_friction(**base_inputs)
        # Default: infra_eco_gap=0.6 > block(0.6)=True, eco(0.2) < caution(0.4)=True → block
        assert result_default["decision"] == "block"

        # Raise block threshold to 0.72 (max allowed: 0.6*1.2=0.72)
        # infra_eco_gap=0.6 is NOT > 0.72 → first branch fails, falls through
        result_override = climate_friction(
            **base_inputs,
            threshold_override={"block": 0.72}
        )
        assert result_override["decision"] != "block" or result_override["alert"] != result_default["alert"], \
            "Climate threshold override should now affect decisions"

    def test_decision_uses_threshold_variables(self):
        """Detection logic uses block_threshold and caution_threshold from overrides."""
        # infra_eco_gap = 0.8 - 0.2 = 0.6 > block_threshold(0.6) ✓
        # ecological(0.2) < caution_threshold(0.4) ✓ → decision = "block"
        result = climate_friction(
            atmospheric=0.7, ecological=0.2, infrastructure=0.8, policy=0.3
        )
        assert result["decision"] == "block"

        # Balanced: infra_eco_gap = 0.6 - 0.7 = -0.1, not > 0.6
        # short_term_focus: atmo(0.6) > 0.6 is False
        result = climate_friction(
            atmospheric=0.6, ecological=0.7, infrastructure=0.6, policy=0.7
        )
        assert result["decision"] == "proceed"

    def test_short_term_focus_block(self):
        """atmospheric > 0.6 and ecological < caution_threshold, with policy < caution_threshold → block."""
        result = climate_friction(
            atmospheric=0.8, ecological=0.3, infrastructure=0.5, policy=0.2
        )
        assert result["decision"] == "block"
        assert "Short-term atmospheric fix" in result["alert"]

    def test_policy_gap_caution(self):
        """Low policy with technical activity → caution."""
        # infra_eco_gap = 0.7 - 0.5 = 0.2, not > block_threshold(0.6)
        # short_term_focus: atmo(0.5) > 0.6 is False
        # low_policy: policy(0.2) < 0.3 ✓, and infra(0.7) > block_threshold(0.6) ✓
        result = climate_friction(
            atmospheric=0.5, ecological=0.5, infrastructure=0.7, policy=0.2
        )
        assert result["decision"] == "caution"
        assert "POLICY GAP" in result["alert"]


# =============================================================================
# Finance Friction: Regime Conflict
# =============================================================================

class TestFinanceFrictionFlow:
    """Test flow alignment and zero-flow behavior."""

    def test_zero_flow_treated_as_not_aligned(self):
        """flow=0.0 with tech=0.7 is 'not aligned' (neither > 0 nor < 0)."""
        # flow_aligned = (0 > 0 and 0.7 > 0.5) or (0 < 0 and 0.7 < 0.5) = False
        result = finance_friction(
            technical=0.7, macro=0.7, flow=0.0, risk=0.7
        )
        # Should trigger because flow is not aligned
        assert result["alert"] is not None
        assert result["conflict_type"] == "flow_contradiction"

    def test_positive_flow_aligned_with_bullish_tech(self):
        """flow > 0 and tech > 0.5 → aligned."""
        result = finance_friction(
            technical=0.7, macro=0.7, flow=0.5, risk=0.7
        )
        # Tech-macro diff = 0, flow aligned, no risk conflict → no alert
        assert result["alert"] is None

    def test_negative_flow_aligned_with_bearish_tech(self):
        """flow < 0 and tech < 0.5 → aligned."""
        result = finance_friction(
            technical=0.3, macro=0.3, flow=-0.5, risk=0.5
        )
        # Tech-macro diff = 0, flow aligned → no alert
        assert result["alert"] is None


# =============================================================================
# Legal Friction: Precedent Drift
# =============================================================================

class TestLegalDriftDirection:
    """Test drift_direction boundary conditions."""

    def test_drift_right_at_boundary(self):
        """socio_political just above 0.5 → 'right'."""
        result = legal_friction(
            black_letter=0.8, precedent=0.8, operational=0.8, socio_political=0.51
        )
        # L[3] = 0.51 > 0.5 → drift_direction = "right"
        assert result["drift_direction"] == "right"

    def test_drift_stable_at_low_value(self):
        """socio_political near 0 with abs < 0.3 → 'stable'."""
        result = legal_friction(
            black_letter=0.8, precedent=0.8, operational=0.8, socio_political=0.2
        )
        # L[3] = 0.2, not > 0.5, not < -0.5 (since input clamped to 0-1...
        # Wait: legal tool clamps socio_political with min=-1, max=1
        # So 0.2 stays 0.2. |0.2| = 0.2 < 0.3 → stable
        assert result["drift_direction"] == "stable"

    def test_drift_fragmenting(self):
        """abs(socio_political) > 0.3 but not > 0.5 → 'fragmenting'."""
        result = legal_friction(
            black_letter=0.8, precedent=0.8, operational=0.8, socio_political=0.4
        )
        # L[3] = 0.4: not > 0.5, not < -0.5, abs(0.4) > 0.3 → fragmenting
        assert result["drift_direction"] == "fragmenting"


# =============================================================================
# Cyber Friction: Attribution Resolver
# =============================================================================

class TestCyberConfidenceTransitions:
    """Test confidence level boundary transitions."""

    def test_high_confidence_when_aligned(self):
        """When no gaps or mismatches → confidence 'high'."""
        result = cyber_friction(
            technical=0.5, threat_intel=0.5, operational_impact=0.5, geopolitical=0.5
        )
        assert result["confidence"] == "high"
        assert result["alert"] is None

    def test_medium_confidence_low_intel(self):
        """avg_intel < 0.4 → confidence 'medium'."""
        # avg_intel = (threat_intel + geopolitical) / 2 = (0.3 + 0.3) / 2 = 0.3 < 0.4
        # tech_intel_gap = 0.5 - 0.3 = 0.2 < 0.35
        # geo_mismatch = |0.5 - 0.3| = 0.2 < 0.35
        result = cyber_friction(
            technical=0.5, threat_intel=0.3, operational_impact=0.5, geopolitical=0.3
        )
        assert result["confidence"] == "medium"
        assert "INTELLIGENCE GAP" in result["alert"]

    def test_intel_boundary_at_0_4(self):
        """avg_intel = 0.4 exactly → confidence stays 'high' (< not <=)."""
        # avg_intel = (0.4 + 0.4) / 2 = 0.4, not < 0.4
        result = cyber_friction(
            technical=0.5, threat_intel=0.4, operational_impact=0.5, geopolitical=0.4
        )
        assert result["confidence"] == "high"


# =============================================================================
# Military Friction: Bottleneck Detection
# =============================================================================

class TestMilitaryBottleneck:
    """Test bottleneck is always reported, even in low-risk cases."""

    def test_bottleneck_reported_even_when_low_risk(self):
        """Even with all-high inputs, a bottleneck layer is identified."""
        result = military_friction(
            maneuver=0.8, intelligence=0.7, sustainment=0.9, political=0.85
        )
        # min is intelligence at 0.7
        assert result["bottleneck"] == "intelligence"
        # Risk should be low
        assert result["risk_rating"] == "low"

    def test_logistics_bottleneck_alert(self):
        """sustainment below threshold triggers LOGISTICS BOTTLENECK."""
        result = military_friction(
            maneuver=0.8, intelligence=0.7, sustainment=0.2, political=0.8
        )
        assert result["bottleneck"] == "sustainment"
        assert "LOGISTICS BOTTLENECK" in result["alert"]


# =============================================================================
# Social Friction: Narrative Rupture
# =============================================================================

class TestSocialCapacityInversion:
    """Test that institutional capacity is correctly inverted."""

    def test_high_institutional_lag_means_low_capacity(self):
        """institutional=0.8 (high lag) → capacity=0.2 (low)."""
        # propagation = (individual + network) / 2 = (0.9 + 0.9) / 2 = 0.9
        # capacity = 1 - institutional = 1 - 0.8 = 0.2
        # velocity_gap = 0.9 - 0.2 = 0.7 > 0.5(rupture) ✓
        # propagation = 0.9 > 0.7(rapid) ✓ → imminent
        result = social_friction(
            individual=0.9, network=0.9, institutional=0.8, cultural=0.5
        )
        assert result["rupture_timing"] == "imminent"
        assert result["alert"] is not None

    def test_low_institutional_lag_means_high_capacity(self):
        """institutional=0.1 (low lag) → capacity=0.9 (high)."""
        # propagation = (0.5 + 0.5) / 2 = 0.5
        # capacity = 1 - 0.1 = 0.9
        # velocity_gap = 0.5 - 0.9 = -0.4, not > 0.5 or > 0.3
        result = social_friction(
            individual=0.5, network=0.5, institutional=0.1, cultural=0.5
        )
        assert result["alert"] is None


# =============================================================================
# Finance Emergence: Confluence Alpha
# =============================================================================

class TestFinanceEmergenceFlowNormalization:
    """Test flow normalization from [-1,1] to [0,1] for kernel."""

    def test_negative_flow_maps_to_low_kernel_value(self):
        """flow=-1.0 normalizes to L=0.0 for kernel."""
        result = finance_emergence(
            technical_setup=0.85, macro_tailwind=0.80,
            flow_positioning=-1.0, risk_compression=0.70
        )
        # flow=-1 → normalized to 0.0 for kernel
        # |flow|=1.0 > 0.5 → flow_favorable
        assert result["window_detected"] is True
        assert result["position_direction"] == "long"  # flow < 0 → long

    def test_positive_flow_maps_to_high_kernel_value(self):
        """flow=1.0 normalizes to L=1.0 for kernel."""
        result = finance_emergence(
            technical_setup=0.85, macro_tailwind=0.80,
            flow_positioning=1.0, risk_compression=0.70
        )
        assert result["window_detected"] is True
        assert result["position_direction"] == "short"  # flow > 0 → short

    def test_zero_flow_no_window(self):
        """flow=0.0 → |flow|=0.0 < 0.5 → not extreme → no window."""
        result = finance_emergence(
            technical_setup=0.85, macro_tailwind=0.80,
            flow_positioning=0.0, risk_compression=0.70
        )
        assert result["window_detected"] is False
        assert "Flow not extreme enough" in result["reason"]


# =============================================================================
# Healthcare Emergence: Precision Therapeutic Window
# =============================================================================

class TestHealthcareEmergenceConfluence:
    """Test confluence logic: ALL layers must exceed threshold."""

    def test_one_layer_below_threshold_no_window(self):
        """Even one layer below alignment threshold blocks window."""
        result = healthcare_emergence(
            genomic_predisposition=0.90,
            environmental_readiness=0.85,
            phenotypic_timing=0.88,
            psychosocial_engagement=0.60  # Below 0.65 threshold
        )
        assert result["window_detected"] is False

    def test_all_layers_above_threshold_window_detected(self):
        """All layers above alignment threshold → window detected."""
        result = healthcare_emergence(
            genomic_predisposition=0.70,
            environmental_readiness=0.70,
            phenotypic_timing=0.70,
            psychosocial_engagement=0.70
        )
        assert result["window_detected"] is True

    def test_optimal_vs_favorable_window(self):
        """All > 0.80 → OPTIMAL, all > 0.65 but not all > 0.80 → FAVORABLE."""
        optimal = healthcare_emergence(
            genomic_predisposition=0.85,
            environmental_readiness=0.85,
            phenotypic_timing=0.85,
            psychosocial_engagement=0.85
        )
        assert "OPTIMAL" in optimal["window_type"]

        favorable = healthcare_emergence(
            genomic_predisposition=0.70,
            environmental_readiness=0.70,
            phenotypic_timing=0.70,
            psychosocial_engagement=0.70
        )
        assert "FAVORABLE" in favorable["window_type"]


# =============================================================================
# Climate Emergence: Resilience Multiplier
# =============================================================================

class TestClimateEmergenceCoupling:
    """Test pairwise coupling logic."""

    def test_all_high_layers_high_multiplier(self):
        """All layers high → strong coupling → HIGH_MULTIPLIER."""
        result = climate_emergence(
            atmospheric_benefit=0.85,
            ecological_benefit=0.85,
            infrastructure_benefit=0.85,
            policy_alignment=0.85
        )
        assert result["window_detected"] is True
        assert result["intervention_type"] == "HIGH_MULTIPLIER"

    def test_one_layer_below_min_no_window(self):
        """min(L) must exceed min_layer threshold (0.50)."""
        result = climate_emergence(
            atmospheric_benefit=0.85,
            ecological_benefit=0.85,
            infrastructure_benefit=0.85,
            policy_alignment=0.3  # Below 0.50 threshold
        )
        assert result["window_detected"] is False


# =============================================================================
# Social Emergence: Catalytic Alignment
# =============================================================================

class TestSocialEmergenceInteractionCoefficients:
    """Test that interaction coefficients are modified by network_bridges."""

    def test_high_network_bridges_boosts_interaction(self):
        """network_bridges=1.0 → I[1] = min(1.0, 0.9 + 1.0*0.1) = 1.0."""
        result_high = social_emergence(
            individual_readiness=0.80,
            network_bridges=1.0,
            policy_window=0.80,
            paradigm_momentum=0.80
        )
        result_low = social_emergence(
            individual_readiness=0.80,
            network_bridges=0.0,  # I[1] = 0.9
            policy_window=0.80,
            paradigm_momentum=0.80
        )
        # Higher network bridges should produce higher M-score
        # (though the main effect is also on L[1] itself)
        # Both detect window since catalyst = min(L[0], L[1], L[2])
        # Low bridges: catalyst = min(0.8, 0.0, 0.8) = 0.0 → no window
        assert result_high["window_detected"] is True
        assert result_low["window_detected"] is False

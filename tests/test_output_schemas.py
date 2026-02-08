"""
Output Schema Consistency Tests

Verifies that all 14 public tools return consistent output schemas
with required keys present in all code paths.

Run with: python -m pytest tests/test_output_schemas.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np

from adapters.openai_adapter import TOOL_MAP


# =============================================================================
# Inputs that trigger different code paths per tool
# =============================================================================

# Inputs designed to trigger alerts/windows (high-activation)
HIGH_INPUTS = {
    "healthcare_phenotype_genotype": {"phenotypic": 0.3, "genomic": 0.9, "environmental": 0.4, "psychosocial": 0.8},
    "finance_regime_conflict": {"technical": 0.9, "macro": 0.3, "flow": -0.8, "risk": 0.2},
    "cyber_attribution_resolver": {"technical": 0.9, "threat_intel": 0.2, "operational_impact": 0.7, "geopolitical": 0.3},
    "climate_maladaptation": {"atmospheric": 0.7, "ecological": 0.2, "infrastructure": 0.8, "policy": 0.3},
    "legal_precedent_drift": {"black_letter": 0.8, "precedent": 0.2, "operational": 0.5, "socio_political": 0.7},
    "military_friction_forecast": {"maneuver": 0.8, "intelligence": 0.7, "sustainment": 0.2, "political": 0.8},
    "social_narrative_rupture": {"individual": 0.9, "network": 0.9, "institutional": 0.8, "cultural": 0.5},
    "healthcare_precision_therapeutic": {"genomic_predisposition": 0.9, "environmental_readiness": 0.85, "phenotypic_timing": 0.9, "psychosocial_engagement": 0.9},
    "finance_confluence_alpha": {"technical_setup": 0.85, "macro_tailwind": 0.80, "flow_positioning": 0.75, "risk_compression": 0.70},
    "cyber_adversary_overreach": {"threat_intel_stretch": 0.85, "geopolitical_pressure": 0.80, "operational_hardening": 0.85, "tool_reuse_fatigue": 0.90},
    "climate_resilience_multiplier": {"atmospheric_benefit": 0.85, "ecological_benefit": 0.85, "infrastructure_benefit": 0.85, "policy_alignment": 0.85},
    "legal_precedent_seeding": {"socio_political_climate": 0.85, "institutional_capacity": 0.80, "statutory_ambiguity": 0.85, "circuit_split": 0.90},
    "military_strategic_initiative": {"enemy_ambiguity": 0.90, "positional_advantage": 0.90, "logistic_readiness": 0.90, "authorization_clarity": 0.90},
    "social_catalytic_alignment": {"individual_readiness": 0.85, "network_bridges": 0.80, "policy_window": 0.85, "paradigm_momentum": 0.90},
}

# Inputs designed to NOT trigger alerts/windows (low-activation)
LOW_INPUTS = {
    "healthcare_phenotype_genotype": {"phenotypic": 0.6, "genomic": 0.7, "environmental": 0.5, "psychosocial": 0.5},
    "finance_regime_conflict": {"technical": 0.5, "macro": 0.5, "flow": 0.5, "risk": 0.5},
    "cyber_attribution_resolver": {"technical": 0.5, "threat_intel": 0.5, "operational_impact": 0.5, "geopolitical": 0.5},
    "climate_maladaptation": {"atmospheric": 0.5, "ecological": 0.5, "infrastructure": 0.5, "policy": 0.5},
    "legal_precedent_drift": {"black_letter": 0.8, "precedent": 0.8, "operational": 0.8, "socio_political": 0.1},
    "military_friction_forecast": {"maneuver": 0.8, "intelligence": 0.8, "sustainment": 0.8, "political": 0.8},
    "social_narrative_rupture": {"individual": 0.3, "network": 0.3, "institutional": 0.1, "cultural": 0.1},
    "healthcare_precision_therapeutic": {"genomic_predisposition": 0.3, "environmental_readiness": 0.3, "phenotypic_timing": 0.3, "psychosocial_engagement": 0.3},
    "finance_confluence_alpha": {"technical_setup": 0.3, "macro_tailwind": 0.3, "flow_positioning": 0.0, "risk_compression": 0.3},
    "cyber_adversary_overreach": {"threat_intel_stretch": 0.3, "geopolitical_pressure": 0.3, "operational_hardening": 0.3, "tool_reuse_fatigue": 0.3},
    "climate_resilience_multiplier": {"atmospheric_benefit": 0.3, "ecological_benefit": 0.3, "infrastructure_benefit": 0.3, "policy_alignment": 0.3},
    "legal_precedent_seeding": {"socio_political_climate": 0.3, "institutional_capacity": 0.3, "statutory_ambiguity": 0.3, "circuit_split": 0.3},
    "military_strategic_initiative": {"enemy_ambiguity": 0.3, "positional_advantage": 0.3, "logistic_readiness": 0.3, "authorization_clarity": 0.3},
    "social_catalytic_alignment": {"individual_readiness": 0.3, "network_bridges": 0.3, "policy_window": 0.3, "paradigm_momentum": 0.3},
}

FRICTION_TOOLS = [
    "healthcare_phenotype_genotype", "finance_regime_conflict",
    "cyber_attribution_resolver", "climate_maladaptation",
    "legal_precedent_drift", "military_friction_forecast",
    "social_narrative_rupture",
]

EMERGENCE_TOOLS = [
    "healthcare_precision_therapeutic", "finance_confluence_alpha",
    "cyber_adversary_overreach", "climate_resilience_multiplier",
    "legal_precedent_seeding", "military_strategic_initiative",
    "social_catalytic_alignment",
]


# =============================================================================
# Universal Keys
# =============================================================================

class TestUniversalKeys:
    """Every public tool must return m_score, spatial_component, overrides_applied."""

    @pytest.mark.parametrize("tool_name", list(TOOL_MAP.keys()))
    def test_m_score_present_high(self, tool_name):
        """m_score present in high-activation output."""
        result = TOOL_MAP[tool_name](**HIGH_INPUTS[tool_name])
        assert "m_score" in result, f"{tool_name} missing m_score"
        assert isinstance(result["m_score"], float)

    @pytest.mark.parametrize("tool_name", list(TOOL_MAP.keys()))
    def test_m_score_present_low(self, tool_name):
        """m_score present in low-activation output."""
        result = TOOL_MAP[tool_name](**LOW_INPUTS[tool_name])
        assert "m_score" in result, f"{tool_name} missing m_score"
        assert isinstance(result["m_score"], float)

    @pytest.mark.parametrize("tool_name", list(TOOL_MAP.keys()))
    def test_spatial_component_present(self, tool_name):
        """spatial_component present in all outputs."""
        result = TOOL_MAP[tool_name](**HIGH_INPUTS[tool_name])
        assert "spatial_component" in result, f"{tool_name} missing spatial_component"

    @pytest.mark.parametrize("tool_name", list(TOOL_MAP.keys()))
    def test_overrides_applied_present(self, tool_name):
        """overrides_applied present (empty dict when no overrides)."""
        result = TOOL_MAP[tool_name](**HIGH_INPUTS[tool_name])
        assert "overrides_applied" in result, f"{tool_name} missing overrides_applied"

    @pytest.mark.parametrize("tool_name", list(TOOL_MAP.keys()))
    def test_thresholds_present(self, tool_name):
        """thresholds dict present in all outputs."""
        result = TOOL_MAP[tool_name](**HIGH_INPUTS[tool_name])
        assert "thresholds" in result, f"{tool_name} missing thresholds"


# =============================================================================
# Friction Tool Schema
# =============================================================================

class TestFrictionSchema:
    """Friction tools must have 'alert' key in both paths."""

    @pytest.mark.parametrize("tool_name", FRICTION_TOOLS)
    def test_alert_key_present_high(self, tool_name):
        """alert key present when triggered."""
        result = TOOL_MAP[tool_name](**HIGH_INPUTS[tool_name])
        assert "alert" in result, f"{tool_name} missing alert key"

    @pytest.mark.parametrize("tool_name", FRICTION_TOOLS)
    def test_alert_key_present_low(self, tool_name):
        """alert key present when NOT triggered (should be None)."""
        result = TOOL_MAP[tool_name](**LOW_INPUTS[tool_name])
        assert "alert" in result, f"{tool_name} missing alert key in low-activation"


# =============================================================================
# Emergence Tool Schema
# =============================================================================

class TestEmergenceSchema:
    """Emergence tools must have 'window_detected' in both paths."""

    @pytest.mark.parametrize("tool_name", EMERGENCE_TOOLS)
    def test_window_detected_key_present_high(self, tool_name):
        """window_detected present when triggered."""
        result = TOOL_MAP[tool_name](**HIGH_INPUTS[tool_name])
        assert "window_detected" in result, f"{tool_name} missing window_detected"
        assert result["window_detected"] is True

    @pytest.mark.parametrize("tool_name", EMERGENCE_TOOLS)
    def test_window_detected_key_present_low(self, tool_name):
        """window_detected present when NOT triggered."""
        result = TOOL_MAP[tool_name](**LOW_INPUTS[tool_name])
        assert "window_detected" in result, f"{tool_name} missing window_detected"
        assert result["window_detected"] is False

    @pytest.mark.parametrize("tool_name", EMERGENCE_TOOLS)
    def test_layer_attribution_present_in_high(self, tool_name):
        """layer_attribution should be present when window detected."""
        result = TOOL_MAP[tool_name](**HIGH_INPUTS[tool_name])
        assert "layer_attribution" in result, \
            f"{tool_name} missing layer_attribution in window-detected branch"


# =============================================================================
# Layer Attribution Consistency
# =============================================================================

class TestLayerAttributionConsistency:
    """layer_attribution values should sum to ~1.0."""

    @pytest.mark.parametrize("tool_name", list(TOOL_MAP.keys()))
    def test_attribution_sums_to_one(self, tool_name):
        """layer_attribution values sum to ~1.0 (when present)."""
        result = TOOL_MAP[tool_name](**HIGH_INPUTS[tool_name])
        if "layer_attribution" in result:
            attr = result["layer_attribution"]
            attr_sum = sum(attr.values())
            assert np.isclose(attr_sum, 1.0, atol=0.01), \
                f"{tool_name} attribution sum={attr_sum}, expected ~1.0"

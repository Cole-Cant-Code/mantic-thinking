"""
Layer Visibility Tests for Mantic Framework v1.2.0

Tests the layer introspection module and tool response additions.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np

from mantic_thinking.mantic.introspection import get_layer_visibility, LAYER_DEFINITIONS


class TestLayerDefinitions:
    """Test layer definition constants."""

    def test_layer_definitions_structure(self):
        """Test that all 4 layers are defined."""
        assert "Micro" in LAYER_DEFINITIONS
        assert "Meso" in LAYER_DEFINITIONS
        assert "Macro" in LAYER_DEFINITIONS
        assert "Meta" in LAYER_DEFINITIONS

    def test_layer_definitions_have_required_fields(self):
        """Test each layer has symbol, description, timescale."""
        for layer_name, layer_def in LAYER_DEFINITIONS.items():
            assert "symbol" in layer_def
            assert "description" in layer_def
            assert "timescale" in layer_def
            assert "examples" in layer_def


class TestGetLayerVisibility:
    """Test layer visibility computation."""

    def test_healthcare_friction_weight_only_mode(self):
        """Test healthcare friction without input values (weight-only mode)."""
        weights = {
            'phenotypic': 0.40,
            'genomic': 0.20,
            'environmental': 0.25,
            'psychosocial': 0.15
        }
        vis = get_layer_visibility("healthcare_phenotype_genotype", weights)
        
        assert vis is not None
        assert vis["dominant"] == "Micro"  # Based on weights
        assert vis["input_driven"] is False
        assert abs(vis["weights_by_layer"]["Micro"] - 0.60) < 1e-10
        assert abs(vis["weights_by_layer"]["Meso"] - 0.40) < 1e-10
        assert "rationale" in vis
        assert "_note" in vis

    def test_healthcare_friction_input_driven_mode(self):
        """Test healthcare friction with input values (input-driven mode)."""
        weights = {
            'phenotypic': 0.40,
            'genomic': 0.20,
            'environmental': 0.25,
            'psychosocial': 0.15
        }
        # High environmental/psychosocial values should shift dominance to Meso
        layer_values = {
            'phenotypic': 0.1,
            'genomic': 0.2,
            'environmental': 0.9,
            'psychosocial': 0.9
        }
        vis = get_layer_visibility("healthcare_phenotype_genotype", weights, layer_values)
        
        assert vis is not None
        assert vis["input_driven"] is True
        assert "contributions_by_layer" in vis
        # Meso should have higher contribution due to high env/psych values
        # Micro: 0.4*0.1 + 0.2*0.2 = 0.04 + 0.04 = 0.08
        # Meso: 0.25*0.9 + 0.15*0.9 = 0.225 + 0.135 = 0.36
        assert vis["contributions_by_layer"]["Meso"] > vis["contributions_by_layer"]["Micro"]
        assert vis["dominant"] == "Meso"

    def test_finance_regime_macro_heavy(self):
        """Test finance friction has Macro weight."""
        weights = {
            'technical': 0.35,
            'macro': 0.30,
            'flow': 0.20,
            'risk': 0.15
        }
        vis = get_layer_visibility("finance_regime_conflict", weights)
        
        assert vis is not None
        assert vis["weights_by_layer"]["Macro"] == 0.30
        assert vis["weights_by_layer"]["Micro"] == 0.35

    def test_unknown_tool_returns_none(self):
        """Test unknown tool name returns None."""
        vis = get_layer_visibility("unknown_tool_xyz", {})
        assert vis is None


class TestToolResponses:
    """Test that tools include layer_visibility in responses."""

    def test_healthcare_friction_includes_layer_visibility(self):
        """Test healthcare friction returns layer_visibility."""
        from mantic_thinking.tools.friction.healthcare_phenotype_genotype import detect
        
        result = detect(
            phenotypic=0.3,
            genomic=0.9,
            environmental=0.4,
            psychosocial=0.8
        )
        
        assert "layer_visibility" in result
        assert result["layer_visibility"]["dominant"] == "Micro"
        assert "rationale" in result["layer_visibility"]

    def test_healthcare_emergence_includes_layer_visibility(self):
        """Test healthcare emergence returns layer_visibility."""
        from mantic_thinking.tools.emergence.healthcare_precision_therapeutic import detect
        
        result = detect(
            genomic_predisposition=0.85,
            environmental_readiness=0.82,
            phenotypic_timing=0.88,
            psychosocial_engagement=0.90
        )
        
        assert "layer_visibility" in result
        assert "dominant" in result["layer_visibility"]
        assert "weights_by_layer" in result["layer_visibility"]

    def test_finance_friction_includes_layer_visibility(self):
        """Test finance friction returns layer_visibility."""
        from mantic_thinking.tools.friction.finance_regime_conflict import detect
        
        result = detect(
            technical=0.7,
            macro=0.6,
            flow=0.5,
            risk=0.6
        )
        
        assert "layer_visibility" in result

    def test_finance_emergence_includes_layer_visibility(self):
        """Test finance emergence returns layer_visibility."""
        from mantic_thinking.tools.emergence.finance_confluence_alpha import detect
        
        result = detect(
            technical_setup=0.85,
            macro_tailwind=0.80,
            flow_positioning=0.75,
            risk_compression=0.70
        )
        
        assert "layer_visibility" in result

    def test_all_tools_include_layer_visibility(self):
        """Test all 17 tools include layer_visibility."""
        from mantic_thinking.adapters.openai_adapter import TOOL_MAP
        
        test_params = {
            "healthcare_phenotype_genotype": {
                "phenotypic": 0.5, "genomic": 0.6, "environmental": 0.4, "psychosocial": 0.5
            },
            "finance_regime_conflict": {
                "technical": 0.7, "macro": 0.6, "flow": 0.5, "risk": 0.6
            },
            "cyber_attribution_resolver": {
                "technical": 0.8, "threat_intel": 0.7, "operational_impact": 0.6, "geopolitical": 0.5
            },
            "climate_maladaptation": {
                "atmospheric": 0.6, "ecological": 0.7, "infrastructure": 0.5, "policy": 0.6
            },
            "legal_precedent_drift": {
                "black_letter": 0.7, "precedent": 0.8, "operational": 0.6, "socio_political": 0.2
            },
            "military_friction_forecast": {
                "maneuver": 0.7, "intelligence": 0.8, "sustainment": 0.6, "political": 0.7
            },
            "social_narrative_rupture": {
                "individual": 0.5, "network": 0.6, "institutional": 0.4, "cultural": 0.3
            },
            "healthcare_precision_therapeutic": {
                "genomic_predisposition": 0.85, "environmental_readiness": 0.82,
                "phenotypic_timing": 0.88, "psychosocial_engagement": 0.90
            },
            "finance_confluence_alpha": {
                "technical_setup": 0.85, "macro_tailwind": 0.80,
                "flow_positioning": 0.75, "risk_compression": 0.70
            },
            "cyber_adversary_overreach": {
                "threat_intel_stretch": 0.90, "geopolitical_pressure": 0.85,
                "operational_hardening": 0.80, "tool_reuse_fatigue": 0.88
            },
            "climate_resilience_multiplier": {
                "atmospheric_benefit": 0.75, "ecological_benefit": 0.80,
                "infrastructure_benefit": 0.78, "policy_alignment": 0.82
            },
            "legal_precedent_seeding": {
                "socio_political_climate": 0.85, "institutional_capacity": 0.80,
                "statutory_ambiguity": 0.88, "circuit_split": 0.82
            },
            "military_strategic_initiative": {
                "enemy_ambiguity": 0.85, "positional_advantage": 0.88,
                "logistic_readiness": 0.82, "authorization_clarity": 0.90
            },
            "social_catalytic_alignment": {
                "individual_readiness": 0.82, "network_bridges": 0.85,
                "policy_window": 0.80, "paradigm_momentum": 0.88
            },
            "system_lock_recursive_control": {
                "agent_autonomy": 0.30, "collective_capacity": 0.35,
                "concentration_control": 0.80, "recursive_depth": 0.75
            },
            "system_lock_dissolution_window": {
                "autonomy_momentum": 0.72, "alternative_readiness": 0.76,
                "control_vulnerability": 0.74, "pattern_flexibility": 0.68
            },
            "generic_detect": {
                "domain_name": "vis_test", "layer_names": ["a", "b", "c", "d"],
                "weights": [0.25, 0.25, 0.25, 0.25],
                "layer_values": [0.7, 0.6, 0.8, 0.5], "mode": "friction",
                "layer_hierarchy": {"a": "Micro", "b": "Meso", "c": "Macro", "d": "Meta"}
            }
        }

        for tool_name, func in TOOL_MAP.items():
            params = test_params[tool_name]
            result = func(**params)
            assert "layer_visibility" in result, f"{tool_name} missing layer_visibility"
            assert "dominant" in result["layer_visibility"], f"{tool_name} layer_visibility missing dominant"
            assert "layer_coupling" in result, f"{tool_name} missing layer_coupling"
            coupling = result["layer_coupling"]
            assert coupling is not None, f"{tool_name} layer_coupling should not be None"
            assert 0.0 <= coupling["coherence"] <= 1.0, f"{tool_name} coherence out of bounds"
            assert "layers" in coupling and isinstance(coupling["layers"], dict), f"{tool_name} coupling layers missing"
            assert set(coupling["layers"].keys()) == set(result["layer_attribution"].keys())
            for layer_name, entry in coupling["layers"].items():
                assert "agreement" in entry, f"{tool_name}.{layer_name} missing agreement"
                assert 0.0 <= entry["agreement"] <= 1.0, f"{tool_name}.{layer_name} agreement out of bounds"
                if "tension_with" in entry:
                    for other_layer, agree in entry["tension_with"].items():
                        assert agree < 0.5, f"{tool_name}.{layer_name} tension_with should be < 0.5"


class TestBackwardCompatibility:
    """Ensure backward compatibility."""

    def test_original_fields_still_present(self):
        """Test that old fields are not removed."""
        from mantic_thinking.tools.friction.healthcare_phenotype_genotype import detect
        
        result = detect(
            phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8
        )
        
        # Original fields must exist
        assert "m_score" in result
        assert "spatial_component" in result
        assert "layer_attribution" in result
        assert "alert" in result
        assert "thresholds" in result


class TestAdapterExplainResult:
    """Test adapter explain_result helpers."""

    def test_kimi_explain_result(self):
        """Test Kimi adapter explain_result."""
        from mantic_thinking.adapters.kimi_adapter import explain_result
        
        result = {
            "m_score": 0.75,
            "layer_visibility": {
                "dominant": "Micro",
                "rationale": "Test rationale",
                "weights_by_layer": {"Micro": 0.6, "Meso": 0.4, "Macro": 0, "Meta": 0}
            }
        }
        
        explanation = explain_result("healthcare_phenotype_genotype", result)
        
        assert explanation is not None
        assert explanation["dominant_layer"] == "Micro"
        assert "reasoning_hints" in explanation

    def test_explain_result_no_layer_visibility(self):
        """Test explain_result returns None if no layer_visibility."""
        from mantic_thinking.adapters.kimi_adapter import explain_result
        
        result = {"m_score": 0.75}  # No layer_visibility
        explanation = explain_result("test_tool", result)
        
        assert explanation is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

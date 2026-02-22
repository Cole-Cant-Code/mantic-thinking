"""
Cross-Model Deep Tests

Tests the Gemini adapter (zero existing coverage), Claude adapter
argument filtering gap, and all-adapter parity across 17 tools.

Run with: python -m pytest tests/test_cross_model_deep.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np

from mantic_thinking.adapters.openai_adapter import get_openai_tools, execute_tool as execute_openai, TOOL_MAP
from mantic_thinking.adapters.kimi_adapter import get_kimi_tools, execute as execute_kimi
from mantic_thinking.adapters.claude_adapter import get_claude_tools, execute_tool as execute_claude
from mantic_thinking.adapters.gemini_adapter import get_gemini_tools, get_gemini_tools_flat, execute_tool as execute_gemini


# Standard test inputs for each tool
TOOL_INPUTS = {
    "healthcare_phenotype_genotype": {"phenotypic": 0.3, "genomic": 0.9, "environmental": 0.4, "psychosocial": 0.8},
    "finance_regime_conflict": {"technical": 0.7, "macro": 0.5, "flow": -0.3, "risk": 0.6},
    "cyber_attribution_resolver": {"technical": 0.6, "threat_intel": 0.4, "operational_impact": 0.5, "geopolitical": 0.7},
    "climate_maladaptation": {"atmospheric": 0.5, "ecological": 0.6, "infrastructure": 0.7, "policy": 0.4},
    "legal_precedent_drift": {"black_letter": 0.7, "precedent": 0.3, "operational": 0.5, "socio_political": 0.6},
    "military_friction_forecast": {"maneuver": 0.6, "intelligence": 0.5, "sustainment": 0.3, "political": 0.7},
    "social_narrative_rupture": {"individual": 0.7, "network": 0.8, "institutional": 0.6, "cultural": 0.3},
    "healthcare_precision_therapeutic": {"genomic_predisposition": 0.85, "environmental_readiness": 0.80, "phenotypic_timing": 0.88, "psychosocial_engagement": 0.90},
    "finance_confluence_alpha": {"technical_setup": 0.85, "macro_tailwind": 0.80, "flow_positioning": 0.75, "risk_compression": 0.70},
    "cyber_adversary_overreach": {"threat_intel_stretch": 0.7, "geopolitical_pressure": 0.6, "operational_hardening": 0.8, "tool_reuse_fatigue": 0.75},
    "climate_resilience_multiplier": {"atmospheric_benefit": 0.7, "ecological_benefit": 0.8, "infrastructure_benefit": 0.6, "policy_alignment": 0.75},
    "legal_precedent_seeding": {"socio_political_climate": 0.7, "institutional_capacity": 0.8, "statutory_ambiguity": 0.75, "circuit_split": 0.85},
    "military_strategic_initiative": {"enemy_ambiguity": 0.7, "positional_advantage": 0.8, "logistic_readiness": 0.85, "authorization_clarity": 0.9},
    "social_catalytic_alignment": {"individual_readiness": 0.75, "network_bridges": 0.8, "policy_window": 0.7, "paradigm_momentum": 0.85},
    "system_lock_recursive_control": {"agent_autonomy": 0.25, "collective_capacity": 0.35, "concentration_control": 0.8, "recursive_depth": 0.75},
    "system_lock_dissolution_window": {"autonomy_momentum": 0.72, "alternative_readiness": 0.78, "control_vulnerability": 0.74, "pattern_flexibility": 0.66},
    "generic_detect": {"domain_name": "test_cross", "layer_names": ["a", "b", "c", "d"], "weights": [0.25, 0.25, 0.25, 0.25], "layer_values": [0.7, 0.6, 0.8, 0.5], "mode": "friction"},
}


# =============================================================================
# Gemini Adapter Tests (Zero Prior Coverage)
# =============================================================================

class TestGeminiAdapter:
    """Gemini adapter has zero existing test coverage."""

    def test_gemini_tool_count(self):
        """Gemini adapter should expose exactly 17 tools."""
        tools = get_gemini_tools()
        declarations = tools[0]["function_declarations"]
        assert len(declarations) == 17

    def test_gemini_flat_tool_count(self):
        """Flat format should also have 17 tools."""
        tools = get_gemini_tools_flat()
        assert len(tools) == 17

    @pytest.mark.parametrize("tool_name", list(TOOL_MAP.keys()))
    def test_gemini_execute_all_tools(self, tool_name):
        """Execute each tool through Gemini adapter successfully."""
        result = execute_gemini(tool_name, TOOL_INPUTS[tool_name])
        assert "m_score" in result
        assert isinstance(result["m_score"], float)

    def test_gemini_unknown_tool_raises(self):
        """Unknown tool name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown tool"):
            execute_gemini("nonexistent_tool", {})

    def test_gemini_no_internal_tools(self):
        """Gemini should NOT expose internal tools."""
        tools = get_gemini_tools_flat()
        tool_names = [t["name"] for t in tools]
        assert "codebase_layer_conflict" not in tool_names
        assert "codebase_alignment_window" not in tool_names
        assert "plan_alignment_window" not in tool_names


# =============================================================================
# Cross-Adapter Parity
# =============================================================================

class TestCrossAdapterParity:
    """All 4 adapters should produce identical M-scores."""

    @pytest.mark.parametrize("tool_name", list(TOOL_MAP.keys()))
    def test_all_adapters_same_m_score(self, tool_name):
        """All 4 adapters produce identical M-score for same inputs."""
        inputs = TOOL_INPUTS[tool_name]

        openai_result = execute_openai(tool_name, inputs)
        kimi_result = execute_kimi(tool_name, inputs)
        gemini_result = execute_gemini(tool_name, inputs)

        # Claude adapter adds _claude_meta but core keys should match
        claude_result = execute_claude(tool_name, inputs)

        m_openai = openai_result["m_score"]
        m_kimi = kimi_result["m_score"]
        m_gemini = gemini_result["m_score"]
        m_claude = claude_result["m_score"]

        assert m_openai == m_kimi == m_gemini == m_claude, \
            f"{tool_name}: OpenAI={m_openai}, Kimi={m_kimi}, Gemini={m_gemini}, Claude={m_claude}"


# =============================================================================
# Adapter Tool Counts
# =============================================================================

class TestAdapterToolCounts:
    """All adapters should expose exactly 17 tools."""

    def test_openai_17_tools(self):
        assert len(get_openai_tools()) == 17

    def test_kimi_17_tools(self):
        assert len(get_kimi_tools()) == 17

    def test_claude_17_tools(self):
        assert len(get_claude_tools()) == 17

    def test_gemini_17_tools(self):
        assert len(get_gemini_tools_flat()) == 17


# =============================================================================
# Claude Adapter Specifics
# =============================================================================

class TestClaudeAdapterSpecifics:
    """Claude adapter adds metadata without corrupting results."""

    def test_claude_meta_present(self):
        """Claude results include _claude_meta."""
        result = execute_claude("healthcare_phenotype_genotype",
                                TOOL_INPUTS["healthcare_phenotype_genotype"])
        assert "_claude_meta" in result
        assert result["_claude_meta"]["execution_successful"] is True

    def test_claude_does_not_corrupt_core_keys(self):
        """Claude's _claude_meta doesn't overwrite any tool keys."""
        inputs = TOOL_INPUTS["healthcare_phenotype_genotype"]
        raw_result = TOOL_MAP["healthcare_phenotype_genotype"](**inputs)
        claude_result = execute_claude("healthcare_phenotype_genotype", inputs)

        for key in raw_result:
            assert key in claude_result, f"Claude adapter lost key: {key}"
            assert claude_result[key] == raw_result[key], \
                f"Claude adapter corrupted key {key}: {raw_result[key]} → {claude_result[key]}"

    def test_claude_filters_extra_kwargs(self):
        """Claude adapter now filters arguments via inspect.signature (like OpenAI)."""
        # Extra param is silently filtered — no TypeError
        result = execute_claude("healthcare_phenotype_genotype", {
            "phenotypic": 0.3, "genomic": 0.9,
            "environmental": 0.4, "psychosocial": 0.8,
            "extra_unknown_param": 999  # Not in detect() signature
        })
        assert "m_score" in result

    def test_openai_filters_extra_kwargs(self):
        """OpenAI adapter DOES filter arguments via inspect.signature."""
        # This should NOT raise - extra param is silently filtered
        result = execute_openai("healthcare_phenotype_genotype", {
            "phenotypic": 0.3, "genomic": 0.9,
            "environmental": 0.4, "psychosocial": 0.8,
            "extra_unknown_param": 999
        })
        assert "m_score" in result

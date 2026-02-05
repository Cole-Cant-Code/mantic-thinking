"""
Cross-Model Compatibility Tests for Mantic Early Warning System

Validates that all tools work correctly across:
- Native Python interface
- OpenAI/Codex function calling format
- Kimi native tool format
- Claude Computer Use format

Run with: python -m pytest tests/test_cross_model.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np

from core.mantic_kernel import mantic_kernel, verify_kernel_integrity, compute_temporal_kernel
from core.validators import clamp_input, normalize_weights, validate_layers
from adapters.openai_adapter import get_openai_tools, execute_tool as execute_openai
from adapters.kimi_adapter import get_kimi_tools, execute as execute_kimi
from adapters.claude_adapter import get_claude_tools, execute_tool as execute_claude

from tools import (
    healthcare_phenotype_genotype,
    finance_regime_conflict,
    cyber_attribution_resolver,
    climate_maladaptation,
    legal_precedent_drift,
    military_friction_forecast,
    social_narrative_rupture,
)


# =============================================================================
# Core Kernel Tests
# =============================================================================

class TestManticKernel:
    """Test the immutable mantic kernel formula."""
    
    def test_kernel_integrity(self):
        """Verify kernel implementation hasn't been tampered with."""
        assert verify_kernel_integrity()
    
    def test_basic_calculation(self):
        """Test basic kernel calculation."""
        W = [0.25, 0.25, 0.25, 0.25]
        L = [0.5, 0.5, 0.5, 0.5]
        I = [1.0, 1.0, 1.0, 1.0]
        
        M, S, attr = mantic_kernel(W, L, I)
        
        assert np.isclose(M, 0.5, atol=1e-10)
        assert np.isclose(S, 0.5, atol=1e-10)
        assert len(attr) == 4
        assert all(np.isclose(a, 0.25, atol=1e-10) for a in attr)
    
    def test_nan_handling(self):
        """Test graceful degradation with missing data."""
        W = [0.25, 0.25, 0.25, 0.25]
        L = [0.5, np.nan, 0.5, 0.5]
        I = [1.0, 1.0, 1.0, 1.0]
        
        M, S, attr = mantic_kernel(W, L, I)
        
        # Should renormalize weights and compute with 3 layers
        # Attribution preserves original indices (missing layer -> 0.0)
        assert len(attr) == 4
        assert np.isclose(attr[1], 0.0, atol=1e-10)
        assert M > 0
    
    def test_weight_validation(self):
        """Test that invalid weights raise errors."""
        with pytest.raises(ValueError):
            # Weights don't sum to 1
            mantic_kernel([0.1, 0.2, 0.3, 0.1], [0.5, 0.5, 0.5, 0.5], [1, 1, 1, 1])
    
    def test_temporal_kernel(self):
        """Test temporal kernel multiplier."""
        W = [0.25, 0.25, 0.25, 0.25]
        L = [0.8, 0.6, 0.9, 0.4]
        I = [1.0, 1.0, 1.0, 1.0]
        
        M1, _, _ = mantic_kernel(W, L, I, f_time=1.0)
        M2, _, _ = mantic_kernel(W, L, I, f_time=2.0)
        
        assert np.isclose(M2, M1 * 2.0, atol=1e-10)


# =============================================================================
# Validator Tests
# =============================================================================

class TestValidators:
    """Test input validation utilities."""
    
    def test_clamp_input(self):
        """Test input clamping."""
        assert clamp_input(0.5) == 0.5
        assert clamp_input(1.5) == 1.0
        assert clamp_input(-0.5) == 0.0
        assert np.isnan(clamp_input(None))
    
    def test_clamp_input_range(self):
        """Test clamping with custom range."""
        assert clamp_input(-0.5, min_val=-1, max_val=1) == -0.5
        assert clamp_input(-1.5, min_val=-1, max_val=1) == -1.0
        assert clamp_input(1.5, min_val=-1, max_val=1) == 1.0
    
    def test_normalize_weights(self):
        """Test weight normalization."""
        w = normalize_weights([1, 1, 1, 1])
        assert np.isclose(w.sum(), 1.0)
        assert all(np.isclose(v, 0.25) for v in w)
    
    def test_validate_layers(self):
        """Test layer validation."""
        layers = validate_layers([0.5, 0.6, None, 0.8])
        assert len(layers) == 4
        assert layers[0] == 0.5
        assert np.isnan(layers[2])


# =============================================================================
# Domain Tool Tests
# =============================================================================

class TestHealthcareTool:
    """Test healthcare phenotype-genotype mismatch detector."""
    
    def test_normal_case(self):
        """Test normal alignment case."""
        result = healthcare_phenotype_genotype.detect(
            phenotypic=0.6, genomic=0.7, environmental=0.5, psychosocial=0.5
        )
        assert result["alert"] is None
        assert result["severity"] == 0.0
        assert "m_score" in result
    
    def test_mismatch_detected(self):
        """Test mismatch detection."""
        result = healthcare_phenotype_genotype.detect(
            phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8
        )
        assert result["alert"] is not None
        assert result["severity"] > 0
        assert result["buffering_layer"] == "psychosocial"
    
    def test_hidden_burden(self):
        """Test hidden burden detection."""
        result = healthcare_phenotype_genotype.detect(
            phenotypic=0.9, genomic=0.1, environmental=0.1, psychosocial=0.3
        )
        assert result["alert"] is not None
        assert "HIDDEN BURDEN" in result["alert"]
    
    def test_clamping(self):
        """Test input clamping."""
        result = healthcare_phenotype_genotype.detect(
            phenotypic=1.5, genomic=-0.5, environmental=0.4, psychosocial=0.8
        )
        # Should clamp inputs and still produce valid result
        assert "m_score" in result


class TestFinanceTool:
    """Test finance regime conflict monitor."""
    
    def test_normal_case(self):
        """Test normal alignment."""
        result = finance_regime_conflict.detect(
            technical=0.7, macro=0.75, flow=0.6, risk=0.6
        )
        assert result["alert"] is None
    
    def test_divergence_detected(self):
        """Test technical-macro divergence."""
        result = finance_regime_conflict.detect(
            technical=0.8, macro=0.3, flow=-0.6, risk=0.7
        )
        assert result["alert"] is not None
        assert result["conflict_type"] is not None
    
    def test_flow_contradiction(self):
        """Test flow contradiction detection."""
        result = finance_regime_conflict.detect(
            technical=0.8, macro=0.75, flow=-0.8, risk=0.6
        )
        # High technical but negative flow should trigger alert
        assert result["alert"] is not None


class TestCyberTool:
    """Test cyber attribution resolver."""
    
    def test_high_confidence(self):
        """Test high confidence case."""
        result = cyber_attribution_resolver.detect(
            technical=0.8, threat_intel=0.85, operational_impact=0.7, geopolitical=0.75
        )
        assert result["confidence"] == "high"
        assert result["alert"] is None
    
    def test_attribution_gap(self):
        """Test attribution gap detection."""
        result = cyber_attribution_resolver.detect(
            technical=0.9, threat_intel=0.3, operational_impact=0.8, geopolitical=0.2
        )
        assert result["confidence"] == "low"
        assert result["alert"] is not None
        assert "ATTRIBUTION GAP" in result["alert"]


class TestClimateTool:
    """Test climate maladaptation preventer."""
    
    def test_proceed(self):
        """Test proceed decision."""
        result = climate_maladaptation.detect(
            atmospheric=0.6, ecological=0.7, infrastructure=0.6, policy=0.7
        )
        assert result["decision"] == "proceed"
    
    def test_block(self):
        """Test block decision."""
        result = climate_maladaptation.detect(
            atmospheric=0.7, ecological=0.2, infrastructure=0.8, policy=0.3
        )
        assert result["decision"] == "block"
        assert result["alternative_suggestion"] is not None


class TestLegalTool:
    """Test legal precedent drift alert."""
    
    def test_stable(self):
        """Test stable precedent."""
        result = legal_precedent_drift.detect(
            black_letter=0.75, precedent=0.8, operational=0.7, socio_political=0.1
        )
        assert result["drift_direction"] == "stable"
    
    def test_drift_detected(self):
        """Test drift detection."""
        result = legal_precedent_drift.detect(
            black_letter=0.8, precedent=0.3, operational=0.7, socio_political=0.6
        )
        assert result["alert"] is not None
        assert result["drift_direction"] == "right"
        assert result["strategy_pivot"] is not None


class TestMilitaryTool:
    """Test military friction forecast."""
    
    def test_no_bottleneck(self):
        """Test balanced capability."""
        result = military_friction_forecast.detect(
            maneuver=0.75, intelligence=0.8, sustainment=0.7, political=0.8
        )
        assert result["risk_rating"] == "low"
    
    def test_logistics_bottleneck(self):
        """Test logistics bottleneck detection."""
        result = military_friction_forecast.detect(
            maneuver=0.8, intelligence=0.7, sustainment=0.3, political=0.6
        )
        assert result["bottleneck"] == "sustainment"
        assert result["alert"] is not None


class TestSocialTool:
    """Test social narrative rupture detector."""
    
    def test_contained(self):
        """Test contained narrative."""
        result = social_narrative_rupture.detect(
            individual=0.4, network=0.3, institutional=0.3, cultural=0.5
        )
        assert result["rupture_timing"] == "contained"
    
    def test_imminent_rupture(self):
        """Test imminent rupture detection."""
        result = social_narrative_rupture.detect(
            individual=0.8, network=0.9, institutional=0.7, cultural=-0.6
        )
        assert result["rupture_timing"] == "imminent"
        assert result["alert"] is not None


# =============================================================================
# Adapter Tests
# =============================================================================

class TestOpenAIAdapter:
    """Test OpenAI/Codex adapter."""
    
    def test_tools_count(self):
        """Test that all 14 tools are available."""
        tools = get_openai_tools()
        assert len(tools) == 14
    
    def test_tool_schema(self):
        """Test tool schema format."""
        tools = get_openai_tools()
        for tool in tools:
            assert tool["type"] == "function"
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]
    
    def test_execute_healthcare(self):
        """Test healthcare tool execution."""
        result = execute_openai("healthcare_phenotype_genotype", {
            "phenotypic": 0.3,
            "genomic": 0.9,
            "environmental": 0.4,
            "psychosocial": 0.8
        })
        assert result["alert"] is not None
        assert "m_score" in result
    
    def test_execute_all_tools(self):
        """Test that all tools can be executed."""
        test_inputs = {
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
            }
        }
        
        for tool_name, params in test_inputs.items():
            result = execute_openai(tool_name, params)
            assert "m_score" in result
            assert "layer_attribution" in result


class TestKimiAdapter:
    """Test Kimi native adapter."""
    
    def test_tools_count(self):
        """Test that all 14 tools are available."""
        tools = get_kimi_tools()
        assert len(tools) == 14
    
    def test_kimi_meta(self):
        """Test Kimi-specific metadata."""
        tools = get_kimi_tools()
        for tool in tools:
            assert "_mantic_meta" in tool
            assert tool["_mantic_meta"]["deterministic"] is True
    
    def test_execute(self):
        """Test tool execution."""
        result = execute_kimi("finance_regime_conflict", {
            "technical": 0.8, "macro": 0.3, "flow": -0.6, "risk": 0.7
        })
        assert "m_score" in result


class TestClaudeAdapter:
    """Test Claude Computer Use adapter."""
    
    def test_tools_count(self):
        """Test that all 14 tools are available."""
        tools = get_claude_tools()
        assert len(tools) == 14
    
    def test_claude_meta(self):
        """Test Claude-specific metadata."""
        tools = get_claude_tools()
        for tool in tools:
            assert "_claude_meta" in tool
            assert tool["_claude_meta"]["idempotent"] is True
    
    def test_execute(self):
        """Test tool execution."""
        result = execute_claude("cyber_attribution_resolver", {
            "technical": 0.9, "threat_intel": 0.3, "operational_impact": 0.8, "geopolitical": 0.2
        })
        assert "m_score" in result
        assert "_claude_meta" in result


# =============================================================================
# Temporal Kernel Tests
# =============================================================================

class TestTemporalKernels:
    """Test all 7 temporal kernel modes."""

    def test_exponential(self):
        """Verify exponential: exp(n * alpha * t)."""
        result = compute_temporal_kernel(t=5, n=1.0, alpha=0.1, kernel_type="exponential")
        expected = np.exp(1.0 * 0.1 * 5)
        assert np.isclose(result, expected, atol=1e-10)

    def test_exponential_decay(self):
        """Verify exponential decay with negative n."""
        result = compute_temporal_kernel(t=5, n=-1.0, alpha=0.1, kernel_type="exponential")
        expected = np.exp(-1.0 * 0.1 * 5)
        assert np.isclose(result, expected, atol=1e-10)
        assert result < 1.0  # Decay

    def test_linear(self):
        """Verify linear decay clamps to 0."""
        result = compute_temporal_kernel(t=5, alpha=0.1, kernel_type="linear")
        expected = max(0, 1 - 0.1 * 5)
        assert np.isclose(result, expected, atol=1e-10)
        # Should clamp at 0 for large t
        result_far = compute_temporal_kernel(t=20, alpha=0.1, kernel_type="linear")
        assert result_far >= 0

    def test_logistic(self):
        """Verify logistic: 1 / (1 + exp(-n*alpha*t)), output in (0, 1)."""
        result = compute_temporal_kernel(t=5, n=1.0, alpha=0.1, kernel_type="logistic")
        expected = 1.0 / (1.0 + np.exp(-1.0 * 0.1 * 5))
        assert np.isclose(result, expected, atol=1e-10)
        assert 0 < result < 1

    def test_s_curve(self):
        """Verify s_curve inflection at t0."""
        # At t=t0, output should be 0.5
        result_at_t0 = compute_temporal_kernel(t=5, alpha=0.1, kernel_type="s_curve", t0=5.0)
        assert np.isclose(result_at_t0, 0.5, atol=1e-10)
        # Before t0, output < 0.5
        result_before = compute_temporal_kernel(t=0, alpha=0.1, kernel_type="s_curve", t0=5.0)
        assert result_before < 0.5
        # After t0, output > 0.5
        result_after = compute_temporal_kernel(t=10, alpha=0.1, kernel_type="s_curve", t0=5.0)
        assert result_after > 0.5

    def test_power_law(self):
        """Verify power_law: (1+t)^(n*alpha*exponent)."""
        result = compute_temporal_kernel(t=10, n=1.0, alpha=0.1, kernel_type="power_law", exponent=1.0)
        expected = (1.0 + 10) ** (1.0 * 0.1 * 1.0)
        assert np.isclose(result, expected, atol=1e-10)

    def test_power_law_domain_guard(self):
        """Verify power_law clamps (1+t) for t < -1 — no NaN."""
        result = compute_temporal_kernel(t=-2, kernel_type="power_law")
        assert not np.isnan(result)
        assert result > 0

    def test_oscillatory(self):
        """Verify oscillatory has periodic component."""
        result = compute_temporal_kernel(t=5, n=1.0, alpha=0.1, kernel_type="oscillatory", frequency=1.0)
        expected = np.exp(1.0 * 0.1 * 5) * 0.5 * (1.0 + 0.5 * np.sin(1.0 * 5))
        assert np.isclose(result, expected, atol=1e-10)

    def test_memory(self):
        """Verify memory: 1 + strength*exp(-t), decays toward 1."""
        result_t0 = compute_temporal_kernel(t=0, kernel_type="memory", memory_strength=1.0)
        assert np.isclose(result_t0, 2.0, atol=1e-10)  # 1 + 1*exp(0) = 2
        result_far = compute_temporal_kernel(t=100, kernel_type="memory", memory_strength=1.0)
        assert np.isclose(result_far, 1.0, atol=1e-6)  # Decays to 1

    def test_positivity_all_modes(self):
        """All modes must return f_time > 0 for reasonable inputs."""
        modes = [
            ("exponential", {}),
            ("linear", {}),
            ("logistic", {}),
            ("s_curve", {"t0": 0.0}),
            ("power_law", {"exponent": 1.0}),
            ("oscillatory", {"frequency": 1.0}),
            ("memory", {"memory_strength": 1.0}),
        ]
        for mode, kw in modes:
            for t in [-10, -5, -1, 0, 1, 5, 10]:
                result = compute_temporal_kernel(t, n=1.0, alpha=0.1, kernel_type=mode, **kw)
                assert result > 0, f"{mode} at t={t} returned {result}"

    def test_backward_compat_decay_rate(self):
        """Old decay_rate parameter should map to alpha."""
        result = compute_temporal_kernel(t=5, decay_rate=0.2, kernel_type="exponential")
        expected = compute_temporal_kernel(t=5, n=1.0, alpha=0.2, kernel_type="exponential")
        assert np.isclose(result, expected, atol=1e-10)

    def test_kernel_integrity_unchanged(self):
        """Core mantic_kernel must still pass integrity check after temporal changes."""
        assert verify_kernel_integrity()

    def test_tool_with_temporal(self):
        """A detect() tool with pre-computed f_time scales M correctly."""
        # Get baseline M-score with f_time=1.0
        result_base = finance_regime_conflict.detect(
            technical=0.7, macro=0.6, flow=0.5, risk=0.6
        )
        # Get f_time from temporal kernel
        f_time = compute_temporal_kernel(t=5, n=-1, alpha=0.1, kernel_type="exponential")
        result_temporal = finance_regime_conflict.detect(
            technical=0.7, macro=0.6, flow=0.5, risk=0.6, f_time=f_time
        )
        # M should scale: M_temporal = M_base * f_time
        assert np.isclose(
            result_temporal["m_score"],
            result_base["m_score"] * f_time,
            atol=1e-10
        )

    def test_unknown_kernel_type(self):
        """Unknown kernel type should raise ValueError."""
        with pytest.raises(ValueError):
            compute_temporal_kernel(t=5, kernel_type="invalid_mode")


# =============================================================================
# Cross-Model Consistency Tests
# =============================================================================

class TestCrossModelConsistency:
    """Verify all adapters produce consistent results."""
    
    def test_same_inputs_same_outputs(self):
        """Test that same inputs produce same outputs across adapters."""
        params = {
            "phenotypic": 0.3,
            "genomic": 0.9,
            "environmental": 0.4,
            "psychosocial": 0.8
        }
        
        openai_result = execute_openai("healthcare_phenotype_genotype", params)
        kimi_result = execute_kimi("healthcare_phenotype_genotype", params)
        claude_result = execute_claude("healthcare_phenotype_genotype", params)
        
        # M-score should be identical (deterministic)
        assert openai_result["m_score"] == kimi_result["m_score"] == claude_result["m_score"]
        
        # Core alert should be the same
        assert openai_result["alert"] == kimi_result["alert"] == claude_result["alert"]


# =============================================================================
# Main entry point for standalone testing
# =============================================================================

if __name__ == "__main__":
    print("Running Mantic Cross-Model Tests...")
    print("=" * 60)
    
    # Run a quick sanity check
    print("\n1. Testing kernel integrity...")
    assert verify_kernel_integrity()
    print("   ✓ Kernel integrity verified")
    
    print("\n2. Testing all 7 tools...")
    tools = [
        ("healthcare", healthcare_phenotype_genotype.detect, 
         {"phenotypic": 0.5, "genomic": 0.6, "environmental": 0.4, "psychosocial": 0.5}),
        ("finance", finance_regime_conflict.detect,
         {"technical": 0.7, "macro": 0.6, "flow": 0.5, "risk": 0.6}),
        ("cyber", cyber_attribution_resolver.detect,
         {"technical": 0.8, "threat_intel": 0.7, "operational_impact": 0.6, "geopolitical": 0.5}),
        ("climate", climate_maladaptation.detect,
         {"atmospheric": 0.6, "ecological": 0.7, "infrastructure": 0.5, "policy": 0.6}),
        ("legal", legal_precedent_drift.detect,
         {"black_letter": 0.7, "precedent": 0.8, "operational": 0.6, "socio_political": 0.2}),
        ("military", military_friction_forecast.detect,
         {"maneuver": 0.7, "intelligence": 0.8, "sustainment": 0.6, "political": 0.7}),
        ("social", social_narrative_rupture.detect,
         {"individual": 0.5, "network": 0.6, "institutional": 0.4, "cultural": 0.3}),
    ]
    
    for name, func, params in tools:
        result = func(**params)
        print(f"   ✓ {name}: M-score = {result['m_score']:.3f}")
    
    print("\n3. Testing adapters...")
    openai_tools = get_openai_tools()
    kimi_tools = get_kimi_tools()
    claude_tools = get_claude_tools()
    print(f"   ✓ OpenAI adapter: {len(openai_tools)} tools")
    print(f"   ✓ Kimi adapter: {len(kimi_tools)} tools")
    print(f"   ✓ Claude adapter: {len(claude_tools)} tools")
    
    print("\n4. Testing cross-model consistency...")
    params = {"phenotypic": 0.3, "genomic": 0.9, "environmental": 0.4, "psychosocial": 0.8}
    openai_r = execute_openai("healthcare_phenotype_genotype", params)
    kimi_r = execute_kimi("healthcare_phenotype_genotype", params)
    claude_r = execute_claude("healthcare_phenotype_genotype", params)
    
    assert openai_r["m_score"] == kimi_r["m_score"] == claude_r["m_score"]
    print(f"   ✓ All adapters produce M-score = {openai_r['m_score']:.3f}")
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("\nMantic Early Warning System is ready for cross-model use.")
    print("Compatible with: Claude, Kimi, Codex, GPT-4o")

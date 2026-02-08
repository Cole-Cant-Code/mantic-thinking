"""
Integration End-to-End Tests

Tests full pipelines: temporal kernel → tool → adapter,
visualization edge cases, batch execution, and script smoke tests.

Run with: python -m pytest tests/test_integration_e2e.py -v
"""

import sys
import os
import subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np

from core.mantic_kernel import mantic_kernel, compute_temporal_kernel
from adapters.openai_adapter import TOOL_MAP, execute_tool as execute_openai
from adapters.kimi_adapter import batch_execute
from adapters.claude_adapter import format_for_claude


# =============================================================================
# Full Pipeline: Temporal → Tool → Adapter
# =============================================================================

class TestFullPipeline:
    """End-to-end pipeline tests."""

    def test_temporal_to_tool_to_adapter(self):
        """Compute temporal kernel, pass to tool, verify result."""
        # Step 1: Compute temporal kernel
        f_time = compute_temporal_kernel(t=2.0, n=1.0, alpha=0.1,
                                          kernel_type="exponential")
        assert f_time > 1.0  # Exponential growth

        # Step 2: Execute tool via adapter with f_time
        result = execute_openai("healthcare_phenotype_genotype", {
            "phenotypic": 0.3, "genomic": 0.9,
            "environmental": 0.4, "psychosocial": 0.8,
            "f_time": f_time
        })

        assert "m_score" in result
        assert isinstance(result["m_score"], float)
        assert result["m_score"] > 0

    def test_temporal_config_through_adapter(self):
        """Pass temporal_config through adapter (not raw f_time)."""
        result = execute_openai("healthcare_phenotype_genotype", {
            "phenotypic": 0.3, "genomic": 0.9,
            "environmental": 0.4, "psychosocial": 0.8,
            "temporal_config": {
                "kernel_type": "s_curve", "alpha": 0.1, "t": 2.0
            }
        })

        assert "m_score" in result
        temporal = result["overrides_applied"]["temporal_config"]
        assert temporal["applied"] is not None

    def test_threshold_and_temporal_through_adapter(self):
        """Both overrides through adapter pipeline."""
        result = execute_openai("healthcare_phenotype_genotype", {
            "phenotypic": 0.3, "genomic": 0.9,
            "environmental": 0.4, "psychosocial": 0.8,
            "threshold_override": {"buffering": 0.35},
            "temporal_config": {
                "kernel_type": "exponential", "alpha": 0.1, "t": 1.0
            }
        })

        audit = result["overrides_applied"]
        assert "threshold_overrides" in audit
        assert "temporal_config" in audit
        assert "f_time" in audit


# =============================================================================
# Kimi Batch Execution
# =============================================================================

class TestKimiBatchExecution:
    """Test Kimi adapter's batch_execute for all 14 tools."""

    def test_batch_execute_all_tools(self):
        """Execute all 14 tools in a batch."""
        tools_with_params = [
            {"tool": "healthcare_phenotype_genotype", "params": {"phenotypic": 0.3, "genomic": 0.9, "environmental": 0.4, "psychosocial": 0.8}},
            {"tool": "finance_regime_conflict", "params": {"technical": 0.7, "macro": 0.5, "flow": -0.3, "risk": 0.6}},
            {"tool": "cyber_attribution_resolver", "params": {"technical": 0.6, "threat_intel": 0.4, "operational_impact": 0.5, "geopolitical": 0.7}},
            {"tool": "climate_maladaptation", "params": {"atmospheric": 0.5, "ecological": 0.6, "infrastructure": 0.7, "policy": 0.4}},
            {"tool": "legal_precedent_drift", "params": {"black_letter": 0.7, "precedent": 0.3, "operational": 0.5, "socio_political": 0.6}},
            {"tool": "military_friction_forecast", "params": {"maneuver": 0.6, "intelligence": 0.5, "sustainment": 0.3, "political": 0.7}},
            {"tool": "social_narrative_rupture", "params": {"individual": 0.7, "network": 0.8, "institutional": 0.6, "cultural": 0.3}},
            {"tool": "healthcare_precision_therapeutic", "params": {"genomic_predisposition": 0.85, "environmental_readiness": 0.80, "phenotypic_timing": 0.88, "psychosocial_engagement": 0.90}},
            {"tool": "finance_confluence_alpha", "params": {"technical_setup": 0.85, "macro_tailwind": 0.80, "flow_positioning": 0.75, "risk_compression": 0.70}},
            {"tool": "cyber_adversary_overreach", "params": {"threat_intel_stretch": 0.7, "geopolitical_pressure": 0.6, "operational_hardening": 0.8, "tool_reuse_fatigue": 0.75}},
            {"tool": "climate_resilience_multiplier", "params": {"atmospheric_benefit": 0.7, "ecological_benefit": 0.8, "infrastructure_benefit": 0.6, "policy_alignment": 0.75}},
            {"tool": "legal_precedent_seeding", "params": {"socio_political_climate": 0.7, "institutional_capacity": 0.8, "statutory_ambiguity": 0.75, "circuit_split": 0.85}},
            {"tool": "military_strategic_initiative", "params": {"enemy_ambiguity": 0.9, "positional_advantage": 0.9, "logistic_readiness": 0.9, "authorization_clarity": 0.9}},
            {"tool": "social_catalytic_alignment", "params": {"individual_readiness": 0.75, "network_bridges": 0.8, "policy_window": 0.7, "paradigm_momentum": 0.85}},
        ]

        results = batch_execute(tools_with_params)
        assert len(results) == 14
        for r in results:
            assert r["success"] is True, f"Tool {r['tool']} failed: {r.get('error')}"
            assert "m_score" in r["result"]


# =============================================================================
# Claude Format Smoke Test
# =============================================================================

class TestClaudeFormatting:
    """Test format_for_claude with various result types."""

    def test_format_friction_result(self):
        """Friction results format without crash."""
        result = TOOL_MAP["healthcare_phenotype_genotype"](
            phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8
        )
        formatted = format_for_claude(result, "healthcare_phenotype_genotype")
        assert isinstance(formatted, str)
        assert "FRICTION" in formatted

    def test_format_emergence_result(self):
        """Emergence results format without crash."""
        result = TOOL_MAP["healthcare_precision_therapeutic"](
            genomic_predisposition=0.9, environmental_readiness=0.85,
            phenotypic_timing=0.9, psychosocial_engagement=0.9
        )
        formatted = format_for_claude(result, "healthcare_precision_therapeutic")
        assert isinstance(formatted, str)
        assert "CONFLUENCE" in formatted

    def test_format_no_alert_result(self):
        """Results without alert/window format cleanly."""
        result = TOOL_MAP["healthcare_phenotype_genotype"](
            phenotypic=0.6, genomic=0.7, environmental=0.5, psychosocial=0.5
        )
        formatted = format_for_claude(result)
        assert isinstance(formatted, str)
        assert "No friction detected" in formatted


# =============================================================================
# Visualization Edge Cases
# =============================================================================

class TestVisualizationEdgeCases:
    """ASCII visualization should not crash on edge inputs."""

    def test_gauge_extreme_values(self):
        """draw_m_gauge should handle M=0, M=1, M>1."""
        from visualization.ascii_charts import draw_m_gauge
        # Normal case
        output = draw_m_gauge(0.5, 0.5)
        assert isinstance(output, str)
        assert len(output) > 0

        # Edge: M=0
        output = draw_m_gauge(0.0, 0.0)
        assert isinstance(output, str)

        # Edge: M=1
        output = draw_m_gauge(1.0, 1.0)
        assert isinstance(output, str)

    def test_attribution_treemap_empty(self):
        """draw_attribution_treemap with zero attributions."""
        from visualization.ascii_charts import draw_attribution_treemap
        output = draw_attribution_treemap([0.0, 0.0, 0.0, 0.0],
                                           ["A", "B", "C", "D"])
        assert isinstance(output, str)


# =============================================================================
# Script Smoke Tests
# =============================================================================

class TestScriptSmoke:
    """Verify scripts run without errors."""

    def test_demo_list_scenarios(self):
        """demo.py --list-scenarios should exit cleanly."""
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        demo_path = os.path.join(repo_root, "demo.py")
        if not os.path.exists(demo_path):
            pytest.skip("demo.py is a local utility and is not shipped in the repo")
        result = subprocess.run(
            [sys.executable, demo_path, "--list-scenarios"],
            capture_output=True, text=True, timeout=30
        )
        assert result.returncode == 0, f"demo.py failed: {result.stderr}"

    def test_self_analysis_runs(self):
        """scripts/self_analysis.py should complete without error."""
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script = os.path.join(repo_root, "scripts", "self_analysis.py")
        if os.path.exists(script):
            result = subprocess.run(
                [sys.executable, script],
                capture_output=True, text=True, timeout=30
            )
            assert result.returncode == 0, f"self_analysis.py failed: {result.stderr}"

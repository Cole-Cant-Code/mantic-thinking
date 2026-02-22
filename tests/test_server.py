"""Tests for the MCP server surface.

Tests tool, resource, and prompt functions directly (not via MCP protocol).
"""
from __future__ import annotations

import json

import pytest

from mantic_thinking.server import (
    # Tools
    health_check,
    detect,
    detect_friction,
    detect_emergence,
    visualize_gauge,
    visualize_attribution,
    visualize_kernels,
    # Resources
    resource_system_prompt,
    resource_presets,
    resource_scaffold,
    resource_tech_spec,
    resource_domain_config,
    resource_all_guidance,
    resource_tool_guidance,
    resource_full_context,
    resource_domains,
    # Prompts
    warmup,
    analyze_domain,
    compare_friction_emergence,
)


# ---------------------------------------------------------------------------
# Detection tools
# ---------------------------------------------------------------------------


class TestHealthCheck:
    def test_returns_ok(self):
        result = health_check()
        assert result["status"] == "ok"
        assert result["presets"] == 16

    def test_version_present(self):
        result = health_check()
        assert "version" in result


class TestDetect:
    def test_friction(self):
        result = detect(
            layer_names=["a", "b", "c", "d"],
            weights=[0.25, 0.25, 0.25, 0.25],
            layer_values=[0.3, 0.9, 0.4, 0.8],
            mode="friction",
        )
        assert "m_score" in result
        assert isinstance(result["m_score"], float)

    def test_emergence(self):
        result = detect(
            layer_names=["a", "b", "c", "d"],
            weights=[0.25, 0.25, 0.25, 0.25],
            layer_values=[0.7, 0.8, 0.6, 0.9],
            mode="emergence",
        )
        assert "m_score" in result

    def test_invalid_mode(self):
        result = detect(
            layer_names=["a", "b", "c", "d"],
            weights=[0.25, 0.25, 0.25, 0.25],
            layer_values=[0.5] * 4,
            mode="invalid",
        )
        assert result["status"] == "error"

    def test_custom_weights(self):
        result = detect(
            layer_names=["signal", "noise", "context", "momentum"],
            weights=[0.50, 0.10, 0.25, 0.15],
            layer_values=[0.9, 0.2, 0.6, 0.7],
        )
        assert "m_score" in result
        # Signal layer has 50% weight and 0.9 value — should dominate attribution
        attr = result.get("layer_attribution", {})
        if attr:
            assert attr.get("signal", 0) > attr.get("noise", 0)

    def test_three_layers(self):
        result = detect(
            layer_names=["x", "y", "z"],
            weights=[0.4, 0.3, 0.3],
            layer_values=[0.8, 0.5, 0.6],
        )
        assert "m_score" in result

    def test_five_layers(self):
        result = detect(
            layer_names=["a", "b", "c", "d", "e"],
            weights=[0.2, 0.2, 0.2, 0.2, 0.2],
            layer_values=[0.5, 0.5, 0.5, 0.5, 0.5],
        )
        assert "m_score" in result


class TestDetectShortcuts:
    def test_friction_shortcut(self):
        result = detect_friction(
            layer_names=["a", "b", "c", "d"],
            weights=[0.25, 0.25, 0.25, 0.25],
            layer_values=[0.8, 0.3, 0.6, 0.7],
        )
        assert "m_score" in result

    def test_emergence_shortcut(self):
        result = detect_emergence(
            layer_names=["a", "b", "c", "d"],
            weights=[0.25, 0.25, 0.25, 0.25],
            layer_values=[0.7, 0.8, 0.6, 0.9],
        )
        assert "m_score" in result


# ---------------------------------------------------------------------------
# Visualization tools
# ---------------------------------------------------------------------------


class TestVisualization:
    def test_gauge(self):
        result = visualize_gauge(0.65, 0.5)
        assert isinstance(result, str)
        assert "M-SCORE" in result

    def test_attribution(self):
        result = visualize_attribution({"layer_a": 0.4, "layer_b": 0.6})
        assert isinstance(result, str)
        assert "TREEMAP" in result

    def test_kernels(self):
        result = visualize_kernels(t=5.0)
        assert isinstance(result, str)
        assert "KERNEL" in result


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


class TestResources:
    def test_system_prompt(self):
        content = resource_system_prompt()
        assert isinstance(content, str)
        assert len(content) > 0
        assert "Mantic Thinking" in content

    def test_presets(self):
        content = resource_presets()
        data = json.loads(content)
        assert len(data) == 16
        # Check a known preset has expected structure
        for name, preset in data.items():
            assert "layer_names" in preset
            assert "weights" in preset
            assert len(preset["layer_names"]) == len(preset["weights"])
            break

    def test_presets_weights_sum(self):
        """Every preset's weights should sum to ~1.0."""
        data = json.loads(resource_presets())
        for name, preset in data.items():
            total = sum(preset["weights"].values())
            assert abs(total - 1.0) < 0.01, f"{name} weights sum to {total}"

    def test_scaffold(self):
        content = resource_scaffold()
        assert isinstance(content, str)
        assert len(content) > 0

    def test_tech_spec(self):
        content = resource_tech_spec()
        assert isinstance(content, str)

    def test_domain_config_healthcare(self):
        content = resource_domain_config("healthcare")
        assert isinstance(content, str)
        assert "No config found" not in content

    def test_domain_config_finance(self):
        content = resource_domain_config("finance")
        assert isinstance(content, str)
        assert "No config found" not in content

    def test_domain_config_unknown(self):
        content = resource_domain_config("nonexistent_domain_xyz")
        assert "No config found" in content

    def test_all_guidance(self):
        content = resource_all_guidance()
        assert isinstance(content, str)
        assert len(content) > 0

    def test_tool_guidance(self):
        content = resource_tool_guidance("healthcare_phenotype_genotype")
        assert isinstance(content, str)

    def test_full_context(self):
        content = resource_full_context("healthcare")
        assert isinstance(content, str)
        assert len(content) > 0

    def test_domains_registry(self):
        content = resource_domains()
        data = json.loads(content)
        assert "healthcare" in data
        assert "tools" in data["healthcare"]
        assert "temporal_kernels" in data["healthcare"]
        assert "_aliases" in data


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------


class TestPrompts:
    def test_warmup(self):
        result = warmup()
        assert isinstance(result, str)
        assert "presets" in result

    def test_analyze_domain(self):
        result = analyze_domain("healthcare", "Patient with high genetic risk")
        assert isinstance(result, str)
        assert "healthcare" in result
        assert "friction" in result.lower()

    def test_compare_friction_emergence(self):
        result = compare_friction_emergence("finance")
        assert isinstance(result, str)
        assert "finance" in result

"""
Tests for Generic Mantic Detector

Covers:
- Domain registration validation (reserved names, layer counts, weight sums)
- Friction mode (divergence detection via range)
- Emergence mode (alignment detection via floor)
- Override governance (thresholds, temporal config, interaction coefficients)
- Layer visibility with caller-provided hierarchy
- Output schema consistency with existing tools
- Edge cases (boundary values, 3-layer, 6-layer)

Run with: python -m pytest tests/test_generic_detect.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np

from mantic_thinking.tools.generic_detect import detect, _RESERVED_DOMAINS


# =============================================================================
# Standard test inputs
# =============================================================================

FOUR_LAYER = {
    "domain_name": "test_domain",
    "layer_names": ["alpha", "beta", "gamma", "delta"],
    "weights": [0.25, 0.25, 0.25, 0.25],
}

DIVERGENT_VALUES = [0.9, 0.3, 0.6, 0.7]  # range = 0.6, should trigger friction
ALIGNED_VALUES = [0.85, 0.80, 0.82, 0.88]  # floor = 0.80, should trigger emergence
LOW_VALUES = [0.3, 0.3, 0.3, 0.3]  # no divergence, no alignment


# =============================================================================
# Domain Registration Validation
# =============================================================================

class TestRegistrationValidation:
    """Validate domain registration rejects bad inputs."""

    def test_reserved_domain_rejected(self):
        for name in _RESERVED_DOMAINS:
            with pytest.raises(ValueError, match="collides with a built-in"):
                detect(domain_name=name, layer_names=["a", "b", "c", "d"],
                       weights=[0.25, 0.25, 0.25, 0.25],
                       layer_values=[0.5, 0.5, 0.5, 0.5], mode="friction")

    def test_reserved_domain_case_insensitive(self):
        with pytest.raises(ValueError, match="collides"):
            detect(domain_name="Healthcare", layer_names=["a", "b", "c", "d"],
                   weights=[0.25, 0.25, 0.25, 0.25],
                   layer_values=[0.5, 0.5, 0.5, 0.5], mode="friction")

    def test_empty_domain_name(self):
        with pytest.raises(ValueError, match="non-empty"):
            detect(domain_name="", layer_names=["a", "b", "c"],
                   weights=[0.4, 0.3, 0.3], layer_values=[0.5, 0.5, 0.5],
                   mode="friction")

    def test_too_few_layers(self):
        with pytest.raises(ValueError, match="3-6"):
            detect(domain_name="tiny", layer_names=["a", "b"],
                   weights=[0.5, 0.5], layer_values=[0.5, 0.5],
                   mode="friction")

    def test_too_many_layers(self):
        with pytest.raises(ValueError, match="3-6"):
            detect(domain_name="huge",
                   layer_names=["a", "b", "c", "d", "e", "f", "g"],
                   weights=[1/7]*7, layer_values=[0.5]*7,
                   mode="friction")

    def test_duplicate_layer_names(self):
        with pytest.raises(ValueError, match="unique"):
            detect(domain_name="dup", layer_names=["a", "a", "b", "c"],
                   weights=[0.25, 0.25, 0.25, 0.25],
                   layer_values=[0.5, 0.5, 0.5, 0.5], mode="friction")

    def test_weights_dont_sum_to_one(self):
        with pytest.raises(ValueError, match="sum to 1.0"):
            detect(domain_name="bad_w", layer_names=["a", "b", "c", "d"],
                   weights=[0.1, 0.1, 0.1, 0.1],
                   layer_values=[0.5, 0.5, 0.5, 0.5], mode="friction")

    def test_negative_weight(self):
        with pytest.raises(ValueError, match="non-negative"):
            detect(domain_name="neg_w", layer_names=["a", "b", "c", "d"],
                   weights=[-0.1, 0.4, 0.4, 0.3],
                   layer_values=[0.5, 0.5, 0.5, 0.5], mode="friction")

    def test_invalid_mode(self):
        with pytest.raises(ValueError, match="friction.*emergence"):
            detect(domain_name="bad_mode", layer_names=["a", "b", "c", "d"],
                   weights=[0.25, 0.25, 0.25, 0.25],
                   layer_values=[0.5, 0.5, 0.5, 0.5], mode="unknown")

    def test_mismatched_lengths(self):
        with pytest.raises(ValueError, match="must match"):
            detect(domain_name="mismatch", layer_names=["a", "b", "c"],
                   weights=[0.25, 0.25, 0.25, 0.25],
                   layer_values=[0.5, 0.5, 0.5], mode="friction")


# =============================================================================
# Friction Mode
# =============================================================================

class TestFrictionMode:
    """Friction mode detects cross-layer divergence via range."""

    def test_divergent_triggers_alert(self):
        result = detect(**FOUR_LAYER, layer_values=DIVERGENT_VALUES, mode="friction")
        assert result["alert"] is not None
        assert "DIVERGENCE" in result["alert"]
        assert result["severity"] > 0
        assert result["mismatch_score"] > 0.4

    def test_uniform_no_alert(self):
        result = detect(**FOUR_LAYER, layer_values=LOW_VALUES, mode="friction")
        assert result["alert"] is None
        assert result["severity"] == 0.0

    def test_threshold_boundary(self):
        # range = 0.4 exactly, threshold = 0.4, should NOT trigger (>)
        result = detect(**FOUR_LAYER, layer_values=[0.5, 0.5, 0.5, 0.9],
                        mode="friction", detection_threshold=0.4)
        assert result["alert"] is None

    def test_just_above_threshold(self):
        # range = 0.41, threshold = 0.4, should trigger
        result = detect(**FOUR_LAYER, layer_values=[0.5, 0.5, 0.5, 0.91],
                        mode="friction", detection_threshold=0.4)
        assert result["alert"] is not None

    def test_alert_names_correct_layers(self):
        result = detect(**FOUR_LAYER, layer_values=[0.1, 0.9, 0.5, 0.5],
                        mode="friction")
        assert "beta" in result["alert"]  # highest
        assert "alpha" in result["alert"]  # lowest


# =============================================================================
# Emergence Mode
# =============================================================================

class TestEmergenceMode:
    """Emergence mode detects cross-layer alignment via floor."""

    def test_aligned_triggers_window(self):
        result = detect(**FOUR_LAYER, layer_values=ALIGNED_VALUES, mode="emergence")
        assert result["window_detected"] is True
        assert result["window_type"] is not None
        assert result["confidence"] > 0

    def test_optimal_vs_favorable(self):
        # All > 0.8 = OPTIMAL
        optimal = detect(**FOUR_LAYER, layer_values=[0.85, 0.9, 0.88, 0.82],
                         mode="emergence")
        assert "OPTIMAL" in optimal["window_type"]
        assert optimal["confidence"] == 0.95

        # All > threshold but not all > 0.8 = FAVORABLE
        favorable = detect(**FOUR_LAYER, layer_values=[0.7, 0.75, 0.72, 0.68],
                           mode="emergence", detection_threshold=0.5)
        assert "FAVORABLE" in favorable["window_type"]
        assert favorable["confidence"] == 0.75

    def test_no_window_below_threshold(self):
        result = detect(**FOUR_LAYER, layer_values=LOW_VALUES, mode="emergence")
        assert result["window_detected"] is False
        assert "improvement_needed" in result

    def test_limiting_factor_identified(self):
        result = detect(**FOUR_LAYER, layer_values=[0.9, 0.5, 0.8, 0.7],
                        mode="emergence", detection_threshold=0.4)
        assert result["limiting_factor"] == "beta"


# =============================================================================
# Universal Output Schema
# =============================================================================

class TestOutputSchema:
    """Generic tool must return same universal keys as hardcoded tools."""

    UNIVERSAL_KEYS = ["m_score", "spatial_component", "layer_attribution",
                      "thresholds", "overrides_applied", "layer_coupling"]

    @pytest.mark.parametrize("mode", ["friction", "emergence"])
    def test_universal_keys_present(self, mode):
        values = DIVERGENT_VALUES if mode == "friction" else ALIGNED_VALUES
        result = detect(**FOUR_LAYER, layer_values=values, mode=mode)
        for key in self.UNIVERSAL_KEYS:
            assert key in result, f"Missing universal key: {key}"

    @pytest.mark.parametrize("mode", ["friction", "emergence"])
    def test_m_score_is_float(self, mode):
        values = DIVERGENT_VALUES if mode == "friction" else ALIGNED_VALUES
        result = detect(**FOUR_LAYER, layer_values=values, mode=mode)
        assert isinstance(result["m_score"], float)

    @pytest.mark.parametrize("mode", ["friction", "emergence"])
    def test_calibration_block_present(self, mode):
        values = DIVERGENT_VALUES if mode == "friction" else ALIGNED_VALUES
        result = detect(**FOUR_LAYER, layer_values=values, mode=mode)
        cal = result["calibration"]
        assert cal["domain_type"] == "user_defined"
        assert cal["domain_name"] == "test_domain"
        assert cal["mode"] == mode
        assert cal["layer_count"] == 4

    @pytest.mark.parametrize("mode", ["friction", "emergence"])
    def test_layer_attribution_matches_layers(self, mode):
        values = DIVERGENT_VALUES if mode == "friction" else ALIGNED_VALUES
        result = detect(**FOUR_LAYER, layer_values=values, mode=mode)
        attr = result["layer_attribution"]
        assert set(attr.keys()) == set(FOUR_LAYER["layer_names"])


# =============================================================================
# Variable Layer Counts
# =============================================================================

class TestVariableLayerCounts:
    """Test with 3, 5, and 6 layers."""

    def test_three_layers(self):
        result = detect(
            domain_name="tri",
            layer_names=["x", "y", "z"],
            weights=[0.4, 0.35, 0.25],
            layer_values=[0.8, 0.3, 0.6],
            mode="friction"
        )
        assert result["alert"] is not None
        assert result["calibration"]["layer_count"] == 3
        assert len(result["layer_attribution"]) == 3

    def test_five_layers(self):
        result = detect(
            domain_name="penta",
            layer_names=["a", "b", "c", "d", "e"],
            weights=[0.25, 0.25, 0.2, 0.15, 0.15],
            layer_values=[0.85, 0.80, 0.82, 0.78, 0.90],
            mode="emergence"
        )
        assert result["window_detected"] is True
        assert result["calibration"]["layer_count"] == 5
        assert len(result["layer_attribution"]) == 5

    def test_six_layers(self):
        result = detect(
            domain_name="hexa",
            layer_names=["a", "b", "c", "d", "e", "f"],
            weights=[0.2, 0.2, 0.15, 0.15, 0.15, 0.15],
            layer_values=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            mode="friction"
        )
        assert result["alert"] is None  # no divergence
        assert result["calibration"]["layer_count"] == 6
        assert len(result["layer_attribution"]) == 6


# =============================================================================
# Override Governance (same as hardcoded tools)
# =============================================================================

class TestOverrideGovernance:
    """Override bounds and audit trail work identically to hardcoded tools."""

    def test_threshold_override_within_bounds(self):
        result = detect(**FOUR_LAYER, layer_values=DIVERGENT_VALUES, mode="friction",
                        threshold_override={"detection": 0.35})
        assert result["thresholds"]["detection"] == 0.35

    def test_threshold_override_clamped(self):
        # Default = 0.4, ±20% = [0.32, 0.48]. Requesting 0.1 → clamped.
        result = detect(**FOUR_LAYER, layer_values=DIVERGENT_VALUES, mode="friction",
                        threshold_override={"detection": 0.1})
        assert result["thresholds"]["detection"] != 0.1
        assert result["overrides_applied"]["threshold_overrides"]["clamped"] is True

    def test_interaction_override(self):
        result = detect(**FOUR_LAYER, layer_values=DIVERGENT_VALUES, mode="friction",
                        interaction_override=[1.5, 1.0, 1.0, 1.0],
                        interaction_override_mode="replace")
        interaction = result["overrides_applied"]["interaction"]
        assert interaction["override_mode"] == "replace"
        assert interaction["used"][0] == 1.5

    def test_unknown_threshold_key_ignored(self):
        result = detect(**FOUR_LAYER, layer_values=DIVERGENT_VALUES, mode="friction",
                        threshold_override={"nonexistent_key": 0.5})
        # Should not crash; key is ignored
        assert result["m_score"] > 0

    def test_temporal_config_all_kernels_allowed(self):
        # Generic domain allows all kernel types (no domain restriction)
        result = detect(**FOUR_LAYER, layer_values=DIVERGENT_VALUES, mode="friction",
                        temporal_config={"kernel_type": "oscillatory", "alpha": 0.1, "t": 2.0})
        tc = result["overrides_applied"]["temporal_config"]
        assert tc["applied"] is not None


# =============================================================================
# Layer Visibility
# =============================================================================

class TestLayerVisibility:
    """Test caller-provided hierarchy for layer visibility."""

    def test_with_hierarchy(self):
        result = detect(
            **FOUR_LAYER, layer_values=DIVERGENT_VALUES, mode="friction",
            layer_hierarchy={
                "alpha": "Micro", "beta": "Micro",
                "gamma": "Meso", "delta": "Macro"
            }
        )
        vis = result["layer_visibility"]
        assert vis is not None
        assert vis["dominant"] in ("Micro", "Meso", "Macro", "Meta")
        assert vis["input_driven"] is True

    def test_without_hierarchy(self):
        result = detect(**FOUR_LAYER, layer_values=DIVERGENT_VALUES, mode="friction")
        assert result["layer_visibility"] is None

    def test_hierarchy_contributions_sum(self):
        result = detect(
            **FOUR_LAYER, layer_values=[0.8, 0.8, 0.8, 0.8], mode="friction",
            layer_hierarchy={
                "alpha": "Micro", "beta": "Meso",
                "gamma": "Macro", "delta": "Meta"
            }
        )
        vis = result["layer_visibility"]
        total = sum(vis["contributions_by_layer"].values())
        # Should equal S (spatial component)
        assert abs(total - result["spatial_component"]) < 1e-6


# =============================================================================
# Layer Coupling
# =============================================================================

class TestLayerCoupling:
    """Layer coupling works with variable layer counts."""

    def test_coupling_keys_match_layers(self):
        result = detect(**FOUR_LAYER, layer_values=DIVERGENT_VALUES, mode="friction")
        coupling = result["layer_coupling"]
        assert "coherence" in coupling
        assert set(coupling["layers"].keys()) == set(FOUR_LAYER["layer_names"])

    def test_uniform_high_coherence(self):
        result = detect(**FOUR_LAYER, layer_values=[0.7, 0.7, 0.7, 0.7],
                        mode="friction")
        assert result["layer_coupling"]["coherence"] == 1.0

    def test_divergent_lower_coherence(self):
        result = detect(**FOUR_LAYER, layer_values=[0.1, 0.9, 0.1, 0.9],
                        mode="friction")
        assert result["layer_coupling"]["coherence"] < 1.0


# =============================================================================
# Adapter Integration
# =============================================================================

class TestAdapterIntegration:
    """Generic tool works through the adapter execute_tool path."""

    def test_execute_via_adapter(self):
        from mantic_thinking.adapters.openai_adapter import execute_tool
        result = execute_tool("generic_detect", {
            "domain_name": "adapter_test",
            "layer_names": ["a", "b", "c", "d"],
            "weights": [0.25, 0.25, 0.25, 0.25],
            "layer_values": [0.5, 0.5, 0.5, 0.5],
            "mode": "friction",
        })
        assert "m_score" in result
        assert result["calibration"]["domain_name"] == "adapter_test"

    def test_tool_count(self):
        from mantic_thinking.adapters.openai_adapter import TOOL_MAP, get_openai_tools
        assert len(TOOL_MAP) == 17
        assert len(get_openai_tools()) == 17

    def test_claude_adapter_includes_generic(self):
        from mantic_thinking.adapters.claude_adapter import get_claude_tools
        tools = get_claude_tools()
        assert len(tools) == 17
        names = [t["name"] for t in tools]
        assert "generic_detect" in names


# =============================================================================
# P0 Crash Path Tests (Codex Review Findings)
# =============================================================================

class TestP0WeightNormalization:
    """P0 #1: Weights that sum to ~1.0 (not exactly 1.0) must not crash kernel."""

    def test_thirds_sum_to_0_9999(self):
        """[0.3333, 0.3333, 0.3333] sums to 0.9999 — must not crash."""
        result = detect(
            domain_name="thirds_test",
            layer_names=["a", "b", "c"],
            weights=[0.3333, 0.3333, 0.3333],
            layer_values=[0.5, 0.5, 0.5],
            mode="friction"
        )
        assert "m_score" in result
        assert isinstance(result["m_score"], float)

    def test_fifths_sum_to_1_0001(self):
        """5 layers at 0.2 + floating point = may not be exactly 1.0."""
        result = detect(
            domain_name="fifths_test",
            layer_names=["a", "b", "c", "d", "e"],
            weights=[0.2, 0.2, 0.2, 0.2, 0.2],
            layer_values=[0.5, 0.5, 0.5, 0.5, 0.5],
            mode="friction"
        )
        assert "m_score" in result

    def test_uneven_weights_normalized(self):
        """Weights that sum to ~0.99 are normalized, not rejected by kernel."""
        result = detect(
            domain_name="uneven_test",
            layer_names=["x", "y", "z", "w"],
            weights=[0.30, 0.25, 0.25, 0.19],  # sums to 0.99
            layer_values=[0.7, 0.6, 0.8, 0.5],
            mode="friction"
        )
        assert "m_score" in result
        # Verify calibration shows normalized weights that sum to 1.0
        cal_weights = result["calibration"]["weight_distribution"]
        assert abs(sum(cal_weights.values()) - 1.0) < 1e-10

    def test_weights_outside_tolerance_still_rejected(self):
        """Weights that are wildly off (sum=0.5) are still rejected."""
        with pytest.raises(ValueError, match="sum to 1.0"):
            detect(
                domain_name="bad_weights",
                layer_names=["a", "b", "c"],
                weights=[0.2, 0.2, 0.1],
                layer_values=[0.5, 0.5, 0.5],
                mode="friction"
            )


class TestP0TemporalKernelValidation:
    """P0 #2: Unknown kernel_type must be rejected, not crash."""

    def test_unknown_kernel_type_rejected(self):
        """Unknown kernel_type should be rejected, not crash compute_temporal_kernel."""
        result = detect(
            **FOUR_LAYER, layer_values=DIVERGENT_VALUES, mode="friction",
            temporal_config={"kernel_type": "totally_fake_kernel", "alpha": 0.1, "t": 2.0}
        )
        # Should not crash — unknown kernel is rejected by allowlist
        assert "m_score" in result
        tc = result["overrides_applied"]["temporal_config"]
        assert tc["rejected"] is not None
        assert "kernel_type" in tc["rejected"]

    def test_all_valid_kernels_accepted(self):
        """All 7 valid kernel types work through generic domain."""
        valid_kernels = ["exponential", "s_curve", "linear", "memory",
                         "oscillatory", "power_law", "logistic"]
        for kernel in valid_kernels:
            result = detect(
                **FOUR_LAYER, layer_values=DIVERGENT_VALUES, mode="friction",
                temporal_config={"kernel_type": kernel, "alpha": 0.1, "t": 2.0}
            )
            assert "m_score" in result, f"kernel '{kernel}' failed"
            tc = result["overrides_applied"]["temporal_config"]
            assert tc["applied"] is not None, f"kernel '{kernel}' not applied"

    def test_generic_in_domain_allowlist(self):
        """Verify 'generic' is registered in DOMAIN_KERNEL_ALLOWLIST."""
        from mantic_thinking.core.validators import DOMAIN_KERNEL_ALLOWLIST
        assert "generic" in DOMAIN_KERNEL_ALLOWLIST
        assert len(DOMAIN_KERNEL_ALLOWLIST["generic"]) == 7


class TestP0InteractionOverrideLength:
    """P0 #3: List interaction_override must match layer count."""

    def test_wrong_length_list_rejected(self):
        """5-layer domain with 4-element list override → ValueError."""
        with pytest.raises(ValueError, match="must match layer count"):
            detect(
                domain_name="five_layer",
                layer_names=["a", "b", "c", "d", "e"],
                weights=[0.2, 0.2, 0.2, 0.2, 0.2],
                layer_values=[0.5, 0.5, 0.5, 0.5, 0.5],
                mode="friction",
                interaction_override=[1.5, 1.0, 1.0, 1.0],  # 4 elements for 5 layers
                interaction_override_mode="replace"
            )

    def test_correct_length_list_accepted_5_layers(self):
        """5-layer domain with 5-element list override works."""
        result = detect(
            domain_name="five_ok",
            layer_names=["a", "b", "c", "d", "e"],
            weights=[0.2, 0.2, 0.2, 0.2, 0.2],
            layer_values=[0.5, 0.5, 0.5, 0.5, 0.5],
            mode="friction",
            interaction_override=[1.5, 1.0, 1.0, 1.0, 1.2],
            interaction_override_mode="replace"
        )
        assert "m_score" in result
        interaction = result["overrides_applied"]["interaction"]
        assert interaction["override_mode"] == "replace"

    def test_correct_length_list_accepted_6_layers(self):
        """6-layer domain with 6-element list override works."""
        result = detect(
            domain_name="six_ok",
            layer_names=["a", "b", "c", "d", "e", "f"],
            weights=[0.2, 0.2, 0.15, 0.15, 0.15, 0.15],
            layer_values=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            mode="friction",
            interaction_override=[1.5, 1.0, 1.0, 1.0, 1.2, 0.8],
            interaction_override_mode="scale"
        )
        assert "m_score" in result

    def test_dict_override_works_any_layer_count(self):
        """Dict-based override works for any layer count (no length issue)."""
        result = detect(
            domain_name="dict_five",
            layer_names=["a", "b", "c", "d", "e"],
            weights=[0.2, 0.2, 0.2, 0.2, 0.2],
            layer_values=[0.5, 0.5, 0.5, 0.5, 0.5],
            mode="friction",
            interaction_override={"a": 1.5, "c": 0.8},
            interaction_override_mode="scale"
        )
        assert "m_score" in result

    def test_4_layer_list_override_still_works(self):
        """Standard 4-layer domain with 4-element list still works."""
        result = detect(
            **FOUR_LAYER, layer_values=DIVERGENT_VALUES, mode="friction",
            interaction_override=[1.5, 1.0, 1.0, 1.0],
            interaction_override_mode="replace"
        )
        assert "m_score" in result
        interaction = result["overrides_applied"]["interaction"]
        assert interaction["used"][0] == 1.5

"""
System Lock Domain Tests

Covers friction/emergence behavior, guardrails, interaction dynamics,
temporal allowlist enforcement, and adapter-facing schema stability.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mantic_thinking.core.validators import DOMAIN_KERNEL_ALLOWLIST
from mantic_thinking.tools.friction.system_lock_recursive_control import (
    WEIGHTS as FRICTION_WEIGHTS,
    DEFAULT_THRESHOLDS as FRICTION_THRESHOLDS,
    detect as detect_friction,
)
from mantic_thinking.tools.emergence.system_lock_dissolution_window import (
    WEIGHTS as EMERGENCE_WEIGHTS,
    DEFAULT_THRESHOLDS as EMERGENCE_THRESHOLDS,
    detect as detect_emergence,
)
from mantic_thinking.tools.generic_detect import _RESERVED_DOMAINS, detect as detect_generic


class TestFrictionThresholdBoundaries:
    """Phase transitions and guard behavior for friction mode."""

    def test_pre_rigidity_phase(self):
        result = detect_friction(0.2, 0.2, 0.3, 0.2)
        assert result["lock_phase"] == "pre_rigidity"
        assert result["m_score"] < FRICTION_THRESHOLDS["asymmetry_warning"]

    def test_rigidity_phase(self):
        result = detect_friction(0.4, 0.4, 0.4, 0.4)
        assert result["lock_phase"] == "rigidity"

    def test_lock_active_phase(self):
        result = detect_friction(0.2, 0.3, 0.8, 0.7)
        assert result["lock_phase"] == "lock_active"
        assert result["alert"] is not None

    def test_lock_critical_phase_with_temporal_amplification(self):
        result = detect_friction(
            0.2,
            0.3,
            0.8,
            0.7,
            temporal_config={"kernel_type": "memory", "t": 1.0, "memory_strength": 1.0},
        )
        assert result["lock_phase"] == "lock_critical"
        assert result["m_score"] >= FRICTION_THRESHOLDS["lock_irreversible"]

    def test_guard_blocks_false_positive_on_uniform_high_input(self):
        # High magnitude but no asymmetry should not trigger lock_active.
        result = detect_friction(0.7, 0.7, 0.7, 0.7)
        assert result["lock_phase"] == "rigidity"
        assert result["alert"] is None


class TestFrictionAsymmetryRatio:
    """Asymmetry ratio behavior and edge handling."""

    def test_high_asymmetry_ratio(self):
        result = detect_friction(0.2, 0.3, 0.8, 0.7)
        assert result["asymmetry_ratio"] == pytest.approx(4.0)

    def test_low_asymmetry_ratio_balanced(self):
        result = detect_friction(0.5, 0.5, 0.5, 0.5)
        assert result["asymmetry_ratio"] == pytest.approx(1.0)

    def test_asymmetry_ratio_with_near_zero_micro_floor(self):
        result = detect_friction(0.0, 0.2, 0.8, 0.8)
        assert result["asymmetry_ratio"] >= 80.0


class TestEmergenceWindowDetection:
    """Window typing and no-window path."""

    def test_structural_dissolution_window(self):
        result = detect_emergence(0.8, 0.82, 0.81, 0.7)
        assert result["window_detected"] is True
        assert result["window_type"] == "STRUCTURAL_DISSOLUTION"

    def test_competitive_displacement_window(self):
        result = detect_emergence(0.65, 0.75, 0.6, 0.5)
        assert result["window_detected"] is True
        assert result["window_type"] == "COMPETITIVE_DISPLACEMENT"

    def test_early_dissolution_window(self):
        result = detect_emergence(0.55, 0.56, 0.57, 0.45)
        assert result["window_detected"] is True
        assert result["window_type"] == "EARLY_DISSOLUTION"

    def test_no_window_detected(self):
        result = detect_emergence(0.3, 0.4, 0.45, 0.5)
        assert result["window_detected"] is False
        assert "limiting_factors" in result


class TestOppositeSemantics:
    """Same formula, opposite interpretation across modes."""

    def test_high_control_signature_risk_not_opportunity(self):
        friction = detect_friction(0.2, 0.3, 0.8, 0.7)
        emergence = detect_emergence(0.2, 0.3, 0.8, 0.7)

        assert friction["alert"] is not None
        assert friction["lock_phase"] in {"lock_active", "lock_critical"}
        assert emergence["window_detected"] is False

    def test_same_layer_profile_opposite_interpretation(self):
        # Moderate, aligned values can be low-risk in friction but still a forming
        # opportunity in emergence semantics.
        friction = detect_friction(0.6, 0.6, 0.6, 0.6)
        emergence = detect_emergence(0.6, 0.6, 0.6, 0.6)

        assert friction["lock_phase"] == "rigidity"
        assert friction["alert"] is None
        assert emergence["window_detected"] is True


class TestWeightValidation:
    """Weight structures and sums remain stable."""

    def test_friction_weights_sum_to_one(self):
        assert isinstance(FRICTION_WEIGHTS, dict)
        assert sum(FRICTION_WEIGHTS.values()) == pytest.approx(1.0)

    def test_emergence_weights_sum_to_one(self):
        assert isinstance(EMERGENCE_WEIGHTS, list)
        assert sum(EMERGENCE_WEIGHTS) == pytest.approx(1.0)


class TestInteractionCoefficients:
    """Dynamic interaction behavior for both tools."""

    def test_friction_lock_amplification_when_macro_exceeds_micro(self):
        dynamic = detect_friction(0.2, 0.3, 0.8, 0.7, interaction_mode="dynamic")
        base = detect_friction(0.2, 0.3, 0.8, 0.7, interaction_mode="base")
        assert dynamic["m_score"] > base["m_score"]

    def test_friction_no_amplification_when_micro_exceeds_macro(self):
        dynamic = detect_friction(0.8, 0.7, 0.2, 0.3, interaction_mode="dynamic")
        base = detect_friction(0.8, 0.7, 0.2, 0.3, interaction_mode="base")
        assert dynamic["m_score"] == pytest.approx(base["m_score"])

    def test_emergence_readiness_boost_when_vulnerability_high(self):
        dynamic = detect_emergence(0.6, 0.6, 0.8, 0.6, interaction_mode="dynamic")
        base = detect_emergence(0.6, 0.6, 0.8, 0.6, interaction_mode="base")
        assert dynamic["m_score"] > base["m_score"]


class TestOutputSchema:
    """Required keys for downstream consumers."""

    def test_friction_output_keys(self):
        result = detect_friction(0.2, 0.3, 0.8, 0.7)
        required = {
            "alert",
            "severity",
            "severity_band",
            "lock_phase",
            "asymmetry_ratio",
            "recursion_assessment",
            "m_score",
            "spatial_component",
            "layer_attribution",
            "thresholds",
            "overrides_applied",
            "layer_visibility",
            "layer_coupling",
        }
        assert required.issubset(result.keys())

    def test_emergence_window_output_keys(self):
        result = detect_emergence(0.8, 0.82, 0.81, 0.7)
        required = {
            "window_detected",
            "window_type",
            "dissolution_sustainability",
            "recommended_action",
            "catalyst_score",
            "m_score",
            "spatial_component",
            "layer_attribution",
            "thresholds",
            "overrides_applied",
            "layer_visibility",
            "layer_coupling",
        }
        assert required.issubset(result.keys())

    def test_emergence_no_window_output_keys(self):
        result = detect_emergence(0.3, 0.4, 0.45, 0.5)
        required = {
            "window_detected",
            "catalyst_score",
            "limiting_factors",
            "status",
            "recommendation",
            "m_score",
            "spatial_component",
            "layer_attribution",
            "thresholds",
            "overrides_applied",
            "layer_visibility",
            "layer_coupling",
        }
        assert required.issubset(result.keys())


class TestDeterminism:
    """Deterministic outputs for fixed inputs."""

    def test_friction_determinism(self):
        r1 = detect_friction(0.2, 0.3, 0.8, 0.7)
        r2 = detect_friction(0.2, 0.3, 0.8, 0.7)
        assert r1["m_score"] == pytest.approx(r2["m_score"])
        assert r1["lock_phase"] == r2["lock_phase"]

    def test_emergence_determinism(self):
        r1 = detect_emergence(0.65, 0.75, 0.6, 0.5)
        r2 = detect_emergence(0.65, 0.75, 0.6, 0.5)
        assert r1["m_score"] == pytest.approx(r2["m_score"])
        assert r1["window_detected"] == r2["window_detected"]


class TestTemporalKernelRestriction:
    """System-lock temporal allowlist behavior in Python tool path."""

    def test_allowlist_registered(self):
        assert DOMAIN_KERNEL_ALLOWLIST["system_lock"] == ["linear", "memory", "s_curve"]

    def test_exponential_soft_rejected_in_overrides_applied(self):
        result = detect_friction(
            0.5,
            0.5,
            0.5,
            0.5,
            temporal_config={"kernel_type": "exponential", "t": 1.0},
        )
        rejected = result["overrides_applied"]["temporal_config"]["rejected"]
        assert "kernel_type" in rejected
        assert result["m_score"] > 0  # detection still returned

    @pytest.mark.parametrize("kernel_config", [
        {"kernel_type": "memory", "t": 1.0, "memory_strength": 1.0},
        {"kernel_type": "s_curve", "t": 1.0, "t0": 0.5},
        {"kernel_type": "linear", "t": 1.0, "alpha": 0.3},
    ])
    def test_allowed_kernels_accepted(self, kernel_config):
        result = detect_friction(0.5, 0.5, 0.5, 0.5, temporal_config=kernel_config)
        applied = result["overrides_applied"]["temporal_config"]["applied"]
        assert applied is not None
        assert applied["kernel_type"] == kernel_config["kernel_type"]


class TestReservedDomainCollision:
    """generic_detect must not shadow built-in system_lock domain."""

    def test_system_lock_reserved(self):
        assert "system_lock" in _RESERVED_DOMAINS

    def test_system_lock_collision_rejected(self):
        with pytest.raises(ValueError, match="collides with a built-in"):
            detect_generic(
                domain_name="system_lock",
                layer_names=["a", "b", "c", "d"],
                weights=[0.25, 0.25, 0.25, 0.25],
                layer_values=[0.5, 0.5, 0.5, 0.5],
                mode="friction",
            )


class TestThresholdOverrideClamping:
    """Threshold override governance remains bounded."""

    def test_friction_threshold_clamping(self):
        result = detect_friction(
            0.2,
            0.3,
            0.8,
            0.7,
            threshold_override={"lock_active": 0.99},
        )
        assert result["thresholds"]["lock_active"] == pytest.approx(0.624)
        assert result["overrides_applied"]["threshold_overrides"]["clamped"] is True

    def test_emergence_threshold_clamping(self):
        result = detect_emergence(
            0.6,
            0.7,
            0.8,
            0.6,
            threshold_override={"dissolution_window": 0.1},
        )
        assert result["thresholds"]["dissolution_window"] == pytest.approx(0.56)
        assert result["overrides_applied"]["threshold_overrides"]["clamped"] is True


class TestSeverityBanding:
    """Severity and band outputs are stable and bounded."""

    def test_severity_is_float_zero_to_one(self):
        result = detect_friction(0.2, 0.3, 0.8, 0.7)
        assert isinstance(result["severity"], float)
        assert 0.0 <= result["severity"] <= 1.0

    def test_severity_band_in_allowed_set(self):
        result = detect_friction(0.2, 0.3, 0.8, 0.7)
        assert result["severity_band"] in {"low", "moderate", "high", "critical"}

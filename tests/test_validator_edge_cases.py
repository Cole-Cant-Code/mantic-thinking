"""
Validator Edge Cases Tests

Tests the input validation and bounded override system at exact
boundaries, with adversarial types, and edge-case defaults.

Run with: python -m pytest tests/test_validator_edge_cases.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np

from mantic_thinking.core.validators import (
    clamp_input, normalize_weights, validate_layers, require_finite_inputs,
    check_mismatch, clamp_threshold_override, validate_temporal_config,
    clamp_f_time, DOMAIN_KERNEL_ALLOWLIST
)


# =============================================================================
# clamp_threshold_override Boundary Tests
# =============================================================================

class TestThresholdOverrideBoundaries:
    """Exact-boundary behavior of the ±20% drift clamping."""

    def test_at_exact_plus_20_percent_not_clamped(self):
        """Requested == default * 1.2 should NOT be clamped."""
        default = 0.4
        requested = default * 1.2  # 0.48
        clamped, was_clamped, info = clamp_threshold_override(requested, default)
        assert not was_clamped, f"Exact +20% boundary should not be clamped, got {info}"
        assert np.isclose(clamped, 0.48)

    def test_just_above_plus_20_percent_clamped(self):
        """Requested > default * 1.2 should be clamped."""
        default = 0.4
        requested = 0.49  # > 0.48
        clamped, was_clamped, info = clamp_threshold_override(requested, default)
        assert was_clamped, "Just above +20% should be clamped"
        assert np.isclose(clamped, 0.48)

    def test_at_exact_minus_20_percent_not_clamped(self):
        """Requested == default * 0.8 should NOT be clamped."""
        default = 0.4
        requested = default * 0.8  # 0.32
        clamped, was_clamped, info = clamp_threshold_override(requested, default)
        assert not was_clamped, f"Exact -20% boundary should not be clamped, got {info}"
        assert np.isclose(clamped, 0.32)

    def test_default_near_hard_max(self):
        """default=0.90: +20% = 1.08, hard max = 0.95 → hard bound wins."""
        default = 0.90
        requested = 1.0
        clamped, was_clamped, info = clamp_threshold_override(requested, default)
        assert was_clamped
        assert clamped <= 0.95, f"Hard bound should cap at 0.95, got {clamped}"

    def test_default_near_hard_min(self):
        """default=0.06: -20% = 0.048, hard min = 0.05 → hard bound wins."""
        default = 0.06
        requested = 0.01
        clamped, was_clamped, info = clamp_threshold_override(requested, default)
        assert was_clamped
        assert clamped >= 0.05, f"Hard bound should floor at 0.05, got {clamped}"

    def test_string_input_falls_back_to_default(self):
        """String input that can't be floated → fallback to default."""
        clamped, was_clamped, info = clamp_threshold_override("not_a_number", 0.4)
        assert was_clamped
        assert clamped == 0.4
        assert "Invalid type" in info.get("reason", "")

    def test_string_numeric_converts(self):
        """String '0.35' can be float() converted."""
        clamped, was_clamped, info = clamp_threshold_override("0.35", 0.4)
        # 0.35 is within ±20% of 0.4 (0.32-0.48)
        assert np.isclose(clamped, 0.35)

    def test_infinity_falls_back_to_default(self):
        """Infinity → fallback to default."""
        clamped, was_clamped, info = clamp_threshold_override(float('inf'), 0.4)
        assert was_clamped
        assert clamped == 0.4

    def test_nan_falls_back_to_default(self):
        """NaN → fallback to default."""
        clamped, was_clamped, info = clamp_threshold_override(float('nan'), 0.4)
        assert was_clamped
        assert clamped == 0.4

    def test_none_returns_default(self):
        """None → returns default without clamping."""
        clamped, was_clamped, info = clamp_threshold_override(None, 0.4)
        assert not was_clamped
        assert clamped == 0.4


# =============================================================================
# validate_temporal_config Edge Cases
# =============================================================================

class TestTemporalConfigEdgeCases:
    """Edge cases in temporal config validation."""

    def test_unknown_domain_rejects_kernel(self):
        """Unknown domain → kernel_type rejected (no allowlist defined)."""
        validated, rejected, clamped = validate_temporal_config(
            {"kernel_type": "oscillatory", "t": 5.0},
            domain="unknown_domain"
        )
        assert "kernel_type" not in validated
        assert "kernel_type" in rejected
        assert "Unknown domain" in rejected["kernel_type"]["reason"]

    def test_none_domain_allows_all_kernels(self):
        """None domain → empty allowlist → all kernel types allowed."""
        validated, rejected, clamped = validate_temporal_config(
            {"kernel_type": "oscillatory", "t": 5.0},
            domain=None
        )
        assert "kernel_type" in validated

    def test_alpha_clamped_at_bounds(self):
        """Alpha outside [0.01, 0.5] is clamped."""
        validated, rejected, clamped = validate_temporal_config(
            {"kernel_type": "exponential", "alpha": 999, "t": 1.0},
            domain="healthcare"
        )
        assert validated["alpha"] == 0.5  # Clamped to max
        assert "alpha" in clamped

    def test_alpha_at_exact_min(self):
        """Alpha at exact minimum (0.01) is not clamped."""
        validated, rejected, clamped = validate_temporal_config(
            {"kernel_type": "exponential", "alpha": 0.01, "t": 1.0},
            domain="healthcare"
        )
        assert validated["alpha"] == 0.01
        assert "alpha" not in clamped

    def test_novelty_clamped_at_bounds(self):
        """n outside [-2.0, 2.0] is clamped."""
        validated, rejected, clamped = validate_temporal_config(
            {"kernel_type": "exponential", "n": 10.0, "t": 1.0},
            domain="healthcare"
        )
        assert validated["n"] == 2.0
        assert "n" in clamped

    def test_invalid_alpha_type_rejected(self):
        """Non-numeric alpha is rejected."""
        validated, rejected, clamped = validate_temporal_config(
            {"kernel_type": "exponential", "alpha": "fast", "t": 1.0},
            domain="healthcare"
        )
        assert "alpha" in rejected
        assert "alpha" not in validated

    def test_none_config_returns_none(self):
        """None config returns (None, {}, {})."""
        validated, rejected, clamped = validate_temporal_config(None)
        assert validated is None
        assert rejected == {}
        assert clamped == {}


# =============================================================================
# clamp_f_time Tests
# =============================================================================

class TestClampFTime:
    """Edge cases for f_time clamping."""

    def test_at_exact_lower_bound_not_clamped(self):
        """f_time=0.1 (exact lower bound) is NOT clamped."""
        clamped, was_clamped, info = clamp_f_time(0.1)
        assert not was_clamped
        assert clamped == 0.1

    def test_at_exact_upper_bound_not_clamped(self):
        """f_time=3.0 (exact upper bound) is NOT clamped."""
        clamped, was_clamped, info = clamp_f_time(3.0)
        assert not was_clamped
        assert clamped == 3.0

    def test_below_lower_bound_clamped(self):
        """f_time=0.05 → clamped to 0.1."""
        clamped, was_clamped, info = clamp_f_time(0.05)
        assert was_clamped
        assert clamped == 0.1

    def test_above_upper_bound_clamped(self):
        """f_time=100 → clamped to 3.0."""
        clamped, was_clamped, info = clamp_f_time(100)
        assert was_clamped
        assert clamped == 3.0

    def test_none_returns_default_1(self):
        """None f_time → returns 1.0."""
        clamped, was_clamped, info = clamp_f_time(None)
        assert clamped == 1.0
        assert not was_clamped

    def test_invalid_type_returns_default(self):
        """String f_time → returns 1.0."""
        clamped, was_clamped, info = clamp_f_time("fast")
        assert clamped == 1.0
        assert was_clamped


# =============================================================================
# normalize_weights Edge Cases
# =============================================================================

class TestNormalizeWeightsEdges:
    """Edge cases in weight normalization."""

    def test_negative_weights_clipped_to_zero(self):
        """Negative weights are clipped to 0, then normalized."""
        result = normalize_weights([-0.5, 0.5, 0.5, 0.5])
        assert np.isclose(result[0], 0.0)
        assert np.isclose(sum(result), 1.0)

    def test_all_zero_weights_raises(self):
        """All-zero weights should raise ValueError."""
        with pytest.raises(ValueError, match="all weights are zero"):
            normalize_weights([0.0, 0.0, 0.0, 0.0])

    def test_all_negative_raises(self):
        """All-negative weights clip to zero, then raise."""
        with pytest.raises(ValueError, match="all weights are zero"):
            normalize_weights([-1.0, -1.0, -1.0, -1.0])


# =============================================================================
# check_mismatch Edge Cases
# =============================================================================

class TestCheckMismatchEdges:
    """Edge cases in mismatch detection."""

    def test_all_identical_values_no_mismatch(self):
        """All identical values → no mismatch in any mode."""
        for mode in ["variance", "range", "pairwise"]:
            has_mismatch, score, _ = check_mismatch(
                [0.5, 0.5, 0.5, 0.5], threshold=0.4, comparison_mode=mode
            )
            assert not has_mismatch, f"Mode {mode}: identical values should not mismatch"
            assert score == 0.0

    def test_insufficient_data(self):
        """Fewer than 2 valid values → no mismatch."""
        has_mismatch, score, desc = check_mismatch(
            [0.5, np.nan, np.nan, np.nan], threshold=0.0
        )
        assert not has_mismatch
        assert "Insufficient data" in desc


# =============================================================================
# require_finite_inputs Tests
# =============================================================================

class TestRequireFiniteInputs:
    """Test strict input validation."""

    def test_none_raises_valueerror(self):
        """None input raises ValueError."""
        with pytest.raises(ValueError, match="required"):
            require_finite_inputs({"x": None})

    def test_nan_raises_valueerror(self):
        """NaN input raises ValueError."""
        with pytest.raises(ValueError, match="finite"):
            require_finite_inputs({"x": float('nan')})

    def test_inf_raises_valueerror(self):
        """Infinity raises ValueError."""
        with pytest.raises(ValueError, match="finite"):
            require_finite_inputs({"x": float('inf')})

    def test_string_raises_typeerror(self):
        """String input raises TypeError."""
        with pytest.raises(TypeError, match="must be a number"):
            require_finite_inputs({"x": "not_a_number"})

    def test_valid_inputs_pass(self):
        """Valid numeric inputs should not raise."""
        require_finite_inputs({"a": 0.5, "b": 1.0, "c": -0.3})  # No exception


# =============================================================================
# Domain Kernel Allowlist Coverage
# =============================================================================

class TestDomainKernelAllowlists:
    """Verify every domain has a defined allowlist."""

    @pytest.mark.parametrize("domain", [
        "healthcare", "finance", "cyber", "climate",
        "legal", "military", "social", "planning"
    ])
    def test_domain_has_allowlist(self, domain):
        """Each domain should have a non-empty kernel allowlist."""
        assert domain in DOMAIN_KERNEL_ALLOWLIST
        assert len(DOMAIN_KERNEL_ALLOWLIST[domain]) > 0

    def test_all_domains_allow_linear(self):
        """'linear' kernel should be allowed in every domain."""
        for domain, allowed in DOMAIN_KERNEL_ALLOWLIST.items():
            assert "linear" in allowed, f"Domain {domain} does not allow 'linear'"

"""
Temporal Kernel Extreme Value Tests

Tests temporal kernel behavior at extreme inputs, overflow boundaries,
and interaction with the f_time clamping system in tools.

Run with: python -m pytest tests/test_temporal_extremes.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np

from core.mantic_kernel import compute_temporal_kernel
from core.validators import clamp_f_time
from tools.friction.healthcare_phenotype_genotype import detect as healthcare_detect


# =============================================================================
# Extreme t Values
# =============================================================================

class TestExtremeTimeValues:
    """Temporal kernel behavior with very large/small t."""

    def test_exponential_very_large_t(self):
        """exp(1.0 * 0.1 * 1000) = exp(100) ≈ 2.69e43 — valid but huge."""
        result = compute_temporal_kernel(t=1000, n=1.0, alpha=0.1,
                                         kernel_type="exponential")
        assert result > 1e10, "Huge t should produce huge exponential"
        assert np.isfinite(result), "Should still be finite"

    def test_exponential_very_negative_t(self):
        """exp(1.0 * 0.1 * -1000) = exp(-100) ≈ 0 → positivity clamp."""
        result = compute_temporal_kernel(t=-1000, n=1.0, alpha=0.1,
                                         kernel_type="exponential")
        assert result == pytest.approx(1e-10), "Should clamp to positivity minimum"

    def test_linear_beyond_decay(self):
        """max(0, 1 - 0.1*20) = max(0, -1) = 0 → positivity clamp."""
        result = compute_temporal_kernel(t=20, alpha=0.1,
                                         kernel_type="linear")
        assert result == pytest.approx(1e-10), "Linear beyond decay → positivity clamp"

    def test_linear_at_zero(self):
        """t=0 → max(0, 1 - 0) = 1.0."""
        result = compute_temporal_kernel(t=0, alpha=0.1, kernel_type="linear")
        assert result == pytest.approx(1.0)

    def test_memory_negative_t(self):
        """t=-5: 1 + 1.0 * exp(5) ≈ 149.4 — large but valid."""
        result = compute_temporal_kernel(t=-5, kernel_type="memory",
                                         memory_strength=1.0)
        assert result > 100, "Negative t in memory kernel should produce large value"
        assert np.isfinite(result)

    def test_s_curve_far_from_t0(self):
        """t=-100, t0=0, alpha=0.1: 1/(1+exp(10)) ≈ 0.000045."""
        result = compute_temporal_kernel(t=-100, alpha=0.1, kernel_type="s_curve",
                                         t0=0)
        assert result < 0.001
        assert result > 0  # Still positive

    def test_s_curve_far_above_t0(self):
        """t=100, t0=0, alpha=0.1: 1/(1+exp(-10)) ≈ 0.99995."""
        result = compute_temporal_kernel(t=100, alpha=0.1, kernel_type="s_curve",
                                         t0=0)
        assert result > 0.999


# =============================================================================
# Power Law Near Singularity
# =============================================================================

class TestPowerLawSingularity:
    """Power law behavior near t=-1 singularity."""

    def test_power_law_near_singularity(self):
        """t=-0.999: base = max(1e-10, 0.001) = 0.001."""
        result = compute_temporal_kernel(t=-0.999, n=1.0, alpha=0.1,
                                         kernel_type="power_law")
        assert result > 0
        assert np.isfinite(result)

    def test_power_law_past_singularity(self):
        """t=-2: base = max(1e-10, -1) = 1e-10."""
        result = compute_temporal_kernel(t=-2, n=1.0, alpha=0.1,
                                         kernel_type="power_law")
        assert result > 0
        assert np.isfinite(result)

    def test_power_law_positive_t(self):
        """t=10: base = 11, 11^(0.1) ≈ 1.27."""
        result = compute_temporal_kernel(t=10, n=1.0, alpha=0.1,
                                         kernel_type="power_law")
        assert result > 1.0  # Growth for positive t


# =============================================================================
# Oscillatory Extreme Frequency
# =============================================================================

class TestOscillatoryExtremes:
    """Oscillatory kernel with extreme parameters."""

    def test_extreme_frequency(self):
        """frequency=10000 with t=1 — rapid oscillation, still valid."""
        result = compute_temporal_kernel(t=1, n=1.0, alpha=0.1,
                                         kernel_type="oscillatory",
                                         frequency=10000)
        assert np.isfinite(result)
        assert result > 0

    def test_zero_frequency(self):
        """frequency=0 → sin(0) = 0, result = exp(n*a*t) * 0.5 * 1.0."""
        result = compute_temporal_kernel(t=1, n=1.0, alpha=0.1,
                                         kernel_type="oscillatory",
                                         frequency=0)
        expected = np.exp(0.1) * 0.5 * (1.0 + 0.0)
        assert result == pytest.approx(expected, rel=1e-6)


# =============================================================================
# Alpha at Bounds
# =============================================================================

class TestAlphaAtBounds:
    """Kernel behavior with alpha at validation bounds."""

    def test_alpha_minimum(self):
        """alpha=0.01 (minimum after clamping) — very slow growth."""
        result = compute_temporal_kernel(t=10, n=1.0, alpha=0.01,
                                         kernel_type="exponential")
        # exp(0.1) ≈ 1.105
        assert result == pytest.approx(np.exp(0.1), rel=1e-6)

    def test_alpha_maximum(self):
        """alpha=0.5 (maximum after clamping) — rapid growth."""
        result = compute_temporal_kernel(t=10, n=1.0, alpha=0.5,
                                         kernel_type="exponential")
        # exp(5.0) ≈ 148.4
        assert result == pytest.approx(np.exp(5.0), rel=1e-6)


# =============================================================================
# f_time Clamping in Tools
# =============================================================================

class TestFTimeClampingInTools:
    """Tools clamp extreme temporal kernel outputs to [0.1, 3.0]."""

    def test_extreme_temporal_clamped_in_tool(self):
        """Tool with extreme temporal_config has f_time clamped to 3.0 max."""
        # exponential with large t produces huge f_time,
        # but tool clamps to [0.1, 3.0]
        result = healthcare_detect(
            phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8,
            temporal_config={"kernel_type": "exponential", "t": 100, "alpha": 0.1}
        )
        f_info = result["overrides_applied"]["f_time"]
        assert f_info["used"] <= 3.0, "f_time should be clamped to max 3.0"
        assert f_info["clamped"] is True

    def test_very_small_temporal_clamped_in_tool(self):
        """Near-zero temporal kernel is clamped to 0.1 minimum."""
        result = healthcare_detect(
            phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8,
            temporal_config={"kernel_type": "linear", "t": 100, "alpha": 0.1}
        )
        f_info = result["overrides_applied"]["f_time"]
        assert f_info["used"] >= 0.1, "f_time should be clamped to min 0.1"


# =============================================================================
# Unknown Kernel Type
# =============================================================================

class TestUnknownKernelType:
    """Unknown kernel types should raise."""

    def test_unknown_kernel_raises(self):
        """Unrecognized kernel_type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown kernel type"):
            compute_temporal_kernel(t=1, kernel_type="hyperbolic")


# =============================================================================
# Backward Compatibility
# =============================================================================

class TestBackwardCompatibility:
    """decay_rate parameter backward compatibility."""

    def test_decay_rate_maps_to_alpha(self):
        """decay_rate parameter should behave identically to alpha."""
        result_alpha = compute_temporal_kernel(t=5, n=1.0, alpha=0.1,
                                                kernel_type="exponential")
        result_decay = compute_temporal_kernel(t=5, n=1.0, decay_rate=0.1,
                                                kernel_type="exponential")
        assert result_alpha == result_decay

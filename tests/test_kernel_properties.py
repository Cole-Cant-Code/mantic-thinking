"""
Kernel Mathematical Properties Tests

Tests the immutable mantic kernel for mathematical invariants,
boundary conditions, and property-based correctness.

Run with: python -m pytest tests/test_kernel_properties.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
import random

# Tools call the safe kernel wrapper; keep the core kernel immutable.
from mantic_thinking.core.safe_kernel import safe_mantic_kernel as mantic_kernel
from mantic_thinking.core.mantic_kernel import compute_temporal_kernel, verify_kernel_integrity


# =============================================================================
# Property-Based Tests (using random valid inputs)
# =============================================================================

class TestAttributionInvariant:
    """Attribution percentages must sum to 1.0 (or all zeros)."""

    @pytest.mark.parametrize("seed", range(50))
    def test_attribution_sums_to_one(self, seed):
        """For random valid inputs, sum(attr) ≈ 1.0 when S > 0."""
        rng = random.Random(seed)
        W_raw = [rng.random() for _ in range(4)]
        W_sum = sum(W_raw)
        W = [w / W_sum for w in W_raw]
        L = [rng.random() for _ in range(4)]
        # v1.4.0+: interaction coefficients are bounded to [0.1, 2.0]
        I = [0.1 + rng.random() * (2.0 - 0.1) for _ in range(4)]

        M, S, attr = mantic_kernel(W, L, I)

        if S > 1e-10:
            assert np.isclose(sum(attr), 1.0, atol=1e-8), \
                f"Attribution sum={sum(attr)}, expected 1.0 (S={S})"
        else:
            assert all(np.isclose(a, 0.0, atol=1e-10) for a in attr), \
                f"When S≈0, all attributions should be 0, got {attr}"

    def test_attribution_all_zeros_when_layers_zero(self):
        """When all layers are zero, attribution should be all zeros."""
        W = [0.25, 0.25, 0.25, 0.25]
        L = [0.0, 0.0, 0.0, 0.0]
        I = [1.0, 1.0, 1.0, 1.0]

        M, S, attr = mantic_kernel(W, L, I)
        assert all(a == 0.0 for a in attr)


class TestMonotonicity:
    """M-score monotonicity properties."""

    def test_m_monotonic_with_f_time(self):
        """Higher f_time produces higher M (for S > 0)."""
        W = [0.25, 0.25, 0.25, 0.25]
        L = [0.5, 0.6, 0.7, 0.8]
        I = [1.0, 1.0, 1.0, 1.0]

        f_times = [0.1, 0.5, 1.0, 1.5, 2.0, 3.0]
        m_scores = [mantic_kernel(W, L, I, f_time=ft)[0] for ft in f_times]

        for i in range(len(m_scores) - 1):
            assert m_scores[i] < m_scores[i + 1], \
                f"M not monotonic: f_time={f_times[i]}→M={m_scores[i]}, " \
                f"f_time={f_times[i+1]}→M={m_scores[i+1]}"

    @pytest.mark.parametrize("layer_idx", [0, 1, 2, 3])
    def test_m_nondecreasing_with_layer_value(self, layer_idx):
        """Increasing any single layer value never decreases M."""
        W = [0.25, 0.25, 0.25, 0.25]
        I = [1.0, 1.0, 1.0, 1.0]

        layer_values = [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
        m_scores = []
        for val in layer_values:
            L = [0.5, 0.5, 0.5, 0.5]
            L[layer_idx] = val
            M, _, _ = mantic_kernel(W, L, I)
            m_scores.append(M)

        for i in range(len(m_scores) - 1):
            assert m_scores[i] <= m_scores[i + 1] + 1e-10, \
                f"M decreased when L[{layer_idx}] went from " \
                f"{layer_values[i]} to {layer_values[i+1]}"


class TestBoundaryConditions:
    """Edge cases and boundary values."""

    def test_all_layers_zero(self):
        """L=[0,0,0,0] produces M=0, S=0, attr=[0,0,0,0]."""
        W = [0.25, 0.25, 0.25, 0.25]
        L = [0.0, 0.0, 0.0, 0.0]
        I = [1.0, 1.0, 1.0, 1.0]

        M, S, attr = mantic_kernel(W, L, I)

        assert M == 0.0
        assert S == 0.0
        assert attr == [0.0, 0.0, 0.0, 0.0]

    def test_all_layers_one_uniform_weights(self):
        """L=[1,1,1,1] with uniform weights produces M=1.0, S=1.0."""
        W = [0.25, 0.25, 0.25, 0.25]
        L = [1.0, 1.0, 1.0, 1.0]
        I = [1.0, 1.0, 1.0, 1.0]

        M, S, attr = mantic_kernel(W, L, I)

        assert np.isclose(M, 1.0, atol=1e-10)
        assert np.isclose(S, 1.0, atol=1e-10)

    def test_k_n_zero_raises_valueerror(self):
        """k_n=0 is rejected with ValueError."""
        W = [0.25, 0.25, 0.25, 0.25]
        L = [0.5, 0.5, 0.5, 0.5]
        I = [1.0, 1.0, 1.0, 1.0]

        with pytest.raises(ValueError, match="must be positive"):
            mantic_kernel(W, L, I, k_n=0.0)

    def test_k_n_negative_raises_valueerror(self):
        """k_n<0 is rejected with ValueError."""
        W = [0.25, 0.25, 0.25, 0.25]
        L = [0.5, 0.5, 0.5, 0.5]
        I = [1.0, 1.0, 1.0, 1.0]

        with pytest.raises(ValueError, match="must be positive"):
            mantic_kernel(W, L, I, k_n=-1.0)

    def test_single_non_nan_layer(self):
        """Kernel allows 1 non-NaN layer (validators require 2)."""
        W = [0.25, 0.25, 0.25, 0.25]
        L = [0.5, np.nan, np.nan, np.nan]
        I = [1.0, 1.0, 1.0, 1.0]

        # Kernel itself does not reject single layer
        M, S, attr = mantic_kernel(W, L, I)

        assert M > 0
        assert len(attr) == 4
        # Only first layer has non-zero attribution
        assert attr[0] > 0
        assert all(np.isclose(attr[i], 0.0) for i in [1, 2, 3])

    def test_zero_weight_layer_has_zero_attribution(self):
        """A layer with weight=0 contributes nothing."""
        W = [0.5, 0.5, 0.0, 0.0]
        L = [0.8, 0.6, 1.0, 1.0]
        I = [1.0, 1.0, 1.0, 1.0]

        M, S, attr = mantic_kernel(W, L, I)

        assert np.isclose(attr[2], 0.0, atol=1e-10)
        assert np.isclose(attr[3], 0.0, atol=1e-10)
        assert attr[0] > 0
        assert attr[1] > 0

    def test_all_nan_raises(self):
        """All NaN layers should raise ValueError."""
        W = [0.25, 0.25, 0.25, 0.25]
        L = [np.nan, np.nan, np.nan, np.nan]
        I = [1.0, 1.0, 1.0, 1.0]

        with pytest.raises(ValueError, match="All layer values are NaN"):
            mantic_kernel(W, L, I)


class TestDeterminism:
    """Bit-identical results across repeated calls."""

    def test_determinism_1000_repeats(self):
        """Same inputs produce bit-identical results 1000 times."""
        W = [0.30, 0.25, 0.25, 0.20]
        L = [0.73, 0.41, 0.88, 0.55]
        I = [0.9, 1.0, 0.8, 0.7]

        reference = mantic_kernel(W, L, I, f_time=1.5)

        for _ in range(1000):
            result = mantic_kernel(W, L, I, f_time=1.5)
            assert result[0] == reference[0], "M-score not deterministic"
            assert result[1] == reference[1], "S not deterministic"
            assert result[2] == reference[2], "Attribution not deterministic"

    def test_kernel_integrity_still_holds(self):
        """verify_kernel_integrity should always pass."""
        assert verify_kernel_integrity()


class TestArrayLengthValidation:
    """Array length mismatches should raise."""

    def test_mismatched_lengths(self):
        """W, L, I must all have same length."""
        with pytest.raises(ValueError, match="Array length mismatch"):
            mantic_kernel([0.5, 0.5], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0])

    def test_weight_sum_validation(self):
        """Weights must sum to ~1.0."""
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            mantic_kernel([0.1, 0.1, 0.1, 0.1], [0.5, 0.5, 0.5, 0.5],
                          [1.0, 1.0, 1.0, 1.0])

    def test_layer_out_of_range_raises(self):
        """Layer values outside [0,1] should raise."""
        with pytest.raises(ValueError, match="Layer values"):
            mantic_kernel([0.25, 0.25, 0.25, 0.25], [1.5, 0.5, 0.5, 0.5],
                          [1.0, 1.0, 1.0, 1.0])

    def test_interaction_out_of_range_raises(self):
        """Interaction coefficients outside [0.1,2.0] should raise."""
        with pytest.raises(ValueError, match="Interaction coefficients"):
            mantic_kernel([0.25, 0.25, 0.25, 0.25], [0.5, 0.5, 0.5, 0.5],
                          [2.5, 1.0, 1.0, 1.0])

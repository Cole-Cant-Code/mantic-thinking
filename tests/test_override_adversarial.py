"""
Override System Robustness Tests

Tests the bounded override system with adversarial inputs,
edge cases, and chained overrides.

Run with: python -m pytest tests/test_override_adversarial.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np

from mantic_thinking.tools.friction.healthcare_phenotype_genotype import detect as healthcare_friction
from mantic_thinking.tools.friction.climate_maladaptation import detect as climate_friction
from mantic_thinking.tools.emergence.healthcare_precision_therapeutic import detect as healthcare_emergence


# =============================================================================
# Adversarial Threshold Overrides
# =============================================================================

class TestAdversarialThresholdOverrides:
    """Test override system with unusual/adversarial inputs."""

    def test_empty_dict_same_as_no_override(self):
        """threshold_override={} behaves identically to None."""
        base = dict(phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8)
        result_none = healthcare_friction(**base)
        result_empty = healthcare_friction(**base, threshold_override={})

        assert result_none["m_score"] == result_empty["m_score"]
        assert result_none["alert"] == result_empty["alert"]

    def test_unknown_keys_ignored(self):
        """Unknown threshold keys are silently ignored."""
        result = healthcare_friction(
            phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8,
            threshold_override={"nonexistent_key": 0.5, "another_fake": 0.9}
        )
        # Result should use default thresholds
        assert result["threshold"] == 0.4  # Default buffering threshold
        assert result["alert"] is not None  # Normal detection

    def test_mixed_valid_and_invalid_keys(self):
        """Valid keys applied, invalid keys ignored."""
        result = healthcare_friction(
            phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8,
            threshold_override={"buffering": 0.35, "nonexistent": 0.99}
        )
        # buffering should be applied (0.35 is within ±20% of 0.4)
        assert result["threshold"] == 0.35
        # Check audit trail
        audit = result["overrides_applied"]["threshold_overrides"]
        assert "nonexistent" not in str(audit.get("applied", {}))


# =============================================================================
# Adversarial Temporal Config
# =============================================================================

class TestAdversarialTemporalConfig:
    """Test temporal config with missing/invalid parameters."""

    def test_kernel_type_without_t_rejected(self):
        """temporal_config with kernel_type but no t is rejected."""
        result = healthcare_friction(
            phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8,
            temporal_config={"kernel_type": "exponential"}
        )
        temporal = result["overrides_applied"]["temporal_config"]
        assert temporal["rejected"] is not None
        assert "t" in temporal["rejected"]

    def test_t_without_kernel_type_rejected(self):
        """temporal_config with t but no kernel_type is rejected."""
        result = healthcare_friction(
            phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8,
            temporal_config={"t": 5.0}
        )
        temporal = result["overrides_applied"]["temporal_config"]
        assert temporal["rejected"] is not None
        assert "kernel_type" in temporal["rejected"]

    def test_domain_forbidden_kernel_rejected(self):
        """Healthcare does not allow 'oscillatory' kernel."""
        result = healthcare_friction(
            phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8,
            temporal_config={"kernel_type": "oscillatory", "t": 5.0}
        )
        temporal = result["overrides_applied"]["temporal_config"]
        assert temporal["rejected"] is not None
        assert "kernel_type" in temporal["rejected"]

    def test_valid_temporal_config_applied(self):
        """Valid temporal config is applied and changes M-score."""
        base = dict(phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8)
        result_no_temporal = healthcare_friction(**base)
        result_temporal = healthcare_friction(
            **base,
            temporal_config={"kernel_type": "exponential", "t": 2.0, "alpha": 0.1}
        )
        # Temporal should change M-score
        assert result_temporal["m_score"] != result_no_temporal["m_score"]
        temporal = result_temporal["overrides_applied"]["temporal_config"]
        assert temporal["applied"] is not None


# =============================================================================
# Combined Overrides
# =============================================================================

class TestCombinedOverrides:
    """Test threshold + temporal overrides together."""

    def test_both_overrides_audited_independently(self):
        """Both threshold and temporal overrides appear in audit."""
        result = healthcare_friction(
            phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8,
            threshold_override={"buffering": 0.35},
            temporal_config={"kernel_type": "s_curve", "alpha": 0.1, "t": 2.0}
        )
        audit = result["overrides_applied"]
        assert "threshold_overrides" in audit
        assert "temporal_config" in audit
        assert "f_time" in audit

    def test_idempotent_override_reapplication(self):
        """Re-applying an already-clamped threshold produces same result."""
        base = dict(phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8)

        # First call with override
        result1 = healthcare_friction(**base, threshold_override={"buffering": 0.35})
        used_threshold = result1["threshold"]

        # Second call using the result's threshold as the new override
        result2 = healthcare_friction(**base, threshold_override={"buffering": used_threshold})

        assert result1["m_score"] == result2["m_score"]
        assert result1["alert"] == result2["alert"]


# =============================================================================
# Sensitivity: Thresholds at ±20% Drift
# =============================================================================

class TestSensitivityAtDriftBounds:
    """Test that ±20% drift changes detection behavior predictably."""

    def test_max_permissive_threshold(self):
        """Threshold at +20% → fewer alerts (more permissive)."""
        # Default buffering threshold = 0.4, +20% = 0.48
        # Construct case with buffering_score ≈ 0.45 (between 0.4 and 0.48)
        # expected = 0.8*0.6 + 0.3*0.4 = 0.60
        # phenotypic=0.15, buffering_score = |0.15 - 0.60| = 0.45
        result_default = healthcare_friction(
            phenotypic=0.15, genomic=0.8, environmental=0.3, psychosocial=0.8
        )
        result_permissive = healthcare_friction(
            phenotypic=0.15, genomic=0.8, environmental=0.3, psychosocial=0.8,
            threshold_override={"buffering": 0.48}
        )
        # Default triggers (0.45 > 0.4), permissive does not (0.45 < 0.48)
        assert result_default["alert"] is not None
        assert result_permissive["alert"] is None

    def test_max_sensitive_threshold(self):
        """Threshold at -20% → more alerts (more sensitive)."""
        # Default buffering threshold = 0.4, -20% = 0.32
        # Construct case with buffering_score ≈ 0.35 (between 0.32 and 0.4)
        # expected = 0.6*0.6 + 0.5*0.4 = 0.56
        # phenotypic=0.9, buffering_score = |0.9 - 0.56| = 0.34
        result_default = healthcare_friction(
            phenotypic=0.9, genomic=0.6, environmental=0.5, psychosocial=0.5
        )
        result_sensitive = healthcare_friction(
            phenotypic=0.9, genomic=0.6, environmental=0.5, psychosocial=0.5,
            threshold_override={"buffering": 0.32}
        )
        # Default does not trigger (0.34 < 0.4), sensitive triggers (0.34 > 0.32)
        assert result_default["alert"] is None
        assert result_sensitive["alert"] is not None


# =============================================================================
# Emergence Overrides
# =============================================================================

class TestEmergenceOverrides:
    """Test that emergence tools honor threshold overrides correctly."""

    def test_alignment_threshold_override_affects_detection(self):
        """Lowering alignment threshold should detect more windows."""
        # inputs where all layers are 0.60 (below default 0.65)
        base = dict(
            genomic_predisposition=0.60,
            environmental_readiness=0.60,
            phenotypic_timing=0.60,
            psychosocial_engagement=0.60
        )
        result_default = healthcare_emergence(**base)
        result_lower = healthcare_emergence(
            **base, threshold_override={"alignment": 0.55}
        )

        assert result_default["window_detected"] is False
        assert result_lower["window_detected"] is True

"""
Regression and Snapshot Tests

Verifies immutability markers, public API surface, and golden
output consistency across releases.

Run with: python -m pytest tests/test_regression_snapshots.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np

from core.mantic_kernel import KERNEL_VERSION, KERNEL_HASH, mantic_kernel, verify_kernel_integrity
import tools


# =============================================================================
# Immutability Markers
# =============================================================================

class TestImmutabilityMarkers:
    """Kernel version and hash must never change."""

    def test_kernel_version(self):
        """KERNEL_VERSION must remain '1.0.0'."""
        assert KERNEL_VERSION == "1.0.0"

    def test_kernel_hash(self):
        """KERNEL_HASH must remain 'immutable_core_v1'."""
        assert KERNEL_HASH == "immutable_core_v1"

    def test_kernel_integrity(self):
        """verify_kernel_integrity() must always return True."""
        assert verify_kernel_integrity() is True


# =============================================================================
# Public API Surface
# =============================================================================

class TestPublicAPISurface:
    """tools.__all__ must contain exactly 14 public tool modules."""

    EXPECTED_TOOLS = sorted([
        "healthcare_phenotype_genotype",
        "finance_regime_conflict",
        "cyber_attribution_resolver",
        "climate_maladaptation",
        "legal_precedent_drift",
        "military_friction_forecast",
        "social_narrative_rupture",
        "healthcare_precision_therapeutic",
        "finance_confluence_alpha",
        "cyber_adversary_overreach",
        "climate_resilience_multiplier",
        "legal_precedent_seeding",
        "military_strategic_initiative",
        "social_catalytic_alignment",
    ])

    def test_all_has_14_tools(self):
        """tools.__all__ has exactly 14 entries."""
        assert len(tools.__all__) == 14

    def test_all_matches_expected(self):
        """tools.__all__ contains exactly the expected 14 names."""
        assert sorted(tools.__all__) == self.EXPECTED_TOOLS

    def test_no_internal_tools_exported(self):
        """Internal tools must NOT be in __all__."""
        assert "codebase_layer_conflict" not in tools.__all__
        assert "codebase_alignment_window" not in tools.__all__
        assert "plan_alignment_window" not in tools.__all__


# =============================================================================
# Golden Output Snapshots
# =============================================================================

class TestGoldenOutputs:
    """Fixed inputs must produce known outputs across releases."""

    def test_kernel_golden_output(self):
        """Known kernel input/output pair must not drift."""
        W = [0.25, 0.25, 0.25, 0.25]
        L = [0.8, 0.6, 0.9, 0.4]
        I = [1.0, 1.0, 1.0, 1.0]

        M, S, attr = mantic_kernel(W, L, I)

        # Golden values (verified at v1.0.0)
        assert np.isclose(M, 0.675, atol=1e-10)
        assert np.isclose(S, 0.675, atol=1e-10)
        assert len(attr) == 4

    def test_healthcare_friction_golden(self):
        """Healthcare friction with known inputs produces known output."""
        from tools.friction.healthcare_phenotype_genotype import detect

        result = detect(phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8)

        # Verify key structural properties (not exact float values)
        assert result["alert"] is not None
        assert "RESILIENCE" in result["alert"]
        assert result["buffering_layer"] == "psychosocial"
        assert 0 < result["m_score"] < 1

    def test_finance_emergence_golden(self):
        """Finance emergence with known inputs produces known output."""
        from tools.emergence.finance_confluence_alpha import detect

        result = detect(
            technical_setup=0.85, macro_tailwind=0.80,
            flow_positioning=0.75, risk_compression=0.70
        )

        assert result["window_detected"] is True
        assert result["position_direction"] == "short"
        assert result["setup_quality"] in ("HIGH_CONVICTION", "MODERATE_CONVICTION")
        assert 0 < result["m_score"] < 1

    @pytest.mark.parametrize("tool_name,inputs", [
        ("healthcare_phenotype_genotype", {"phenotypic": 0.5, "genomic": 0.5, "environmental": 0.5, "psychosocial": 0.5}),
        ("finance_regime_conflict", {"technical": 0.5, "macro": 0.5, "flow": 0.0, "risk": 0.5}),
        ("climate_maladaptation", {"atmospheric": 0.5, "ecological": 0.5, "infrastructure": 0.5, "policy": 0.5}),
    ])
    def test_neutral_inputs_no_alert(self, tool_name, inputs):
        """Neutral (0.5) inputs should generally not trigger alerts."""
        from adapters.openai_adapter import TOOL_MAP
        result = TOOL_MAP[tool_name](**inputs)
        # For balanced inputs, most tools should not alert
        # (finance_regime_conflict WILL alert because flow=0 is not aligned)
        if tool_name != "finance_regime_conflict":
            assert result.get("alert") is None or result.get("decision") == "proceed"

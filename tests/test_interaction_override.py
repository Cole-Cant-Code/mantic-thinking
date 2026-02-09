"""Interaction coefficient (I) override tests.

These tests validate the new interaction override API:
- validation/clamping
- tool-level behavior changes when overrides are applied
- audit trail in overrides_applied
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from mantic_thinking.core.validators import (
    validate_interaction_override,
    apply_interaction_override,
)


def test_validate_interaction_override_list_ok():
    validated, rejected, clamped = validate_interaction_override([0.6, 1.0, 0.8, 1.0], ["a", "b", "c", "d"])
    assert validated == [0.6, 1.0, 0.8, 1.0]
    assert rejected == {}
    assert clamped == {}


def test_validate_interaction_override_list_clamped_and_rejected():
    validated, rejected, clamped = validate_interaction_override([0.0, "x", 10.0, 1.0], ["a", "b", "c", "d"])

    # 0.0 clamps up to 0.1
    assert validated[0] == pytest.approx(0.1)
    assert "0" in clamped

    # "x" rejected -> defaulted to 1.0
    assert validated[1] == pytest.approx(1.0)
    assert "1" in rejected

    # 10 clamps down to 2.0
    assert validated[2] == pytest.approx(2.0)
    assert "2" in clamped


def test_validate_interaction_override_dict_ok_missing_filled():
    validated, rejected, clamped = validate_interaction_override({"b": 0.7}, ["a", "b", "c", "d"])
    assert validated == [1.0, 0.7, 1.0, 1.0]
    assert rejected == {}
    assert clamped == {}


def test_apply_interaction_override_scale_and_replace():
    used, final_clamped = apply_interaction_override([1.0, 0.5, 1.0, 1.0], [0.8, 2.0, 1.0, 1.0], mode="scale")
    assert used == [0.8, 1.0, 1.0, 1.0]
    assert final_clamped == {}

    used2, final_clamped2 = apply_interaction_override([1.0, 0.5, 1.0, 1.0], [0.8, 2.0, 1.0, 1.0], mode="replace")
    assert used2 == [0.8, 2.0, 1.0, 1.0]
    assert final_clamped2 == {}


def test_tool_interaction_override_changes_score_and_audit():
    from mantic_thinking.tools.friction.healthcare_phenotype_genotype import detect

    base = detect(phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8)
    tuned = detect(
        phenotypic=0.3,
        genomic=0.9,
        environmental=0.4,
        psychosocial=0.8,
        interaction_override={"phenotypic": 0.7},
        interaction_override_mode="scale",
    )

    assert tuned["m_score"] != base["m_score"]
    assert tuned["m_score"] < base["m_score"]

    audit = tuned["overrides_applied"].get("interaction")
    assert audit is not None
    assert audit["interaction_mode"] == "dynamic"
    assert audit["override_mode"] == "scale"
    assert audit["used"][0] == pytest.approx(0.7)


def test_tool_interaction_override_amplification_above_one():
    """Regression: interaction_override > 1.0 must not crash the kernel.

    Before the fix, INTERACTION_BOUNDS allowed up to 2.0 but
    mantic_kernel hard-rejected I > 1.0 with a ValueError.
    """
    from mantic_thinking.tools.friction.healthcare_phenotype_genotype import detect

    base = detect(phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8)
    amplified = detect(
        phenotypic=0.3,
        genomic=0.9,
        environmental=0.4,
        psychosocial=0.8,
        interaction_override={"psychosocial": 1.2},
        interaction_override_mode="scale",
    )

    # Amplifying a layer should increase the score
    assert amplified["m_score"] > base["m_score"]

    audit = amplified["overrides_applied"].get("interaction")
    assert audit is not None
    assert audit["used"][3] == pytest.approx(1.2)


def test_interaction_mode_base_is_audited_and_differs_when_dynamic_exists():
    from mantic_thinking.tools.emergence.finance_confluence_alpha import detect

    # Choose a flow value where the tool's dynamic I differs from base.
    args = dict(technical_setup=0.6, macro_tailwind=0.6, flow_positioning=0.0, risk_compression=0.6)

    dynamic = detect(**args)
    base = detect(**args, interaction_mode="base")

    assert dynamic["m_score"] != base["m_score"]

    audit = base["overrides_applied"].get("interaction")
    assert audit is not None
    assert audit["interaction_mode"] == "base"
    assert audit["requested"] is None

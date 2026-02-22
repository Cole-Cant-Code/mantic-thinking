"""
Tests for tool YAML guidance loading, reasoning scaffold, and
full context assembly for LLM system prompt injection.

Covers the three-stage load order: Scaffold → Domain Config → Tool Guidance.
"""

import pytest


class TestToolGuidanceLoading:
    """Core guidance loading from openai_adapter."""

    def test_load_all_tool_guidance(self):
        """All 16 built-in tools load without error."""
        from mantic_thinking.adapters.openai_adapter import get_tool_guidance

        result = get_tool_guidance()
        assert isinstance(result, str)
        assert len(result) > 0
        assert "## Tool Calibration Guidance" in result

    def test_load_single_tool(self):
        """Subset loading works for a single tool."""
        from mantic_thinking.adapters.openai_adapter import get_tool_guidance

        result = get_tool_guidance(["healthcare_phenotype_genotype"])
        assert "healthcare_phenotype_genotype" in result
        # Should NOT include other tools
        assert "finance_regime_conflict" not in result

    def test_load_multiple_tools(self):
        """Subset loading works for multiple tools."""
        from mantic_thinking.adapters.openai_adapter import get_tool_guidance

        result = get_tool_guidance([
            "healthcare_phenotype_genotype",
            "finance_confluence_alpha",
        ])
        assert "healthcare_phenotype_genotype" in result
        assert "finance_confluence_alpha" in result
        assert "cyber_attribution_resolver" not in result

    def test_unknown_tool_skipped(self):
        """Unknown tool names are silently skipped."""
        from mantic_thinking.adapters.openai_adapter import get_tool_guidance

        result = get_tool_guidance(["nonexistent_tool_xyz"])
        assert isinstance(result, str)
        assert "## Tool Calibration Guidance" in result
        # Should just have the header, no tool sections
        assert "nonexistent_tool_xyz" not in result

    def test_generic_detect_skipped(self):
        """generic_detect has no YAML and is silently skipped."""
        from mantic_thinking.adapters.openai_adapter import get_tool_guidance

        result = get_tool_guidance(["generic_detect"])
        assert isinstance(result, str)
        assert "generic_detect" not in result

    def test_all_16_tools_present(self):
        """All 16 built-in tool names appear in full guidance output."""
        from mantic_thinking.adapters.openai_adapter import get_tool_guidance

        result = get_tool_guidance()

        expected_tools = [
            "healthcare_phenotype_genotype",
            "finance_regime_conflict",
            "cyber_attribution_resolver",
            "climate_maladaptation",
            "legal_precedent_drift",
            "military_friction_forecast",
            "social_narrative_rupture",
            "system_lock_recursive_control",
            "healthcare_precision_therapeutic",
            "finance_confluence_alpha",
            "cyber_adversary_overreach",
            "climate_resilience_multiplier",
            "legal_precedent_seeding",
            "military_strategic_initiative",
            "social_catalytic_alignment",
            "system_lock_dissolution_window",
        ]

        for tool_name in expected_tools:
            assert tool_name in result, f"Missing tool: {tool_name}"


class TestGuidanceContent:
    """Verify guidance output contains expected structured content."""

    def test_guidance_contains_parameters(self):
        """Output includes parameter names from YAML."""
        from mantic_thinking.adapters.openai_adapter import get_tool_guidance

        result = get_tool_guidance(["healthcare_phenotype_genotype"])
        assert "phenotypic" in result
        assert "genomic" in result
        assert "environmental" in result
        assert "psychosocial" in result

    def test_guidance_contains_selection(self):
        """Output includes use_when and not_for from YAML."""
        from mantic_thinking.adapters.openai_adapter import get_tool_guidance

        result = get_tool_guidance(["healthcare_phenotype_genotype"])
        assert "**Use when:**" in result
        assert "**Not for:**" in result

    def test_guidance_contains_interpretation(self):
        """Output includes high/low M interpretation."""
        from mantic_thinking.adapters.openai_adapter import get_tool_guidance

        result = get_tool_guidance(["healthcare_phenotype_genotype"])
        assert "**High M:**" in result
        assert "**Low M:**" in result

    def test_guidance_contains_tuning(self):
        """Output includes dampen/amplify tuning guidance."""
        from mantic_thinking.adapters.openai_adapter import get_tool_guidance

        result = get_tool_guidance(["healthcare_phenotype_genotype"])
        assert "**Tuning:**" in result
        assert "Dampen" in result
        assert "Amplify" in result

    def test_guidance_contains_layer_mapping(self):
        """Output includes layer hierarchy (Micro/Meso/Macro/Meta)."""
        from mantic_thinking.adapters.openai_adapter import get_tool_guidance

        result = get_tool_guidance(["healthcare_phenotype_genotype"])
        assert "Micro" in result
        assert "Meso" in result

    def test_guidance_contains_tool_type(self):
        """Output includes friction/emergence type."""
        from mantic_thinking.adapters.openai_adapter import get_tool_guidance

        friction = get_tool_guidance(["healthcare_phenotype_genotype"])
        assert "friction" in friction

        emergence = get_tool_guidance(["finance_confluence_alpha"])
        assert "emergence" in emergence


class TestYamlLoading:
    """Test the internal YAML loader."""

    def test_load_friction_yaml(self):
        """Friction tool YAML loads successfully."""
        from mantic_thinking.adapters.openai_adapter import _load_tool_yaml

        data = _load_tool_yaml("healthcare_phenotype_genotype")
        assert data is not None
        assert data["tool"] == "healthcare_phenotype_genotype"
        assert data["type"] == "friction"
        assert data["domain"] == "healthcare"
        assert "parameters" in data
        assert "selection" in data

    def test_load_emergence_yaml(self):
        """Emergence tool YAML loads successfully."""
        from mantic_thinking.adapters.openai_adapter import _load_tool_yaml

        data = _load_tool_yaml("finance_confluence_alpha")
        assert data is not None
        assert data["tool"] == "finance_confluence_alpha"
        assert data["type"] == "emergence"
        assert data["domain"] == "finance"

    def test_load_nonexistent_returns_none(self):
        """Non-existent tool returns None."""
        from mantic_thinking.adapters.openai_adapter import _load_tool_yaml

        data = _load_tool_yaml("nonexistent_tool")
        assert data is None


class TestAdapterWrappers:
    """Verify all adapters expose the guidance function."""

    def test_claude_adapter_has_guidance(self):
        """Claude adapter exposes get_claude_tool_guidance."""
        from mantic_thinking.adapters.claude_adapter import get_claude_tool_guidance

        result = get_claude_tool_guidance()
        assert isinstance(result, str)
        assert "## Tool Calibration Guidance" in result

    def test_gemini_adapter_has_guidance(self):
        """Gemini adapter exposes get_gemini_tool_guidance."""
        from mantic_thinking.adapters.gemini_adapter import get_gemini_tool_guidance

        result = get_gemini_tool_guidance()
        assert isinstance(result, str)
        assert "## Tool Calibration Guidance" in result

    def test_kimi_adapter_has_guidance(self):
        """Kimi adapter exposes get_kimi_tool_guidance."""
        from mantic_thinking.adapters.kimi_adapter import get_kimi_tool_guidance

        result = get_kimi_tool_guidance()
        assert isinstance(result, str)
        assert "## Tool Calibration Guidance" in result

    def test_all_adapters_return_same_content(self):
        """All adapter wrappers return identical content for same input."""
        from mantic_thinking.adapters.claude_adapter import get_claude_tool_guidance
        from mantic_thinking.adapters.gemini_adapter import get_gemini_tool_guidance
        from mantic_thinking.adapters.kimi_adapter import get_kimi_tool_guidance

        claude = get_claude_tool_guidance(["healthcare_phenotype_genotype"])
        gemini = get_gemini_tool_guidance(["healthcare_phenotype_genotype"])
        kimi = get_kimi_tool_guidance(["healthcare_phenotype_genotype"])

        assert claude == gemini == kimi

    def test_adapter_subset_loading(self):
        """Adapter wrappers support subset loading."""
        from mantic_thinking.adapters.claude_adapter import get_claude_tool_guidance

        result = get_claude_tool_guidance(["cyber_attribution_resolver"])
        assert "cyber_attribution_resolver" in result
        assert "healthcare_phenotype_genotype" not in result


class TestScaffold:
    """Test the reasoning scaffold loader."""

    def test_scaffold_loads(self):
        """Scaffold file loads successfully."""
        from mantic_thinking.adapters.openai_adapter import get_scaffold

        result = get_scaffold()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_scaffold_contains_formula(self):
        """Scaffold includes the core formula."""
        from mantic_thinking.adapters.openai_adapter import get_scaffold

        result = get_scaffold()
        assert "M =" in result

    def test_scaffold_contains_layer_hierarchy(self):
        """Scaffold includes the 4-layer hierarchy."""
        from mantic_thinking.adapters.openai_adapter import get_scaffold

        result = get_scaffold()
        assert "Micro" in result
        assert "Meso" in result
        assert "Macro" in result
        assert "Meta" in result

    def test_scaffold_contains_modes(self):
        """Scaffold explains friction and emergence modes."""
        from mantic_thinking.adapters.openai_adapter import get_scaffold

        result = get_scaffold()
        assert "Friction" in result
        assert "Emergence" in result

    def test_scaffold_contains_translation_rules(self):
        """Scaffold includes translation guidance."""
        from mantic_thinking.adapters.openai_adapter import get_scaffold

        result = get_scaffold()
        assert "What You Think" in result or "Translation" in result

    def test_scaffold_contains_load_order(self):
        """Scaffold references the load order."""
        from mantic_thinking.adapters.openai_adapter import get_scaffold

        result = get_scaffold()
        assert "Scaffold" in result
        assert "Domain Config" in result
        assert "Tool Guidance" in result


class TestDomainConfig:
    """Test domain config loading."""

    def test_load_healthcare_config(self):
        """Healthcare domain config loads."""
        from mantic_thinking.adapters.openai_adapter import get_domain_config

        result = get_domain_config("healthcare")
        assert isinstance(result, str)
        assert "Mantic-Health" in result or "Clinical" in result

    def test_load_finance_config(self):
        """Finance domain config loads."""
        from mantic_thinking.adapters.openai_adapter import get_domain_config

        result = get_domain_config("finance")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_load_cyber_config(self):
        """Cyber domain config loads (maps to security)."""
        from mantic_thinking.adapters.openai_adapter import get_domain_config

        result = get_domain_config("cyber")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_unknown_domain_returns_empty(self):
        """Unknown domain returns empty string."""
        from mantic_thinking.adapters.openai_adapter import get_domain_config

        result = get_domain_config("nonexistent_domain")
        assert result == ""


class TestFullContext:
    """Test the full context assembly (Scaffold → Config → Guidance)."""

    def test_full_context_no_domain(self):
        """Full context without domain includes scaffold + all tools."""
        from mantic_thinking.adapters.openai_adapter import get_full_context

        result = get_full_context()
        assert "Mantic Reasoning Scaffold" in result
        assert "## Tool Calibration Guidance" in result
        # Should include all built-in domain tools
        assert "healthcare_phenotype_genotype" in result
        assert "finance_confluence_alpha" in result

    def test_full_context_with_domain(self):
        """Full context with domain includes scaffold + domain config + scoped tools."""
        from mantic_thinking.adapters.openai_adapter import get_full_context

        result = get_full_context("healthcare")
        # Stage 1: Scaffold
        assert "Mantic Reasoning Scaffold" in result
        # Stage 2: Domain config
        assert "Mantic-Health" in result or "Clinical" in result
        # Stage 3: Scoped tool guidance (only healthcare tools)
        assert "healthcare_phenotype_genotype" in result
        assert "healthcare_precision_therapeutic" in result
        # Should NOT include other domain tools
        assert "finance_regime_conflict" not in result

    def test_full_context_order(self):
        """Scaffold appears before tool guidance in output."""
        from mantic_thinking.adapters.openai_adapter import get_full_context

        result = get_full_context()
        scaffold_pos = result.find("Mantic Reasoning Scaffold")
        guidance_pos = result.find("## Tool Calibration Guidance")
        assert scaffold_pos < guidance_pos

    def test_all_adapters_expose_context(self):
        """All adapters expose get_*_context()."""
        from mantic_thinking.adapters.claude_adapter import get_claude_context
        from mantic_thinking.adapters.gemini_adapter import get_gemini_context
        from mantic_thinking.adapters.kimi_adapter import get_kimi_context

        claude = get_claude_context("finance")
        gemini = get_gemini_context("finance")
        kimi = get_kimi_context("finance")

        assert claude == gemini == kimi
        assert "Mantic Reasoning Scaffold" in claude
        assert "finance" in claude.lower()


class TestCodexFixes:
    """Regression tests for Codex review findings."""

    def test_cybersecurity_alias_scopes_tools(self):
        """'cybersecurity' alias scopes to cyber tools only."""
        from mantic_thinking.adapters.openai_adapter import get_full_context

        result = get_full_context("cybersecurity")
        assert "cyber_attribution_resolver" in result
        assert "finance_regime_conflict" not in result

    def test_health_alias_scopes_tools(self):
        """'health' alias scopes to healthcare tools only."""
        from mantic_thinking.adapters.openai_adapter import get_full_context

        result = get_full_context("health")
        assert "healthcare_phenotype_genotype" in result
        assert "finance_regime_conflict" not in result

    def test_security_alias_scopes_tools(self):
        """'security' alias scopes to cyber tools only."""
        from mantic_thinking.adapters.openai_adapter import get_full_context

        result = get_full_context("security")
        assert "cyber_attribution_resolver" in result
        assert "healthcare_phenotype_genotype" not in result

    def test_command_alias_scopes_tools(self):
        """'command' alias scopes to military tools only."""
        from mantic_thinking.adapters.openai_adapter import get_full_context

        result = get_full_context("command")
        assert "military_friction_forecast" in result
        assert "finance_regime_conflict" not in result

    def test_path_traversal_filtered(self):
        """Path traversal in tool_names is filtered out."""
        from mantic_thinking.adapters.openai_adapter import get_tool_guidance

        result = get_tool_guidance(["../../etc/passwd", "healthcare_phenotype_genotype"])
        assert "healthcare_phenotype_genotype" in result
        assert "passwd" not in result

    def test_all_invalid_tool_names_filtered(self):
        """All-invalid tool_names returns header only."""
        from mantic_thinking.adapters.openai_adapter import get_tool_guidance

        result = get_tool_guidance(["../../../etc/shadow", "__import__('os')"])
        assert "## Tool Calibration Guidance" in result
        assert "shadow" not in result
        assert "import" not in result

    def test_malformed_yaml_skipped(self):
        """Malformed YAML doesn't crash guidance loading."""
        from mantic_thinking.adapters.openai_adapter import _load_tool_yaml

        # Non-existent tool returns None gracefully
        assert _load_tool_yaml("nonexistent") is None

"""
Mantic Early Warning System - Domain Tools

Two complementary suites:
- Friction Tools (7): Detect cross-layer conflicts and mismatches
- Emergence Tools (7): Detect alignment windows and opportunities

Friction Tools:
- healthcare_phenotype_genotype: Phenotype-Genotype Mismatch Detector
- finance_regime_conflict: Regime Conflict Monitor
- cyber_attribution_resolver: Attribution Uncertainty Resolver
- climate_maladaptation: Maladaptation Preventer
- legal_precedent_drift: Precedent Drift Alert
- military_friction_forecast: Friction Forecast Engine
- social_narrative_rupture: Narrative Rupture Detector

Emergence (Confluence) Tools:
- healthcare_precision_therapeutic: Precision Therapeutic Window
- finance_confluence_alpha: Confluence Alpha Engine
- cyber_adversary_overreach: Adversary Overreach Detector
- climate_resilience_multiplier: Resilience Multiplier
- legal_precedent_seeding: Precedent Seeding Optimizer
- military_strategic_initiative: Strategic Initiative Window
- social_catalytic_alignment: Catalytic Alignment Detector
"""

import importlib

_TOOL_MODULES = {
    # Friction
    "healthcare_phenotype_genotype": "mantic_thinking.tools.friction.healthcare_phenotype_genotype",
    "finance_regime_conflict": "mantic_thinking.tools.friction.finance_regime_conflict",
    "cyber_attribution_resolver": "mantic_thinking.tools.friction.cyber_attribution_resolver",
    "climate_maladaptation": "mantic_thinking.tools.friction.climate_maladaptation",
    "legal_precedent_drift": "mantic_thinking.tools.friction.legal_precedent_drift",
    "military_friction_forecast": "mantic_thinking.tools.friction.military_friction_forecast",
    "social_narrative_rupture": "mantic_thinking.tools.friction.social_narrative_rupture",
    # Emergence
    "healthcare_precision_therapeutic": "mantic_thinking.tools.emergence.healthcare_precision_therapeutic",
    "finance_confluence_alpha": "mantic_thinking.tools.emergence.finance_confluence_alpha",
    "cyber_adversary_overreach": "mantic_thinking.tools.emergence.cyber_adversary_overreach",
    "climate_resilience_multiplier": "mantic_thinking.tools.emergence.climate_resilience_multiplier",
    "legal_precedent_seeding": "mantic_thinking.tools.emergence.legal_precedent_seeding",
    "military_strategic_initiative": "mantic_thinking.tools.emergence.military_strategic_initiative",
    "social_catalytic_alignment": "mantic_thinking.tools.emergence.social_catalytic_alignment",
}


def __getattr__(name):
    """
    Lazy-load tool modules on first access.

    This keeps `import mantic_thinking.tools` lightweight while still supporting:
      - `from mantic_thinking.tools import healthcare_phenotype_genotype`
      - `mantic_thinking.tools.healthcare_phenotype_genotype.detect(...)`
    """
    if name in _TOOL_MODULES:
        module = importlib.import_module(_TOOL_MODULES[name])
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(list(globals().keys()) + list(_TOOL_MODULES.keys())))


__all__ = [
    # Friction
    "healthcare_phenotype_genotype",
    "finance_regime_conflict",
    "cyber_attribution_resolver",
    "climate_maladaptation",
    "legal_precedent_drift",
    "military_friction_forecast",
    "social_narrative_rupture",
    # Emergence
    "healthcare_precision_therapeutic",
    "finance_confluence_alpha",
    "cyber_adversary_overreach",
    "climate_resilience_multiplier",
    "legal_precedent_seeding",
    "military_strategic_initiative",
    "social_catalytic_alignment",
]

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

# Friction tools
from .friction import healthcare_phenotype_genotype
from .friction import finance_regime_conflict
from .friction import cyber_attribution_resolver
from .friction import climate_maladaptation
from .friction import legal_precedent_drift
from .friction import military_friction_forecast
from .friction import social_narrative_rupture

# Emergence tools
from .emergence import healthcare_precision_therapeutic
from .emergence import finance_confluence_alpha
from .emergence import cyber_adversary_overreach
from .emergence import climate_resilience_multiplier
from .emergence import legal_precedent_seeding
from .emergence import military_strategic_initiative
from .emergence import social_catalytic_alignment

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

# NOTE: Internal tools (codebase analysis) exist in subpackages but are NOT exported here.
# Import directly if needed: from tools.friction.codebase_layer_conflict import detect
# These are for self-analysis only and not part of the public API.

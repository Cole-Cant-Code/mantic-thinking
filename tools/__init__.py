"""
Mantic Early Warning System - Domain Tools

Two complementary suites:
- Friction Tools (8): Detect cross-layer conflicts and mismatches
- Emergence Tools (8): Detect alignment windows and opportunities

Friction Tools:
- healthcare_phenotype_genotype: Phenotype-Genotype Mismatch Detector
- finance_regime_conflict: Regime Conflict Monitor
- cyber_attribution_resolver: Attribution Uncertainty Resolver
- climate_maladaptation: Maladaptation Preventer
- legal_precedent_drift: Precedent Drift Alert
- military_friction_forecast: Friction Forecast Engine
- social_narrative_rupture: Narrative Rupture Detector
- codebase_layer_conflict: Codebase Layer Conflict Detector

Emergence (Confluence) Tools:
- healthcare_precision_therapeutic: Precision Therapeutic Window
- finance_confluence_alpha: Confluence Alpha Engine
- cyber_adversary_overreach: Adversary Overreach Detector
- climate_resilience_multiplier: Resilience Multiplier
- legal_precedent_seeding: Precedent Seeding Optimizer
- military_strategic_initiative: Strategic Initiative Window
- social_catalytic_alignment: Catalytic Alignment Detector
- codebase_alignment_window: Codebase Alignment Window Detector
"""

# Friction tools
from .friction import healthcare_phenotype_genotype
from .friction import finance_regime_conflict
from .friction import cyber_attribution_resolver
from .friction import climate_maladaptation
from .friction import legal_precedent_drift
from .friction import military_friction_forecast
from .friction import social_narrative_rupture
from .friction import codebase_layer_conflict

# Emergence tools
from .emergence import healthcare_precision_therapeutic
from .emergence import finance_confluence_alpha
from .emergence import cyber_adversary_overreach
from .emergence import climate_resilience_multiplier
from .emergence import legal_precedent_seeding
from .emergence import military_strategic_initiative
from .emergence import social_catalytic_alignment
from .emergence import codebase_alignment_window

__all__ = [
    # Friction
    "healthcare_phenotype_genotype",
    "finance_regime_conflict",
    "cyber_attribution_resolver",
    "climate_maladaptation",
    "legal_precedent_drift",
    "military_friction_forecast",
    "social_narrative_rupture",
    "codebase_layer_conflict",
    # Emergence
    "healthcare_precision_therapeutic",
    "finance_confluence_alpha",
    "cyber_adversary_overreach",
    "climate_resilience_multiplier",
    "legal_precedent_seeding",
    "military_strategic_initiative",
    "social_catalytic_alignment",
    "codebase_alignment_window",
]

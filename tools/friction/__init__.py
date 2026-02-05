"""
Mantic Early Warning System - Friction Tools

These tools detect cross-layer conflicts and mismatches
when layers diverge or contradict each other.

Logic Pattern: if abs(L1 - L2) > 0.5: alert()
"""

from . import healthcare_phenotype_genotype
from . import finance_regime_conflict
from . import cyber_attribution_resolver
from . import climate_maladaptation
from . import legal_precedent_drift
from . import military_friction_forecast
from . import social_narrative_rupture
from . import codebase_layer_conflict

__all__ = [
    "healthcare_phenotype_genotype",
    "finance_regime_conflict",
    "cyber_attribution_resolver",
    "climate_maladaptation",
    "legal_precedent_drift",
    "military_friction_forecast",
    "social_narrative_rupture",
    "codebase_layer_conflict",
]

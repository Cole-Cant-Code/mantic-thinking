"""
Mantic Early Warning System - Emergence (Confluence) Tools

These tools detect alignment windows and high-leverage opportunities
when multiple layers synchronize favorably.

Logic Pattern: if all(L > 0.6 for L in layers): window_detected()
"""

from . import healthcare_precision_therapeutic
from . import finance_confluence_alpha
from . import cyber_adversary_overreach
from . import climate_resilience_multiplier
from . import legal_precedent_seeding
from . import military_strategic_initiative
from . import social_catalytic_alignment
from . import codebase_alignment_window

__all__ = [
    "healthcare_precision_therapeutic",
    "finance_confluence_alpha",
    "cyber_adversary_overreach",
    "climate_resilience_multiplier",
    "legal_precedent_seeding",
    "military_strategic_initiative",
    "social_catalytic_alignment",
    "codebase_alignment_window",
]

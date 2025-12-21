"""
Synergy Handlers: Cross-jewel event processors.

Each handler responds to specific synergy events and creates
appropriate artifacts in the target jewel.

Wave 0-1 handlers:
- GestaltToBrainHandler: Captures architecture snapshots to Brain

Wave 2 handlers (Extensions):
- AtelierToBrainHandler: Captures Atelier pieces to Brain
- CoalitionToBrainHandler: Captures Coalition task results to Brain
- BrainToCoalitionHandler: Enriches Coalition formation with context

Wave 3 handlers (Tier 3 - Full Integration):
- DomainToBrainHandler: Captures drill results to Brain
- ParkToBrainHandler: Captures scenario results to Brain

Witness handlers (8th Crown Jewel):
- WitnessToBrainHandler: Captures thoughts and commits to Brain

Note: Garden handlers deprecated 2025-12-21. See:
  spec/protocols/_archive/gardener-evergreen-heritage.md
"""

from .atelier_brain import AtelierToBrainHandler
from .base import BaseSynergyHandler
from .coalition_brain import BrainToCoalitionHandler, CoalitionToBrainHandler
from .domain_brain import DomainToBrainHandler, ParkToBrainHandler
from .gestalt_brain import GestaltToBrainHandler
from .witness_brain import WitnessToBrainHandler

__all__ = [
    # Base
    "BaseSynergyHandler",
    # Wave 0-1: Hero Path
    "GestaltToBrainHandler",
    # Wave 2: Extensions
    "AtelierToBrainHandler",
    "CoalitionToBrainHandler",
    "BrainToCoalitionHandler",
    # Wave 3: Tier 3 (Full Integration)
    "DomainToBrainHandler",
    "ParkToBrainHandler",
    # Witness (8th Crown Jewel)
    "WitnessToBrainHandler",
]

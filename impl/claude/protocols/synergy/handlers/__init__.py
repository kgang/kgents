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

Wave 4 handlers (Gardener-Logos Phase 6):
- GardenToBrainHandler: Captures garden state changes to Brain
- GestaltToGardenHandler: Updates garden plots when Gestalt analyzes

Witness handlers (8th Crown Jewel):
- WitnessToBrainHandler: Captures thoughts and commits to Brain
- WitnessToGardenHandler: Updates plots when commits detected

Self.Garden Phase 2:
- GardenToWitnessHandler: Forwards garden gestures to Witness thought stream
"""

from .atelier_brain import AtelierToBrainHandler
from .base import BaseSynergyHandler
from .coalition_brain import BrainToCoalitionHandler, CoalitionToBrainHandler
from .domain_brain import DomainToBrainHandler, ParkToBrainHandler
from .garden_brain import GardenToBrainHandler
from .garden_witness import GardenToWitnessHandler
from .gestalt_brain import GestaltToBrainHandler
from .gestalt_garden import GestaltToGardenHandler
from .witness_brain import WitnessToBrainHandler
from .witness_garden import WitnessToGardenHandler

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
    # Wave 4: Garden (Gardener-Logos Phase 6)
    "GardenToBrainHandler",
    "GestaltToGardenHandler",
    # Witness (8th Crown Jewel)
    "WitnessToBrainHandler",
    "WitnessToGardenHandler",
    # Self.Garden Phase 2
    "GardenToWitnessHandler",
]

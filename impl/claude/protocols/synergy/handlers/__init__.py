"""
Synergy Handlers: Cross-jewel event processors.

Each handler responds to specific synergy events and creates
appropriate artifacts in the target jewel.

Current handlers:
- GestaltToBrainHandler: Captures architecture snapshots to Brain
- GardenerToBrainHandler: Captures session learnings to Brain
- BrainToGardenerHandler: Surfaces relevant crystals as context
"""

from .base import BaseSynergyHandler
from .gestalt_brain import GestaltToBrainHandler

__all__ = [
    "BaseSynergyHandler",
    "GestaltToBrainHandler",
]

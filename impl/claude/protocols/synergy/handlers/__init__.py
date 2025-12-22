"""
Synergy Handlers: Cross-jewel event processors.

Each handler responds to specific synergy events and creates
appropriate artifacts in the target jewel.

Witness handlers (8th Crown Jewel):
- WitnessToBrainHandler: Captures thoughts and commits to Brain

Note: Gestalt, Coalition, Domain, Park handlers removed 2025-12-21.
Note: Garden handlers deprecated 2025-12-21. See:
  spec/protocols/_archive/gardener-evergreen-heritage.md
Note: Atelier handlers removed 2025-12-21.
"""

from .base import BaseSynergyHandler
from .witness_brain import WitnessToBrainHandler

__all__ = [
    # Base
    "BaseSynergyHandler",
    # Witness (8th Crown Jewel)
    "WitnessToBrainHandler",
]

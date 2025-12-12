"""
Metabolic Engine: The thermodynamic heart of kgents.

The metabolism subsystem tracks activity-based pressure and triggers
creative "fever" events when the system runs hot.

The Accursed Share: surplus must be spent, not suppressed.

Exports:
- MetabolicEngine: Pressure tracking and fever triggers
- FeverEvent: Record of a fever trigger
- FeverStream: Oblique strategies and fever dreams
- create_metabolic_engine: Factory function
- get_metabolic_engine: Global singleton accessor
"""

from .engine import (
    MetabolicEngine,
    create_metabolic_engine,
    get_metabolic_engine,
    set_global_engine,
)
from .fever import FeverEvent, FeverStream

__all__ = [
    "MetabolicEngine",
    "FeverEvent",
    "FeverStream",
    "create_metabolic_engine",
    "get_metabolic_engine",
    "set_global_engine",
]

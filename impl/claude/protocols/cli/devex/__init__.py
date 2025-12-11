"""
DevEx: Developer Experience utilities for kgents.

This module implements feedback loops for the Exocortex Symbiosis:

Meta-Bootstrap (self-observation):
- hydrate_signal: Append events to HYDRATE.md
- flinch_store: D-gent backed test failure storage

DevEx V4 Phase 2 (Sensorium):
- ghost_writer: Living Filesystem projection to .kgents/ghost/
"""

from .flinch_store import Flinch, FlinchStore, get_flinch_store
from .ghost_writer import GhostWriter, create_ghost_writer, project_once
from .hydrate_signal import HydrateEvent, append_hydrate_signal

__all__ = [
    # Meta-Bootstrap
    "append_hydrate_signal",
    "HydrateEvent",
    "Flinch",
    "FlinchStore",
    "get_flinch_store",
    # DevEx V4 Phase 2
    "GhostWriter",
    "create_ghost_writer",
    "project_once",
]

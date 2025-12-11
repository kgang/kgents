"""
DevEx: Developer Experience utilities for kgents meta-bootstrap.

This module implements cheap feedback loops that let the system
observe itself during development.

Loops implemented:
- hydrate_signal: Append events to HYDRATE.md
- (future: ghost_writer, flinch, rituals)
"""

from .hydrate_signal import HydrateEvent, append_hydrate_signal

__all__ = ["append_hydrate_signal", "HydrateEvent"]

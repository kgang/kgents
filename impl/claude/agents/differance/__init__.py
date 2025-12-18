"""
Différance Engine: Traced Wiring Diagrams with Ghost Heritage.

Every kgents output has a lineage—decisions made, alternatives rejected, paths
not taken. The Différance Engine makes this lineage visible, navigable, and
generative.

Core Insight:
    Différance = difference + deferral. Every wiring decision simultaneously:
    1. Creates a difference (this path, not that one)
    2. Creates a deferral (the ghost path remains potentially explorable)

The trace monoid records both: what was chosen AND what was deferred.

See: spec/protocols/differance.md
"""

from __future__ import annotations

from .store import DifferanceStore
from .trace import (
    Alternative,
    TraceMonoid,
    WiringTrace,
)

__all__ = [
    # Core Types
    "Alternative",
    "WiringTrace",
    "TraceMonoid",
    # Storage
    "DifferanceStore",
]

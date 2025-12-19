"""
Umwelt Protocol: Agent-Specific World Projection.

.. deprecated::
    This module is deprecated. Import from agents.poly.umwelt instead.

    Migration:
        from bootstrap.umwelt import Umwelt, Projector
        →
        from agents.poly.umwelt import Umwelt, Projector

Re-exports from agents.poly.umwelt for backward compatibility.
No deprecation warning emitted—pure re-exports maintain compatibility.
"""

# Re-export everything from the new location
from agents.poly.umwelt import (
    Contract,
    GroundingError,
    HypotheticalProjector,
    LightweightUmwelt,
    Projector,
    TemporalLens,
    TemporalProjector,
    Umwelt,
)

__all__ = [
    "Contract",
    "GroundingError",
    "HypotheticalProjector",
    "LightweightUmwelt",
    "Projector",
    "TemporalLens",
    "TemporalProjector",
    "Umwelt",
]

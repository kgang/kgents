"""
Gestalt Agent: Architecture Visualization as Dynamical System.

The gestalt polynomial models codebase architecture analysis as a state machine:
- IDLE: Ready for analysis operations
- SCANNING: Full codebase analysis in progress
- WATCHING: Live file watching mode (incremental updates)
- ANALYZING: Deep analysis on specific module or region
- HEALING: Architecture drift repair suggestions

The Insight:
    Architecture is not static documentation—it is a living garden.
    Each scan reconstitutes the codebase's gestalt (wholeness).
    The graph emerges from observation, not retrieval.

Crown Jewel: world.codebase (Gestalt Architecture Visualizer)
Vision: "Living garden where code breathes"

See: plans/core-apps/gestalt-architecture-visualizer.md
See: docs/skills/vertical-slice-pattern.md
"""

from .operad import GESTALT_OPERAD, create_gestalt_operad
from .polynomial import (
    GESTALT_POLYNOMIAL,
    AnalyzeInput,
    GestaltInput,
    GestaltOutput,
    GestaltPhase,
    HealInput,
    IdleInput,
    ScanInput,
    WatchInput,
    gestalt_directions,
    gestalt_transition,
)

__all__ = [
    # Phase
    "GestaltPhase",
    # Inputs
    "ScanInput",
    "WatchInput",
    "AnalyzeInput",
    "HealInput",
    "IdleInput",
    "GestaltInput",
    # Outputs
    "GestaltOutput",
    # Functions
    "gestalt_directions",
    "gestalt_transition",
    # Polynomial
    "GESTALT_POLYNOMIAL",
    # Operad
    "GESTALT_OPERAD",
    "create_gestalt_operad",
]

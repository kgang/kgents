"""I-gent v2.5 Screens - Generative TUI at different LOD levels."""

from .cockpit import CockpitScreen, create_demo_snapshot
from .flux import FluxScreen
from .loom import LoomScreen, create_demo_cognitive_tree
from .mri import MRIScreen

__all__ = [
    # LOD Level 0: ORBIT - Agent cards overview
    "FluxScreen",
    # LOD Level 1: SURFACE - Operational cockpit view
    "CockpitScreen",
    "create_demo_snapshot",
    # LOD Level 2: INTERNAL - Deep agent inspection
    "MRIScreen",
    # Cognitive Loom - Temporal navigation (branching history)
    "LoomScreen",
    "create_demo_cognitive_tree",
]

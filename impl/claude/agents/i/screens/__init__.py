"""I-gent v2.5 Screens - Generative TUI at different LOD levels."""

# Base classes for screen inheritance
from .base import KgentsModalScreen, KgentsScreen

# Screen implementations
from .cockpit import CockpitScreen, create_demo_snapshot
from .debugger_screen import DebuggerScreen
from .flux import FluxScreen
from .loom import LoomScreen, create_demo_cognitive_tree
from .memory_map import (
    LanguageGameWidget,
    MemoryCrystalWidget,
    MemoryMapScreen,
    PheromoneFieldWidget,
)

# Mixins for DashboardApp decomposition
from .mixins import (
    DashboardHelpMixin,
    DashboardNavigationMixin,
    DashboardScreensMixin,
)
from .mri import MRIScreen
from .observatory import ObservatoryScreen
from .substrate import SubstrateScreen, create_substrate_screen
from .terrarium import TerrariumScreen

# Transition system for gentle eye navigation
from .transitions import GentleNavigator, ScreenTransition, TransitionStyle

__all__ = [
    # Base classes
    "KgentsScreen",
    "KgentsModalScreen",
    # Transition system
    "TransitionStyle",
    "ScreenTransition",
    "GentleNavigator",
    # Mixins
    "DashboardNavigationMixin",
    "DashboardScreensMixin",
    "DashboardHelpMixin",
    # LOD Level -1: ORBITAL - Ecosystem view (all gardens)
    "ObservatoryScreen",
    # LOD Level 0: SURFACE - Single garden (Terrarium) or Flux
    "TerrariumScreen",
    "FluxScreen",
    # LOD Level 1: COCKPIT - Operational agent view
    "CockpitScreen",
    "create_demo_snapshot",
    # LOD Level 2: INTERNAL - Deep agent inspection
    "MRIScreen",
    "DebuggerScreen",
    # Cognitive Loom - Temporal navigation (branching history)
    "LoomScreen",
    "create_demo_cognitive_tree",
    # Memory Map - Four Pillars visualization
    "MemoryMapScreen",
    "MemoryCrystalWidget",
    "PheromoneFieldWidget",
    "LanguageGameWidget",
    # Substrate Dashboard - Allocation and routing visualization
    "SubstrateScreen",
    "create_substrate_screen",
]

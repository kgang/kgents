"""
Reactive Screens: Full-screen compositions that tell the story.

Screens are the "ecosystems" of our visual language. They compose:
- Cards (AgentCard, YieldCard) as "organisms"
- Primitives (Glyph, Bar, Sparkline, DensityField) as building blocks

Wave 4: DashboardScreen, ForgeScreen, DebuggerScreen

"The glyph is the atom. The bar is a sentence. The card is a paragraph. The screen is the story."
"""

from agents.i.reactive.screens.dashboard import DashboardScreen, DashboardScreenState
from agents.i.reactive.screens.debugger import DebuggerScreen, DebuggerScreenState
from agents.i.reactive.screens.forge import ForgeScreen, ForgeScreenState

__all__ = [
    # Dashboard
    "DashboardScreen",
    "DashboardScreenState",
    # Forge
    "ForgeScreen",
    "ForgeScreenState",
    # Debugger
    "DebuggerScreen",
    "DebuggerScreenState",
]

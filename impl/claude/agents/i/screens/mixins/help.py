"""
Help and documentation overlays for DashboardApp.

This mixin extracts all help-related actions from DashboardApp,
providing a clean separation for user assistance and keybinding reference.

Philosophy: Help should be discoverable and context-aware.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class DashboardHelpMixin:
    """Help and documentation overlays.

    This mixin handles:
    - Main help overlay (navigation guide)
    - Keybindings reference
    - Context-sensitive help

    Expects the implementing class to have:
    - self.notify(message, timeout): method to show notifications (from App)
    """

    # ========================================================================
    # Help Actions
    # ========================================================================

    def action_show_help(self) -> None:
        """Show help overlay (?).

        Displays comprehensive navigation guide with:
        - Zoom controls
        - Screen shortcuts
        - LOD level descriptions
        - General keybindings
        """
        from typing import Any, cast

        help_text = """
DASHBOARD NAVIGATION

Zoom:
  +/=  - Zoom in (more detail)
  -/_  - Zoom out (broader view)

Screens:
  1-6  - Jump to specific screen
  f    - Open Forge (agent composition)
  d    - Open Debugger (turn analysis)
  m    - Open Memory Map

Other:
  ?    - Show this help
  q    - Quit

LOD Levels:
  1    - Observatory (ecosystem view)
  2    - Dashboard (system health)
  3    - Cockpit (single agent)
  4-6  - Flux / Loom / MRI
"""
        # Cast self to have notify method from App
        cast(Any, self).notify(help_text, timeout=10)

    def action_show_keybindings(self) -> None:
        """Show keybindings reference.

        Displays a comprehensive list of all available keybindings
        organized by category.
        """
        from typing import Any, cast

        keybindings_text = """
KEYBINDINGS REFERENCE

Navigation:
  +/=       - Zoom in (increase detail)
  -/_       - Zoom out (decrease detail)
  1-6       - Jump to specific screen
  Tab       - Cycle to next screen

Screens:
  f         - Forge (composition)
  d         - Debugger (forensics)
  m         - Memory Map

System:
  ?         - Show help
  q         - Quit application
  r         - Refresh (if available)
"""
        cast(Any, self).notify(keybindings_text, timeout=15)

    def action_show_lod_info(self) -> None:
        """Show information about LOD levels.

        Displays detailed explanation of the Level of Detail system
        and what each level represents.
        """
        from typing import Any, cast

        lod_info = """
LEVEL OF DETAIL (LOD) SYSTEM

The dashboard uses a zoom-based navigation model inspired
by cartography: different levels of detail reveal different
aspects of the system.

  Key 1: Observatory
    Ecosystem view - all agents, gardens, flux state.
    Like viewing a city from orbit.

  Key 2: Dashboard
    System health - metabolism, triad, traces.
    Like viewing a neighborhood from above.

  Key 3: Cockpit
    Single agent focus - state, actions, config.
    Like viewing a single building.

  Key 4-6: Flux / Loom / MRI
    Detailed views - event streams, patterns, memory.
    Like viewing inside a single room.

Special Screens (Non-LOD):
  - Forge (f): Agent composition studio
  - Debugger (d): Turn DAG, execution traces
  - Memory Map (m): Four Pillars visualization

Use +/- to zoom, or number keys for direct access.
"""
        cast(Any, self).notify(lod_info, timeout=20)


__all__ = ["DashboardHelpMixin"]

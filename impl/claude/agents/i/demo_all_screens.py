"""
Demo All Screens - Interactive demo of all LOD levels.

Run with: uv run python impl/claude/agents/i/demo_all_screens.py

Navigation:
  1: Show FluxScreen (LOD 0: ORBIT)
  2: Show CockpitScreen (LOD 1: SURFACE)
  3: Show MRIScreen (LOD 2: INTERNAL)
  4: Show LoomScreen (Cognitive Loom)
  q: Quit
"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from agents.i.data.state import create_demo_flux_state
from agents.i.screens.cockpit import CockpitScreen, create_demo_snapshot
from agents.i.screens.flux import FluxScreen
from agents.i.screens.loom import LoomScreen
from agents.i.screens.mri import MRIScreen


class MenuScreen(Screen[None]):
    """Main menu for selecting demo screens."""

    CSS = """
    MenuScreen {
        background: #1a1a1a;
    }

    MenuScreen #menu {
        width: 100%;
        height: 100%;
        align: center middle;
        padding: 2;
    }

    MenuScreen .title {
        text-style: bold;
        color: #f5d08a;
        text-align: center;
        margin-bottom: 2;
    }

    MenuScreen .subtitle {
        color: #b3a89a;
        text-align: center;
        margin-bottom: 2;
    }

    MenuScreen .menu-item {
        color: #f5f0e6;
        margin: 1 0;
    }

    MenuScreen .hint {
        color: #6a6560;
        margin-top: 2;
        text-align: center;
    }
    """

    BINDINGS = [
        Binding("1", "show_flux", "FluxScreen"),
        Binding("2", "show_cockpit", "CockpitScreen"),
        Binding("3", "show_mri", "MRIScreen"),
        Binding("4", "show_loom", "LoomScreen"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           ALETHIC WORKBENCH - SCREEN DEMO                    ║
║                                                              ║
║     "Don't just look at the agent. Look THROUGH the agent."  ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   [1]  FluxScreen    (LOD 0: ORBIT)     Agent Cards Overview ║
║   [2]  CockpitScreen (LOD 1: SURFACE)   Operational View     ║
║   [3]  MRIScreen     (LOD 2: INTERNAL)  Deep Inspection      ║
║   [4]  LoomScreen    (Temporal)         Cognitive Loom       ║
║                                                              ║
║   [q]  Quit                                                  ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   Press a number key to view a screen.                       ║
║   Press Escape to return to this menu from any screen.       ║
║                                                              ║
║   All screens are running in demo mode with sample data.     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""",
            id="menu",
        )
        yield Footer()

    def action_show_flux(self) -> None:
        """Show FluxScreen (LOD 0)."""
        state = create_demo_flux_state()
        self.app.push_screen(FluxScreen(state=state, demo_mode=True))

    def action_show_cockpit(self) -> None:
        """Show CockpitScreen (LOD 1)."""
        snapshot = create_demo_snapshot()
        self.app.push_screen(
            CockpitScreen(
                agent_snapshot=snapshot,
                demo_mode=True,
            )
        )

    def action_show_mri(self) -> None:
        """Show MRIScreen (LOD 2)."""
        snapshot = create_demo_snapshot()
        self.app.push_screen(
            MRIScreen(
                agent_snapshot=snapshot,
                demo_mode=True,
            )
        )

    def action_show_loom(self) -> None:
        """Show LoomScreen."""
        self.app.push_screen(
            LoomScreen(
                agent_id="demo-agent",
                agent_name="Demo Agent",
                demo_mode=True,
            )
        )

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()


class DemoApp(App[None]):
    """
    Demo application showing all Alethic Workbench screens.

    Navigate between different LOD levels to see:
    - ORBIT: Agent overview with density fields
    - SURFACE: Operational cockpit with metrics
    - INTERNAL: MRI deep inspection
    - Temporal: Cognitive Loom branching history
    """

    TITLE = "Alethic Workbench Demo"

    CSS = """
    Screen {
        background: #1a1a1a;
    }
    """

    def on_mount(self) -> None:
        """Mount the menu screen."""
        self.push_screen(MenuScreen())


def main() -> None:
    """Run the demo application."""
    app = DemoApp()
    app.run()


if __name__ == "__main__":
    main()

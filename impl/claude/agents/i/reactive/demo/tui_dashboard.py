"""
TUI Dashboard Demo: Wave 10 adapter demonstration.

A full TUI application demonstrating all Wave 10 adapters:
- TextualAdapter: Wraps KgentsWidgets
- FlexContainer: Layout management
- ThemeBinding: Dark/light theme toggle
- FocusSync: Animated focus navigation

Run with:
    python -m agents.i.reactive.demo.tui_dashboard

Controls:
    Tab / Shift+Tab: Navigate focus
    Ctrl+T: Toggle theme (dark/light)
    Ctrl+Q: Quit
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.i.reactive.adapters import (
    FocusSync,
    TextualAdapter,
    ThemeBinding,
    create_focus_sync,
    create_theme_binding,
)
from agents.i.reactive.adapters.textual_layout import flex_column, flex_row
from agents.i.reactive.adapters.textual_theme import get_dark_css, get_light_css
from agents.i.reactive.pipeline.focus import FocusTransitionStyle
from agents.i.reactive.pipeline.theme import ThemeMode, ThemeProvider
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget
from agents.i.reactive.wiring.clock import Clock, ClockConfig
from agents.i.reactive.wiring.interactions import FocusDirection
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static

# =============================================================================
# Demo Widgets
# =============================================================================


@dataclass(frozen=True)
class AgentCardState:
    """State for an agent card widget."""

    name: str = "Agent"
    status: str = "idle"
    task_count: int = 0
    memory_mb: float = 0.0


class AgentCardWidget(KgentsWidget[AgentCardState]):
    """A card displaying agent information."""

    def __init__(
        self,
        name: str = "Agent",
        status: str = "idle",
        task_count: int = 0,
        memory_mb: float = 0.0,
    ) -> None:
        self.state = Signal.of(
            AgentCardState(
                name=name,
                status=status,
                task_count=task_count,
                memory_mb=memory_mb,
            )
        )

    def project(self, target: RenderTarget) -> str | Text | dict[str, Any]:
        s = self.state.value
        status_icon = {
            "idle": "[dim][ ][/]",
            "running": "[green][*][/]",
            "error": "[red][!][/]",
            "complete": "[blue][+][/]",
        }.get(s.status, "[ ]")

        match target:
            case RenderTarget.CLI:
                return f"{s.name} {status_icon} - {s.task_count} tasks, {s.memory_mb:.1f}MB"
            case RenderTarget.TUI:
                return Text.from_markup(
                    f"{status_icon} [bold]{s.name}[/]\n"
                    f"  Tasks: {s.task_count}\n"
                    f"  Memory: {s.memory_mb:.1f}MB"
                )
            case RenderTarget.JSON:
                return {
                    "name": s.name,
                    "status": s.status,
                    "task_count": s.task_count,
                    "memory_mb": s.memory_mb,
                }
            case _:
                return str(s)

    def set_status(self, status: str) -> None:
        self.state.update(
            lambda s: AgentCardState(
                name=s.name,
                status=status,
                task_count=s.task_count,
                memory_mb=s.memory_mb,
            )
        )

    def increment_tasks(self) -> None:
        self.state.update(
            lambda s: AgentCardState(
                name=s.name,
                status=s.status,
                task_count=s.task_count + 1,
                memory_mb=s.memory_mb,
            )
        )


@dataclass(frozen=True)
class ClockDisplayState:
    """State for clock display."""

    timestamp: float = 0.0
    running: bool = True


class ClockDisplayWidget(KgentsWidget[ClockDisplayState]):
    """A widget displaying elapsed time."""

    def __init__(self) -> None:
        self.state = Signal.of(ClockDisplayState())

    def project(self, target: RenderTarget) -> str | Text:
        s = self.state.value
        seconds = int(s.timestamp / 1000)
        minutes = seconds // 60
        secs = seconds % 60
        status = "[green]Running[/]" if s.running else "[red]Paused[/]"

        match target:
            case RenderTarget.TUI:
                return Text.from_markup(f"[bold]{minutes:02d}:{secs:02d}[/] {status}")
            case _:
                return f"{minutes:02d}:{secs:02d}"

    def update_time(self, timestamp: float, running: bool) -> None:
        self.state.set(ClockDisplayState(timestamp=timestamp, running=running))


# =============================================================================
# Dashboard App
# =============================================================================


class DashboardApp(App[object]):
    """Wave 10 TUI Dashboard Demo."""

    TITLE = "kgents TUI Dashboard"
    SUB_TITLE = "Wave 10 Adapter Demo"

    CSS = """
    Screen {
        background: $background;
    }

    #main-container {
        width: 100%;
        height: 100%;
        padding: 1;
    }

    .card {
        border: tall $primary;
        padding: 1;
        margin: 1;
        width: 24;
        height: 6;
    }

    .card:focus-within {
        border: tall $secondary;
    }

    #clock-display {
        dock: top;
        height: 3;
        content-align: center middle;
        border: tall $primary;
        margin-bottom: 1;
    }

    #cards-container {
        layout: horizontal;
        height: auto;
    }

    .agent-adapter {
        width: 24;
        height: auto;
        border: round $primary;
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+t", "toggle_theme", "Toggle Theme"),
        Binding("ctrl+q", "quit", "Quit"),
        Binding("tab", "focus_next", "Next"),
        Binding("shift+tab", "focus_prev", "Previous"),
    ]

    def __init__(self) -> None:
        super().__init__()

        # Theme provider and binding
        self.theme_provider = ThemeProvider.create(ThemeMode.DARK)
        self.theme_binding = create_theme_binding()

        # Clock
        self.clock = Clock.create(ClockConfig(fps=10))
        self.clock_widget = ClockDisplayWidget()

        # Agent cards
        self.agents = [
            AgentCardWidget("K-gent", "running", 3, 128.5),
            AgentCardWidget("A-gent", "idle", 0, 64.0),
            AgentCardWidget("D-gent", "complete", 12, 256.2),
            AgentCardWidget("T-gent", "error", 1, 32.1),
        ]

        # Focus sync
        self.focus_sync = create_focus_sync()
        for i, agent in enumerate(self.agents):
            self.focus_sync.animated_focus.register(
                f"agent-{i}",
                tab_index=i,
                position=(i * 26, 0),
            )

    def compose(self) -> ComposeResult:
        """Compose the dashboard UI."""
        yield Header()

        with Container(id="main-container"):
            # Clock display
            yield Static(id="clock-display")

            # Agent cards
            with Horizontal(id="cards-container"):
                for i, agent in enumerate(self.agents):
                    adapter = TextualAdapter(
                        agent,
                        id=f"agent-{i}",
                        classes="agent-adapter",
                    )
                    yield adapter

        yield Footer()

    def on_mount(self) -> None:
        """Handle mount event."""
        # Start clock (auto_start=True by default, so just subscribe)
        self.clock.state.subscribe(self._on_clock_tick)

        # Update clock display
        self._update_clock_display()

        # Bind theme
        self.theme_binding.bind(self, self.theme_provider)

        # Focus first agent
        self.focus_sync.focus("agent-0", style=FocusTransitionStyle.NONE)

    def _on_clock_tick(self, state: Any) -> None:
        """Handle clock tick."""
        self.clock_widget.update_time(state.elapsed, state.running)
        self._update_clock_display()

    def _update_clock_display(self) -> None:
        """Update the clock static widget."""
        clock_static = self.query_one("#clock-display", Static)
        output = self.clock_widget.project(RenderTarget.TUI)
        clock_static.update(output)

    def action_toggle_theme(self) -> None:
        """Toggle between dark and light theme."""
        new_mode = self.theme_provider.toggle_mode()

        # Theme binding handles CSS updates automatically via subscription
        # Just refresh the display
        self.refresh()
        self.notify(f"Theme: {new_mode.name}")

    def action_focus_next(self) -> None:
        """Move focus to next widget."""
        self.focus_sync.move_focus(FocusDirection.FORWARD)
        focused = self.focus_sync.focused_id
        if focused:
            widget = self.query_one(f"#{focused}")
            widget.focus()

    def action_focus_prev(self) -> None:
        """Move focus to previous widget."""
        self.focus_sync.move_focus(FocusDirection.BACKWARD)
        focused = self.focus_sync.focused_id
        if focused:
            widget = self.query_one(f"#{focused}")
            widget.focus()


# =============================================================================
# Entry Point
# =============================================================================


def main() -> None:
    """Run the dashboard demo."""
    app = DashboardApp()
    app.run()


if __name__ == "__main__":
    main()

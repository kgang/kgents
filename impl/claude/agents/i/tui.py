"""
TUI Renderer: Terminal User Interface for the stigmergic field.

Renders the field state as ASCII art with optional ANSI colors.
Integrates with the CLI and supports keyboard navigation.

See: spec/i-gents/README.md
"""

from __future__ import annotations

import asyncio
import sys
import termios
import tty
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, Optional

from .field import (
    DialecticPhase,
    Entity,
    EntityType,
    FieldSimulator,
    FieldState,
    create_demo_field,
)


class Color(Enum):
    """ANSI color codes."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def get_entity_color(entity: Entity) -> str:
    """Get ANSI color for an entity type."""
    colors = {
        EntityType.ID: Color.CYAN.value,
        EntityType.COMPOSE: Color.CYAN.value,
        EntityType.GROUND: Color.WHITE.value + Color.DIM.value,
        EntityType.JUDGE: Color.YELLOW.value,
        EntityType.CONTRADICT: Color.RED.value,
        EntityType.SUBLATE: Color.MAGENTA.value,
        EntityType.FIX: Color.BLUE.value,
        EntityType.TASK: Color.WHITE.value + Color.BOLD.value,
        EntityType.HYPOTHESIS: Color.MAGENTA.value,
        EntityType.ARTIFACT: Color.GREEN.value,
    }
    return colors.get(entity.entity_type, Color.WHITE.value)


def get_phase_color(phase: DialecticPhase) -> str:
    """Get ANSI color for dialectic phase."""
    colors = {
        DialecticPhase.DORMANT: Color.DIM.value,
        DialecticPhase.FLUX: Color.GREEN.value,
        DialecticPhase.TENSION: Color.RED.value,
        DialecticPhase.SUBLATE: Color.MAGENTA.value,
        DialecticPhase.FIX: Color.BLUE.value,
        DialecticPhase.COOLING: Color.CYAN.value,
    }
    return colors.get(phase, Color.WHITE.value)


def get_log_color(level: str) -> str:
    """Get ANSI color for log level."""
    colors = {
        "info": Color.DIM.value,
        "success": Color.GREEN.value,
        "warning": Color.YELLOW.value,
        "error": Color.RED.value,
        "meta": Color.CYAN.value,
    }
    return colors.get(level, Color.WHITE.value)


@dataclass
class RenderConfig:
    """Configuration for TUI rendering."""

    use_color: bool = True
    show_compost: bool = True
    show_metrics: bool = True
    show_help: bool = True
    compost_lines: int = 5
    field_padding: int = 2


class FieldRenderer:
    """Renders a FieldState to terminal."""

    def __init__(
        self,
        state: FieldState,
        config: Optional[RenderConfig] = None,
    ):
        self.state = state
        self.config = config or RenderConfig()
        self._tick_symbol = 0

    def render(self) -> str:
        """Render complete TUI frame."""
        lines = []

        # Header
        lines.extend(self._render_header())

        # Metrics bar
        if self.config.show_metrics:
            lines.extend(self._render_metrics())

        # Field grid
        lines.extend(self._render_field())

        # Status line
        lines.extend(self._render_status())

        # Compost heap (event log)
        if self.config.show_compost:
            lines.extend(self._render_compost())

        # Help bar
        if self.config.show_help:
            lines.extend(self._render_help())

        return "\n".join(lines)

    def _c(self, color: str, text: str) -> str:
        """Apply color if enabled."""
        if self.config.use_color:
            return f"{color}{text}{Color.RESET.value}"
        return text

    def _render_header(self) -> list[str]:
        """Render the header line."""
        elapsed = datetime.now() - self.state.start_time
        hours = int(elapsed.total_seconds()) // 3600
        minutes = (int(elapsed.total_seconds()) % 3600) // 60
        seconds = int(elapsed.total_seconds()) % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        width = self.state.width + self.config.field_padding * 2 + 2
        title = "KGENTS"
        header = f"┌─ {title} " + "─" * (width - len(title) - 20) + f" t: {time_str} ─┐"

        return [self._c(Color.DIM.value, header)]

    def _render_metrics(self) -> list[str]:
        """Render entropy and heat bars."""
        width = self.state.width + self.config.field_padding * 2

        def bar(value: float, label: str, color: str) -> str:
            bar_width = 20
            filled = int(value / 100 * bar_width)
            empty = bar_width - filled
            bar_str = "█" * filled + "░" * empty
            pct = f"{int(value)}%"
            line = f"│  [{label} {self._c(color, bar_str)}] {pct}"
            padding = width - len(label) - bar_width - len(pct) - 6
            return line + " " * padding + "│"

        entropy_color = Color.GREEN.value if self.state.entropy > 30 else Color.RED.value
        heat_color = Color.RED.value if self.state.heat > 70 else Color.YELLOW.value

        return [
            bar(self.state.entropy, "ENTROPY", entropy_color),
            bar(self.state.heat, "HEAT   ", heat_color),
            "│" + " " * (width + 2) + "│",
        ]

    def _render_field(self) -> list[str]:
        """Render the field grid with entities."""
        lines = []

        # Create grid
        grid: list[list[str]] = [
            [" " for _ in range(self.state.width)] for _ in range(self.state.height)
        ]

        # Place entities
        for entity in self.state.entities.values():
            if 0 <= entity.x < self.state.width and 0 <= entity.y < self.state.height:
                symbol = entity.symbol
                color = get_entity_color(entity)

                # Highlight focused entity
                if self.state.focus == entity.id:
                    symbol = f"[{symbol}]"
                    color = Color.BOLD.value + color

                grid[entity.y][entity.x] = self._c(color, symbol)

        # Render with border
        " " * self.config.field_padding
        top_border = "│  ┌" + "─" * self.state.width + "┐  │"
        bottom_border = "│  └" + "─" * self.state.width + "┘  │"

        lines.append(top_border)
        for row in grid:
            line = "│  │" + "".join(row) + "│  │"
            lines.append(line)
        lines.append(bottom_border)

        return lines

    def _render_status(self) -> list[str]:
        """Render status line."""
        width = self.state.width + self.config.field_padding * 2

        phase = self.state.dialectic_phase
        phase_color = get_phase_color(phase)
        phase_str = self._c(phase_color, phase.value.upper())

        focus_str = ""
        if self.state.focus:
            entity = self.state.get_entity(self.state.focus)
            if entity:
                color = get_entity_color(entity)
                focus_str = f"  FOCUS: [{self._c(color, entity.symbol)}] {entity.id}"

        line = f"│  PHASE: {phase_str}{focus_str}"
        padding = width - len(f"  PHASE: {phase.value.upper()}{focus_str}") + 2
        line += " " * padding + "│"

        return ["│" + " " * (width + 2) + "│", line]

    def _render_compost(self) -> list[str]:
        """Render the compost heap (event log)."""
        lines = ["│" + " " * (self.state.width + self.config.field_padding * 2 + 2) + "│"]

        events = self.state.get_recent_events(self.config.compost_lines)
        width = self.state.width + self.config.field_padding * 2

        for event in events:
            time_str = event.get("time", "")[-8:]  # HH:MM:SS
            source = event.get("source", "")[:10].ljust(10)
            message = event.get("message", "")
            level = event.get("level", "info")

            color = get_log_color(level)
            entry = f"[{time_str}] {source} {message}"

            # Truncate if too long
            max_len = width - 2
            if len(entry) > max_len:
                entry = entry[: max_len - 3] + "..."

            line = f"│  {self._c(color, entry)}"
            padding = width - len(entry) + 2
            line += " " * padding + "│"
            lines.append(line)

        return lines

    def _render_help(self) -> list[str]:
        """Render help bar."""
        width = self.state.width + self.config.field_padding * 2 + 2

        help_text = "[1]FIELD [2]FORGE [o]OBSERVE [q]QUIT [?]HELP"
        padding = (width - len(help_text)) // 2
        line = "│" + " " * padding + help_text + " " * (width - padding - len(help_text)) + "│"

        bottom = "└" + "─" * width + "┘"

        return [
            "│" + " " * width + "│",
            self._c(Color.DIM.value, line),
            self._c(Color.DIM.value, bottom),
        ]


class KeyHandler:
    """Handles keyboard input for TUI navigation."""

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[], None]] = {}

    def register(self, key: str, handler: Callable[[], None]) -> None:
        """Register a handler for a key."""
        self._handlers[key] = handler

    def handle(self, key: str) -> bool:
        """Handle a key press. Returns True if handled."""
        if key in self._handlers:
            self._handlers[key]()
            return True
        return False


class TUIApplication:
    """
    Main TUI application for the stigmergic field.

    Manages the render loop, keyboard input, and simulation.
    """

    def __init__(
        self,
        state: Optional[FieldState] = None,
        config: Optional[RenderConfig] = None,
    ):
        self.state = state or create_demo_field()
        self.config = config or RenderConfig()
        self.simulator = FieldSimulator(self.state)
        self.renderer = FieldRenderer(self.state, self.config)
        self.keys = KeyHandler()
        self._running = False
        self._setup_key_handlers()

    def _setup_key_handlers(self) -> None:
        """Set up keyboard handlers."""
        # Quit
        self.keys.register("q", self._quit)

        # Pause/resume
        self.keys.register(" ", self._toggle_pause)

        # Navigation
        self.keys.register("h", lambda: self._move_focus(-1, 0))
        self.keys.register("j", lambda: self._move_focus(0, 1))
        self.keys.register("k", lambda: self._move_focus(0, -1))
        self.keys.register("l", lambda: self._move_focus(1, 0))
        self.keys.register("\t", self._cycle_focus)

        # Actions
        self.keys.register("o", self._observe)

    def _quit(self) -> None:
        """Quit the application."""
        self._running = False

    def _toggle_pause(self) -> None:
        """Toggle simulation pause."""
        if self.simulator.is_paused:
            self.simulator.resume()
            self.state.log_event("pause", "tui", "Simulation resumed")
        else:
            self.simulator.pause()
            self.state.log_event("pause", "tui", "Simulation paused")

    def _move_focus(self, dx: int, dy: int) -> None:
        """Move focused entity."""
        if not self.state.focus:
            return
        entity = self.state.get_entity(self.state.focus)
        if entity:
            entity.move(dx, dy, (self.state.width, self.state.height))

    def _cycle_focus(self) -> None:
        """Cycle focus to next entity."""
        agents = list(self.state.get_agents())
        if not agents:
            return

        if self.state.focus is None:
            self.state.focus = agents[0].id
        else:
            ids = [a.id for a in agents]
            try:
                idx = ids.index(self.state.focus)
                self.state.focus = ids[(idx + 1) % len(ids)]
            except ValueError:
                self.state.focus = agents[0].id

    def _observe(self) -> None:
        """Spawn W-gent for focused entity."""
        if not self.state.focus:
            self.state.log_event("observe", "tui", "No entity focused", level="warning")
            return

        # In a real implementation, this would spawn a W-gent process
        self.state.log_event(
            "observe",
            "tui",
            f"Observing {self.state.focus} (would spawn W-gent)",
            level="meta",
        )

    def _clear_screen(self) -> None:
        """Clear terminal screen."""
        print("\033[2J\033[H", end="")

    def _get_key(self) -> Optional[str]:
        """Get a single keypress (non-blocking)."""
        import select

        if select.select([sys.stdin], [], [], 0.0)[0]:
            return sys.stdin.read(1)
        return None

    async def run(self) -> None:
        """Run the TUI application."""
        self._running = True

        # Save terminal state
        old_settings = termios.tcgetattr(sys.stdin)

        try:
            # Set terminal to raw mode
            tty.setraw(sys.stdin.fileno())

            while self._running:
                # Render
                self._clear_screen()
                print(self.renderer.render())

                # Process input
                key = self._get_key()
                if key:
                    self.keys.handle(key)

                # Simulate
                self.simulator.tick()

                # Frame delay
                await asyncio.sleep(0.1)

        finally:
            # Restore terminal state
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            self._clear_screen()

    def run_sync(self) -> None:
        """Run the TUI application synchronously."""
        asyncio.run(self.run())


def render_field_once(state: FieldState, config: Optional[RenderConfig] = None) -> str:
    """Render a field state once (for export or testing)."""
    renderer = FieldRenderer(state, config)
    return renderer.render()


def run_demo() -> None:
    """Run a demo of the TUI."""
    app = TUIApplication()
    app.run_sync()


if __name__ == "__main__":
    run_demo()

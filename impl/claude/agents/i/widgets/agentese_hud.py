"""
AGENTESE HUD Widget - Displays current AGENTESE path invocations.

Shows what agents are doing in real-time using the AGENTESE path notation:
  robin → world.pubmed.search("β-sheet")
          └─ concept.biology.protein.structure

The HUD:
- Shows agent name + path being invoked
- Fades after 2 seconds of inactivity
- Color-coded by context (world=blue, self=amber, void=purple)
- Stacks recent calls (max 3 visible)

"The noun is a lie. There is only the rate of change."
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Callable

from textual.reactive import reactive
from textual.widget import Widget

if TYPE_CHECKING:
    from textual.app import RenderResult


class AgentContext(Enum):
    """AGENTESE context categories."""

    WORLD = "world"  # External: entities, environments, tools
    SELF = "self"  # Internal: memory, capability, state
    CONCEPT = "concept"  # Abstract: platonics, definitions, logic
    VOID = "void"  # Accursed Share: entropy, serendipity
    TIME = "time"  # Temporal: traces, forecasts, schedules


# Context colors from Earth palette
CONTEXT_COLORS = {
    AgentContext.WORLD: "#8b7ba5",  # Muted violet (world = external)
    AgentContext.SELF: "#e6a352",  # Warm amber (self = internal)
    AgentContext.CONCEPT: "#7d9c7a",  # Sage green (concept = abstract)
    AgentContext.VOID: "#9b59b6",  # Purple (void = entropy)
    AgentContext.TIME: "#d4a574",  # Warm tan (time = temporal)
}


@dataclass
class AgentesePath:
    """A single AGENTESE path invocation."""

    agent_id: str
    agent_name: str
    path: str  # e.g., "world.pubmed.search"
    args: str = ""  # e.g., '"β-sheet"'
    sub_path: str = ""  # Optional nested path
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def context(self) -> AgentContext:
        """Extract the context from the path."""
        if self.path.startswith("world."):
            return AgentContext.WORLD
        elif self.path.startswith("self."):
            return AgentContext.SELF
        elif self.path.startswith("concept."):
            return AgentContext.CONCEPT
        elif self.path.startswith("void."):
            return AgentContext.VOID
        elif self.path.startswith("time."):
            return AgentContext.TIME
        else:
            return AgentContext.WORLD  # Default

    @property
    def color(self) -> str:
        """Get the color for this path's context."""
        return CONTEXT_COLORS[self.context]

    def format_display(self, max_width: int = 60) -> str:
        """Format for display in HUD."""
        main_line = f"{self.agent_name} → {self.path}"
        if self.args:
            main_line += f"({self.args})"

        if len(main_line) > max_width:
            main_line = main_line[: max_width - 3] + "..."

        if self.sub_path:
            sub_line = f"          └─ {self.sub_path}"
            if len(sub_line) > max_width:
                sub_line = sub_line[: max_width - 3] + "..."
            return f"{main_line}\n{sub_line}"

        return main_line


class AgentHUD(Widget):
    """
    AGENTESE HUD widget.

    Displays recent AGENTESE path invocations in a compact overlay.
    """

    DEFAULT_CSS = """
    AgentHUD {
        dock: top;
        height: auto;
        max-height: 8;
        width: 100%;
        background: #252525;
        padding: 0 2;
        border-bottom: solid #4a4a5c;
    }

    AgentHUD.hidden {
        display: none;
    }

    AgentHUD.fading {
        opacity: 0.5;
    }

    AgentHUD .hud-title {
        color: #b3a89a;
        text-style: bold;
    }

    AgentHUD .path-world {
        color: #8b7ba5;
    }

    AgentHUD .path-self {
        color: #e6a352;
    }

    AgentHUD .path-concept {
        color: #7d9c7a;
    }

    AgentHUD .path-void {
        color: #9b59b6;
    }

    AgentHUD .path-time {
        color: #d4a574;
    }
    """

    # Reactive properties
    is_shown: reactive[bool] = reactive(True)
    is_fading: reactive[bool] = reactive(False)

    def __init__(
        self,
        max_entries: int = 3,
        fade_delay_ms: int = 2000,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._entries: list[AgentesePath] = []
        self._max_entries = max_entries
        self._fade_delay_ms = fade_delay_ms
        self._fade_timer_handle: asyncio.TimerHandle | None = None
        self._callbacks: list[Callable[[AgentesePath], None]] = []

    def add_path(self, path: AgentesePath) -> None:
        """Add a new AGENTESE path invocation."""
        self._entries.insert(0, path)
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[: self._max_entries]

        # Show HUD
        self.is_shown = True
        self.is_fading = False
        self.remove_class("hidden", "fading")

        # Reset fade timer
        self._schedule_fade()

        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(path)
            except Exception:
                pass

        self.refresh()

    def invoke(
        self,
        agent_id: str,
        agent_name: str,
        path: str,
        args: str = "",
        sub_path: str = "",
    ) -> None:
        """
        Record an AGENTESE invocation.

        This is the main API for the HUD - call this when an agent
        invokes an AGENTESE path.

        Args:
            agent_id: The agent's ID
            agent_name: Display name for the agent
            path: The AGENTESE path (e.g., "world.pubmed.search")
            args: Arguments to the path (e.g., '"β-sheet"')
            sub_path: Optional nested/related path
        """
        entry = AgentesePath(
            agent_id=agent_id,
            agent_name=agent_name,
            path=path,
            args=args,
            sub_path=sub_path,
        )
        self.add_path(entry)

    def _schedule_fade(self) -> None:
        """Schedule the fade effect after delay."""
        # Cancel existing timer
        if self._fade_timer_handle:
            self._fade_timer_handle.cancel()

        # Schedule fade
        self.set_timer(self._fade_delay_ms / 1000.0, self._start_fade)

    def _start_fade(self) -> None:
        """Start fading the HUD."""
        self.is_fading = True
        self.add_class("fading")

        # Schedule hide after fade
        self.set_timer(0.5, self._hide)

    def _hide(self) -> None:
        """Hide the HUD."""
        self.is_shown = False
        self.add_class("hidden")
        self._entries.clear()
        self.refresh()

    def render(self) -> "RenderResult":
        """Render the AGENTESE HUD."""
        if not self.is_shown or not self._entries:
            return ""

        lines = ["─ AGENTESE ─"]

        for entry in self._entries:
            display = entry.format_display(max_width=60)
            lines.append(f"  {display}")

        return "\n".join(lines)

    def watch_is_shown(self, value: bool) -> None:
        """React to visibility changes."""
        if value:
            self.remove_class("hidden")
        else:
            self.add_class("hidden")

    def watch_is_fading(self, value: bool) -> None:
        """React to fading state changes."""
        if value:
            self.add_class("fading")
        else:
            self.remove_class("fading")

    def subscribe(self, callback: Callable[[AgentesePath], None]) -> None:
        """Subscribe to path invocation events."""
        self._callbacks.append(callback)

    def unsubscribe(self, callback: Callable[[AgentesePath], None]) -> None:
        """Unsubscribe from path invocation events."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def clear(self) -> None:
        """Clear all entries and hide."""
        self._entries.clear()
        self.is_shown = False
        self.add_class("hidden")
        self.refresh()

    def get_recent(self, count: int = 10) -> list[AgentesePath]:
        """Get recent path invocations."""
        return self._entries[:count]


class CompactAgentHUD(Widget):
    """
    Compact single-line AGENTESE HUD.

    Shows only the most recent path in a minimal format.
    Good for status bar integration.
    """

    DEFAULT_CSS = """
    CompactAgentHUD {
        height: 1;
        width: auto;
        min-width: 20;
        color: #b3a89a;
    }

    CompactAgentHUD.active {
        color: #f5f0e6;
    }

    CompactAgentHUD.world {
        color: #8b7ba5;
    }

    CompactAgentHUD.self {
        color: #e6a352;
    }

    CompactAgentHUD.concept {
        color: #7d9c7a;
    }

    CompactAgentHUD.void {
        color: #9b59b6;
    }

    CompactAgentHUD.time {
        color: #d4a574;
    }
    """

    current_path: reactive[str] = reactive("")

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._current_entry: AgentesePath | None = None

    def set_path(self, entry: AgentesePath) -> None:
        """Set the current path to display."""
        self._current_entry = entry
        self.current_path = f"{entry.agent_name}→{entry.path}"

        # Update context class
        self.remove_class("world", "self", "concept", "void", "time")
        self.add_class(entry.context.value)
        self.add_class("active")

        self.refresh()

    def clear(self) -> None:
        """Clear the display."""
        self._current_entry = None
        self.current_path = ""
        self.remove_class("active", "world", "self", "concept", "void", "time")
        self.refresh()

    def render(self) -> "RenderResult":
        """Render the compact HUD."""
        if not self.current_path:
            return "⌘ ─"
        return f"⌘ {self.current_path}"

    def watch_current_path(self, value: str) -> None:
        """React to path changes."""
        self.refresh()


# Demo data for testing
def create_demo_paths() -> list[AgentesePath]:
    """Create demo AGENTESE paths for testing."""
    return [
        AgentesePath(
            agent_id="robin",
            agent_name="robin",
            path="world.pubmed.search",
            args='"β-sheet protein folding"',
            sub_path="concept.biology.protein.structure",
        ),
        AgentesePath(
            agent_id="robin",
            agent_name="robin",
            path="self.memory.recall",
            args='"previous_hypotheses"',
        ),
        AgentesePath(
            agent_id="g-gent",
            agent_name="g-gent",
            path="concept.category.morphism",
            args="Hom(A,B)",
        ),
        AgentesePath(
            agent_id="psi",
            agent_name="psi",
            path="void.sip",
            args="",
            sub_path="concept.metaphor.generate",
        ),
        AgentesePath(
            agent_id="o-gent",
            agent_name="o-gent",
            path="time.trace.witness",
            args="robin.last_hour",
        ),
    ]

"""
FluxScreen - The Semantic Weather Map.

The default screen for I-gent v2.5. Agents are rendered as density
fields (currents of cognition), not boxes or rooms.

Navigation:
  h/j/k/l - Move cursor
  Enter   - Focus agent (zoom in)
  Escape  - Zoom out
  w       - Wire overlay (hold)
  b       - Body overlay
  p       - Psi-gent insight
  /       - L-gent search
  q       - Quit
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Footer, Header, Static

from ..data.lod import LODLevel, LODProjector
from ..data.ogent import XYZHealth
from ..data.state import AgentSnapshot, FluxState, create_demo_flux_state
from ..theme.earth import EARTH_CSS, EARTH_PALETTE
from ..theme.heartbeat import HeartbeatMixin, get_heartbeat_controller
from ..theme.posture import PostureMapper, render_posture_with_tooltip
from ..widgets.agentese_hud import AgentesePath, AgentHUD, CompactAgentHUD
from ..widgets.density_field import DensityField, Phase
from ..widgets.glitch import (
    GlitchController,
    GlitchEvent,
    GlitchIndicator,
    get_glitch_controller,
)
from ..widgets.health_bar import CompactHealthBar
from .base import KgentsScreen
from .overlays import BodyOverlay, HelpOverlay, WireOverlay

if TYPE_CHECKING:
    pass


class AgentCard(Widget, HeartbeatMixin):
    """
    A card displaying an agent in the flux.

    Contains a DensityField plus metadata and XYZ health.
    """

    DEFAULT_CSS = """
    AgentCard {
        width: 24;
        height: 10;
        border: solid #4a4a5c;
        padding: 0 1;
        margin: 0 1;
    }

    AgentCard:focus-within {
        border: solid #e6a352;
        background: #252525;
    }

    AgentCard .agent-header {
        height: 1;
        color: #f5f0e6;
        text-style: bold;
    }

    AgentCard .agent-phase {
        height: 1;
        color: #b3a89a;
    }

    AgentCard .agent-summary {
        height: 1;
        color: #6a6560;
    }

    AgentCard .agent-health {
        height: 1;
        color: #b3a89a;
    }

    AgentCard .density-container {
        height: 4;
    }
    """

    def __init__(
        self,
        snapshot: AgentSnapshot,
        health: XYZHealth | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        HeartbeatMixin.__init__(self)
        self.snapshot = snapshot
        self.health = health
        self.can_focus = True

        # Set heartbeat BPM based on agent activity
        bpm = HeartbeatMixin.activity_to_bpm(snapshot.activity)
        self.set_bpm(bpm)

        # Also consider phase
        phase_bpm = HeartbeatMixin.phase_to_bpm(snapshot.phase.value)
        self.set_bpm((bpm + phase_bpm) // 2)  # Average of activity and phase BPM

        # Register with heartbeat controller
        get_heartbeat_controller().register(self)

        # Initialize posture mapper
        self._posture_mapper = PostureMapper()

    def compose(self) -> ComposeResult:
        """Compose the agent card."""
        # Get posture for this agent's phase and activity
        posture = self._posture_mapper.from_phase(
            self.snapshot.phase.value,
            self.snapshot.activity,
        )
        posture_display = render_posture_with_tooltip(posture, show_tooltip=False)

        yield Static(f"{posture_display} {self.snapshot.name}", classes="agent-header")
        yield Static(f"[{self.snapshot.phase.value}]", classes="agent-phase")
        with Container(classes="density-container"):
            yield DensityField(
                agent_id=self.snapshot.id,
                agent_name=self.snapshot.name,
                activity=self.snapshot.activity,
                phase=self.snapshot.phase,
            )
        # Health bar (or placeholder if no health data)
        if self.health:
            yield CompactHealthBar(health=self.health, classes="agent-health")
        else:
            yield Static("X:--% Y:--% Z:--%", classes="agent-health")
        yield Static(
            self.snapshot.summary[:20] + "..."
            if len(self.snapshot.summary) > 20
            else self.snapshot.summary,
            classes="agent-summary",
        )

    def update_snapshot(self, snapshot: AgentSnapshot) -> None:
        """Update the displayed snapshot."""
        self.snapshot = snapshot
        # Update child widgets
        for widget in self.query(DensityField):
            widget.activity = snapshot.activity
            widget.phase = snapshot.phase

    def update_health(self, health: XYZHealth) -> None:
        """Update the displayed health values."""
        self.health = health
        # Update CompactHealthBar if present
        for widget in self.query(CompactHealthBar):
            widget.update_health(health)


class EmptyStateWidget(Static):
    """
    Widget shown when no agents are registered.

    Provides a welcoming message and hints for getting started.
    """

    DEFAULT_CSS = """
    EmptyStateWidget {
        width: 100%;
        height: 100%;
        align: center middle;
        text-align: center;
        color: #6a6560;
        padding: 4;
    }

    EmptyStateWidget .empty-title {
        text-style: bold;
        color: #b3a89a;
        margin-bottom: 2;
    }

    EmptyStateWidget .empty-hint {
        color: #6a6560;
        margin-top: 1;
    }
    """

    def render(self) -> str:
        """Render the empty state message."""
        return """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║                    NO AGENTS DETECTED                     ║
║                                                           ║
║     The flux is calm. No currents of cognition flow.      ║
║                                                           ║
║                         ░░░░░░░                           ║
║                        ░░░░░░░░░                          ║
║                         ░░░░░░░                           ║
║                                                           ║
║     Press 'r' to refresh or run 'kgents daemon start'     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""


class FluxGrid(Widget):
    """
    Grid of agents in the flux view.

    Handles layout and navigation between agents.
    """

    DEFAULT_CSS = """
    FluxGrid {
        width: 100%;
        height: 100%;
        layout: grid;
        grid-size: 4 3;
        grid-gutter: 1;
        padding: 1;
        background: #1a1a1a;
    }
    """

    def __init__(
        self,
        state: FluxState,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.state = state
        self._cards: dict[str, AgentCard] = {}
        self._empty_widget: EmptyStateWidget | None = None

    def compose(self) -> ComposeResult:
        """Compose the grid of agent cards."""
        # Handle empty state gracefully
        if not self.state.agents:
            self._empty_widget = EmptyStateWidget()
            yield self._empty_widget
            return

        # Sort agents by grid position
        sorted_agents = sorted(
            self.state.agents.values(),
            key=lambda a: (a.grid_y, a.grid_x),
        )

        for agent in sorted_agents:
            card = AgentCard(agent, id=f"agent-{agent.id}")
            self._cards[agent.id] = card
            yield card

    @property
    def is_empty(self) -> bool:
        """Check if the grid is in empty state."""
        return len(self._cards) == 0

    def focus_agent(self, agent_id: str) -> None:
        """Focus a specific agent card."""
        card = self._cards.get(agent_id)
        if card:
            card.focus()

    def get_focused_agent_id(self) -> str | None:
        """Get the ID of the currently focused agent."""
        # Check all cards for focus state
        for agent_id, card in self._cards.items():
            if card.has_focus:
                return agent_id
        return None

    def update_agent(self, snapshot: AgentSnapshot) -> None:
        """Update an agent card with new snapshot data."""
        card = self._cards.get(snapshot.id)
        if card:
            card.update_snapshot(snapshot)

    def update_health(self, agent_id: str, health: XYZHealth) -> None:
        """Update an agent card's health display."""
        card = self._cards.get(agent_id)
        if card:
            card.update_health(health)

    def get_card(self, agent_id: str) -> AgentCard | None:
        """Get an agent card by ID."""
        return self._cards.get(agent_id)


class StatusBar(Static):
    """
    Status bar showing flux status and entropy.
    """

    DEFAULT_CSS = """
    StatusBar {
        dock: top;
        height: 1;
        background: #252525;
        color: #f5f0e6;
        padding: 0 2;
    }
    """

    flux_level: reactive[str] = reactive("HIGH")
    entropy_status: reactive[str] = reactive("STABLE")

    def render(self) -> str:
        return f"KGENTS v2.5  │  ⌬ FLUX: {self.flux_level}  │  ⏣ ENTROPY: {self.entropy_status}"


class FluxScreen(KgentsScreen):
    """
    The Semantic Flux screen.

    Navigate currents of cognition. Agents are density fields,
    not rooms to visit.
    """

    # Visual anchor for gentle transitions
    ANCHOR = "main-container"

    CSS = (
        EARTH_CSS
        + """
    FluxScreen {
        background: #1a1a1a;
    }

    FluxScreen #main-container {
        width: 100%;
        height: 100%;
    }

    FluxScreen #prompt-area {
        dock: bottom;
        height: 3;
        background: #252525;
        padding: 1 2;
        color: #f5f0e6;
    }

    FluxScreen #help-text {
        dock: bottom;
        height: 1;
        background: #1a1a1a;
        color: #6a6560;
        padding: 0 2;
    }

    FluxScreen #glitch-indicator {
        dock: right;
        width: 3;
        height: 1;
    }

    FluxScreen #agentese-hud {
        dock: top;
        height: auto;
        max-height: 6;
        margin-top: 1;
    }

    FluxScreen #compact-hud {
        dock: left;
        width: 30;
        height: 1;
    }
    """
    )

    BINDINGS = [
        Binding("h", "move_left", "Left", show=False),
        Binding("j", "move_down", "Down", show=False),
        Binding("k", "move_up", "Up", show=False),
        Binding("l", "move_right", "Right", show=False),
        Binding("left", "move_left", "Left", show=False),
        Binding("down", "move_down", "Down", show=False),
        Binding("up", "move_up", "Up", show=False),
        Binding("right", "move_right", "Right", show=False),
        Binding("enter", "focus_agent", "Focus"),
        Binding("escape", "zoom_out", "Back"),
        Binding("plus", "zoom_in", "Zoom In", show=True),
        Binding("minus", "zoom_out_lod", "Zoom Out", show=True),
        Binding("equal", "zoom_in", "Zoom In", show=False),  # + without shift
        Binding("underscore", "zoom_out_lod", "Zoom Out", show=False),  # - with shift
        Binding("m", "show_mri", "MRI View", show=True),
        Binding("t", "show_loom", "Loom View", show=True),
        Binding("w", "toggle_wire", "Wire"),
        Binding("b", "toggle_body", "Body"),
        Binding("p", "psi_insight", "Psi"),
        Binding("slash", "search", "Search"),
        Binding("question_mark", "show_help", "Help"),
        Binding("g", "trigger_glitch", "Glitch", show=False),
        Binding("tab", "next_agent", "Next", show=False),
        Binding("shift+tab", "prev_agent", "Prev", show=False),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        state: FluxState | None = None,
        demo_mode: bool = False,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.state = state or create_demo_flux_state()
        self._demo_mode = demo_mode
        self._grid: FluxGrid | None = None
        self._current_row = 0
        self._current_col = 0
        self._glitch_controller = get_glitch_controller()
        self._glitch_indicator: GlitchIndicator | None = None
        self._agentese_hud: AgentHUD | None = None
        self._compact_hud: CompactAgentHUD | None = None
        self._current_lod: LODLevel = LODLevel.ORBIT
        self._lod_projector = LODProjector()

    def compose(self) -> ComposeResult:
        """Compose the flux screen."""
        yield StatusBar()
        # AGENTESE HUD at the top (hidden by default, appears on invocations)
        self._agentese_hud = AgentHUD(id="agentese-hud")
        self._agentese_hud.add_class("hidden")
        yield self._agentese_hud
        with Container(id="main-container"):
            self._grid = FluxGrid(self.state)
            yield self._grid
        yield Static(
            "h/j/k/l: navigate  enter: focus  w: wire  b: body  g: glitch  q: quit",
            id="help-text",
        )
        yield Static(">>> ", id="prompt-area")
        self._glitch_indicator = GlitchIndicator(id="glitch-indicator")
        yield self._glitch_indicator

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Focus the initially focused agent
        if self.state.focused_id and self._grid:
            self._grid.focus_agent(self.state.focused_id)
        elif self._grid and self.state.agents:
            # Focus first agent
            first_id = sorted(self.state.agents.keys())[0]
            self._grid.focus_agent(first_id)

        # Subscribe to glitch events
        self._glitch_controller.subscribe(self._on_glitch_event)

    def _on_glitch_event(self, event: GlitchEvent) -> None:
        """Handle glitch events from the controller."""
        if self._glitch_indicator:
            self._glitch_indicator.set_glitch(True, event.intensity)

            # Schedule indicator reset
            self.set_timer(event.duration_ms / 1000.0, self._reset_glitch_indicator)

        # If targeting a specific agent, trigger their density field glitch
        if event.target_id != "*" and self._grid:
            card = self._grid.get_card(event.target_id)
            if card:
                for density_field in card.query(DensityField):
                    self.call_later(density_field.trigger_glitch, event.duration_ms)

        # For global glitch, trigger all agent cards
        elif event.target_id == "*" and self._grid:
            for agent_id in self.state.agents:
                card = self._grid.get_card(agent_id)
                if card:
                    for density_field in card.query(DensityField):
                        self.call_later(density_field.trigger_glitch, event.duration_ms)

    def _reset_glitch_indicator(self) -> None:
        """Reset the glitch indicator after effect ends."""
        if self._glitch_indicator:
            self._glitch_indicator.set_glitch(False)

    def _get_grid_position(self, agent_id: str) -> tuple[int, int]:
        """Get grid position of an agent."""
        agent = self.state.agents.get(agent_id)
        if agent:
            return (agent.grid_x, agent.grid_y)
        return (0, 0)

    def _find_agent_in_direction(self, dx: int, dy: int) -> str | None:
        """Find the nearest agent in the given direction."""
        if not self._grid:
            return None

        current_id = self._grid.get_focused_agent_id()
        if not current_id:
            return None

        current = self.state.agents.get(current_id)
        if not current:
            return None

        cx, cy = current.grid_x, current.grid_y
        target_x, target_y = cx + dx, cy + dy

        # Find agent at target position
        best_agent = None
        best_distance = float("inf")

        for agent_id, agent in self.state.agents.items():
            if agent_id == current_id:
                continue

            # Check if agent is in the desired direction
            ax, ay = agent.grid_x, agent.grid_y
            in_direction = (
                (dx > 0 and ax > cx)
                or (dx < 0 and ax < cx)
                or (dy > 0 and ay > cy)
                or (dy < 0 and ay < cy)
                or (dx == 0 and dy == 0)
            )

            if in_direction:
                # Calculate distance
                dist = abs(ax - target_x) + abs(ay - target_y)
                if dist < best_distance:
                    best_distance = dist
                    best_agent = agent_id

        return best_agent

    def action_move_left(self) -> None:
        """Move cursor left (h)."""
        next_id = self._find_agent_in_direction(-1, 0)
        if next_id and self._grid:
            self._grid.focus_agent(next_id)
            self.state.focused_id = next_id

    def action_move_right(self) -> None:
        """Move cursor right (l)."""
        next_id = self._find_agent_in_direction(1, 0)
        if next_id and self._grid:
            self._grid.focus_agent(next_id)
            self.state.focused_id = next_id

    def action_move_up(self) -> None:
        """Move cursor up (k)."""
        next_id = self._find_agent_in_direction(0, -1)
        if next_id and self._grid:
            self._grid.focus_agent(next_id)
            self.state.focused_id = next_id

    def action_move_down(self) -> None:
        """Move cursor down (j)."""
        next_id = self._find_agent_in_direction(0, 1)
        if next_id and self._grid:
            self._grid.focus_agent(next_id)
            self.state.focused_id = next_id

    def action_focus_agent(self) -> None:
        """Focus/zoom into the selected agent (Enter)."""
        if self._grid:
            agent_id = self._grid.get_focused_agent_id()
            if agent_id:
                self.state.focused_id = agent_id
                # TODO: Show detailed agent view
                self.notify(f"Focused: {agent_id}")

    def action_zoom_out(self) -> None:
        """Zoom out / go back (Escape)."""
        # TODO: Implement zoom levels
        self.notify("Zoom out")

    def action_toggle_wire(self) -> None:
        """Toggle WIRE overlay (w)."""
        if not self._grid:
            return

        agent_id = self._grid.get_focused_agent_id()
        if not agent_id:
            self.notify("Select an agent first")
            return

        agent = self.state.agents.get(agent_id)
        agent_name = agent.name if agent else agent_id

        # Push WIRE overlay
        self.app.push_screen(
            WireOverlay(
                agent_id=agent_id,
                agent_name=agent_name,
            )
        )

    def action_toggle_body(self) -> None:
        """Toggle BODY overlay (b)."""
        if not self._grid:
            return

        agent_id = self._grid.get_focused_agent_id()
        if not agent_id:
            self.notify("Select an agent first")
            return

        agent = self.state.agents.get(agent_id)
        agent_name = agent.name if agent else agent_id

        # Push BODY overlay
        self.app.push_screen(
            BodyOverlay(
                agent_id=agent_id,
                agent_name=agent_name,
            )
        )

    def action_psi_insight(self) -> None:
        """Show Psi-gent insight (p)."""
        # TODO: Implement Psi integration
        self.notify("Psi insight (not yet implemented)")

    def action_search(self) -> None:
        """L-gent semantic search (/)."""
        # TODO: Implement search
        self.notify("Search (not yet implemented)")

    def action_show_help(self) -> None:
        """Show help overlay (?)."""
        self.app.push_screen(HelpOverlay())

    def action_next_agent(self) -> None:
        """Focus next agent in registration order (Tab)."""
        self.state.focus_next()
        if self.state.focused_id and self._grid:
            self._grid.focus_agent(self.state.focused_id)

    def action_prev_agent(self) -> None:
        """Focus previous agent in registration order (Shift+Tab)."""
        self.state.focus_prev()
        if self.state.focused_id and self._grid:
            self._grid.focus_agent(self.state.focused_id)

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    async def action_trigger_glitch(self) -> None:
        """Manually trigger a glitch effect (g key for demo/testing)."""
        if not self._grid:
            return

        agent_id = self._grid.get_focused_agent_id()
        if agent_id:
            # Trigger glitch on focused agent
            await self._glitch_controller.trigger_agent_glitch(
                agent_id,
                duration_ms=200,
                intensity=0.4,
                source="manual:g_key",
            )
        else:
            # Trigger global glitch if no agent focused
            await self._glitch_controller.trigger_global_glitch(
                intensity=0.3,
                duration_ms=100,
                source="manual:g_key",
            )

    async def trigger_void_glitch(self, agent_id: str) -> None:
        """Trigger a glitch when agent enters VOID phase."""
        event = self._glitch_controller.on_void_phase(agent_id)
        # The controller handles the event emission synchronously,
        # but we still need to schedule cleanup
        await self._glitch_controller.trigger_agent_glitch(
            agent_id,
            duration_ms=event.duration_ms,
            intensity=event.intensity,
            source="phase:VOID",
        )

    def update_agent(self, snapshot: AgentSnapshot) -> None:
        """Update an agent with new snapshot data."""
        # Check for VOID phase transition to trigger glitch
        old_agent = self.state.agents.get(snapshot.id)
        if old_agent and old_agent.phase != Phase.VOID and snapshot.phase == Phase.VOID:
            # Agent just entered VOID phase - trigger glitch
            self._glitch_controller.on_void_phase(snapshot.id)

        if self._grid:
            self._grid.update_agent(snapshot)

    def update_health(self, agent_id: str, health: XYZHealth) -> None:
        """Update an agent's health display."""
        if self._grid:
            self._grid.update_health(agent_id, health)

    # ========================================================================
    # AGENTESE HUD Methods
    # ========================================================================

    def invoke_agentese(
        self,
        agent_id: str,
        agent_name: str,
        path: str,
        args: str = "",
        sub_path: str = "",
    ) -> None:
        """
        Record an AGENTESE path invocation.

        Call this when an agent invokes an AGENTESE path to display it in the HUD.

        Args:
            agent_id: The agent's ID
            agent_name: Display name for the agent
            path: The AGENTESE path (e.g., "world.pubmed.search")
            args: Arguments to the path (e.g., '"β-sheet"')
            sub_path: Optional nested/related path
        """
        if self._agentese_hud:
            self._agentese_hud.invoke(
                agent_id=agent_id,
                agent_name=agent_name,
                path=path,
                args=args,
                sub_path=sub_path,
            )

            # If it's a void.* path, also trigger a glitch
            if path.startswith("void."):
                self._glitch_controller.on_void_phase(agent_id)

    def add_agentese_path(self, path: AgentesePath) -> None:
        """Add a pre-constructed AGENTESE path to the HUD."""
        if self._agentese_hud:
            self._agentese_hud.add_path(path)

            # Trigger glitch on void.* paths
            if path.path.startswith("void."):
                self._glitch_controller.on_void_phase(path.agent_id)

    # ========================================================================
    # SEMANTIC ZOOM Methods (LOD)
    # ========================================================================

    def action_zoom_in(self) -> None:
        """
        Zoom in (+ key) - deeper LOD level.

        ORBIT → SURFACE → INTERNAL
        """
        next_lod = self._current_lod.zoom_in()
        if next_lod:
            self._current_lod = next_lod
            self.notify(f"Zoomed to: {self._current_lod.name}")

            # If zooming to INTERNAL (MRI), show the MRI screen
            if self._current_lod == LODLevel.INTERNAL:
                self.action_show_mri()
        else:
            self.notify("Already at maximum zoom (INTERNAL)")

    def action_zoom_out_lod(self) -> None:
        """
        Zoom out (- key) - shallower LOD level.

        INTERNAL → SURFACE → ORBIT
        """
        prev_lod = self._current_lod.zoom_out()
        if prev_lod:
            self._current_lod = prev_lod
            self.notify(f"Zoomed to: {self._current_lod.name}")
        else:
            self.notify("Already at minimum zoom (ORBIT)")

    def action_show_mri(self) -> None:
        """
        Show MRI view (m key) - deep agent inspection.

        This is the INTERNAL LOD level (LOD 2).
        """
        if not self._grid:
            self.notify("No agents available")
            return

        agent_id = self._grid.get_focused_agent_id()
        if not agent_id:
            self.notify("Select an agent first")
            return

        agent = self.state.agents.get(agent_id)
        if not agent:
            self.notify("Agent not found")
            return

        # Import MRI screen here to avoid circular imports
        from .mri import MRIScreen

        # Push MRI screen
        self.app.push_screen(
            MRIScreen(
                agent_snapshot=agent,
                agent_id=agent_id,
                agent_name=agent.name,
            )
        )

    def action_show_loom(self) -> None:
        """
        Show Loom view (t key) - topological history navigation.

        Opens the Cognitive Loom screen for the focused agent.
        """
        if not self._grid:
            self.notify("No agents available")
            return

        agent_id = self._grid.get_focused_agent_id()
        if not agent_id:
            self.notify("Select an agent first")
            return

        agent = self.state.agents.get(agent_id)
        if not agent:
            self.notify("Agent not found")
            return

        # Import Loom screen here to avoid circular imports
        from .loom import LoomScreen

        # Push Loom screen (with demo mode if in demo)
        self.app.push_screen(
            LoomScreen(
                agent_id=agent_id,
                agent_name=agent.name,
                demo_mode=self._demo_mode,
            )
        )

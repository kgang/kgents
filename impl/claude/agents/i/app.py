"""
I-gent v2.5: The Semantic Flux Application.

"Agents are not rooms to visit—they are currents of cognition
that you tune into."

Usage:
    python -m agents.i.app

Or via the CLI:
    kgents i flux

With live data:
    python -m agents.i.app --live
"""

from __future__ import annotations

import asyncio
import random
from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import App

from .data.ogent import OgentPoller, XYZHealth
from .data.registry import (
    AgentRegistry,
    MemoryRegistry,
    RegisteredAgent,
    RegistryEvent,
    RegistryEventType,
    create_demo_registry,
)
from .data.state import (
    AgentSnapshot,
    FluxState,
    SessionState,
    create_demo_flux_state,
)
from .screens.flux import FluxScreen
from .theme.earth import EARTH_CSS
from .widgets.agentese_hud import create_demo_paths
from .widgets.glitch import get_glitch_controller

if TYPE_CHECKING:
    pass


# Demo mode intervals
DEMO_GLITCH_INTERVAL = 10.0  # Trigger glitch every 10 seconds
DEMO_HUD_INTERVAL = 5.0  # Show AGENTESE path every 5 seconds


# Default state file location
DEFAULT_STATE_PATH = Path.home() / ".kgents" / "i-gent-state.json"


class FluxApp(App[None]):
    """
    I-gent v2.5: The Semantic Flux.

    A TUI for visualizing the kgents agent ecosystem as a
    semantic weather map. Agents are density fields, connections
    are flow arrows with throughput-based styling.

    Key features:
    - Density field rendering (░▒▓█)
    - h/j/k/l vim-style navigation
    - Flow arrows with bandwidth visualization
    - Glitch effects for void/error states
    - Session state persistence
    - Live data integration via registry and O-gent polling
    """

    TITLE = "KGENTS Flux"
    CSS = EARTH_CSS

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("?", "help", "Help"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(
        self,
        state: FluxState | None = None,
        state_path: Path | None = None,
        demo_mode: bool = False,
        live_mode: bool = False,
        registry: AgentRegistry | None = None,
    ) -> None:
        """
        Initialize the Flux application.

        Args:
            state: Initial flux state (if None, loads from state_path or creates demo)
            state_path: Path to session state file
            demo_mode: If True, always use demo data
            live_mode: If True, enable live data updates via O-gent polling
            registry: Custom agent registry (if None, uses demo registry)
        """
        super().__init__()
        self._state_path = state_path or DEFAULT_STATE_PATH
        self._demo_mode = demo_mode
        self._live_mode = live_mode
        self._agent_registry = registry
        self._poller: OgentPoller | None = None
        self._flux_screen: FluxScreen | None = None
        self._demo_glitch_task: asyncio.Task[None] | None = None
        self._demo_hud_task: asyncio.Task[None] | None = None
        self._demo_paths = create_demo_paths()
        self._demo_path_index = 0

        if state:
            self._flux_state = state
        elif demo_mode:
            self._flux_state = create_demo_flux_state()
        else:
            # Try to load from file, fall back to demo
            session = SessionState.load(self._state_path)
            if session.flux.agents:
                self._flux_state = session.flux
            else:
                self._flux_state = create_demo_flux_state()

    async def _setup_live_mode(self) -> None:
        """Set up live mode with registry and poller."""
        if not self._live_mode:
            return

        # Create demo registry if none provided
        if not self._agent_registry:
            self._agent_registry = create_demo_registry()

        # Sync state from registry
        await self._sync_from_registry()

        # Subscribe to registry events
        self._agent_registry.subscribe(self._on_registry_event)

        # Create and start poller
        self._poller = OgentPoller(registry=self._agent_registry)
        self._poller.subscribe(self._on_health_update)
        await self._poller.start()

    async def _sync_from_registry(self) -> None:
        """Synchronize flux state from registry."""
        if not self._agent_registry:
            return

        agents = await self._agent_registry.discover()
        for reg_agent in agents:
            # Create or update AgentSnapshot
            snapshot = AgentSnapshot(
                id=reg_agent.id,
                name=reg_agent.name,
                phase=reg_agent.cached_phase,
                activity=reg_agent.cached_activity,
                grid_x=reg_agent.grid_x,
                grid_y=reg_agent.grid_y,
                summary=reg_agent.cached_summary,
                connections={k: 0.5 for k in reg_agent.connections},  # Convert to float
            )
            self._flux_state.add_agent(snapshot)

    def _on_registry_event(self, event: RegistryEvent) -> None:
        """Handle registry events."""
        if event.event_type == RegistryEventType.AGENT_REGISTERED:
            if event.agent:
                self._handle_agent_registered(event.agent)
        elif event.event_type == RegistryEventType.AGENT_UNREGISTERED:
            self._handle_agent_unregistered(event.agent_id)
        elif event.event_type == RegistryEventType.AGENT_UPDATED:
            if event.agent:
                self._handle_agent_updated(event.agent)

    def _handle_agent_registered(self, reg_agent: RegisteredAgent) -> None:
        """Handle new agent registration."""
        snapshot = AgentSnapshot(
            id=reg_agent.id,
            name=reg_agent.name,
            phase=reg_agent.cached_phase,
            activity=reg_agent.cached_activity,
            grid_x=reg_agent.grid_x,
            grid_y=reg_agent.grid_y,
            summary=reg_agent.cached_summary,
        )
        self._flux_state.add_agent(snapshot)
        # Trigger screen refresh
        if self._flux_screen:
            self._flux_screen.refresh()
        self.notify(f"Agent registered: {reg_agent.name}")

    def _handle_agent_unregistered(self, agent_id: str) -> None:
        """Handle agent unregistration."""
        self._flux_state.remove_agent(agent_id)
        if self._flux_screen:
            self._flux_screen.refresh()
        self.notify(f"Agent unregistered: {agent_id}")

    def _handle_agent_updated(self, reg_agent: RegisteredAgent) -> None:
        """Handle agent update."""
        snapshot = self._flux_state.get_agent(reg_agent.id)
        if snapshot:
            snapshot.phase = reg_agent.cached_phase
            snapshot.activity = reg_agent.cached_activity
            snapshot.summary = reg_agent.cached_summary
            # Update screen
            if self._flux_screen:
                self._flux_screen.update_agent(snapshot)

    def _on_health_update(self, agent_id: str, health: XYZHealth) -> None:
        """Handle health update from O-gent poller."""
        if self._flux_screen:
            self._flux_screen.update_health(agent_id, health)

    async def on_mount(self) -> None:
        """Called when app is mounted."""
        # Set up live mode if enabled
        await self._setup_live_mode()

        # Push the flux screen
        self._flux_screen = FluxScreen(
            state=self._flux_state, demo_mode=self._demo_mode
        )
        self.push_screen(self._flux_screen)

        # Start demo mode timers if enabled
        if self._demo_mode:
            self._demo_glitch_task = asyncio.create_task(self._demo_glitch_loop())
            self._demo_hud_task = asyncio.create_task(self._demo_hud_loop())

    async def on_unmount(self) -> None:
        """Called when app is unmounted."""
        # Stop demo mode tasks
        if self._demo_glitch_task:
            self._demo_glitch_task.cancel()
            try:
                await self._demo_glitch_task
            except asyncio.CancelledError:
                pass
            self._demo_glitch_task = None

        if self._demo_hud_task:
            self._demo_hud_task.cancel()
            try:
                await self._demo_hud_task
            except asyncio.CancelledError:
                pass
            self._demo_hud_task = None

        # Stop poller
        if self._poller:
            await self._poller.stop()

        # Unsubscribe from registry
        if self._agent_registry:
            self._agent_registry.unsubscribe(self._on_registry_event)

        # Save state
        if not self._demo_mode:
            session = SessionState(
                flux=self._flux_state,
                last_focused_id=self._flux_state.focused_id,
            )
            try:
                session.save(self._state_path)
            except Exception:
                pass  # Silently fail on save errors

    async def _demo_glitch_loop(self) -> None:
        """Demo mode: auto-trigger glitches every DEMO_GLITCH_INTERVAL seconds."""
        controller = get_glitch_controller()
        while True:
            await asyncio.sleep(DEMO_GLITCH_INTERVAL)
            if not self._flux_screen:
                continue

            # Pick a random agent to glitch
            agent_ids = list(self._flux_state.agents.keys())
            if agent_ids:
                target_id = random.choice(agent_ids)
                await controller.trigger_agent_glitch(
                    target_id,
                    duration_ms=300,
                    intensity=0.4,
                    source="demo:auto",
                )

    async def _demo_hud_loop(self) -> None:
        """Demo mode: auto-show AGENTESE paths every DEMO_HUD_INTERVAL seconds."""
        while True:
            await asyncio.sleep(DEMO_HUD_INTERVAL)
            if not self._flux_screen:
                continue

            # Cycle through demo paths
            path = self._demo_paths[self._demo_path_index]
            self._demo_path_index = (self._demo_path_index + 1) % len(self._demo_paths)

            # Invoke on the screen
            self._flux_screen.invoke_agentese(
                agent_id=path.agent_id,
                agent_name=path.agent_name,
                path=path.path,
                args=path.args,
                sub_path=path.sub_path,
            )

    def action_help(self) -> None:
        """Show help."""
        self.notify(
            "h/j/k/l: navigate | enter: focus | w: wire | b: body | p: psi | /: search | q: quit",
            timeout=5,
        )

    async def action_refresh(self) -> None:
        """Refresh data from registry."""
        if self._live_mode and self._agent_registry:
            await self._sync_from_registry()
            if self._flux_screen:
                self._flux_screen.refresh()
            self.notify("Refreshed from registry")


def run_flux(
    demo: bool = False,
    live: bool = False,
    state_path: Path | None = None,
    registry: AgentRegistry | None = None,
) -> None:
    """
    Run the Flux application.

    Args:
        demo: If True, use demo data
        live: If True, enable live data updates via O-gent polling
        state_path: Custom path for session state
        registry: Custom agent registry (for live mode)
    """
    app = FluxApp(
        demo_mode=demo,
        live_mode=live,
        state_path=state_path,
        registry=registry,
    )
    app.run()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="I-gent v2.5: The Semantic Flux")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run with demo data",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Enable live data updates via O-gent polling",
    )
    parser.add_argument(
        "--state",
        type=Path,
        help="Path to session state file",
    )

    args = parser.parse_args()
    run_flux(demo=args.demo, live=args.live, state_path=args.state)

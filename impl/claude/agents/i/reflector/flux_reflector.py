"""
FluxReflector - Bridges RuntimeEvents to Textual Widgets.

The FluxReflector is a Reflector implementation that routes CLI events
to the FluxApp TUI. When `kgents status` runs, the FluxApp sees the
same events and can update its widgets accordingly.

Event Routing:
    CommandStartEvent   -> AgentHUD.flash_path("cmd.<command>")
    CommandEndEvent     -> EventStream + status indicator
    AgentHealthEvent    -> DensityField.update_agent()
    PheromoneEvent      -> Waveform.pulse()
    ProposalAddedEvent  -> ProposalOverlay (if open)
    ErrorEvent          -> GlitchController.trigger()

Thread Safety:
    Events may arrive from non-Textual threads. The FluxReflector
    uses call_from_thread() to safely dispatch to Textual's event loop.

Usage:
    # In one terminal
    $ kgents dashboard  # Launches DashboardApp with FluxReflector

    # In another terminal
    $ kgents status  # Dashboard shows event in traces panel
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

from protocols.cli.reflector.protocol import BaseReflector, PromptInfo

if TYPE_CHECKING:
    from protocols.cli.reflector.events import (
        AgentHealthEvent,
        CommandEndEvent,
        CommandStartEvent,
        ErrorEvent,
        PheromoneEvent,
        ProposalAddedEvent,
        RuntimeEvent,
    )
    from textual.app import App

    from ..app import FluxApp
    from ..screens.flux import FluxScreen
    from ..widgets.agentese_hud import AgentHUD
    from ..widgets.density_field import DensityField
    from ..widgets.waveform import ProcessingWaveform


@dataclass
class FluxReflector(BaseReflector):
    """
    Bridges RuntimeEvents to Textual widgets.

    Updates FluxApp when CLI events arrive:
    - CommandStartEvent -> flash AGENTESE HUD
    - CommandEndEvent -> update status indicator
    - AgentHealthEvent -> update density field
    - PheromoneEvent -> trigger waveform pulse
    - ErrorEvent -> trigger glitch effect

    Attributes:
        app: The FluxApp instance to update
        _event_queue: Queue for thread-safe event processing
        _human_buffer: Accumulated human output
        _semantic_buffer: Accumulated semantic output
    """

    app: "FluxApp | None" = None
    _event_queue: asyncio.Queue["RuntimeEvent"] = field(
        default_factory=asyncio.Queue, repr=False
    )
    _human_buffer: list[str] = field(default_factory=list, repr=False)
    _semantic_buffer: dict[str, Any] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        """Initialize parent class."""
        super().__init__()

    def set_app(self, app: "FluxApp") -> None:
        """
        Set the FluxApp reference.

        This is typically called after the app is initialized,
        since the reflector may be created before the app.
        """
        self.app = app

    def _handle_event(self, event: "RuntimeEvent") -> None:
        """
        Implementation-specific event handling.

        Routes events to appropriate widget update methods.
        Uses call_from_thread for thread safety.
        """
        if self.app is None:
            return

        # Queue event for processing
        self._event_queue.put_nowait(event)

        # Schedule processing in Textual's event loop
        try:
            self.app.call_from_thread(self._process_event, event)
        except RuntimeError:
            # App not running, queue for later
            pass

    def _process_event(self, event: "RuntimeEvent") -> None:
        """
        Process event in Textual's main thread.

        This method is called via call_from_thread() to ensure
        thread-safe widget updates.
        """
        if self.app is None:
            return

        from protocols.cli.reflector.events import (
            AgentHealthEvent,
            CommandEndEvent,
            CommandStartEvent,
            ErrorEvent,
            EventType,
            PheromoneEvent,
            ProposalAddedEvent,
        )

        # Route by event type
        if event.event_type == EventType.COMMAND_START:
            self._handle_command_start(event)  # type: ignore
        elif event.event_type == EventType.COMMAND_END:
            self._handle_command_end(event)  # type: ignore
        elif event.event_type == EventType.AGENT_HEALTH_UPDATE:
            self._handle_agent_health(event)  # type: ignore
        elif event.event_type == EventType.PHEROMONE_EMITTED:
            self._handle_pheromone(event)  # type: ignore
        elif event.event_type == EventType.PROPOSAL_ADDED:
            self._handle_proposal_added(event)  # type: ignore
        elif event.event_type == EventType.ERROR:
            self._handle_error(event)  # type: ignore

    def _handle_command_start(self, event: "CommandStartEvent") -> None:
        """Handle command start - flash HUD with command path."""
        if self.app is None:
            return

        flux_screen = self._get_flux_screen()
        if flux_screen is None:
            return

        # Flash the AGENTESE HUD with the command
        flux_screen.invoke_agentese(
            agent_id="cli",
            agent_name="CLI",
            path=f"cmd.{event.command}",
            args=" ".join(event.args) if event.args else "",
            sub_path=f"trace.{event.trace_id}" if event.trace_id else "",
        )

        # Notify
        self.app.notify(f"Command: {event.command}", timeout=2)

    def _handle_command_end(self, event: "CommandEndEvent") -> None:
        """Handle command end - update status and log to event stream."""
        if self.app is None:
            return

        flux_screen = self._get_flux_screen()
        if flux_screen is None:
            return

        # Update status bar if exit_code indicates error
        if event.exit_code != 0:
            self.app.notify(
                f"Command '{event.command}' failed (exit {event.exit_code})",
                severity="warning",
                timeout=3,
            )
        else:
            # Success notification for longer commands
            if event.duration_ms > 1000:
                self.app.notify(
                    f"Command '{event.command}' completed ({event.duration_ms}ms)",
                    timeout=2,
                )

    def _handle_agent_health(self, event: "AgentHealthEvent") -> None:
        """Handle agent health update - update density field."""
        if self.app is None:
            return

        flux_screen = self._get_flux_screen()
        if flux_screen is None:
            return

        # Convert XYZ health dict to XYZHealth object if needed
        from ..data.ogent import XYZHealth

        health = XYZHealth(
            x_telemetry=event.health.get("x", 1.0),
            y_semantic=event.health.get("y", 1.0),
            z_economic=event.health.get("z", 1.0),
        )

        # Update the flux screen
        flux_screen.update_health(event.agent_id, health)

        # Update activity in density field
        try:
            from ..widgets.density_field import DensityField

            density_field = flux_screen.query_one(
                f"DensityField#{event.agent_id}", DensityField
            )
            density_field.set_activity(event.activity)
        except Exception:
            pass  # Widget not found, ignore

    def _handle_pheromone(self, event: "PheromoneEvent") -> None:
        """Handle pheromone event - trigger waveform pulse."""
        if self.app is None:
            return

        flux_screen = self._get_flux_screen()
        if flux_screen is None:
            return

        # Try to find waveform widget and pulse it
        try:
            from ..widgets.waveform import ProcessingWaveform

            waveform = flux_screen.query_one("ProcessingWaveform", ProcessingWaveform)
            # Trigger a pulse based on pheromone level
            if hasattr(waveform, "pulse"):
                waveform.pulse(intensity=event.level)
        except Exception:
            pass  # Widget not found, ignore

    def _handle_proposal_added(self, event: "ProposalAddedEvent") -> None:
        """Handle proposal added - notify user."""
        if self.app is None:
            return

        from typing import Literal

        # Show notification with proposal info
        severity: Literal["information", "warning", "error"] = (
            "warning" if event.priority == "critical" else "information"
        )
        self.app.notify(
            f"Proposal from {event.from_agent}: {event.action}",
            severity=severity,
            timeout=5,
        )

    def _handle_error(self, event: "ErrorEvent") -> None:
        """Handle error event - trigger glitch and notify."""
        if self.app is None:
            return

        from typing import Literal

        from ..widgets.glitch import get_glitch_controller

        # Trigger global glitch effect
        controller = get_glitch_controller()
        asyncio.create_task(
            controller.trigger_global_glitch(
                duration_ms=500,
                intensity=0.6 if not event.recoverable else 0.3,
                source=f"error:{event.error_code}",
            )
        )

        # Notify with error details
        severity: Literal["information", "warning", "error"] = (
            "error" if not event.recoverable else "warning"
        )
        self.app.notify(
            f"Error: {event.message}",
            severity=severity,
            timeout=5,
        )

    def _get_flux_screen(self) -> "FluxScreen | None":
        """Get the FluxScreen from the app if available."""
        if self.app is None:
            return None

        try:
            # Get the current screen
            screen = self.app.screen
            # Check if it's a FluxScreen
            if hasattr(screen, "invoke_agentese"):
                return screen  # type: ignore
            return None
        except Exception:
            return None

    def emit_human(self, text: str) -> None:
        """
        Emit human-readable output.

        For FluxReflector, this buffers output that can be
        displayed in an event stream widget if desired.
        """
        self._human_buffer.append(text)

        # Optionally display in a toast/notification for important messages
        if self.app is not None and len(text) < 100:
            # Only show short messages as notifications
            pass  # We let handlers decide when to notify

    def emit_semantic(self, data: dict[str, Any]) -> None:
        """
        Emit structured semantic output.

        For FluxReflector, this updates internal state that
        widgets can query for detailed information.
        """
        self._semantic_buffer.update(data)

    def get_human_output(self) -> str:
        """Get accumulated human output."""
        return "\n".join(self._human_buffer)

    def get_semantic_output(self) -> dict[str, Any]:
        """Get accumulated semantic output."""
        return dict(self._semantic_buffer)

    def clear_buffers(self) -> None:
        """Clear output buffers."""
        self._human_buffer.clear()
        self._semantic_buffer.clear()

    async def drain_queue(self) -> list["RuntimeEvent"]:
        """
        Drain all queued events.

        Useful for testing or when the app is catching up
        after being suspended.
        """
        events: list["RuntimeEvent"] = []
        while not self._event_queue.empty():
            try:
                event = self._event_queue.get_nowait()
                events.append(event)
            except asyncio.QueueEmpty:
                break
        return events


def create_flux_reflector(app: "FluxApp | None" = None) -> FluxReflector:
    """
    Create a FluxReflector instance.

    Args:
        app: Optional FluxApp to connect. Can be set later via set_app().

    Returns:
        Configured FluxReflector instance

    Example:
        # Create reflector before app
        reflector = create_flux_reflector()

        # Create app with reflector
        app = FluxApp(reflector=reflector)
        reflector.set_app(app)

        # Or create with app directly
        app = FluxApp()
        reflector = create_flux_reflector(app)
    """
    reflector = FluxReflector(app=app)
    reflector.__post_init__()  # Ensure parent init runs
    return reflector

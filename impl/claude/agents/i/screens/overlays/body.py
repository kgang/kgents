"""
BODY Overlay - Omega-gent proprioception display.

The BODY overlay shows the agent's "body awareness":
- Strain (CPU)
- Pressure (Memory)
- Reach (Replicas)
- Temperature (Budget health)
- Trauma (Errors)
- Morphology (Omega pipeline)

Trigger: Press 'b' key while focused on an agent

Navigation:
- Escape: Close overlay

Note: Body overlay is view-only. Morphology changes are
routed through the kgents CLI for safety.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Static

from ...widgets.proprioception import (
    ProprioceptionBars,
    ProprioceptionState,
    TraumaLevel,
    create_demo_proprioception,
)

if TYPE_CHECKING:
    pass


class BodyOverlay(ModalScreen[None]):
    """
    BODY overlay for Omega proprioception.

    Shows the physical/resource state of an agent.
    This is a view-only overlay - modifications go through CLI.
    """

    CSS = """
    BodyOverlay {
        align: center middle;
    }

    BodyOverlay #body-container {
        width: 70%;
        height: 60%;
        max-width: 80;
        max-height: 25;
        border: solid #4a4a5c;
        background: #1a1a1a;
    }

    BodyOverlay #body-header {
        dock: top;
        height: 1;
        background: #252525;
        color: #f5f0e6;
        text-style: bold;
        padding: 0 2;
    }

    BodyOverlay #body-help {
        dock: bottom;
        height: 2;
        background: #252525;
        color: #6a6560;
        padding: 0 2;
    }

    BodyOverlay #body-content {
        width: 100%;
        height: 100%;
        padding: 1;
    }

    BodyOverlay #status-indicator {
        height: 2;
        margin-bottom: 1;
    }

    BodyOverlay .status-healthy {
        color: #7d9c7a;  /* Sage green */
    }

    BodyOverlay .status-warning {
        color: #e6a352;  /* Amber */
    }

    BodyOverlay .status-critical {
        color: #c97b84;  /* Dusty rose */
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Back", show=True),
    ]

    def __init__(
        self,
        agent_id: str = "",
        agent_name: str = "",
        state: ProprioceptionState | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._agent_id = agent_id
        self._agent_name = agent_name or agent_id
        self._state = state

    def compose(self) -> ComposeResult:
        """Compose the BODY overlay."""
        # Use demo state if none provided
        state = self._state if self._state is not None else create_demo_proprioception()

        with Container(id="body-container"):
            yield Static(f"─ BODY: {self._agent_name} ─", id="body-header")
            with Vertical(id="body-content"):
                # Status indicator
                status_class = "status-healthy" if state.is_healthy() else "status-warning"
                if state.trauma not in (TraumaLevel.NONE, TraumaLevel.MINOR):
                    status_class = "status-critical"

                status_text = "● HEALTHY" if state.is_healthy() else "● DEGRADED"
                if state.trauma == TraumaLevel.SEVERE:
                    status_text = "● CRITICAL"

                yield Static(
                    f"\n  STATUS: {status_text}",
                    id="status-indicator",
                    classes=status_class,
                )

                # Main proprioception bars
                yield ProprioceptionBars(state=state, id="proprioception")

            yield Static(
                "[View only. Route morphology changes through kgents CLI.]\n[esc] back",
                id="body-help",
            )

    async def action_dismiss(self, result: None = None) -> None:
        """Dismiss the overlay."""
        self.dismiss()

    def update_state(self, state: ProprioceptionState) -> None:
        """Update the proprioception state."""
        self._state = state
        try:
            bars = self.query_one("#proprioception", ProprioceptionBars)
            bars.update_state(state)

            # Update status indicator
            status = self.query_one("#status-indicator")
            status_class = "status-healthy" if state.is_healthy() else "status-warning"
            if state.trauma not in (TraumaLevel.NONE, TraumaLevel.MINOR):
                status_class = "status-critical"

            status_text = "● HEALTHY" if state.is_healthy() else "● DEGRADED"
            if state.trauma == TraumaLevel.SEVERE:
                status_text = "● CRITICAL"

            status.remove_class("status-healthy", "status-warning", "status-critical")
            status.add_class(status_class)
            from textual.widgets import Static

            if isinstance(status, Static):
                status.update(f"\n  STATUS: {status_text}")
        except Exception:
            pass

    def set_strain(self, value: float) -> None:
        """Update CPU strain."""
        if self._state:
            self._state.strain = value
        try:
            bars = self.query_one("#proprioception", ProprioceptionBars)
            bars.set_strain(value)
        except Exception:
            pass

    def set_pressure(self, value: float) -> None:
        """Update memory pressure."""
        if self._state:
            self._state.pressure = value
        try:
            bars = self.query_one("#proprioception", ProprioceptionBars)
            bars.set_pressure(value)
        except Exception:
            pass

    def set_reach(self, count: int) -> None:
        """Update replica count."""
        if self._state:
            self._state.reach = count
        try:
            bars = self.query_one("#proprioception", ProprioceptionBars)
            bars.set_reach(count)
        except Exception:
            pass

    def set_temperature(self, value: float) -> None:
        """Update budget temperature."""
        if self._state:
            self._state.temperature = value
        try:
            bars = self.query_one("#proprioception", ProprioceptionBars)
            bars.set_temperature(value)
        except Exception:
            pass

    def set_trauma(self, level: TraumaLevel, message: str = "") -> None:
        """Update trauma level."""
        if self._state:
            self._state.trauma = level
        try:
            bars = self.query_one("#proprioception", ProprioceptionBars)
            bars.set_trauma(level, message)
        except Exception:
            pass

"""
Proprioception Widget - Omega-gent body awareness display.

Proprioception is the sense of one's body in space. For agents,
this means awareness of resource consumption and physical state.

The Five Dimensions:
- Strain: CPU load (how hard is the agent "thinking"?)
- Pressure: Memory usage (how much is being held in mind?)
- Reach: Number of replicas (how distributed is the agent?)
- Temperature: Budget health (is the agent within budget?)
- Trauma: Any errors or issues (is the agent "hurt"?)

This is the key visual component of the BODY overlay.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

if TYPE_CHECKING:
    from textual.app import RenderResult


class TraumaLevel(Enum):
    """Level of agent trauma/errors."""

    NONE = "none"
    MINOR = "minor"  # Recoverable errors
    MODERATE = "moderate"  # Degraded performance
    SEVERE = "severe"  # Critical failure


# Bar characters
BAR_FULL = "▓"
BAR_EMPTY = "░"
BAR_HALF = "▒"


def render_percent_bar(value: float, width: int = 10) -> str:
    """
    Render a percentage bar.

    Args:
        value: Value from 0.0 to 1.0
        width: Width in characters

    Returns:
        String like "▓▓▓▓▓░░░░░"
    """
    filled = int(value * width)
    empty = width - filled
    return BAR_FULL * filled + BAR_EMPTY * empty


def render_replica_dots(count: int, max_count: int = 10) -> str:
    """
    Render replica count as dots.

    Args:
        count: Number of active replicas
        max_count: Maximum replicas to show

    Returns:
        String like "●●●○○○○○○○"
    """
    active = min(count, max_count)
    inactive = max_count - active
    return "●" * active + "○" * inactive


@dataclass
class ProprioceptionState:
    """
    Proprioception state for an agent.

    Captures the "body awareness" of an agent.
    """

    strain: float = 0.0  # CPU usage 0.0-1.0
    pressure: float = 0.0  # Memory usage 0.0-1.0
    reach: int = 1  # Number of replicas
    temperature: float = 1.0  # Budget health 0.0-1.0
    trauma: TraumaLevel = TraumaLevel.NONE
    morphology: str = "Base()"  # Omega morphology string

    def is_healthy(self) -> bool:
        """Check if all metrics are healthy."""
        return (
            self.strain < 0.8
            and self.pressure < 0.9
            and self.temperature > 0.3
            and self.trauma == TraumaLevel.NONE
        )


def create_demo_proprioception() -> ProprioceptionState:
    """Create demo proprioception state for testing."""
    return ProprioceptionState(
        strain=0.28,
        pressure=0.52,
        reach=3,
        temperature=0.85,
        trauma=TraumaLevel.NONE,
        morphology='Base() >> with_ganglia(3) >> with_vault("1Gi")',
    )


class ProprioceptionBar(Widget):
    """
    Single proprioception metric bar.

    Displays a labeled bar with percentage value.
    """

    DEFAULT_CSS = """
    ProprioceptionBar {
        width: 100%;
        height: 1;
        padding: 0;
    }

    ProprioceptionBar.healthy {
        color: #7d9c7a;  /* Sage green */
    }

    ProprioceptionBar.warning {
        color: #e6a352;  /* Amber */
    }

    ProprioceptionBar.critical {
        color: #c97b84;  /* Dusty rose */
    }
    """

    label: reactive[str] = reactive("metric")
    value: reactive[float] = reactive(0.0)
    bar_width: reactive[int] = reactive(10)
    show_percent: reactive[bool] = reactive(True)

    def __init__(
        self,
        label: str = "metric",
        value: float = 0.0,
        bar_width: int = 10,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.label = label
        self.value = value
        self.bar_width = bar_width
        self._update_class()

    def _update_class(self) -> None:
        """Update CSS class based on value."""
        self.remove_class("healthy", "warning", "critical")
        if self.value >= 0.8:
            self.add_class("critical")
        elif self.value >= 0.6:
            self.add_class("warning")
        else:
            self.add_class("healthy")

    def watch_value(self, new_value: float) -> None:
        """React to value changes."""
        self._update_class()
        self.refresh()

    def render(self) -> "RenderResult":
        """Render the bar."""
        bar = render_percent_bar(self.value, self.bar_width)
        percent = f"{int(self.value * 100):3d}%"
        return f"{self.label:14} {bar}  {percent}"

    def set_value(self, value: float) -> None:
        """Set the value (0.0-1.0)."""
        self.value = max(0.0, min(1.0, value))


class ReplicaIndicator(Widget):
    """
    Replica count indicator using dots.
    """

    DEFAULT_CSS = """
    ReplicaIndicator {
        width: 100%;
        height: 1;
        padding: 0;
        color: #8ac4e8;  /* Sky blue */
    }
    """

    label: reactive[str] = reactive("reach")
    count: reactive[int] = reactive(1)
    max_count: reactive[int] = reactive(10)

    def __init__(
        self,
        label: str = "reach",
        count: int = 1,
        max_count: int = 10,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.label = label
        self.count = count
        self.max_count = max_count

    def watch_count(self, new_value: int) -> None:
        """React to count changes."""
        self.refresh()

    def render(self) -> "RenderResult":
        """Render the replica indicator."""
        dots = render_replica_dots(self.count, self.max_count)
        return f"{self.label:14} {dots}  {self.count} replicas"

    def set_count(self, count: int) -> None:
        """Set the replica count."""
        self.count = max(0, count)


class TraumaIndicator(Widget):
    """
    Trauma/error level indicator.
    """

    DEFAULT_CSS = """
    TraumaIndicator {
        width: 100%;
        height: 1;
        padding: 0;
    }

    TraumaIndicator.none {
        color: #7d9c7a;  /* Sage - healthy */
    }

    TraumaIndicator.minor {
        color: #e6a352;  /* Amber */
    }

    TraumaIndicator.moderate {
        color: #c97b84;  /* Dusty rose */
    }

    TraumaIndicator.severe {
        color: #6b4b8a;  /* Purple - void */
    }
    """

    label: reactive[str] = reactive("trauma")
    level: reactive[TraumaLevel] = reactive(TraumaLevel.NONE)
    message: reactive[str] = reactive("")

    def __init__(
        self,
        label: str = "trauma",
        level: TraumaLevel = TraumaLevel.NONE,
        message: str = "",
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.label = label
        self.level = level
        self.message = message
        self._update_class()

    def _update_class(self) -> None:
        """Update CSS class based on trauma level."""
        self.remove_class("none", "minor", "moderate", "severe")
        self.add_class(self.level.value)

    def watch_level(self, new_value: TraumaLevel) -> None:
        """React to level changes."""
        self._update_class()
        self.refresh()

    def render(self) -> "RenderResult":
        """Render the trauma indicator."""
        display = self.level.value
        if self.message:
            display += f" ({self.message})"
        return f"{self.label:14} {display}"

    def set_level(self, level: TraumaLevel, message: str = "") -> None:
        """Set the trauma level."""
        self.level = level
        self.message = message


class ProprioceptionBars(Widget):
    """
    Omega-gent proprioception display.

    Shows all body awareness metrics in a vertical stack.
    """

    DEFAULT_CSS = """
    ProprioceptionBars {
        width: 100%;
        height: auto;
        border: solid #4a4a5c;
        padding: 1;
    }

    ProprioceptionBars .proprioception-title {
        color: #b3a89a;
        text-style: bold;
        height: 1;
        margin-bottom: 1;
    }

    ProprioceptionBars .morphology-line {
        color: #6a6560;
        height: 2;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        state: ProprioceptionState | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._state = state or ProprioceptionState()

    def compose(self) -> ComposeResult:
        """Compose the proprioception display."""
        yield Static("─ Proprioception ─", classes="proprioception-title")
        yield Static(f"MORPHOLOGY: {self._state.morphology}", classes="morphology-line")
        yield Static("")
        yield ProprioceptionBar(label="strain:", value=self._state.strain, id="strain")
        yield ProprioceptionBar(label="pressure:", value=self._state.pressure, id="pressure")
        yield ReplicaIndicator(label="reach:", count=self._state.reach, id="reach")
        yield ProprioceptionBar(
            label="temperature:", value=self._state.temperature, id="temperature"
        )
        yield TraumaIndicator(label="trauma:", level=self._state.trauma, id="trauma")

    def update_state(self, state: ProprioceptionState) -> None:
        """Update all proprioception values from state."""
        self._state = state

        # Update individual widgets
        try:
            self.query_one("#strain", ProprioceptionBar).set_value(state.strain)
            self.query_one("#pressure", ProprioceptionBar).set_value(state.pressure)
            self.query_one("#reach", ReplicaIndicator).set_count(state.reach)
            self.query_one("#temperature", ProprioceptionBar).set_value(state.temperature)
            self.query_one("#trauma", TraumaIndicator).set_level(state.trauma)
        except Exception:
            pass  # Widget not mounted yet

    def set_strain(self, value: float) -> None:
        """Set CPU strain."""
        self._state.strain = value
        try:
            self.query_one("#strain", ProprioceptionBar).set_value(value)
        except Exception:
            pass

    def set_pressure(self, value: float) -> None:
        """Set memory pressure."""
        self._state.pressure = value
        try:
            self.query_one("#pressure", ProprioceptionBar).set_value(value)
        except Exception:
            pass

    def set_reach(self, count: int) -> None:
        """Set replica count."""
        self._state.reach = count
        try:
            self.query_one("#reach", ReplicaIndicator).set_count(count)
        except Exception:
            pass

    def set_temperature(self, value: float) -> None:
        """Set budget temperature."""
        self._state.temperature = value
        try:
            self.query_one("#temperature", ProprioceptionBar).set_value(value)
        except Exception:
            pass

    def set_trauma(self, level: TraumaLevel, message: str = "") -> None:
        """Set trauma level."""
        self._state.trauma = level
        try:
            self.query_one("#trauma", TraumaIndicator).set_level(level, message)
        except Exception:
            pass

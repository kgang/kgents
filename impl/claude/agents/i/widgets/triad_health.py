"""
TriadHealthWidget - Displays Database Triad health status.

Renders the three triad layers as compact colored bars:
- Durability (PostgreSQL): Green/sage gradient - "Is truth safe?"
- Resonance (Qdrant): Blue/cyan gradient - "Is meaning accessible?"
- Reflex (Redis): Amber/gold gradient - "Is it fast?"

Also displays:
- CDC lag (coherency_with_truth)
- Synapse status
- Outbox queue depth

AGENTESE: self.vitals.triad.manifest
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from textual.reactive import reactive
from textual.widget import Widget

if TYPE_CHECKING:
    from textual.app import RenderResult


# Characters for health bar rendering
BAR_FULL = "█"
BAR_EMPTY = "░"
BAR_PARTIAL = "▓▒"


@dataclass
class TriadHealth:
    """Health status of the Database Triad."""

    # Layer health (0.0-1.0)
    durability: float = 0.0  # PostgreSQL
    resonance: float = 0.0  # Qdrant
    reflex: float = 0.0  # Redis

    # CDC metrics
    cdc_lag_ms: float = 0.0
    outbox_pending: int = 0
    synapse_active: bool = False

    # Timestamps
    last_sync: datetime | None = None
    last_check: datetime | None = None

    @property
    def coherency_with_truth(self) -> float:
        """
        Calculate coherency with truth.

        Formula: 1.0 - (lag_ms / 5000)
        - 0ms lag = 1.0 (perfect coherency)
        - 5000ms lag = 0.0 (threshold)
        """
        return max(0.0, 1.0 - (self.cdc_lag_ms / 5000))

    @property
    def overall(self) -> float:
        """Overall triad health (average of layers)."""
        return (self.durability + self.resonance + self.reflex) / 3

    @property
    def status_text(self) -> str:
        """Human-readable status."""
        if self.overall >= 0.9:
            return "HEALTHY"
        elif self.overall >= 0.5:
            return "DEGRADED"
        else:
            return "CRITICAL"


def render_single_bar(
    value: float,
    width: int,
    filled_char: str = BAR_FULL,
    empty_char: str = BAR_EMPTY,
) -> str:
    """Render a single health bar."""
    filled = int(value * width)
    empty = width - filled
    return filled_char * filled + empty_char * empty


class TriadHealthWidget(Widget):
    """
    Displays Database Triad health as three compact bars.

    Layout:
        ┌── Triad Health ──┐
        │ D ████████░░ PG  │
        │ R ██████░░░░ Qd  │
        │ F █████████░ Rd  │
        │ Coherency: 92%   │
        │ Lag: 127ms       │
        └──────────────────┘

    Where:
        D = Durability (PostgreSQL)
        R = Resonance (Qdrant)
        F = Reflex (Redis)
    """

    DEFAULT_CSS = """
    TriadHealthWidget {
        width: auto;
        height: auto;
        min-height: 6;
        padding: 0 1;
        border: round $surface;
    }

    TriadHealthWidget .durability {
        color: #7d9c7a;  /* Muted sage - durability */
    }

    TriadHealthWidget .resonance {
        color: #8ac4e8;  /* Sky blue - resonance */
    }

    TriadHealthWidget .reflex {
        color: #e6a352;  /* Warm amber - reflex */
    }

    TriadHealthWidget .coherency-high {
        color: #7d9c7a;  /* Sage for high coherency */
    }

    TriadHealthWidget .coherency-medium {
        color: #e6a352;  /* Amber for medium */
    }

    TriadHealthWidget .coherency-low {
        color: #e88a8a;  /* Salmon for low */
    }

    TriadHealthWidget .title {
        color: #6b7e5e;  /* Olive green for title */
        text-style: bold;
    }
    """

    # Reactive health values
    durability: reactive[float] = reactive(0.0)
    resonance: reactive[float] = reactive(0.0)
    reflex: reactive[float] = reactive(0.0)
    cdc_lag_ms: reactive[float] = reactive(0.0)
    outbox_pending: reactive[int] = reactive(0)
    synapse_active: reactive[bool] = reactive(False)

    def __init__(
        self,
        health: TriadHealth | None = None,
        bar_width: int = 8,
        show_title: bool = True,
        compact: bool = False,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.bar_width = bar_width
        self.show_title = show_title
        self.compact = compact

        if health:
            self.update_health(health)

    def update_health(self, health: TriadHealth) -> None:
        """Update the displayed health values."""
        self.durability = health.durability
        self.resonance = health.resonance
        self.reflex = health.reflex
        self.cdc_lag_ms = health.cdc_lag_ms
        self.outbox_pending = health.outbox_pending
        self.synapse_active = health.synapse_active

    def watch_durability(self, new_value: float) -> None:
        self.refresh()

    def watch_resonance(self, new_value: float) -> None:
        self.refresh()

    def watch_reflex(self, new_value: float) -> None:
        self.refresh()

    def watch_cdc_lag_ms(self, new_value: float) -> None:
        self.refresh()

    def _coherency(self) -> float:
        """Calculate coherency with truth."""
        return max(0.0, 1.0 - (self.cdc_lag_ms / 5000))

    def render(self) -> "RenderResult":
        """Render the triad health bars."""
        lines: list[str] = []

        if self.show_title:
            lines.append("─── Triad Health ───")

        # Layer bars
        d_bar = render_single_bar(self.durability, self.bar_width)
        r_bar = render_single_bar(self.resonance, self.bar_width)
        f_bar = render_single_bar(self.reflex, self.bar_width)

        lines.append(f"D {d_bar} PG")
        lines.append(f"R {r_bar} Qd")
        lines.append(f"F {f_bar} Rd")

        if not self.compact:
            # Coherency
            coherency = self._coherency()
            coherency_pct = int(coherency * 100)
            lines.append(f"Coherency: {coherency_pct}%")

            # CDC lag
            if self.cdc_lag_ms < 1000:
                lag_str = f"{int(self.cdc_lag_ms)}ms"
            else:
                lag_str = f"{self.cdc_lag_ms / 1000:.1f}s"
            lines.append(f"Lag: {lag_str}")

            # Outbox
            if self.outbox_pending > 0:
                lines.append(f"Outbox: {self.outbox_pending}")

            # Synapse status
            synapse_status = "●" if self.synapse_active else "○"
            lines.append(f"Synapse: {synapse_status}")

        return "\n".join(lines)


class CompactTriadHealth(Widget):
    """
    Compact single-line triad health display.

    Layout: D:87% R:92% F:78% [●]
    """

    DEFAULT_CSS = """
    CompactTriadHealth {
        width: auto;
        height: 1;
        padding: 0;
        color: #b3a89a;  /* Dusty tan - secondary text */
    }

    CompactTriadHealth .healthy {
        color: #7d9c7a;
    }

    CompactTriadHealth .degraded {
        color: #e6a352;
    }

    CompactTriadHealth .critical {
        color: #e88a8a;
    }
    """

    durability: reactive[float] = reactive(0.0)
    resonance: reactive[float] = reactive(0.0)
    reflex: reactive[float] = reactive(0.0)
    synapse_active: reactive[bool] = reactive(False)

    def __init__(
        self,
        health: TriadHealth | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        if health:
            self.update_health(health)

    def update_health(self, health: TriadHealth) -> None:
        """Update the displayed health values."""
        self.durability = health.durability
        self.resonance = health.resonance
        self.reflex = health.reflex
        self.synapse_active = health.synapse_active
        self._update_class()

    def _update_class(self) -> None:
        """Update CSS class based on health level."""
        overall = (self.durability + self.resonance + self.reflex) / 3
        self.remove_class("healthy", "degraded", "critical")
        if overall >= 0.8:
            self.add_class("healthy")
        elif overall >= 0.5:
            self.add_class("degraded")
        else:
            self.add_class("critical")

    def watch_durability(self, new_value: float) -> None:
        self._update_class()
        self.refresh()

    def watch_resonance(self, new_value: float) -> None:
        self._update_class()
        self.refresh()

    def watch_reflex(self, new_value: float) -> None:
        self._update_class()
        self.refresh()

    def watch_synapse_active(self, new_value: bool) -> None:
        self.refresh()

    def render(self) -> "RenderResult":
        """Render the compact health display."""
        synapse = "●" if self.synapse_active else "○"
        return (
            f"D:{int(self.durability * 100):2d}% "
            f"R:{int(self.resonance * 100):2d}% "
            f"F:{int(self.reflex * 100):2d}% "
            f"[{synapse}]"
        )


class MiniTriadHealth(Widget):
    """
    Minimal inline triad health using block characters.

    Layout: ▓▓▓▒░ (overall triad health in 5 chars)
    """

    DEFAULT_CSS = """
    MiniTriadHealth {
        width: 5;
        height: 1;
        padding: 0;
    }

    MiniTriadHealth.healthy {
        color: #7d9c7a;
    }

    MiniTriadHealth.degraded {
        color: #e6a352;
    }

    MiniTriadHealth.critical {
        color: #e88a8a;
    }
    """

    overall: reactive[float] = reactive(0.0)

    def __init__(
        self,
        health: TriadHealth | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        if health:
            self.overall = health.overall
        self._update_class()

    def update_health(self, health: TriadHealth) -> None:
        """Update the displayed health value."""
        self.overall = health.overall

    def _update_class(self) -> None:
        """Update CSS class based on health level."""
        self.remove_class("healthy", "degraded", "critical")
        if self.overall >= 0.8:
            self.add_class("healthy")
        elif self.overall >= 0.5:
            self.add_class("degraded")
        else:
            self.add_class("critical")

    def watch_overall(self, new_value: float) -> None:
        """React to health changes."""
        self._update_class()
        self.refresh()

    def render(self) -> "RenderResult":
        """Render the mini health bar."""
        chars = "░▒▓█"
        filled = int(self.overall * 5)
        result = ""
        for i in range(5):
            if i < filled:
                result += chars[3]
            elif i == filled:
                remainder = (self.overall * 5) - filled
                char_idx = int(remainder * 3)
                result += chars[char_idx]
            else:
                result += chars[0]
        return result


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TriadHealth",
    "TriadHealthWidget",
    "CompactTriadHealth",
    "MiniTriadHealth",
]

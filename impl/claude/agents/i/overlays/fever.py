"""
FeverOverlay - Visualizes entropy and fever events.

When the system runs hot (entropy > threshold), this overlay appears,
showing the fever state, oblique strategies, and the entropy gradient.

The Accursed Share principle: surplus must be spent, not suppressed.
This overlay is the visual manifestation of that spending.

Features:
- Entropy gauge with color-coded state
- Current oblique strategy display
- Fever event history
- Visual distortion based on entropy level

Usage:
    # Push as modal when entropy exceeds threshold
    app.push_screen(FeverOverlay(entropy=0.85, fever_event=event))

Keybindings:
    Esc     - Close overlay
    Space   - Draw new oblique strategy
    D       - Trigger fever dream (LLM-based)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agents.i.screens.base import KgentsModalScreen
from agents.i.widgets.entropy import entropy_to_border_style, entropy_to_params
from protocols.agentese.metabolism.fever import FeverEvent, FeverStream
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Container, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Static

# =============================================================================
# Entropy State
# =============================================================================


@dataclass
class EntropyState:
    """Current entropy state for visualization."""

    entropy: float  # 0.0 to 1.0
    last_fever_event: FeverEvent | None = None
    fever_stream: FeverStream = field(default_factory=FeverStream)
    history: list[tuple[datetime, str]] = field(default_factory=list)

    @property
    def state_name(self) -> str:
        """Human-readable state name."""
        if self.entropy < 0.3:
            return "calm"
        elif self.entropy < 0.6:
            return "warming"
        elif self.entropy < 0.85:
            return "hot"
        else:
            return "fever"

    @property
    def state_color(self) -> str:
        """Textual color for current state."""
        if self.entropy < 0.3:
            return "green"
        elif self.entropy < 0.6:
            return "yellow"
        elif self.entropy < 0.85:
            return "orange"
        else:
            return "red"


# =============================================================================
# Gauge Widget
# =============================================================================


class EntropyGauge(Static):
    """
    Visual gauge showing entropy level.

    Displays as a horizontal bar with color-coded sections:
    [████████░░░░░░░░░░░░] 40% warming

    The bar character changes with entropy level:
    - Low: solid blocks (█)
    - Medium: medium shade (▓)
    - High: light shade (░)
    """

    entropy: reactive[float] = reactive(0.0)

    def render(self) -> str:
        """Render the entropy gauge."""
        width = 30
        filled = int(self.entropy * width)
        empty = width - filled

        # Choose fill character based on entropy
        if self.entropy < 0.3:
            fill_char = "█"
        elif self.entropy < 0.6:
            fill_char = "▓"
        elif self.entropy < 0.85:
            fill_char = "▒"
        else:
            fill_char = "░"

        bar = fill_char * filled + "░" * empty
        pct = int(self.entropy * 100)

        state = EntropyState(self.entropy)
        return f"[{bar}] {pct}% {state.state_name}"


# =============================================================================
# Oblique Strategy Display
# =============================================================================


class ObliqueDisplay(Static):
    """Displays the current oblique strategy."""

    strategy: reactive[str] = reactive("Honor thy error as a hidden intention.")

    def render(self) -> str:
        """Render the strategy with quotes."""
        return f'"{self.strategy}"'


# =============================================================================
# Fever Overlay
# =============================================================================


class FeverOverlay(KgentsModalScreen[None]):
    """
    Modal overlay for entropy/fever visualization.

    Appears when entropy exceeds threshold, showing:
    - Current entropy gauge
    - Oblique strategy
    - Visual distortion effects
    """

    DEFAULT_CSS = """
    FeverOverlay {
        align: center middle;
    }

    FeverOverlay > Container {
        width: 60;
        height: auto;
        max-height: 80%;
        padding: 1 2;
    }

    FeverOverlay.calm > Container {
        border: solid green;
        background: $surface;
    }

    FeverOverlay.warming > Container {
        border: solid yellow;
        background: $surface;
    }

    FeverOverlay.hot > Container {
        border: double orange;
        background: $surface-darken-1;
    }

    FeverOverlay.fever > Container {
        border: thick red;
        background: $surface-darken-2;
    }

    FeverOverlay .title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    FeverOverlay .gauge {
        text-align: center;
        margin: 1 0;
    }

    FeverOverlay .oblique {
        text-align: center;
        text-style: italic;
        color: $text-muted;
        margin: 2 1;
        padding: 1;
    }

    FeverOverlay.fever .oblique {
        color: $warning;
        text-style: bold italic;
    }

    FeverOverlay .instructions {
        text-align: center;
        color: $text-disabled;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("space", "draw_oblique", "Draw Strategy"),
        Binding("d", "dream", "Fever Dream"),
    ]

    def __init__(
        self,
        entropy: float = 0.0,
        fever_event: FeverEvent | None = None,
        name: str | None = None,
    ) -> None:
        """
        Initialize fever overlay.

        Args:
            entropy: Current entropy level (0.0 to 1.0)
            fever_event: Optional active fever event
            name: Optional widget name
        """
        super().__init__(name=name)
        self.state = EntropyState(entropy=entropy, last_fever_event=fever_event)
        self._gauge = EntropyGauge(classes="gauge")
        self._oblique = ObliqueDisplay(classes="oblique")
        self._instructions = Static(
            "[Space] Draw  [D] Dream  [Esc] Close",
            classes="instructions",
        )

        # Initialize gauge
        self._gauge.entropy = entropy

        # Set initial oblique
        if fever_event and fever_event.oblique_strategy:
            self._oblique.strategy = fever_event.oblique_strategy
        else:
            self._oblique.strategy = self.state.fever_stream.oblique()

    def compose(self) -> ComposeResult:
        """Compose the overlay content."""
        with Container():
            yield Static(self._get_title(), classes="title")
            yield self._gauge
            yield self._oblique
            yield self._instructions

    def _get_title(self) -> str:
        """Get title based on entropy state."""
        state = self.state.state_name
        return {
            "calm": "Entropy Pool",
            "warming": "Entropy Rising",
            "hot": "System Running Hot",
            "fever": "FEVER STATE",
        }.get(state, "Entropy")

    def on_mount(self) -> None:
        """Apply state-based styling on mount."""
        self.add_class(self.state.state_name)

    def action_draw_oblique(self) -> None:
        """Draw a new oblique strategy."""
        self._oblique.strategy = self.state.fever_stream.oblique()
        self.state.history.append((datetime.now(), self._oblique.strategy))

    async def action_dream(self) -> None:
        """Trigger a fever dream (requires LLM)."""
        # In a full implementation, this would call FeverStream.dream()
        # For now, we use oblique as fallback
        dream = await self.state.fever_stream.dream(
            {
                "entropy": self.state.entropy,
                "state": self.state.state_name,
            }
        )
        self._oblique.strategy = dream
        self.state.history.append((datetime.now(), f"[dream] {dream}"))

    def update_entropy(self, new_entropy: float) -> None:
        """Update entropy level and visual state."""
        old_state = self.state.state_name
        self.state = EntropyState(
            entropy=new_entropy,
            fever_stream=self.state.fever_stream,
            history=self.state.history,
        )
        self._gauge.entropy = new_entropy

        # Update class if state changed
        new_state = self.state.state_name
        if old_state != new_state:
            self.remove_class(old_state)
            self.add_class(new_state)


# =============================================================================
# Factory Functions
# =============================================================================


def create_fever_overlay(
    entropy: float,
    fever_event: FeverEvent | None = None,
) -> FeverOverlay:
    """
    Create a FeverOverlay instance.

    Args:
        entropy: Current entropy level
        fever_event: Optional active fever event

    Returns:
        Configured FeverOverlay
    """
    return FeverOverlay(entropy=entropy, fever_event=fever_event)


def should_show_fever_overlay(entropy: float, threshold: float = 0.7) -> bool:
    """
    Determine if fever overlay should be shown.

    Args:
        entropy: Current entropy level
        threshold: Threshold above which to show overlay

    Returns:
        True if overlay should be shown
    """
    return entropy > threshold


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "EntropyState",
    "EntropyGauge",
    "ObliqueDisplay",
    "FeverOverlay",
    "create_fever_overlay",
    "should_show_fever_overlay",
]

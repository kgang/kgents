"""
ProcessingWaveform Widget - Visualizes agent processing patterns.

The waveform shape reflects the type of cognitive operation:
- Logical: Square wave (╭╮╭╮╭╮) - discrete, deterministic
- Creative: Noisy sine (~∿~∿~) - exploratory, probabilistic
- Waiting: Flat line (──────) - idle, no processing

This is the key visual component of the WIRE overlay.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

if TYPE_CHECKING:
    from textual.app import RenderResult


class OperationType(Enum):
    """Type of cognitive operation being performed."""

    LOGICAL = "LOGICAL"  # Deterministic, step-by-step
    CREATIVE = "CREATIVE"  # Exploratory, generative
    WAITING = "WAITING"  # Idle, awaiting input
    ERROR = "ERROR"  # Processing error


# Waveform patterns by operation type
WAVEFORM_PATTERNS = {
    OperationType.LOGICAL: "╭╮╭╮╭╮╭╮╭╮╭╮╭╮╭╮╭╮╭╮╭╮╭╮╭╮╭╮╭╮╭╮",
    OperationType.CREATIVE: "~∿~∿~∿~∿~∿~∿~∿~∿~∿~∿~∿~∿~∿~∿~∿~∿",
    OperationType.WAITING: "────────────────────────────────────",
    OperationType.ERROR: "▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░▓░",
}

# Labels for each operation type
OPERATION_LABELS = {
    OperationType.LOGICAL: "logical: square wave",
    OperationType.CREATIVE: "creative: noisy sine",
    OperationType.WAITING: "idle: flat line",
    OperationType.ERROR: "error: glitch pattern",
}


def generate_waveform(
    width: int,
    operation_type: OperationType = OperationType.WAITING,
    offset: int = 0,
) -> str:
    """
    Generate a waveform string of the given width.

    Args:
        width: Width of the waveform in characters
        operation_type: Type of operation (affects pattern)
        offset: Animation offset for scrolling effect

    Returns:
        String of waveform characters
    """
    pattern = WAVEFORM_PATTERNS.get(
        operation_type, WAVEFORM_PATTERNS[OperationType.WAITING]
    )

    # Create a seamless loop by repeating the pattern
    extended_pattern = pattern * ((width // len(pattern)) + 2)

    # Apply offset for animation
    start = offset % len(pattern)
    return extended_pattern[start : start + width]


class ProcessingWaveform(Widget):
    """
    Renders the processing waveform based on operation type.

    The waveform animates when processing is active, giving
    a sense of cognitive flow.
    """

    DEFAULT_CSS = """
    ProcessingWaveform {
        width: 100%;
        height: 3;
        padding: 0 1;
    }

    ProcessingWaveform.logical {
        color: #8ac4e8;  /* Sky blue for logical */
    }

    ProcessingWaveform.creative {
        color: #e88a8a;  /* Salmon pink for creative */
    }

    ProcessingWaveform.waiting {
        color: #6a6560;  /* Dim for waiting */
    }

    ProcessingWaveform.error {
        color: #6b4b8a;  /* Purple for error */
    }
    """

    # Reactive properties
    operation_type: reactive[OperationType] = reactive(OperationType.WAITING)
    animating: reactive[bool] = reactive(False)
    animation_offset: reactive[int] = reactive(0)
    label: reactive[str] = reactive("")

    def __init__(
        self,
        operation_type: OperationType = OperationType.WAITING,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.operation_type = operation_type
        self.label = OPERATION_LABELS.get(operation_type, "")
        self._update_classes()

    def _update_classes(self) -> None:
        """Update CSS classes based on operation type."""
        self.remove_class("logical", "creative", "waiting", "error")
        class_map = {
            OperationType.LOGICAL: "logical",
            OperationType.CREATIVE: "creative",
            OperationType.WAITING: "waiting",
            OperationType.ERROR: "error",
        }
        css_class = class_map.get(self.operation_type, "waiting")
        self.add_class(css_class)

    def watch_operation_type(self, new_value: OperationType) -> None:
        """React to operation type changes."""
        self.label = OPERATION_LABELS.get(new_value, "")
        self._update_classes()
        self.refresh()

    def watch_animation_offset(self, new_value: int) -> None:
        """React to animation offset changes."""
        self.refresh()

    def render(self) -> "RenderResult":
        """Render the waveform."""
        width = max(20, self.size.width - 2)
        waveform = generate_waveform(width, self.operation_type, self.animation_offset)

        # Include label on second line
        label_line = f"({self.label})" if self.label else ""

        return f"{waveform}\n{label_line}"

    def set_operation(self, operation_type: OperationType) -> None:
        """Set the operation type."""
        self.operation_type = operation_type

    async def start_animation(self, interval_ms: int = 100) -> None:
        """Start the waveform animation."""
        if self.animating:
            return
        self.animating = True
        self._animate_timer = self.set_interval(
            interval_ms / 1000.0,
            self._animate_step,
        )

    def _animate_step(self) -> None:
        """Perform one animation step."""
        if self.animating:
            self.animation_offset += 1

    def stop_waveform_animation(self) -> None:
        """Stop the waveform animation."""
        self.animating = False
        if hasattr(self, "_animate_timer"):
            self._animate_timer.stop()

    def pulse(self, intensity: float = 1.0) -> None:
        """
        Trigger a visual pulse on the waveform.

        This is called by FluxReflector when a PheromoneEvent arrives.
        The pulse effect momentarily increases animation speed or
        bumps the offset to create a visual "beat".

        Args:
            intensity: Pulse intensity from 0.0 to 1.0 (higher = stronger)
        """
        # Bump the animation offset based on intensity
        # This creates an immediate visual "jump" in the waveform
        bump = int(3 + intensity * 5)  # 3-8 character jump
        self.animation_offset += bump

        # If creative mode, temporarily increase offset more
        if self.operation_type == OperationType.CREATIVE:
            self.animation_offset += int(intensity * 3)

        self.refresh()


class WaveformDisplay(Widget):
    """
    Compound widget: waveform with border and title.

    Used in the WIRE overlay.
    """

    DEFAULT_CSS = """
    WaveformDisplay {
        width: 100%;
        height: 5;
        border: solid #4a4a5c;
        padding: 0 1;
    }

    WaveformDisplay .waveform-title {
        color: #b3a89a;
        text-style: bold;
    }
    """

    title: reactive[str] = reactive("Processing Waveform")

    def __init__(
        self,
        operation_type: OperationType = OperationType.WAITING,
        title: str = "Processing Waveform",
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._operation_type = operation_type
        self.title = title

    def compose(self) -> ComposeResult:
        """Compose the waveform display."""
        yield Static(f"─ {self.title} ─", classes="waveform-title")
        yield ProcessingWaveform(operation_type=self._operation_type, id="waveform")

    def set_operation(self, operation_type: OperationType) -> None:
        """Set the operation type on the internal waveform."""
        waveform = self.query_one("#waveform", ProcessingWaveform)
        waveform.set_operation(operation_type)

    async def start_animation(self, interval_ms: int = 100) -> None:
        """Start animation on the internal waveform."""
        waveform = self.query_one("#waveform", ProcessingWaveform)
        await waveform.start_animation(interval_ms)

    def stop_waveform_animation(self) -> None:
        """Stop animation on the internal waveform."""
        waveform = self.query_one("#waveform", ProcessingWaveform)
        waveform.stop_waveform_animation()

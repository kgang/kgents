"""
Slider Widget - Direct manipulation for continuous values.

Direct manipulation for entropy/temperature. Drag or keyboard to adjust
agent creativity in real-time.

WHAT: A horizontal slider for continuous value selection.
WHY: Direct manipulation is joy-inducing. Feeling the agent's temperature
     change as you drag is more visceral than typing a number.
HOW: Slider(value=0.7, min_val=0.0, max_val=1.0, label="Temperature")
FEEL: Like a physical knob. The resistance at the boundaries is satisfying.
      You feel the range, not just see it.

Navigation:
  - h/left: Decrease value by step
  - l/right: Increase value by step
  - H: Jump to minimum
  - L: Jump to maximum
  - 0-9: Set to that fraction (0=0%, 5=50%, 9=90%)

Principle 4 (Joy-Inducing): Direct manipulation feels playful.
Principle 6 (Heterarchical): Agent temperature is agent-controlled, slider is view.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from textual.reactive import reactive
from textual.widget import Widget

if TYPE_CHECKING:
    from textual.app import RenderResult


# Slider track characters
SLIDER_CHARS = {
    "track_empty": "─",
    "track_filled": "━",
    "thumb": "●",
    "left_cap": "○",
    "right_cap": "○",
    "boundary_left": "[",
    "boundary_right": "]",
}


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value to range [min_val, max_val]."""
    return max(min_val, min(max_val, value))


def generate_slider_track(
    value: float,
    min_val: float,
    max_val: float,
    width: int,
    show_value: bool = True,
    label: str = "",
) -> str:
    """
    Generate slider track visualization.

    Args:
        value: Current value
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        width: Total width in characters
        show_value: Whether to show numeric value
        label: Label to display

    Returns:
        Rendered slider string
    """
    # Normalize value to 0-1
    range_val = max_val - min_val
    if range_val <= 0:
        normalized = 0.5
    else:
        normalized = clamp((value - min_val) / range_val, 0.0, 1.0)

    # Calculate track width (minus caps and value display)
    value_str = f" {value:.2f}" if show_value else ""
    label_str = f"{label}: " if label else ""
    overhead = len(label_str) + len(value_str) + 2  # 2 for caps
    track_width = max(5, width - overhead)

    # Calculate thumb position
    thumb_pos = int(normalized * (track_width - 1))
    thumb_pos = int(clamp(float(thumb_pos), 0.0, float(track_width - 1)))

    # Build track
    track = []
    for i in range(track_width):
        if i == thumb_pos:
            track.append(SLIDER_CHARS["thumb"])
        elif i < thumb_pos:
            track.append(SLIDER_CHARS["track_filled"])
        else:
            track.append(SLIDER_CHARS["track_empty"])

    track_str = "".join(track)

    return f"{label_str}{SLIDER_CHARS['left_cap']}{track_str}{SLIDER_CHARS['right_cap']}{value_str}"


class Slider(Widget):
    """
    Horizontal slider for continuous value selection.

    Direct manipulation widget for adjusting agent parameters like
    temperature, entropy threshold, or any continuous value.

    Supports keyboard navigation (h/l or arrows) and numeric shortcuts (0-9).
    Emits callbacks when value changes for reactive updates.

    Principle 4 (Joy-Inducing): Direct manipulation is satisfying.
    """

    DEFAULT_CSS = """
    Slider {
        width: 100%;
        height: 1;
        color: #d4a574;
    }

    Slider:focus {
        color: #f5d08a;
    }

    Slider.active {
        color: #e6a352;
    }

    Slider .thumb {
        color: #f5f0e6;
        text-style: bold;
    }

    Slider .track-filled {
        color: #e6a352;
    }

    Slider .track-empty {
        color: #4a4a5c;
    }
    """

    BINDINGS = [
        ("h", "decrease", "Decrease"),
        ("l", "increase", "Increase"),
        ("left", "decrease", "Decrease"),
        ("right", "increase", "Increase"),
        ("H", "jump_min", "Min"),
        ("L", "jump_max", "Max"),
        ("0", "set_0", "0%"),
        ("1", "set_10", "10%"),
        ("2", "set_20", "20%"),
        ("3", "set_30", "30%"),
        ("4", "set_40", "40%"),
        ("5", "set_50", "50%"),
        ("6", "set_60", "60%"),
        ("7", "set_70", "70%"),
        ("8", "set_80", "80%"),
        ("9", "set_90", "90%"),
    ]

    # Reactive properties
    value: reactive[float] = reactive(0.5)
    min_val: reactive[float] = reactive(0.0)
    max_val: reactive[float] = reactive(1.0)
    step: reactive[float] = reactive(0.1)
    label: reactive[str] = reactive("")
    show_value: reactive[bool] = reactive(True)

    def __init__(
        self,
        value: float = 0.5,
        min_val: float = 0.0,
        max_val: float = 1.0,
        step: float = 0.1,
        label: str = "",
        show_value: bool = True,
        on_change: Callable[[float], None] | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        """
        Initialize slider widget.

        Args:
            value: Initial value
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            step: Step size for keyboard navigation
            label: Label to display before slider
            show_value: Whether to show numeric value after slider
            on_change: Callback when value changes
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        # Set callback first to avoid AttributeError in watcher
        self._on_change = on_change
        # Set range before value so clamping works correctly
        self.min_val = min_val
        self.max_val = max_val
        self.value = clamp(value, min_val, max_val)
        self.step = step
        self.label = label
        self.show_value = show_value

    def render(self) -> "RenderResult":
        """Render the slider."""
        width = max(20, self.size.width)
        return generate_slider_track(
            self.value,
            self.min_val,
            self.max_val,
            width,
            self.show_value,
            self.label,
        )

    def watch_value(self, new_value: float) -> None:
        """React to value changes."""
        # Clamp to range
        clamped = clamp(new_value, self.min_val, self.max_val)
        if clamped != new_value:
            self.value = clamped
            return

        # Call callback
        if self._on_change:
            self._on_change(new_value)

        self.refresh()

    def watch_min_val(self, new_min: float) -> None:
        """React to min_val changes."""
        # Re-clamp value
        self.value = clamp(self.value, new_min, self.max_val)
        self.refresh()

    def watch_max_val(self, new_max: float) -> None:
        """React to max_val changes."""
        # Re-clamp value
        self.value = clamp(self.value, self.min_val, new_max)
        self.refresh()

    def watch_label(self, new_label: str) -> None:
        """React to label changes."""
        self.refresh()

    def watch_show_value(self, new_show: bool) -> None:
        """React to show_value changes."""
        self.refresh()

    # ─────────────────────────────────────────────────────────────
    # Actions (keyboard bindings)
    # ─────────────────────────────────────────────────────────────

    def action_decrease(self) -> None:
        """Decrease value by step."""
        self.value = clamp(self.value - self.step, self.min_val, self.max_val)

    def action_increase(self) -> None:
        """Increase value by step."""
        self.value = clamp(self.value + self.step, self.min_val, self.max_val)

    def action_jump_min(self) -> None:
        """Jump to minimum value."""
        self.value = self.min_val

    def action_jump_max(self) -> None:
        """Jump to maximum value."""
        self.value = self.max_val

    def _set_percentage(self, percentage: float) -> None:
        """Set value to a percentage of the range."""
        range_val = self.max_val - self.min_val
        self.value = self.min_val + range_val * percentage

    def action_set_0(self) -> None:
        """Set to 0%."""
        self._set_percentage(0.0)

    def action_set_10(self) -> None:
        """Set to 10%."""
        self._set_percentage(0.1)

    def action_set_20(self) -> None:
        """Set to 20%."""
        self._set_percentage(0.2)

    def action_set_30(self) -> None:
        """Set to 30%."""
        self._set_percentage(0.3)

    def action_set_40(self) -> None:
        """Set to 40%."""
        self._set_percentage(0.4)

    def action_set_50(self) -> None:
        """Set to 50%."""
        self._set_percentage(0.5)

    def action_set_60(self) -> None:
        """Set to 60%."""
        self._set_percentage(0.6)

    def action_set_70(self) -> None:
        """Set to 70%."""
        self._set_percentage(0.7)

    def action_set_80(self) -> None:
        """Set to 80%."""
        self._set_percentage(0.8)

    def action_set_90(self) -> None:
        """Set to 90%."""
        self._set_percentage(0.9)

    # ─────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────

    def set_value(self, value: float) -> None:
        """
        Set the slider value.

        Args:
            value: New value (will be clamped to range)
        """
        self.value = clamp(value, self.min_val, self.max_val)

    def set_range(self, min_val: float, max_val: float) -> None:
        """
        Set the value range.

        Args:
            min_val: New minimum value
            max_val: New maximum value
        """
        self.min_val = min_val
        self.max_val = max_val
        # Re-clamp value
        self.value = clamp(self.value, min_val, max_val)

    def set_callback(self, callback: Callable[[float], None] | None) -> None:
        """
        Set the on_change callback.

        Args:
            callback: Function called when value changes
        """
        self._on_change = callback

    def get_normalized_value(self) -> float:
        """
        Get value normalized to 0-1 range.

        Returns:
            Value as 0.0-1.0 regardless of actual min/max
        """
        range_val = self.max_val - self.min_val
        if range_val <= 0:
            return 0.5
        return (self.value - self.min_val) / range_val

    def set_normalized_value(self, normalized: float) -> None:
        """
        Set value from normalized 0-1 range.

        Args:
            normalized: Value in 0.0-1.0 range
        """
        range_val = self.max_val - self.min_val
        self.value = self.min_val + range_val * clamp(normalized, 0.0, 1.0)


# Export public API
__all__ = [
    "Slider",
    "generate_slider_track",
    "clamp",
    "SLIDER_CHARS",
]

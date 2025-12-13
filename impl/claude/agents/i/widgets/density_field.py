"""
DensityField Widget - Renders agents as density clusters.

The core visual innovation of I-gent v2.5: agents are not boxes,
they are currents of cognition rendered as block element clusters.

Activity level 0.0-1.0 maps to block density:
  0.0-0.2: idle (light shade, sparse)
  0.2-0.5: waking (transitioning)
  0.5-0.8: active (medium-high density)
  0.8-1.0: intense (full blocks, pulsing)
  void:    glitched (dithered pattern)
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from textual.reactive import reactive
from textual.widget import Widget

if TYPE_CHECKING:
    from textual.app import RenderResult

from ..data.core_types import Phase
from ..theme.earth import EarthTheme
from .entropy import entropy_to_params

# Re-export Phase for backwards compatibility
__all__ = ["Phase", "DensityField", "DENSITY_CHARS", "GLITCH_CHARS"]

# Block characters for density rendering (lightest to densest)
DENSITY_CHARS = " ░▒▓█"

# Dither patterns for void/glitch state
GLITCH_CHARS = "▚▞▛▜▙▟"

# Zalgo combining characters for glitch effect
ZALGO_ABOVE = [
    "\u0300",
    "\u0301",
    "\u0302",
    "\u0303",
    "\u0304",
    "\u0305",
    "\u0306",
    "\u0307",
    "\u0308",
    "\u0309",
    "\u030a",
    "\u030b",
]
ZALGO_BELOW = [
    "\u0316",
    "\u0317",
    "\u0318",
    "\u0319",
    "\u031a",
    "\u031b",
    "\u031c",
    "\u031d",
    "\u031e",
    "\u031f",
    "\u0320",
    "\u0321",
]


def activity_to_density_char(activity: float, x: int, y: int) -> str:
    """
    Map activity level to a density character.

    Uses position-based variation for organic texture.
    """
    # Add slight position-based variation for texture
    noise = ((x * 7 + y * 13) % 5) / 10.0
    varied_activity = max(0.0, min(1.0, activity + noise - 0.2))
    idx = min(4, int(varied_activity * 5))

    return DENSITY_CHARS[idx]


def generate_density_grid(
    width: int,
    height: int,
    activity: float,
    phase: Phase,
    name: str = "",
    focused: bool = False,
    dither_rate: float = 0.0,
    jitter: int = 0,
) -> list[str]:
    """
    Generate a density grid for an agent.

    Args:
        width: Grid width in characters
        height: Grid height in characters
        activity: Activity level 0.0-1.0
        phase: Current phase
        name: Agent name to embed
        focused: Whether widget is focused
        dither_rate: Entropy-based dithering (0.0-0.4)
        jitter: Entropy-based position jitter (0-3 pixels)

    Returns:
        List of strings, one per row
    """
    lines: list[str] = []

    if phase == Phase.VOID:
        # Glitch pattern for void state
        for y in range(height):
            row = ""
            for x in range(width):
                row += random.choice(GLITCH_CHARS)
            lines.append(row)
        return lines

    # Normal density rendering with optional dithering
    for y in range(height):
        row = ""
        for x in range(width):
            char = activity_to_density_char(activity, x, y)

            # Apply dithering based on entropy
            if dither_rate > 0 and random.random() < dither_rate:
                # Randomly shift character up or down in density
                if random.random() < 0.5 and char != DENSITY_CHARS[0]:
                    # Reduce density
                    idx = DENSITY_CHARS.index(char)
                    char = DENSITY_CHARS[max(0, idx - 1)]
                elif char != DENSITY_CHARS[-1]:
                    # Increase density
                    idx = DENSITY_CHARS.index(char)
                    char = DENSITY_CHARS[min(len(DENSITY_CHARS) - 1, idx + 1)]

            row += char
        lines.append(row)

    # Embed name in center if there's room
    if name and height >= 3 and width >= len(name) + 4:
        center_y = height // 2
        center_x = (width - len(name)) // 2

        # Create name row with surrounding density
        name_row = list(lines[center_y])
        for i, c in enumerate(name):
            if center_x + i < len(name_row):
                name_row[center_x + i] = c
        lines[center_y] = "".join(name_row)

    return lines


def add_glitch_effect(text: str, intensity: float = 0.3) -> str:
    """
    Add Zalgo-style glitch corruption to text.

    Used when void.* is invoked or on error.
    """
    result = []
    for char in text:
        result.append(char)
        if random.random() < intensity:
            # Add random combining characters
            if random.random() < 0.5:
                result.append(random.choice(ZALGO_ABOVE))
            if random.random() < 0.5:
                result.append(random.choice(ZALGO_BELOW))
    return "".join(result)


class DensityField(Widget):
    """
    Render an agent as a density cluster.

    The density changes based on activity level, creating
    a "weather radar" effect where agents are currents
    of cognition, not static boxes.
    """

    DEFAULT_CSS = """
    DensityField {
        width: auto;
        height: auto;
        min-width: 12;
        min-height: 5;
        padding: 0;
    }

    DensityField:focus {
        background: #252525;
    }

    DensityField.idle {
        color: #4a4a5c;
    }

    DensityField.waking {
        color: #c97b84;
    }

    DensityField.active {
        color: #e6a352;
    }

    DensityField.intense {
        color: #f5d08a;
    }

    DensityField.void {
        color: #6b4b8a;
    }

    DensityField.materializing {
        color: #7d9c7a;  /* Sage for birth */
    }

    DensityField.dematerializing {
        color: #6b4b8a;  /* Purple for void/death */
    }
    """

    # Reactive properties
    activity: reactive[float] = reactive(0.0)
    phase: reactive[Phase] = reactive(Phase.DORMANT)
    agent_name: reactive[str] = reactive("")
    agent_id: reactive[str] = reactive("")
    entropy: reactive[float] = reactive(0.0)  # NEW: Uncertainty level 0.0-1.0
    glitching: reactive[bool] = reactive(False)
    materializing: reactive[bool] = reactive(False)
    dematerializing: reactive[bool] = reactive(False)
    materialization_progress: reactive[float] = reactive(1.0)  # 0.0 to 1.0

    def __init__(
        self,
        agent_id: str = "",
        agent_name: str = "",
        activity: float = 0.0,
        phase: Phase = Phase.DORMANT,
        entropy: float = 0.0,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.activity = activity
        self.phase = phase
        self.entropy = entropy
        # Heartbeat animation state
        self._heartbeat_active = False
        self._pulse_offset = 0.0
        self._update_classes()

    def _update_classes(self) -> None:
        """Update CSS classes based on activity level."""
        # Remove all state classes
        self.remove_class(
            "idle",
            "waking",
            "active",
            "intense",
            "void",
            "materializing",
            "dematerializing",
        )

        if self.materializing:
            self.add_class("materializing")
        elif self.dematerializing:
            self.add_class("dematerializing")
        elif self.phase == Phase.VOID or self.glitching:
            self.add_class("void")
        elif self.activity >= 0.8:
            self.add_class("intense")
        elif self.activity >= 0.5:
            self.add_class("active")
        elif self.activity >= 0.2:
            self.add_class("waking")
        else:
            self.add_class("idle")

    def watch_activity(self, new_value: float) -> None:
        """React to activity changes."""
        self._update_classes()
        self.refresh()

    def watch_phase(self, new_value: Phase) -> None:
        """React to phase changes."""
        self._update_classes()
        self.refresh()

    def watch_glitching(self, new_value: bool) -> None:
        """React to glitch state changes."""
        self._update_classes()
        self.refresh()

    def watch_entropy(self, new_value: float) -> None:
        """React to entropy changes."""
        self.refresh()

    def render(self) -> "RenderResult":
        """Render the density field with entropy-aware distortion."""
        # Get widget dimensions
        width = max(12, self.size.width)
        height = max(3, self.size.height)

        # Compute entropy parameters
        entropy_params = entropy_to_params(self.entropy)

        # Generate density grid
        # During materialization, reduce effective activity based on progress
        effective_activity = self.activity * self.materialization_progress

        grid = generate_density_grid(
            width=width,
            height=height,
            activity=effective_activity,
            phase=self.phase,
            name=self.agent_name.upper()[: width - 4] if self.agent_name else "",
            focused=self.has_focus,
            dither_rate=entropy_params.dither_rate,
            jitter=entropy_params.jitter_amplitude,
        )

        # Apply effects based on state
        if self.glitching or entropy_params.glitch_intensity > 0:
            # Use entropy-based intensity, or override with manual glitching
            intensity = 0.3 if self.glitching else entropy_params.glitch_intensity
            grid = [add_glitch_effect(line, intensity) for line in grid]
        elif self.materializing or self.dematerializing:
            # Apply partial visibility effect during (de)materialization
            grid = self._apply_materialization_effect(grid)

        return "\n".join(grid)

    def _apply_materialization_effect(self, grid: list[str]) -> list[str]:
        """Apply materialization/dematerialization visual effect."""
        result = []
        progress = self.materialization_progress

        for y, line in enumerate(grid):
            new_line = ""
            for x, char in enumerate(line):
                # Random chance to show character based on progress and position
                # Center materializes first, edges last
                center_x = len(line) / 2
                center_y = len(grid) / 2
                dist_from_center = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                max_dist = (center_x**2 + center_y**2) ** 0.5

                # Normalize distance (0 at center, 1 at corner)
                norm_dist = dist_from_center / max_dist if max_dist > 0 else 0

                # Calculate visibility threshold
                if self.materializing:
                    # Center appears first during materialization
                    threshold = 1.0 - progress + norm_dist * 0.5
                else:
                    # Edges disappear first during dematerialization
                    threshold = progress + (1.0 - norm_dist) * 0.5

                if random.random() > threshold:
                    new_line += char
                else:
                    new_line += " "
            result.append(new_line)

        return result

    async def trigger_glitch(self, duration_ms: int = 200) -> None:
        """
        Trigger a glitch effect for the specified duration.

        Called when void.* is invoked or on error.
        This makes the Accursed Share visible.
        """
        self.glitching = True
        self.refresh()

        # Schedule glitch end
        self.set_timer(duration_ms / 1000.0, self._end_glitch)

    def _end_glitch(self) -> None:
        """End the glitch effect."""
        self.glitching = False
        self.refresh()

    def watch_agent_name(self, new_value: str) -> None:
        """React to name changes."""
        self.refresh()

    def set_activity(self, activity: float) -> None:
        """Set activity level (0.0 to 1.0)."""
        self.activity = max(0.0, min(1.0, activity))

    def set_phase(self, phase: Phase) -> None:
        """Set the agent phase."""
        self.phase = phase

    async def materialize(self, duration_ms: int = 500, steps: int = 10) -> None:
        """
        Play materialization animation - agent appears from nothing.

        The agent fades in from center outward.

        Args:
            duration_ms: Total animation duration in milliseconds
            steps: Number of animation steps
        """
        self.materializing = True
        self.materialization_progress = 0.0
        self._update_classes()

        step_duration = duration_ms / steps / 1000.0

        for i in range(steps + 1):
            self.materialization_progress = i / steps
            self.refresh()
            await self._sleep_for_animation(step_duration)

        self.materializing = False
        self.materialization_progress = 1.0
        self._update_classes()
        self.refresh()

    async def dematerialize(self, duration_ms: int = 500, steps: int = 10) -> None:
        """
        Play dematerialization animation - agent fades to nothing.

        The agent fades out from edges inward.

        Args:
            duration_ms: Total animation duration in milliseconds
            steps: Number of animation steps
        """
        self.dematerializing = True
        self.materialization_progress = 1.0
        self._update_classes()

        step_duration = duration_ms / steps / 1000.0

        for i in range(steps + 1):
            self.materialization_progress = 1.0 - (i / steps)
            self.refresh()
            await self._sleep_for_animation(step_duration)

        self.dematerializing = False
        self.materialization_progress = 0.0
        self._update_classes()
        self.refresh()

    async def _sleep_for_animation(self, duration: float) -> None:
        """Sleep helper for animation (using asyncio)."""
        import asyncio

        await asyncio.sleep(duration)

    def watch_materializing(self, new_value: bool) -> None:
        """React to materializing state changes."""
        self._update_classes()
        self.refresh()

    def watch_dematerializing(self, new_value: bool) -> None:
        """React to dematerializing state changes."""
        self._update_classes()
        self.refresh()

    def watch_materialization_progress(self, new_value: float) -> None:
        """React to materialization progress changes."""
        self.refresh()

    # ─────────────────────────────────────────────────────────────
    # Heartbeat Pulsing - Alive agents breathe
    # Principle 4 (Joy-Inducing): Subtle animation that feels alive.
    # ─────────────────────────────────────────────────────────────

    async def start_heartbeat(
        self,
        base_rate_ms: int = 2000,
        amplitude: float = 0.1,
    ) -> None:
        """
        Start heartbeat pulsing animation.

        The agent's activity level subtly pulses, creating a "breathing" effect.
        Rate is derived from base activity - more active agents breathe faster.

        Args:
            base_rate_ms: Base heartbeat period in milliseconds
            amplitude: How much activity varies (0.0-0.2)
        """
        import asyncio
        import math

        self._heartbeat_active = True
        phase = 0.0

        while self._heartbeat_active:
            # Calculate breathing rate based on activity
            # More active = faster breathing
            rate_factor = 0.5 + self.activity * 0.5
            rate_ms = base_rate_ms / rate_factor

            # Sinusoidal pulse
            pulse = math.sin(phase) * amplitude
            _ = max(
                0.0, min(1.0, self.activity + pulse)
            )  # Calculate but use pulse directly

            # Update rendering (without changing the base activity)
            self._pulse_offset = pulse
            self.refresh()

            # Advance phase
            phase += 0.1
            await asyncio.sleep(rate_ms / 1000.0 / 10)

    def stop_heartbeat(self) -> None:
        """Stop heartbeat pulsing."""
        self._heartbeat_active = False
        self._pulse_offset = 0.0
        self.refresh()

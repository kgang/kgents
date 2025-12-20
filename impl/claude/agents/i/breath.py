"""
I-gent Breath Cycle: The contemplative pulse of the garden.

A zen element unique to I-gents: a slow-pulsing animation (4-second cycle) that:
1. Invites pause: Not everything needs immediate action
2. Signals liveliness: The system is alive, not frozen
3. Provides rhythm: A heartbeat for the garden

The breath is purely aesthetic—it carries no data. Its purpose is contemplative:
reminding the operator that they are tending a garden, not debugging a machine.
"""

import math
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class BreathCycle:
    """
    Manages the breath cycle state and rendering.

    The breath follows a sine wave pattern over a configurable period.
    Default is 4 seconds (slow, contemplative).
    """

    period_seconds: float = 4.0
    _start_time: Optional[float] = None

    def __post_init__(self) -> None:
        if self._start_time is None:
            self._start_time = time.time()

    @property
    def start_time(self) -> float:
        """Return the start time, guaranteed non-None after __post_init__."""
        assert self._start_time is not None  # Always set in __post_init__
        return self._start_time

    @property
    def position(self) -> float:
        """
        Current position in breath cycle (0.0 - 1.0).

        0.0 = start of inhale
        0.25 = peak of inhale
        0.5 = start of exhale
        0.75 = trough of exhale
        1.0 = back to start
        """
        elapsed = time.time() - self.start_time
        return (elapsed % self.period_seconds) / self.period_seconds

    @property
    def phase_name(self) -> str:
        """Human-readable phase: 'inhale' or 'exhale'."""
        pos = self.position
        if pos < 0.25 or pos >= 0.75:
            return "inhale"
        else:
            return "exhale"

    @property
    def intensity(self) -> float:
        """
        Current intensity (0.0 - 1.0) following sine wave.

        This can be used for animation intensity, opacity, etc.
        """
        # Sine wave: starts at 0, peaks at 0.25, back to 0 at 0.5, trough at 0.75
        return (math.sin(self.position * 2 * math.pi - math.pi / 2) + 1) / 2

    def render(self, width: int = 12) -> str:
        """
        Render the breath indicator as an ASCII bar.

        The bar pulses based on current position:
        - At inhale peak: ████████████
        - At exhale trough: ░░░░░░░░░░░░
        - In between: Gradient pattern centered on position

        Args:
            width: Width of the indicator bar

        Returns:
            ASCII string representing breath state
        """
        pos = self.position
        intensity = self.intensity

        # Create a wave pattern
        pattern = []
        for i in range(width):
            cell_pos = i / width
            # Distance from current breath position
            dist = min(abs(cell_pos - pos), abs(cell_pos - pos + 1), abs(cell_pos - pos - 1))
            # Intensity based on distance and overall breath intensity
            cell_intensity = max(0, 1 - dist * 5) * intensity

            if cell_intensity > 0.8:
                pattern.append("█")
            elif cell_intensity > 0.6:
                pattern.append("▓")
            elif cell_intensity > 0.4:
                pattern.append("▒")
            elif cell_intensity > 0.2:
                pattern.append("░")
            else:
                pattern.append("░")

        return "".join(pattern)

    def render_with_phase(self, width: int = 12) -> str:
        """Render breath indicator with phase name."""
        bar = self.render(width)
        return f"{bar}  ({self.phase_name})"

    def render_minimal(self) -> str:
        """Minimal render: just a pulsing dot."""
        intensity = self.intensity
        if intensity > 0.75:
            return "●"
        elif intensity > 0.5:
            return "◐"
        elif intensity > 0.25:
            return "○"
        else:
            return "◌"


class BreathManager:
    """
    Manages breath cycles for multiple gardens/views.

    Each garden can have its own breath cycle, synchronized or independent.
    """

    def __init__(self, synchronized: bool = True):
        """
        Initialize breath manager.

        Args:
            synchronized: If True, all cycles share the same start time
        """
        self.synchronized = synchronized
        self.global_start = time.time()
        self.cycles: dict[str, BreathCycle] = {}

    def get_cycle(self, garden_id: str) -> BreathCycle:
        """Get or create a breath cycle for a garden."""
        if garden_id not in self.cycles:
            start = self.global_start if self.synchronized else None
            self.cycles[garden_id] = BreathCycle(_start_time=start)
        return self.cycles[garden_id]

    def render(self, garden_id: str, width: int = 12) -> str:
        """Render breath for a garden."""
        return self.get_cycle(garden_id).render(width)

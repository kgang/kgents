"""
Cymatics Engine: Vibration visualization through wave interference.

Cymatics makes vibration visible. In kgents, we make agent behavior visible
through cymatic patterns. When agents communicate, their "frequencies"
interfere to create Chladni-like patterns.

The physics:
- Each vibration source emits circular waves
- Waves combine via superposition: A_total = sum(A_i * sin(2*pi*f_i*t - k*r_i + phi_i))
- Constructive interference creates "nodes" (bright regions)
- Destructive interference creates "antinodes" (dark regions)

Applications in kgents:
- Coalition health visualization (harmonic = stable patterns)
- Agent communication frequency (rapid exchange = complex patterns)
- Memory resonance (access patterns create interference)

Key insight: Cymatics reveals the hidden structure of agent interactions.
The pattern was always there; we simply found the medium that reveals it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

from agents.i.reactive.signal import Signal

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class VibrationSource:
    """A source of vibration in the cymatics field.

    Represents an agent, event, or state change that creates "ripples"
    in the visualization space.

    Attributes:
        frequency: Vibration frequency in Hz (events/second). Higher = faster oscillation.
        amplitude: Intensity of the vibration (0-1). Higher = stronger waves.
        phase: Phase offset in radians (0-2*pi). Used for synchronization.
        position: (x, y) position in normalized space (-1 to 1).
        decay: Distance decay factor. Higher = waves fade faster with distance.
    """

    frequency: float  # Hz (0.1 to 10 typical)
    amplitude: float  # 0-1
    phase: float = 0.0  # radians
    position: tuple[float, float] = (0.0, 0.0)  # normalized (-1 to 1)
    decay: float = 0.5  # distance decay factor

    def __post_init__(self) -> None:
        """Validate source parameters."""
        if self.frequency <= 0:
            object.__setattr__(self, "frequency", 0.1)
        if not 0 <= self.amplitude <= 1:
            object.__setattr__(self, "amplitude", max(0.0, min(1.0, self.amplitude)))

    def wave_at(self, x: float, y: float, time: float) -> float:
        """Calculate wave amplitude at point (x, y) at given time.

        Uses the wave equation: A * exp(-decay * r) * sin(2*pi*f*t - k*r + phi)
        where r is distance from source.

        Args:
            x: X coordinate (-1 to 1)
            y: Y coordinate (-1 to 1)
            time: Current time in seconds

        Returns:
            Wave amplitude at the point (-amplitude to +amplitude)
        """
        # Distance from source
        dx = x - self.position[0]
        dy = y - self.position[1]
        r = math.sqrt(dx * dx + dy * dy)

        # Wave number (spatial frequency)
        k = 2 * math.pi * self.frequency * 0.5  # Adjusted for visual effect

        # Distance decay (exponential falloff)
        distance_factor = math.exp(-self.decay * r)

        # Wave equation
        wave = self.amplitude * distance_factor * math.sin(
            2 * math.pi * self.frequency * time - k * r + self.phase
        )

        return wave


@dataclass(frozen=True)
class ChladniPattern:
    """Result of cymatics interference computation.

    A Chladni pattern shows where waves constructively and destructively
    interfere. Nodes are points of minimal displacement (antinodes in
    traditional cymatics); antinodes are points of maximum displacement.

    The pattern can be sampled continuously via the field() method.
    """

    # Points of constructive interference (high amplitude regions)
    nodes: tuple[tuple[float, float], ...]

    # Points of destructive interference (low amplitude regions)
    antinodes: tuple[tuple[float, float], ...]

    # The amplitude grid (for rendering)
    grid: tuple[tuple[float, ...], ...]

    # Grid resolution
    resolution: int

    # Minimum and maximum amplitudes in the pattern
    min_amplitude: float
    max_amplitude: float

    def field(self, x: float, y: float) -> float:
        """Get interpolated amplitude at continuous point (x, y).

        Args:
            x: X coordinate (-1 to 1)
            y: Y coordinate (-1 to 1)

        Returns:
            Interpolated amplitude at the point
        """
        # Convert to grid indices
        grid_x = (x + 1) / 2 * (self.resolution - 1)
        grid_y = (y + 1) / 2 * (self.resolution - 1)

        # Clamp to valid range
        grid_x = max(0, min(self.resolution - 1.001, grid_x))
        grid_y = max(0, min(self.resolution - 1.001, grid_y))

        # Bilinear interpolation
        x0, y0 = int(grid_x), int(grid_y)
        x1, y1 = min(x0 + 1, self.resolution - 1), min(y0 + 1, self.resolution - 1)

        fx, fy = grid_x - x0, grid_y - y0

        # Sample grid values
        v00 = self.grid[y0][x0]
        v10 = self.grid[y0][x1]
        v01 = self.grid[y1][x0]
        v11 = self.grid[y1][x1]

        # Interpolate
        v0 = v00 * (1 - fx) + v10 * fx
        v1 = v01 * (1 - fx) + v11 * fx
        return v0 * (1 - fy) + v1 * fy

    def normalized_field(self, x: float, y: float) -> float:
        """Get amplitude normalized to [0, 1] range.

        Args:
            x: X coordinate (-1 to 1)
            y: Y coordinate (-1 to 1)

        Returns:
            Normalized amplitude (0 = min, 1 = max)
        """
        value = self.field(x, y)
        if self.max_amplitude == self.min_amplitude:
            return 0.5
        return (value - self.min_amplitude) / (self.max_amplitude - self.min_amplitude)


@dataclass
class CymaticsEngine:
    """Physics-based cymatics simulation.

    Computes wave interference patterns from multiple vibration sources.
    The engine maintains a list of sources and can compute the resulting
    Chladni pattern at any time.

    Usage:
        engine = CymaticsEngine.create(resolution=64)
        engine.add_source(VibrationSource(frequency=2.0, amplitude=1.0, position=(0, 0)))
        engine.add_source(VibrationSource(frequency=2.0, amplitude=1.0, position=(0.5, 0)))
        pattern = engine.compute(time=0.5)
        amplitude = pattern.field(0.25, 0.0)  # Sample at point
    """

    # List of vibration sources
    _sources: list[VibrationSource] = field(default_factory=list)

    # Grid resolution for pattern computation
    resolution: int = 64

    # Current simulation time
    _time: float = 0.0

    @classmethod
    def create(cls, resolution: int = 64) -> CymaticsEngine:
        """Create an empty cymatics engine.

        Args:
            resolution: Grid resolution for pattern computation (higher = more detail)

        Returns:
            New CymaticsEngine instance
        """
        return cls(_sources=[], resolution=resolution, _time=0.0)

    @property
    def sources(self) -> list[VibrationSource]:
        """Get current vibration sources (read-only copy)."""
        return list(self._sources)

    @property
    def source_count(self) -> int:
        """Number of active sources."""
        return len(self._sources)

    @property
    def time(self) -> float:
        """Current simulation time."""
        return self._time

    def add_source(self, source: VibrationSource) -> None:
        """Add a vibration source to the simulation.

        Args:
            source: VibrationSource to add
        """
        self._sources.append(source)

    def remove_source(self, position: tuple[float, float], tolerance: float = 0.01) -> bool:
        """Remove source at or near the given position.

        Args:
            position: (x, y) position to search for
            tolerance: Distance tolerance for matching

        Returns:
            True if a source was removed, False otherwise
        """
        for i, source in enumerate(self._sources):
            dx = source.position[0] - position[0]
            dy = source.position[1] - position[1]
            if math.sqrt(dx * dx + dy * dy) <= tolerance:
                self._sources.pop(i)
                return True
        return False

    def clear(self) -> None:
        """Remove all vibration sources."""
        self._sources.clear()

    def amplitude_at(self, x: float, y: float, time: float | None = None) -> float:
        """Calculate total wave amplitude at a point.

        Uses superposition: total amplitude = sum of individual wave amplitudes.

        Args:
            x: X coordinate (-1 to 1)
            y: Y coordinate (-1 to 1)
            time: Time for calculation (defaults to current time)

        Returns:
            Total amplitude at the point
        """
        t = time if time is not None else self._time
        total = 0.0
        for source in self._sources:
            total += source.wave_at(x, y, t)
        return total

    def step(self, dt: float) -> None:
        """Advance simulation time.

        Args:
            dt: Time delta in seconds
        """
        self._time += dt

    def reset_time(self) -> None:
        """Reset simulation time to zero."""
        self._time = 0.0

    def compute(self, time: float | None = None) -> ChladniPattern:
        """Compute the Chladni pattern at current (or specified) time.

        This samples the wave field on a grid and identifies nodes
        and antinodes (local maxima and minima).

        Args:
            time: Time for computation (defaults to current time)

        Returns:
            ChladniPattern with grid, nodes, and antinodes
        """
        t = time if time is not None else self._time

        # Compute amplitude grid
        grid: list[list[float]] = []
        min_amp = float("inf")
        max_amp = float("-inf")

        for j in range(self.resolution):
            row: list[float] = []
            y = -1.0 + 2.0 * j / (self.resolution - 1)
            for i in range(self.resolution):
                x = -1.0 + 2.0 * i / (self.resolution - 1)
                amp = self.amplitude_at(x, y, t)
                row.append(amp)
                min_amp = min(min_amp, amp)
                max_amp = max(max_amp, amp)
            grid.append(row)

        # Handle empty case
        if not self._sources:
            min_amp = 0.0
            max_amp = 0.0

        # Find nodes (local maxima) and antinodes (local minima)
        nodes: list[tuple[float, float]] = []
        antinodes: list[tuple[float, float]] = []

        for j in range(1, self.resolution - 1):
            for i in range(1, self.resolution - 1):
                center = grid[j][i]
                neighbors = [
                    grid[j - 1][i],
                    grid[j + 1][i],
                    grid[j][i - 1],
                    grid[j][i + 1],
                ]

                # Convert to world coordinates
                x = -1.0 + 2.0 * i / (self.resolution - 1)
                y = -1.0 + 2.0 * j / (self.resolution - 1)

                # Local maximum (constructive interference)
                if all(center >= n for n in neighbors):
                    nodes.append((x, y))

                # Local minimum (destructive interference)
                if all(center <= n for n in neighbors):
                    antinodes.append((x, y))

        # Convert to immutable tuples
        grid_tuple = tuple(tuple(row) for row in grid)

        return ChladniPattern(
            nodes=tuple(nodes),
            antinodes=tuple(antinodes),
            grid=grid_tuple,
            resolution=self.resolution,
            min_amplitude=min_amp,
            max_amplitude=max_amp,
        )


# =============================================================================
# Convenience Functions
# =============================================================================


def create_harmonic_sources(
    count: int,
    base_frequency: float = 2.0,
    amplitude: float = 1.0,
    radius: float = 0.5,
) -> list[VibrationSource]:
    """Create a ring of harmonically-related vibration sources.

    This creates sources with the same frequency arranged in a circle,
    which produces symmetric Chladni patterns.

    Args:
        count: Number of sources to create
        base_frequency: Frequency for all sources
        amplitude: Amplitude for all sources
        radius: Radius of the circle

    Returns:
        List of VibrationSource objects
    """
    sources = []
    for i in range(count):
        angle = 2 * math.pi * i / count
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        sources.append(
            VibrationSource(
                frequency=base_frequency,
                amplitude=amplitude,
                phase=0.0,
                position=(x, y),
            )
        )
    return sources


def create_dissonant_sources(
    frequencies: list[float],
    amplitude: float = 1.0,
    spread: float = 0.3,
) -> list[VibrationSource]:
    """Create sources with different frequencies (dissonant).

    Dissonant frequencies create chaotic, unstable patterns—useful for
    visualizing coalition conflicts or system stress.

    Args:
        frequencies: List of frequencies for each source
        amplitude: Amplitude for all sources
        spread: Horizontal spread of sources

    Returns:
        List of VibrationSource objects
    """
    sources = []
    count = len(frequencies)
    for i, freq in enumerate(frequencies):
        x = -spread + 2 * spread * i / max(1, count - 1) if count > 1 else 0
        sources.append(
            VibrationSource(
                frequency=freq,
                amplitude=amplitude,
                phase=0.0,
                position=(x, 0.0),
            )
        )
    return sources


def pattern_stability(pattern: ChladniPattern) -> float:
    """Measure the stability/harmony of a Chladni pattern.

    Stable patterns have high contrast between nodes and antinodes.
    Chaotic patterns have low contrast (everything is mid-amplitude).

    Args:
        pattern: ChladniPattern to analyze

    Returns:
        Stability score from 0 (chaotic) to 1 (perfectly harmonic)
    """
    if pattern.max_amplitude == pattern.min_amplitude:
        return 0.0  # No variation = no pattern

    # Measure amplitude variance as stability indicator
    total = 0.0
    count = 0
    mean = (pattern.max_amplitude + pattern.min_amplitude) / 2

    for row in pattern.grid:
        for val in row:
            total += (val - mean) ** 2
            count += 1

    variance = total / count if count > 0 else 0
    max_variance = ((pattern.max_amplitude - pattern.min_amplitude) / 2) ** 2

    if max_variance == 0:
        return 0.0

    # Higher variance = more defined pattern = more stable
    return min(1.0, variance / max_variance)

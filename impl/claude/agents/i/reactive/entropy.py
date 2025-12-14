"""
Pure Entropy Algebra: Deterministic visual distortion from entropy state.

CRITICAL: No random.random() in any render path!

The Accursed Share made visible. Higher entropy = more chaos = more life.
Everything derives deterministically from (entropy, seed, t).
Same inputs -> same output, always.

This is a pure functor: State -> VisualDistortion
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# Golden ratio for deterministic pseudo-randomness
PHI = 1.618033988749


@dataclass(frozen=True)
class VisualDistortion:
    """
    Pure computation of visual distortion from entropy.

    All fields are deterministic functions of (entropy, seed, t).
    No randomness involved.
    """

    blur: float
    skew: float
    jitter_x: float
    jitter_y: float
    pulse: float


def _hash(n: float) -> float:
    """Deterministic hash using golden ratio. Maps any float to [0, 1)."""
    return (n * PHI) % 1.0


def entropy_to_distortion(
    entropy: float,
    seed: int,
    t: float = 0.0,
) -> VisualDistortion:
    """
    Pure function: (entropy, seed, t) -> VisualDistortion

    The Accursed Share made visible. Higher entropy = more chaos = more life.

    No randomness! Everything derives deterministically from inputs.
    Same (entropy, seed, t) -> same distortion, always.

    Args:
        entropy: 0.0-1.0, level of chaos
        seed: Deterministic seed for this entity (hash of agent_id)
        t: Time in milliseconds (passed from parent for consistency)

    Returns:
        VisualDistortion with all visual chaos parameters
    """
    # Clamp entropy to valid range
    e = max(0.0, min(1.0, entropy))

    # Non-linear scaling (drama!)
    intensity = e * e

    # Time-based oscillation for living feel
    wave = math.sin(t * 0.001 + seed)
    wave2 = math.cos(t * 0.0013 + seed * PHI)

    return VisualDistortion(
        blur=intensity * 2 * (1 + wave * 0.3),
        skew=intensity * 8 * wave2,
        jitter_x=intensity * 4 * _hash(seed) * wave,
        jitter_y=intensity * 4 * _hash(seed + 1) * wave2,
        pulse=1 + intensity * 0.15 * math.sin(t * 0.002 + seed),
    )


# ASCII density characters - visual representation of entropy levels
DENSITY_RUNES = " ·∴∵◦○◎●◉█"
SPARK_CHARS = "▁▂▃▄▅▆▇█"

# Phase glyphs - semantic meaning through visual character
PHASE_GLYPHS: dict[str, str] = {
    "idle": "○",
    "active": "◉",
    "waiting": "◐",
    "error": "◈",
    "yielding": "◇",
    "thinking": "◎",
    "complete": "●",
}


def entropy_to_rune(entropy: float) -> str:
    """
    Map entropy to ASCII density character.

    Pure function: entropy -> glyph character

    Args:
        entropy: 0.0-1.0

    Returns:
        Single character representing entropy density
    """
    e = max(0.0, min(1.0, entropy))
    idx = int(e * (len(DENSITY_RUNES) - 1))
    return DENSITY_RUNES[min(idx, len(DENSITY_RUNES) - 1)]


def entropy_to_spark(entropy: float) -> str:
    """
    Map entropy to sparkline character (vertical bar).

    Pure function: entropy -> vertical bar character

    Args:
        entropy: 0.0-1.0

    Returns:
        Single character representing entropy as vertical bar
    """
    e = max(0.0, min(1.0, entropy))
    idx = int(e * (len(SPARK_CHARS) - 1))
    return SPARK_CHARS[min(idx, len(SPARK_CHARS) - 1)]


def phase_to_glyph(phase: str) -> str:
    """
    Map phase name to glyph character.

    Pure function: phase -> glyph

    Args:
        phase: One of "idle", "active", "waiting", "error", "yielding", etc.

    Returns:
        Glyph character for the phase, or "·" if unknown
    """
    return PHASE_GLYPHS.get(phase, "·")


def distortion_to_css(distortion: VisualDistortion) -> str:
    """
    Convert VisualDistortion to CSS filter/transform string.

    For use with HTML rendering targets (marimo, web).

    Args:
        distortion: Computed visual distortion

    Returns:
        CSS style string
    """
    parts = [
        f"filter: blur({distortion.blur:.2f}px)",
        f"transform: skewX({distortion.skew:.2f}deg) "
        f"translate({distortion.jitter_x:.2f}px, {distortion.jitter_y:.2f}px) "
        f"scale({distortion.pulse:.3f})",
    ]
    return "; ".join(parts)


def distortion_to_rich_style(distortion: VisualDistortion) -> str:
    """
    Convert VisualDistortion to Rich style hints.

    For use with Textual/Rich rendering. Note: Rich doesn't support
    actual blur/skew, so we approximate with color intensity.

    Args:
        distortion: Computed visual distortion

    Returns:
        Rich style string (e.g., "bold" or "dim" based on intensity)
    """
    # Use pulse as intensity indicator
    if distortion.pulse > 1.1:
        return "bold"
    if distortion.blur > 1.0:
        return "dim"
    return ""

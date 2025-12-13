"""
EntropyVisualizer - Maps uncertainty to visual distortion.

The key insight: distortion is signal, not decoration.

When an agent is confused, its borders should literally dissolve.
When it draws from the Accursed Share (void.*), reality should glitch.

This module provides a FUNCTIONAL mapping from entropy level (0.0-1.0)
to visual distortion parameters. Same entropy → same visual.
No randomness in the mapping (randomness is in the glitch execution).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EntropyParams:
    """
    Visual parameters derived from entropy level.

    These parameters are used by widgets to render entropy-aware distortion.
    The mapping is deterministic: same entropy → same params.
    """

    edge_opacity: float  # 1.0 = crisp, 0.5 = fading
    dither_rate: float  # 0.0 = none, 0.4 = heavy
    jitter_amplitude: int  # 0 = stable, 3 = shaking
    glitch_intensity: float  # 0.0 = none, 0.6 = corrupted


def entropy_to_params(entropy: float) -> EntropyParams:
    """
    Map entropy level to visual parameters.

    This is the FUNCTIONAL core of entropy visualization:
    - Low entropy (0.0-0.3): Crisp, stable, minimal distortion
    - Medium entropy (0.3-0.7): Soft edges, slight dithering
    - High entropy (0.7-1.0): Heavy distortion, glitch effects

    Args:
        entropy: Uncertainty level from 0.0 (certain) to 1.0 (confused)

    Returns:
        EntropyParams for rendering

    Examples:
        >>> params = entropy_to_params(0.0)
        >>> params.edge_opacity
        1.0
        >>> params.glitch_intensity
        0.0

        >>> params = entropy_to_params(0.5)
        >>> params.dither_rate
        0.2

        >>> params = entropy_to_params(1.0)
        >>> params.glitch_intensity
        0.6
    """
    # Clamp entropy to valid range
    entropy = max(0.0, min(1.0, entropy))

    # Edge opacity: sharp at low entropy, fading at high
    # Linear decay from 1.0 to 0.5
    edge_opacity = 1.0 - entropy * 0.5

    # Dither rate: none at low, increases with entropy
    # Linear growth from 0.0 to 0.4
    dither_rate = entropy * 0.4

    # Jitter amplitude: stable at low, shaking at high
    # Linear growth from 0 to 3 pixels
    jitter_amplitude = int(entropy * 3)

    # Glitch intensity: only kicks in above 0.7 threshold
    # This creates a phase transition: normal → suddenly glitched
    if entropy > 0.7:
        # Map 0.7-1.0 to 0.0-0.6
        glitch_intensity = (entropy - 0.7) / 0.3 * 0.6
    else:
        glitch_intensity = 0.0

    return EntropyParams(
        edge_opacity=edge_opacity,
        dither_rate=dither_rate,
        jitter_amplitude=jitter_amplitude,
        glitch_intensity=glitch_intensity,
    )


def entropy_to_border_style(entropy: float) -> str:
    """
    Map entropy to border character style.

    As entropy increases, borders dissolve:
    - Low (0.0-0.3): Sharp box (─│┌┐└┘)
    - Medium (0.3-0.6): Soft box (╌╎┏┓┗┛)
    - High (0.6-0.8): Broken box (┄┆┌┐└┘ with gaps)
    - Void (0.8-1.0): No box (spaces)

    Args:
        entropy: Uncertainty level 0.0-1.0

    Returns:
        Border style name ("solid", "soft", "broken", "none")
    """
    if entropy < 0.3:
        return "solid"
    elif entropy < 0.6:
        return "soft"
    elif entropy < 0.8:
        return "broken"
    else:
        return "none"


# Export all public APIs
__all__ = [
    "EntropyParams",
    "entropy_to_params",
    "entropy_to_border_style",
]

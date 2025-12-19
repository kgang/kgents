"""
ExtendedTarget: Render targets beyond the core four.

This module extends RenderTarget with additional targets (SSE, VR placeholders)
while maintaining backward compatibility with the core enum.

Target Taxonomy:
    - CLI: Low fidelity, synchronous, non-interactive
    - TUI: Medium fidelity, synchronous, interactive
    - JSON: Lossless data, synchronous, non-interactive
    - MARIMO: High fidelity, reactive, interactive
    - SSE: Streaming, asynchronous, non-interactive
    - WEBGL: High fidelity, interactive (placeholder)
    - WEBXR: Maximum fidelity, immersive (placeholder)
    - AUDIO: Sonification (placeholder)

The Galois Connection (from spec):
    compress ⊣ embed

    Each target has a fidelity level. Higher fidelity targets can embed
    lower fidelity representations, but compression loses information.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.i.reactive.widget import RenderTarget


class ExtendedTarget(Enum):
    """
    Extended rendering targets.

    Core targets (backward-compatible with RenderTarget):
        CLI, TUI, MARIMO, JSON

    Extended targets:
        SSE - Server-Sent Events streaming
        WEBGL - Three.js scenes (placeholder)
        WEBXR - WebXR VR/AR (placeholder)
        AUDIO - Sonification (placeholder)
    """

    # Core targets (match RenderTarget values for compatibility)
    CLI = auto()
    TUI = auto()
    MARIMO = auto()
    JSON = auto()

    # Extended targets
    SSE = auto()
    WEBGL = auto()
    WEBXR = auto()
    AUDIO = auto()

    @classmethod
    def from_render_target(cls, target: "RenderTarget") -> "ExtendedTarget":
        """
        Convert core RenderTarget to ExtendedTarget.

        This allows code using the old enum to work with the extended system.

        Args:
            target: Core RenderTarget enum value

        Returns:
            Corresponding ExtendedTarget value

        Example:
            from agents.i.reactive.widget import RenderTarget
            ext = ExtendedTarget.from_render_target(RenderTarget.CLI)
        """
        # Import here to avoid circular dependency
        from agents.i.reactive.widget import RenderTarget

        mapping = {
            RenderTarget.CLI: cls.CLI,
            RenderTarget.TUI: cls.TUI,
            RenderTarget.MARIMO: cls.MARIMO,
            RenderTarget.JSON: cls.JSON,
        }
        return mapping[target]

    @property
    def is_streaming(self) -> bool:
        """Whether this target supports streaming output."""
        return self in (ExtendedTarget.SSE,)

    @property
    def is_interactive(self) -> bool:
        """Whether this target supports user interaction."""
        return self in (
            ExtendedTarget.TUI,
            ExtendedTarget.MARIMO,
            ExtendedTarget.WEBGL,
            ExtendedTarget.WEBXR,
        )

    @property
    def is_placeholder(self) -> bool:
        """Whether this target is a placeholder (not yet implemented)."""
        return self in (
            ExtendedTarget.WEBGL,
            ExtendedTarget.WEBXR,
            ExtendedTarget.AUDIO,
        )


@dataclass(frozen=True)
class TargetCapability:
    """
    Capabilities of a render target.

    Attributes:
        fidelity: 0.0-1.0 scale of information preservation
        interactive: Whether target supports interaction
        streaming: Whether target supports streaming output
        async_: Whether target requires async rendering
        implemented: Whether target is fully implemented
    """

    fidelity: float
    interactive: bool
    streaming: bool
    async_: bool
    implemented: bool


# Capability specifications per target
_CAPABILITIES: dict[ExtendedTarget, TargetCapability] = {
    ExtendedTarget.CLI: TargetCapability(
        fidelity=0.3,
        interactive=False,
        streaming=False,
        async_=False,
        implemented=True,
    ),
    ExtendedTarget.TUI: TargetCapability(
        fidelity=0.5,
        interactive=True,
        streaming=False,
        async_=False,
        implemented=True,
    ),
    ExtendedTarget.JSON: TargetCapability(
        fidelity=1.0,  # Lossless for data
        interactive=False,
        streaming=False,
        async_=False,
        implemented=True,
    ),
    ExtendedTarget.MARIMO: TargetCapability(
        fidelity=0.8,
        interactive=True,
        streaming=False,
        async_=False,
        implemented=True,
    ),
    ExtendedTarget.SSE: TargetCapability(
        fidelity=0.5,
        interactive=False,
        streaming=True,
        async_=True,
        implemented=True,
    ),
    ExtendedTarget.WEBGL: TargetCapability(
        fidelity=0.9,
        interactive=True,
        streaming=False,
        async_=False,
        implemented=False,  # Placeholder
    ),
    ExtendedTarget.WEBXR: TargetCapability(
        fidelity=0.95,
        interactive=True,
        streaming=False,
        async_=False,
        implemented=False,  # Placeholder
    ),
    ExtendedTarget.AUDIO: TargetCapability(
        fidelity=0.2,  # Very lossy (sonification)
        interactive=False,
        streaming=True,
        async_=True,
        implemented=False,  # Placeholder
    ),
}


def target_capabilities(target: ExtendedTarget) -> TargetCapability:
    """
    Get the capabilities of a render target.

    Args:
        target: The target to query

    Returns:
        TargetCapability describing the target's properties
    """
    return _CAPABILITIES[target]


def target_fidelity(target: ExtendedTarget) -> float:
    """
    Get the fidelity level of a render target.

    Fidelity measures information preservation:
        1.0 = lossless (JSON)
        0.0 = maximum compression (not useful)

    Args:
        target: The target to query

    Returns:
        Fidelity level 0.0-1.0
    """
    return _CAPABILITIES[target].fidelity


class FidelityLevel(Enum):
    """
    Named fidelity levels for human-readable target selection.

    Use these when you want to select a target by fidelity
    rather than by specific implementation.
    """

    MAXIMUM = "maximum"  # WebXR
    HIGH = "high"  # WebGL, marimo
    MEDIUM = "medium"  # TUI, SSE
    LOW = "low"  # CLI
    LOSSLESS = "lossless"  # JSON (special case)


def targets_by_fidelity(level: FidelityLevel) -> list[ExtendedTarget]:
    """
    Get targets matching a fidelity level.

    Args:
        level: Desired fidelity level

    Returns:
        List of targets at that level, sorted by fidelity descending
    """
    thresholds = {
        FidelityLevel.MAXIMUM: (0.9, 1.0),
        FidelityLevel.HIGH: (0.7, 0.9),
        FidelityLevel.MEDIUM: (0.4, 0.7),
        FidelityLevel.LOW: (0.0, 0.4),
        FidelityLevel.LOSSLESS: (1.0, 1.0),  # Exact match
    }

    low, high = thresholds[level]
    matches = [
        t for t, cap in _CAPABILITIES.items() if low <= cap.fidelity <= high and cap.implemented
    ]
    return sorted(matches, key=lambda t: _CAPABILITIES[t].fidelity, reverse=True)


__all__ = [
    "ExtendedTarget",
    "TargetCapability",
    "FidelityLevel",
    "target_capabilities",
    "target_fidelity",
    "targets_by_fidelity",
]

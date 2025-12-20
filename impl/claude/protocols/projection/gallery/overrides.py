"""
Gallery Overrides: Developer control system for rapid iteration.

Overrides allow developers to inject state at any layer:
- Global: affect all widgets (entropy, time, seed)
- Per-widget: override specific widget properties
- Per-pilot: modify demonstration parameters

The override system is hierarchical:
    CLI flags > Environment vars > Defaults

Usage:
    # From environment
    export KGENTS_GALLERY_ENTROPY=0.5
    export KGENTS_GALLERY_SEED=42

    # From CLI
    python -m protocols.projection.gallery --entropy=0.8 --seed=123

    # Programmatic
    overrides = GalleryOverrides(entropy=0.3, seed=999)
    gallery.show_all(overrides=overrides)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Literal

from agents.i.reactive.widget import RenderTarget

TargetName = Literal["cli", "tui", "marimo", "json"]


def _target_from_name(name: str) -> RenderTarget:
    """Convert string target name to RenderTarget enum."""
    mapping = {
        "cli": RenderTarget.CLI,
        "tui": RenderTarget.TUI,
        "marimo": RenderTarget.MARIMO,
        "json": RenderTarget.JSON,
    }
    return mapping.get(name.lower(), RenderTarget.CLI)


@dataclass(frozen=True)
class GalleryOverrides:
    """
    Immutable override configuration for gallery rendering.

    All fields are optional. None means "use widget default".
    This enables surgical overrides without affecting unrelated properties.

    Attributes:
        target: Override render target for all widgets
        entropy: Global entropy override (0.0-1.0)
        seed: Deterministic seed for reproducible chaos
        time_ms: Fixed time in milliseconds (None = use current)
        verbose: Enable verbose output with debug info
        phase: Override phase for phase-aware widgets
        style: Override style (compact, full, minimal)
        breathing: Override breathing animation
        widget_overrides: Per-widget property overrides (widget_name -> props)
    """

    target: RenderTarget | None = None
    entropy: float | None = None
    seed: int | None = None
    time_ms: float | None = None
    verbose: bool = False
    phase: str | None = None
    style: str | None = None
    breathing: bool | None = None
    widget_overrides: dict[str, dict[str, Any]] = field(default_factory=dict)

    def with_target(self, target: RenderTarget) -> GalleryOverrides:
        """Return new overrides with updated target."""
        return GalleryOverrides(
            target=target,
            entropy=self.entropy,
            seed=self.seed,
            time_ms=self.time_ms,
            verbose=self.verbose,
            phase=self.phase,
            style=self.style,
            breathing=self.breathing,
            widget_overrides=self.widget_overrides,
        )

    def with_entropy(self, entropy: float) -> GalleryOverrides:
        """Return new overrides with updated entropy."""
        return GalleryOverrides(
            target=self.target,
            entropy=max(0.0, min(1.0, entropy)),
            seed=self.seed,
            time_ms=self.time_ms,
            verbose=self.verbose,
            phase=self.phase,
            style=self.style,
            breathing=self.breathing,
            widget_overrides=self.widget_overrides,
        )

    def with_seed(self, seed: int) -> GalleryOverrides:
        """Return new overrides with updated seed."""
        return GalleryOverrides(
            target=self.target,
            entropy=self.entropy,
            seed=seed,
            time_ms=self.time_ms,
            verbose=self.verbose,
            phase=self.phase,
            style=self.style,
            breathing=self.breathing,
            widget_overrides=self.widget_overrides,
        )

    def with_widget_override(self, widget_name: str, props: dict[str, Any]) -> GalleryOverrides:
        """Return new overrides with widget-specific override."""
        new_widget_overrides = dict(self.widget_overrides)
        existing = new_widget_overrides.get(widget_name, {})
        new_widget_overrides[widget_name] = {**existing, **props}
        return GalleryOverrides(
            target=self.target,
            entropy=self.entropy,
            seed=self.seed,
            time_ms=self.time_ms,
            verbose=self.verbose,
            phase=self.phase,
            style=self.style,
            breathing=self.breathing,
            widget_overrides=new_widget_overrides,
        )

    def get_widget_override(self, widget_name: str) -> dict[str, Any]:
        """Get overrides for a specific widget."""
        return self.widget_overrides.get(widget_name, {})


def get_overrides_from_env() -> GalleryOverrides:
    """
    Build GalleryOverrides from environment variables.

    Environment Variables:
        KGENTS_GALLERY_TARGET: cli, tui, marimo, json
        KGENTS_GALLERY_ENTROPY: float 0.0-1.0
        KGENTS_GALLERY_SEED: int
        KGENTS_GALLERY_TIME: float (milliseconds)
        KGENTS_GALLERY_VERBOSE: 1, true, yes
        KGENTS_GALLERY_PHASE: idle, active, waiting, error, etc.
        KGENTS_GALLERY_STYLE: compact, full, minimal
        KGENTS_GALLERY_BREATHING: 1, true, yes
    """
    target = None
    if target_str := os.environ.get("KGENTS_GALLERY_TARGET"):
        target = _target_from_name(target_str)

    entropy = None
    if entropy_str := os.environ.get("KGENTS_GALLERY_ENTROPY"):
        try:
            entropy = max(0.0, min(1.0, float(entropy_str)))
        except ValueError:
            pass

    seed = None
    if seed_str := os.environ.get("KGENTS_GALLERY_SEED"):
        try:
            seed = int(seed_str)
        except ValueError:
            pass

    time_ms = None
    if time_str := os.environ.get("KGENTS_GALLERY_TIME"):
        try:
            time_ms = float(time_str)
        except ValueError:
            pass

    verbose = os.environ.get("KGENTS_GALLERY_VERBOSE", "").lower() in (
        "1",
        "true",
        "yes",
    )

    phase = os.environ.get("KGENTS_GALLERY_PHASE")
    style = os.environ.get("KGENTS_GALLERY_STYLE")

    breathing = None
    if breathing_str := os.environ.get("KGENTS_GALLERY_BREATHING"):
        breathing = breathing_str.lower() in ("1", "true", "yes")

    return GalleryOverrides(
        target=target,
        entropy=entropy,
        seed=seed,
        time_ms=time_ms,
        verbose=verbose,
        phase=phase,
        style=style,
        breathing=breathing,
    )


def merge_overrides(base: GalleryOverrides, cli: GalleryOverrides) -> GalleryOverrides:
    """
    Merge two override configs. CLI takes precedence.

    Precedence: cli > base (env)
    """
    return GalleryOverrides(
        target=cli.target if cli.target is not None else base.target,
        entropy=cli.entropy if cli.entropy is not None else base.entropy,
        seed=cli.seed if cli.seed is not None else base.seed,
        time_ms=cli.time_ms if cli.time_ms is not None else base.time_ms,
        verbose=cli.verbose or base.verbose,
        phase=cli.phase if cli.phase is not None else base.phase,
        style=cli.style if cli.style is not None else base.style,
        breathing=cli.breathing if cli.breathing is not None else base.breathing,
        widget_overrides={**base.widget_overrides, **cli.widget_overrides},
    )


# Default overrides (no changes)
DEFAULT_OVERRIDES = GalleryOverrides()

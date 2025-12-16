"""
Projection Component Gallery: Dense pilot experiences for rapid iteration.

This gallery provides a comprehensive showcase of ALL projection components
with production-grade developer overrides for rapid iteration.

Architecture:
    Gallery = Category[Widget, Pilot]

    Where:
    - Widget: Any KgentsWidget[S] from the reactive substrate
    - Pilot: A pre-configured demonstration with override hooks

Usage:
    # CLI gallery runner
    python -m protocols.projection.gallery --all
    python -m protocols.projection.gallery --widget=glyph --entropy=0.5
    python -m protocols.projection.gallery --category=chrome --target=tui

    # Programmatic usage
    from protocols.projection.gallery import Gallery, run_gallery

    gallery = Gallery()
    gallery.show_all(target=RenderTarget.CLI)

    # With overrides
    gallery.show("agent_card", overrides={"phase": "error", "entropy": 0.8})

Developer Overrides:
    Environment Variables:
        KGENTS_GALLERY_TARGET=cli|tui|marimo|json  # Default target
        KGENTS_GALLERY_ENTROPY=0.0-1.0              # Global entropy override
        KGENTS_GALLERY_SEED=int                     # Deterministic seed
        KGENTS_GALLERY_TIME=float                   # Fixed time (ms)
        KGENTS_GALLERY_VERBOSE=1                    # Verbose output

    CLI Flags:
        --target, -t      Render target
        --entropy, -e     Entropy override (0.0-1.0)
        --seed, -s        Deterministic seed
        --time, -T        Fixed time in ms
        --widget, -w      Specific widget to show
        --category, -c    Category filter (primitives, chrome, streaming, cards)
        --all, -a         Show all widgets
        --compare         Side-by-side target comparison
        --benchmark       Run render benchmarks
        --interactive     Enter interactive mode (TUI only)
"""

from protocols.projection.gallery.overrides import (
    GalleryOverrides,
    get_overrides_from_env,
    merge_overrides,
)
from protocols.projection.gallery.pilots import (
    PILOT_REGISTRY,
    Pilot,
    PilotCategory,
    register_pilot,
)
from protocols.projection.gallery.runner import Gallery, run_gallery

__all__ = [
    # Core
    "Gallery",
    "run_gallery",
    # Pilots
    "Pilot",
    "PilotCategory",
    "PILOT_REGISTRY",
    "register_pilot",
    # Overrides
    "GalleryOverrides",
    "get_overrides_from_env",
    "merge_overrides",
]

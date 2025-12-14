"""
Interactive Playground for Reactive Substrate.

Launch an interactive REPL with all widgets pre-imported for experimentation.

Usage:
    python -m agents.i.reactive.playground

Or from Python:
    from agents.i.reactive.playground import launch
    launch()

Example session:
    >>> card = AgentCardWidget(AgentCardState(name="Test", phase="active"))
    >>> print(card.to_cli())
    [●] Test
    [░░░░░░░░░░] 0%
    >>> card.to_json()
    {'name': 'Test', 'phase': 'active', ...}
"""

from __future__ import annotations

import code
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def get_playground_namespace() -> dict[str, object]:
    """
    Build the namespace for the playground REPL.

    Imports all reactive primitives so users can start experimenting immediately.
    """
    # Core imports
    from agents.i.reactive import (
        # Primitives - Cards
        AgentCardState,
        AgentCardWidget,
        # Primitives - Composed
        BarState,
        BarWidget,
        CompositeWidget,
        # Core
        Computed,
        DensityFieldState,
        DensityFieldWidget,
        DialecticCardState,
        DialecticCardWidget,
        Effect,
        Entity,
        # Primitives - Atomic
        GlyphState,
        GlyphWidget,
        KgentsWidget,
        RenderTarget,
        ShadowCardState,
        ShadowCardWidget,
        ShadowItem,
        Signal,
        SparklineState,
        SparklineWidget,
        Wind,
        YieldCardState,
        YieldCardWidget,
        # Meta
        __version__,
    )

    namespace = {
        # Core
        "Signal": Signal,
        "Computed": Computed,
        "Effect": Effect,
        "KgentsWidget": KgentsWidget,
        "CompositeWidget": CompositeWidget,
        "RenderTarget": RenderTarget,
        # Primitives - Atomic
        "GlyphWidget": GlyphWidget,
        "GlyphState": GlyphState,
        # Primitives - Composed
        "BarWidget": BarWidget,
        "BarState": BarState,
        "SparklineWidget": SparklineWidget,
        "SparklineState": SparklineState,
        "DensityFieldWidget": DensityFieldWidget,
        "DensityFieldState": DensityFieldState,
        "Entity": Entity,
        "Wind": Wind,
        # Primitives - Cards
        "AgentCardWidget": AgentCardWidget,
        "AgentCardState": AgentCardState,
        "YieldCardWidget": YieldCardWidget,
        "YieldCardState": YieldCardState,
        "ShadowCardWidget": ShadowCardWidget,
        "ShadowCardState": ShadowCardState,
        "ShadowItem": ShadowItem,
        "DialecticCardWidget": DialecticCardWidget,
        "DialecticCardState": DialecticCardState,
        # Meta
        "__version__": __version__,
    }

    # Add some pre-built examples
    namespace["example_card"] = AgentCardWidget(
        AgentCardState(
            name="Example Agent",
            phase="active",
            activity=(0.3, 0.5, 0.7, 0.9, 0.6),
            capability=0.85,
        )
    )

    namespace["example_bar"] = BarWidget(
        BarState(value=0.75, width=20, style="gradient", label="Memory")
    )

    namespace["example_sparkline"] = SparklineWidget(
        SparklineState(
            values=(0.2, 0.4, 0.6, 0.8, 0.6, 0.9, 0.7, 0.5),
            label="CPU",
        )
    )

    return namespace


def print_banner() -> None:
    """Print the playground welcome banner."""
    from agents.i.reactive import __version__

    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║              Reactive Substrate Playground v{__version__}              ║
╠══════════════════════════════════════════════════════════════╣
║  All widgets are pre-imported. Try:                          ║
║                                                              ║
║    >>> print(example_card.to_cli())                          ║
║    >>> bar = BarWidget(BarState(value=0.5, width=20))        ║
║    >>> print(bar.to_cli())                                   ║
║    >>> example_card.to_json()                                ║
║                                                              ║
║  Available widgets:                                          ║
║    GlyphWidget, BarWidget, SparklineWidget, DensityFieldWidget║
║    AgentCardWidget, YieldCardWidget, ShadowCardWidget         ║
║    DialecticCardWidget                                        ║
║                                                              ║
║  Reactive primitives:                                        ║
║    Signal, Computed, Effect                                  ║
║                                                              ║
║  Pre-built examples:                                         ║
║    example_card, example_bar, example_sparkline              ║
║                                                              ║
║  Type help(AgentCardWidget) for documentation.               ║
║  Type exit() or Ctrl-D to quit.                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def launch() -> None:
    """
    Launch the interactive playground.

    Opens a Python REPL with all reactive widgets pre-imported.
    """
    print_banner()

    namespace = get_playground_namespace()

    # Try to use IPython if available (better REPL experience)
    try:
        from IPython import embed

        embed(user_ns=namespace, colors="neutral")  # type: ignore[no-untyped-call]
    except ImportError:
        # Fall back to standard library REPL
        code.interact(
            banner="",  # We already printed our banner
            local=namespace,
            exitmsg="Goodbye!",
        )


def main() -> None:
    """Entry point for module execution."""
    # Check for --help
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return

    launch()


if __name__ == "__main__":
    main()

"""
Observe Handler: Open the Terrarium TUI.

The Glass Box - see inside the agent ecosystem.

Usage:
    kgents observe              # Open Terrarium TUI
    kgents observe --compact    # Minimal display mode
    kgents observe --simple     # Use simple renderer (no Textual)
    kgents observe --focus L    # Focus on specific agent

Options:
    --compact     Compact single-line-per-agent display
    --simple      Use simple ANSI renderer instead of Textual
    --focus AGENT Focus view on specific agent

Example:
    $ kgents observe

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │ TERRARIUM ●                                                      12:34:56 UTC│
    ├──────────────────────────────────────────────────────────────────────────────┤
    │                                                                              │
    │  ┌─ AGENTS ──────────────────────────┐  ┌─ PHEROMONE LEVELS ───────────────┐│
    │  │ B-gent  ████████░░  80%  Processing│  │ WARNING      ████████░░░░░░░ 0.8 ││
    │  │ D-gent  ██████████ 100%  Idle      │  │ METAPHOR     ██████░░░░░░░░░ 0.6 ││
    │  │ L-gent  ██████████ 100%  Indexing  │  │ MEMORY       █████████░░░░░░ 0.9 ││
    │  └────────────────────────────────────┘  └──────────────────────────────────┘│
    │                                                                              │
    │  ┌─ THOUGHT STREAM ─────────────────────────────────────────────────────────┐│
    │  │ 12:34:52 [B-gent  ] Processing invoice batch #2847                       ││
    │  │ 12:34:53 [L-gent  ] Indexed 47 new symbols from cartographer.py          ││
    │  │ 12:34:54 [F-gent  ] ⚠ test_graph.py:142 flaking (3rd occurrence)         ││
    │  └──────────────────────────────────────────────────────────────────────────┘│
    │                                                                              │
    │  ┌─ TOKEN ECONOMY ──────────────────────────────────────────────────────────┐│
    │  │ Budget: 847,234 / 1,000,000 tokens (85%)                                 ││
    │  │ Burn Rate: ▁▂▃▅▆▇█▇▆▅▃▂▁▁▂▃▄▅▆▇█▇▆▄▃▂▁ (12 tok/min)                     ││
    │  │ Top Consumer: L-gent (embedding generation)                              ││
    │  └──────────────────────────────────────────────────────────────────────────┘│
    │                                                                              │
    │  [q]uit  [r]efresh  [d]etail  [t]ether  [p]heromones                         │
    └──────────────────────────────────────────────────────────────────────────────┘

Controls:
    q - Quit
    r - Refresh now
    d - Toggle detail mode
    t - Open tether dialog
    Ctrl+C - Exit

Principle alignment:
    - Transparent Infrastructure: The cockpit shows everything
    - Joy-Inducing: Beautiful visualization of agent activity
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any


def cmd_observe(args: list[str]) -> int:
    """
    Open the Terrarium TUI.

    The glass box visualization of the agent ecosystem.
    """
    if args and args[0] in ("--help", "-h"):
        print(__doc__)
        return 0

    # Parse args
    options = _parse_args(args)

    if options.get("error"):
        print(f"Error: {options['error']}")
        return 1

    return asyncio.run(
        _cmd_observe(
            compact=options.get("compact", False),
            simple=options.get("simple", False),
            focus=options.get("focus"),
        )
    )


async def _cmd_observe(
    compact: bool = False,
    simple: bool = False,
    focus: str | None = None,
) -> int:
    """Execute the observe command."""
    try:
        from infra.k8s import ClusterStatus, KindCluster
    except ImportError:
        # Allow observe to work without cluster check in simple mode
        pass

    # Optional cluster check
    try:
        from infra.k8s import ClusterStatus, KindCluster

        cluster = KindCluster()
        if cluster.status() != ClusterStatus.RUNNING:
            print("K-Terrarium not running. Run 'kgents infra init' first.")
            print("(Or use --simple for a demo view)")
            return 1
    except ImportError:
        if not simple:
            print("Warning: Could not check cluster status")

    try:
        from agents.i.terrarium_tui import (
            TEXTUAL_AVAILABLE,
            Resolution,
            TerrariumApp,
            TerrariumDataSource,
            run_terrarium,
        )
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure agents.i.terrarium_tui is properly installed")
        return 1

    # Determine which renderer to use
    use_textual = not simple and TEXTUAL_AVAILABLE

    if not use_textual and not simple:
        print("Textual not available. Using simple renderer.")
        print("Install with: pip install textual")

    print("K-Terrarium Observe")
    print("=" * 40)
    print("Starting Terrarium TUI...")
    print("Press Ctrl+C to exit")
    print()

    try:
        await run_terrarium(
            use_textual=use_textual,
            compact=compact,
            focus=focus,
        )
        return 0

    except KeyboardInterrupt:
        print("\nExiting...")
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        return 1


def _parse_args(args: list[str]) -> dict[str, Any]:
    """Parse command line arguments."""
    options: dict[str, Any] = {}
    i = 0

    while i < len(args):
        arg = args[i]

        if arg == "--compact":
            options["compact"] = True
            i += 1
        elif arg == "--simple":
            options["simple"] = True
            i += 1
        elif arg == "--focus":
            if i + 1 >= len(args):
                options["error"] = "--focus requires an agent name"
                return options
            options["focus"] = args[i + 1]
            i += 2
        elif arg.startswith("-"):
            options["error"] = f"Unknown option: {arg}"
            return options
        else:
            # Unexpected positional arg
            options["error"] = f"Unexpected argument: {arg}"
            return options

    return options

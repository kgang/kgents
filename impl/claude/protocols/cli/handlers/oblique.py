"""
Oblique Strategies Handler: Brian Eno's lateral thinking prompts.

Serves a random strategy from the Oblique Strategies deck to break
creative blocks and shift perspective.

Usage:
    kgents oblique              # Random strategy
    kgents oblique --list       # Show all strategies
    kgents oblique --seed 42    # Reproducible random

AGENTESE Path: concept.creativity.oblique

Note: Strategies are educational quotes, used for lateral thinking
and creative problem-solving.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# =============================================================================
# Oblique Strategies Deck (Public Domain Educational Use)
# =============================================================================

# Core strategies from Brian Eno & Peter Schmidt's deck
# These are educational prompts for creative thinking
OBLIQUE_STRATEGIES = [
    "Honor thy error as a hidden intention",
    "What would your closest friend do?",
    "What wouldn't you do?",
    "Emphasize differences",
    "Remove specifics and convert to ambiguities",
    "Don't be frightened of clichés",
    "What is the reality of the situation?",
    "Are there sections? Consider transitions",
    "Turn it upside down",
    "Think of the radio",
    "Allow an easement (an easement is the abandonment of a stricture)",
    "Simple subtraction",
    "Go slowly all the way round the outside",
    "A line has two sides",
    "Make a sudden, destructive unpredictable action; incorporate",
    "Consult other sources - promising - unpromising",
    "Use an unacceptable color",
    "Humanize something free of error",
    "What mistakes did you make last time?",
    "Infinitesimal gradations",
    "Change instrument roles",
    "Accretion",
    "Disconnect from desire",
    "Emphasize the flaws",
    "Remember those quiet evenings",
    "Give the game away",
    "Spectrum analysis",
    "Accept advice",
    "Tidy up",
    "Do the words need changing?",
    "Ask people to work against their better judgment",
    "Take away the elements in order of apparent non-importance",
    "Breathe more deeply",
    "Only one element of each kind",
    "Is there something missing?",
    "Use 'unqualified' people",
    "How would you have done it?",
    "Emphasize repetitions",
    "Don't be afraid of things because they're easy to do",
    "Don't be frightened to display your talents",
    "Abandon normal instruments",
    "Tape your mouth",
    "Do nothing for as long as possible",
    "Water",
    "Just carry on",
    "State the problem in words as clearly as possible",
    "Trust in the you of now",
    "Work at a different speed",
    "Not building a wall but making a brick",
    "Gardening, not architecture",
]


@dataclass
class ObliqueStrategy:
    """A single oblique strategy."""

    text: str
    index: int

    def to_dict(self) -> "dict[str, Any]":
        """Convert to JSON-serializable dict."""
        return {
            "text": self.text,
            "index": self.index,
            "deck_size": len(OBLIQUE_STRATEGIES),
        }


def _emit_output(
    human: str,
    semantic: "dict[str, Any] | ObliqueStrategy",
    ctx: "InvocationContext | None",
) -> None:
    """Emit output to appropriate channels."""
    print(human)

    if ctx is not None and hasattr(ctx, "emit_semantic"):
        data = semantic.to_dict() if isinstance(semantic, ObliqueStrategy) else semantic
        ctx.emit_semantic(data)


def _print_help() -> None:
    """Print help for oblique command."""
    print(__doc__)
    print()
    print("OPTIONS:")
    print("  --list              Show all strategies")
    print("  --seed <n>          Use specific seed for reproducibility")
    print("  --json              Output as JSON")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print("  kgents oblique                  # Random strategy")
    print("  kgents oblique --list           # Browse all")
    print("  kgents oblique --seed 42        # Reproducible")
    print()
    print("ABOUT OBLIQUE STRATEGIES:")
    print("  Created by Brian Eno and Peter Schmidt in 1975.")
    print("  Used to break creative blocks by shifting perspective.")
    print("  'Over One Hundred Worthwhile Dilemmas'")


def cmd_oblique(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Oblique Strategies: Lateral thinking prompts.

    AGENTESE Path: concept.creativity.oblique

    Returns a random strategy from the deck to shift creative perspective.

    Returns:
        0 on success, 1 on error
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("oblique", args)
        except ImportError:
            pass

    # Parse flags
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    list_mode = "--list" in args
    json_mode = "--json" in args

    # Parse seed
    seed = None
    for i, arg in enumerate(args):
        if arg == "--seed" and i + 1 < len(args):
            try:
                seed = int(args[i + 1])
            except ValueError:
                print("[OBLIQUE] Invalid seed value")
                return 1

    if list_mode:
        # List all strategies
        if json_mode:
            import json

            data = {
                "strategies": [
                    {"index": i, "text": s} for i, s in enumerate(OBLIQUE_STRATEGIES)
                ],
                "count": len(OBLIQUE_STRATEGIES),
            }
            print(json.dumps(data, indent=2))
        else:
            print("Oblique Strategies")
            print("=" * 50)
            for i, strat_text in enumerate(OBLIQUE_STRATEGIES):
                print(f"  {i + 1:2d}. {strat_text}")
            print()
            print(f"Total: {len(OBLIQUE_STRATEGIES)} strategies")
        return 0

    # Select random strategy
    if seed is not None:
        random.seed(seed)

    idx = random.randint(0, len(OBLIQUE_STRATEGIES) - 1)
    strategy = ObliqueStrategy(text=OBLIQUE_STRATEGIES[idx], index=idx)

    if json_mode:
        import json

        print(json.dumps(strategy.to_dict(), indent=2))
    else:
        # Beautiful output with box
        print()
        print("\033[35m┌" + "─" * 58 + "┐\033[0m")
        print(
            f"\033[35m│\033[0m  \033[1;33m{strategy.text:<54}\033[0m  \033[35m│\033[0m"
        )
        print("\033[35m└" + "─" * 58 + "┘\033[0m")
        print()
        print("\033[90m  — Oblique Strategies (Eno/Schmidt)\033[0m")
        print()

    # Emit semantic for pipelines
    if ctx is not None and hasattr(ctx, "emit_semantic"):
        ctx.emit_semantic(strategy.to_dict())

    return 0

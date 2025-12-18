"""
Joy Handler: Thin routing to void.joy.* AGENTESE paths.

Playful creative disruption commands - Brian Eno's Oblique Strategies and more.

Usage:
    kg joy               # Get an oblique strategy (default)
    kg joy oblique       # Get an Oblique Strategy card
    kg joy surprise      # Get a surprise creative prompt
    kg joy challenge     # Get a creative challenge
    kg joy flinch        # Surface what you're avoiding
    kg joy play          # Random combination of all modes

AGENTESE Paths:
    void.joy.oblique   - Brian Eno / Peter Schmidt Oblique Strategies
    void.joy.surprise  - Creative disruption prompts
    void.joy.challenge - Constraint-based creative challenges
    void.joy.flinch    - Productive friction (the edge of growth)
    void.joy.play      - Random creative mode

> "Honor thy error as a hidden intention." — Oblique Strategies
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# Subcommand -> AGENTESE path mapping
JOY_SUBCOMMAND_MAP: dict[str, str] = {
    "oblique": "void.joy.oblique",
    "surprise": "void.joy.surprise",
    "challenge": "void.joy.challenge",
    "flinch": "void.joy.flinch",
    "play": "void.joy.play",
}


def cmd_joy(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Playful creative disruption via void.joy.* paths.

    Routes CLI invocations to void.joy.* paths via the projection functor.
    """
    # Help
    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0

    # Parse subcommand (default: oblique)
    subcommand = "oblique"
    for arg in args:
        if arg in JOY_SUBCOMMAND_MAP:
            subcommand = arg
            break

    # Route to AGENTESE path
    path = JOY_SUBCOMMAND_MAP.get(subcommand, "void.joy.oblique")

    # Parse kwargs from remaining args
    kwargs: dict[str, str | bool] = {}
    if "--json" in args:
        kwargs["json_output"] = True

    # Handle positional args (context for oblique/surprise/etc.)
    positional = [a for a in args if not a.startswith("-") and a not in JOY_SUBCOMMAND_MAP]
    if positional:
        kwargs["context"] = " ".join(positional)

    # Project through CLI functor
    from protocols.cli.projection import project_command

    return project_command(
        path=path,
        args=args,
        ctx=ctx,
        kwargs=kwargs,
    )

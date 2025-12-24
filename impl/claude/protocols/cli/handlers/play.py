"""
Play Handler: Interactive Playground for kgents.

Zero-to-delight in under 5 minutes via guided interactive tutorials.
The playground teaches through doing, not through documentation.

Usage:
    kgents play              # Interactive menu
    kgents play hello        # Jump to Hello World tutorial
    kgents play compose      # Jump to Composition tutorial
    kgents play functor      # Jump to Functor/Maybe tutorial
    kgents play soul         # Jump to K-gent dialogue tutorial
    kgents play repl         # Free exploration REPL
    kgents play --help       # Show help

Example:
    kgents play
    -> Shows interactive menu with 5 tutorials
"""

from __future__ import annotations

import asyncio
import sys
from typing import TYPE_CHECKING, Any

from protocols.cli.handler_meta import handler

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_help() -> None:
    """Print help for play command."""
    print(__doc__)
    print()
    print("TUTORIALS:")
    print("  hello       Your first agent (Agent[str, str])")
    print("  compose     Pipe agents together (>>)")
    print("  functor     Lift to Maybe (handle optional values)")
    print("  soul        Chat with K-gent (Kent's simulacrum)")
    print("  repl        Free exploration (pre-imported modules)")
    print()
    print("OPTIONS:")
    print("  --json      Output progress as JSON")
    print("  --help, -h  Show this help")


@handler("play", is_async=False, needs_pty=True, tier=2, description="Interactive playground tutorials")
def cmd_play(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Interactive Playground: Learn kgents by doing.

    The playground provides guided tutorials that:
    1. Show you the code being written
    2. Explain the concept in one sentence
    3. Let you modify and experiment
    4. Provide clear next steps
    """
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("play", args)
        except ImportError:
            pass

    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    json_mode = "--json" in args

    # Get subcommand
    subcommand = None
    for arg in args:
        if arg.startswith("-"):
            continue
        subcommand = arg
        break

    # Special case: REPL must run synchronously (not inside asyncio.run)
    if subcommand == "repl":
        from ._playground.repl import start_repl_sync

        return start_repl_sync(json_mode, ctx)

    result = asyncio.run(_async_play(subcommand, json_mode, ctx))

    # Handle sentinel: -1 means "run REPL sync" (selected from menu)
    if result == -1:
        from ._playground.repl import start_repl_sync

        return start_repl_sync(json_mode, ctx)

    return result


async def _async_play(
    subcommand: str | None,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Async implementation of play command."""
    try:
        from ._playground import (
            TUTORIALS,
            _load_tutorials,
            run_tutorial,
            show_menu,
            start_repl,
        )

        # Ensure tutorials are loaded
        _load_tutorials()

        # Direct jump to tutorial or REPL
        if subcommand:
            if subcommand == "repl":
                return await start_repl(json_mode, ctx)
            if subcommand in TUTORIALS:
                return await run_tutorial(subcommand, json_mode, ctx)
            _emit_output(
                f"[PLAY] Unknown tutorial: {subcommand}",
                {"error": f"Unknown tutorial: {subcommand}"},
                ctx,
            )
            _emit_output(
                f"Available: {', '.join(TUTORIALS.keys())}",
                {"available": list(TUTORIALS.keys())},
                ctx,
            )
            return 1

        # Interactive menu
        return await show_menu(json_mode, ctx)

    except ImportError as e:
        _emit_output(
            f"[PLAY] Module not available: {e}",
            {"error": f"Module not available: {e}"},
            ctx,
        )
        return 1
    except Exception as e:
        _emit_output(
            f"[PLAY] Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


def _emit_output(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """Emit output via dual-channel if ctx available, else print."""
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)

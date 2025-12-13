"""
Playground REPL: Free exploration with pre-imported modules.

Provides an interactive Python environment with all kgents
modules pre-imported, ready for experimentation.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


REPL_BANNER = """
============================================================
          kgents Playground - Free Exploration
============================================================

All kgents modules are pre-imported. Try:

  >>> agent = GreetAgent()
  >>> run_async(agent.invoke("World"))
  'Hello, World!'

  >>> pipeline = DoubleAgent() >> StringifyAgent()
  >>> run_async(pipeline.invoke(21))
  'Result: 42'

Type 'exit()' or Ctrl+D to quit.
============================================================
"""


def start_repl_sync(
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """
    Start an interactive REPL with pre-imported modules.

    This is a SYNC function because all REPL backends (IPython, ptpython,
    code.interact) are blocking/synchronous. Must be called outside of
    an async context.
    """
    import asyncio

    if json_mode:
        import json

        data = {"status": "repl_not_supported_in_json_mode"}
        _emit_output(json.dumps(data), data, ctx)
        return 1

    _emit_output(REPL_BANNER, {"status": "repl_starting"}, ctx)

    # Build pre-import namespace
    namespace = _build_namespace()

    # Add async helper that works in sync REPL
    def run_async(coro: Any) -> Any:
        """Helper to run async code in the REPL."""
        return asyncio.run(coro)

    namespace["run_async"] = run_async
    namespace["asyncio"] = asyncio

    # Try to use IPython if available (best experience)
    try:
        from IPython import embed  # type: ignore[import-not-found]

        _emit_output(
            "\nUsing IPython. Use run_async(coro) for async code.",
            {"repl": "ipython"},
            ctx,
        )
        embed(
            user_ns=namespace,
            banner1="",
            confirm_exit=False,
        )
        return 0
    except ImportError:
        pass

    # Fall back to ptpython if available (sync mode)
    try:
        from ptpython.repl import embed as pt_embed  # type: ignore[import-not-found]

        _emit_output(
            "\nUsing ptpython. Use run_async(coro) for async code.",
            {"repl": "ptpython"},
            ctx,
        )
        pt_embed(globals=namespace, locals=namespace)
        return 0
    except ImportError:
        pass

    # Fall back to standard Python REPL
    import code

    _emit_output(
        "\nNote: Using basic Python REPL. Install 'ipython' for a better experience.",
        {"repl": "basic"},
        ctx,
    )
    _emit_output(
        "Use run_async(coro) to run async code, e.g.:",
        {},
        ctx,
    )
    _emit_output(
        "  >>> run_async(agent.invoke('World'))",
        {},
        ctx,
    )
    _emit_output("", {}, ctx)

    # Start REPL
    code.interact(
        local=namespace,
        banner="",
        exitmsg="[Goodbye!]",
    )

    return 0


async def start_repl(
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """
    Async wrapper for start_repl_sync.

    Returns a sentinel value that signals the caller to run the REPL
    synchronously after exiting the async context.
    """
    if json_mode:
        import json

        data = {"status": "repl_not_supported_in_json_mode"}
        _emit_output(json.dumps(data), data, ctx)
        return 1

    # Return special code to signal "run REPL sync"
    return -1  # Sentinel: means "run REPL outside async"


def _build_namespace() -> dict[str, Any]:
    """Build the pre-import namespace for the REPL."""
    namespace: dict[str, Any] = {}

    # Try to import core modules
    try:
        from bootstrap.types import Agent

        namespace["Agent"] = Agent
    except ImportError:
        pass

    # Import archetypes
    try:
        from agents.a import Capability, Delta, Kappa, Lambda, get_halo

        namespace["Kappa"] = Kappa
        namespace["Lambda"] = Lambda
        namespace["Delta"] = Delta
        namespace["Capability"] = Capability
        namespace["get_halo"] = get_halo
    except ImportError:
        pass

    # Import Maybe functor
    try:
        from agents.c import Just, Maybe, MaybeFunctor, Nothing

        namespace["Maybe"] = Maybe
        namespace["Just"] = Just
        namespace["Nothing"] = Nothing
        namespace["MaybeFunctor"] = MaybeFunctor
    except ImportError:
        pass

    # Import Flux
    try:
        from agents.flux import Flux, FluxAgent, FluxConfig

        namespace["Flux"] = Flux
        namespace["FluxAgent"] = FluxAgent
        namespace["FluxConfig"] = FluxConfig
    except ImportError:
        pass

    # Import K-gent Soul
    try:
        from agents.k import BudgetTier, DialogueMode, KgentSoul

        namespace["KgentSoul"] = KgentSoul
        namespace["DialogueMode"] = DialogueMode
        namespace["BudgetTier"] = BudgetTier
    except ImportError:
        pass

    # Import example agents
    try:
        from agents.examples.hello_world import GreetAgent

        namespace["GreetAgent"] = GreetAgent
    except ImportError:
        pass

    try:
        from agents.examples.composed_pipeline import (
            DoubleAgent,
            ParseIntAgent,
            StringifyAgent,
        )

        namespace["DoubleAgent"] = DoubleAgent
        namespace["StringifyAgent"] = StringifyAgent
        namespace["ParseIntAgent"] = ParseIntAgent
    except ImportError:
        pass

    return namespace


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

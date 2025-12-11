"""
J-gent CLI Commands - JIT Agent Intelligence operations.

This module is a thin wrapper that delegates to the Prism-based JitCLI.
See: agents/j/cli.py for the full implementation.
"""

from __future__ import annotations

import asyncio


def cmd_jit(args: list[str]) -> int:
    """J-gent JIT CLI handler - delegates to Prism."""
    from agents.j.cli import JitCLI
    from protocols.cli.prism import Prism

    return asyncio.run(Prism(JitCLI()).dispatch(args))

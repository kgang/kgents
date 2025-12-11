"""
G-gent CLI Commands - Grammar/DSL operations.

This module is a thin wrapper that delegates to the Prism-based GrammarianCLI.
See: agents/g/cli.py for the full implementation.
"""

from __future__ import annotations

import asyncio


def cmd_grammar(args: list[str]) -> int:
    """G-gent Grammar CLI handler - delegates to Prism."""
    from agents.g.cli import GrammarianCLI
    from protocols.cli.prism import Prism

    return asyncio.run(Prism(GrammarianCLI()).dispatch(args))

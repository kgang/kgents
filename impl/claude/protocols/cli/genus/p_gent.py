"""
P-gent CLI Commands - Parser operations.

This module is a thin wrapper that delegates to the Prism-based ParserCLI.
See: agents/p/cli.py for the full implementation.
"""

from __future__ import annotations

import asyncio


def cmd_parse(args: list[str]) -> int:
    """P-gent Parser CLI handler - delegates to Prism."""
    from agents.p.cli import ParserCLI
    from protocols.cli.prism import Prism

    return asyncio.run(Prism(ParserCLI()).dispatch(args))

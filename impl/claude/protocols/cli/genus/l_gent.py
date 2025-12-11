"""
L-gent CLI Commands - Library/Catalog operations.

This module is a thin wrapper that delegates to the Prism-based LibraryCLI.
See: agents/l/cli.py for the full implementation.
"""

from __future__ import annotations

import asyncio


def cmd_library(args: list[str]) -> int:
    """L-gent Library CLI handler - delegates to Prism."""
    from agents.l.cli import LibraryCLI
    from protocols.cli.prism import Prism

    return asyncio.run(Prism(LibraryCLI()).dispatch(args))

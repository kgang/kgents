"""
I-gent CLI Commands - Garden/Interface operations.

This module is a thin wrapper that delegates to the Prism-based GardenCLI.
See: agents/i/cli.py for the full implementation.
"""

from __future__ import annotations

import asyncio


def cmd_garden(args: list[str]) -> int:
    """I-gent Garden CLI handler - delegates to Prism."""
    from agents.i.cli import GardenCLI
    from protocols.cli.prism import Prism

    return asyncio.run(Prism(GardenCLI()).dispatch(args))

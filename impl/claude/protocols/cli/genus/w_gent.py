"""
W-gent CLI Commands - Witness/Wire operations.

This module is a thin wrapper that delegates to the Prism-based WitnessCLI.
See: agents/w/cli.py for the full implementation.
"""

from __future__ import annotations

import asyncio


def cmd_witness(args: list[str]) -> int:
    """W-gent Witness CLI handler - delegates to Prism."""
    from agents.w.cli import WitnessCLI
    from protocols.cli.prism import Prism

    return asyncio.run(Prism(WitnessCLI()).dispatch(args))

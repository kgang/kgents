"""
Core Tools: Type I Tools for U-gent Infrastructure.

This module provides the core file and search tools as Tool[A,B] adapters.
All tools delegate to existing infrastructure (FileEditGuard, world.file).

The 5 Core Tools:
- ReadTool: Read file content (L0)
- WriteTool: Write file content (L2)
- EditTool: Edit via string replacement (L2)
- GlobTool: Pattern-based file discovery (L0)
- GrepTool: Content search (L0)

Registration:
    from services.tooling.tools import register_core_tools
    register_core_tools(registry)

Composition:
    from services.tooling.tools import ReadTool, GrepTool
    pipeline = ReadTool() >> GrepTool()

See: spec/services/tooling.md §3 (Core Tools)
See: plans/ugent-tooling-phase1-handoff.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .file import EditTool, ReadTool, WriteTool, create_read_proof
from .search import GlobTool, GrepTool

if TYPE_CHECKING:
    from ..registry import ToolRegistry


def register_core_tools(registry: "ToolRegistry") -> None:
    """
    Register all core tools with the registry.

    This is the single registration point for Phase 1 tools.
    Called during application bootstrap.

    Args:
        registry: ToolRegistry to register with
    """
    # File tools (delegate to FileEditGuard)
    registry.register(ReadTool())
    registry.register(WriteTool())
    registry.register(EditTool())

    # Search tools
    registry.register(GlobTool())
    registry.register(GrepTool())


__all__ = [
    # File tools
    "ReadTool",
    "WriteTool",
    "EditTool",
    "create_read_proof",
    # Search tools
    "GlobTool",
    "GrepTool",
    # Registration
    "register_core_tools",
]

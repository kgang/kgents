"""
U-gent Tools: Tool[A,B] Adapters for Agent Infrastructure.

This module provides tools as categorical morphisms Tool[A,B].
All tools compose via >> and integrate with the trust gate.

Phase 1 - Core Tools (5 tools):
- ReadTool: Read file content (L0)
- WriteTool: Write file content (L2)
- EditTool: Edit via string replacement (L2)
- GlobTool: Pattern-based file discovery (L0)
- GrepTool: Content search (L0)

Phase 2 - System Tools (4 tools):
- BashTool: Shell execution with safety (L3)
- KillShellTool: Background process termination (L2)
- WebFetchTool: URL fetch with caching (L1)
- WebSearchTool: Web search with citations (L1)

Registration:
    from services.tooling.tools import register_core_tools, register_system_tools
    register_core_tools(registry)
    register_system_tools(registry)

Composition:
    from services.tooling.tools import ReadTool, GrepTool
    pipeline = ReadTool() >> GrepTool()

See: spec/services/tooling.md §3 (Tools)
See: plans/ugent-tooling-phase1-handoff.md
See: plans/ugent-tooling-phase2-handoff.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .file import EditTool, ReadTool, WriteTool, create_read_proof
from .search import GlobTool, GrepTool
from .system import BashTool, KillShellTool
from .web import WebFetchTool, WebSearchTool

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


def register_system_tools(registry: "ToolRegistry") -> None:
    """
    Register all system tools with the registry.

    This is the single registration point for Phase 2 tools.
    Called during application bootstrap.

    Args:
        registry: ToolRegistry to register with
    """
    # Shell tools
    registry.register(BashTool())
    registry.register(KillShellTool())

    # Web tools
    registry.register(WebFetchTool())
    registry.register(WebSearchTool())


def register_all_tools(registry: "ToolRegistry") -> None:
    """
    Register all available tools.

    Convenience function that registers both core and system tools.

    Args:
        registry: ToolRegistry to register with
    """
    register_core_tools(registry)
    register_system_tools(registry)


__all__ = [
    # File tools
    "ReadTool",
    "WriteTool",
    "EditTool",
    "create_read_proof",
    # Search tools
    "GlobTool",
    "GrepTool",
    # System tools
    "BashTool",
    "KillShellTool",
    # Web tools
    "WebFetchTool",
    "WebSearchTool",
    # Registration
    "register_core_tools",
    "register_system_tools",
    "register_all_tools",
]

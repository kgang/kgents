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

Phase 3 - Orchestration Tools (6 tools):
- TodoListTool: List tasks with optional filter (L0)
- TodoCreateTool: Create/replace task list (L0)
- TodoUpdateTool: Update task status (L0)
- EnterPlanModeTool: Enter plan mode (L0)
- ExitPlanModeTool: Exit plan mode with approval (L0)
- ClarifyTool: Structured human-in-the-loop questions (L0)

Registration:
    from services.tooling.tools import register_all_tools
    register_all_tools(registry)

Composition:
    from services.tooling.tools import ReadTool, GrepTool
    pipeline = ReadTool() >> GrepTool()

See: spec/services/tooling.md §3 (Tools)
See: plans/ugent-tooling-phase3-handoff.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .clarify import ClarifyTool, QuestionBuilder
from .file import EditTool, ReadTool, WriteTool, create_read_proof
from .mode import (
    EnterPlanModeTool,
    ExitPlanModeTool,
    ModeQueryTool,
    get_mode_state,
    reset_mode_state,
    set_approval_handler,
    set_mode_state,
)
from .portal import (
    OpenPortal,
    PortalTool,
    PortalWriteTool,
    get_open_portals,
    reset_open_portals,
)
from .search import GlobTool, GrepTool
from .system import BashTool, KillShellTool
from .task import (
    TodoCreateTool,
    TodoListTool,
    TodoTool,
    TodoUpdateTool,
    get_task_store,
    reset_task_store,
    set_task_store,
)
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


def register_orchestration_tools(registry: "ToolRegistry") -> None:
    """
    Register all orchestration tools with the registry.

    This is the single registration point for Phase 3 tools.
    Called during application bootstrap.

    Args:
        registry: ToolRegistry to register with
    """
    # Task tools
    registry.register(TodoListTool())
    registry.register(TodoCreateTool())
    registry.register(TodoUpdateTool())

    # Mode tools
    registry.register(EnterPlanModeTool())
    registry.register(ExitPlanModeTool())
    registry.register(ModeQueryTool())

    # Clarify tool
    registry.register(ClarifyTool())

    # Portal tools
    registry.register(PortalTool())
    registry.register(PortalWriteTool())


def register_all_tools(registry: "ToolRegistry") -> None:
    """
    Register all available tools.

    Convenience function that registers all tool phases.

    Args:
        registry: ToolRegistry to register with
    """
    register_core_tools(registry)
    register_system_tools(registry)
    register_orchestration_tools(registry)


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
    # Task tools
    "TodoTool",
    "TodoListTool",
    "TodoCreateTool",
    "TodoUpdateTool",
    "get_task_store",
    "set_task_store",
    "reset_task_store",
    # Mode tools
    "EnterPlanModeTool",
    "ExitPlanModeTool",
    "ModeQueryTool",
    "get_mode_state",
    "set_mode_state",
    "reset_mode_state",
    "set_approval_handler",
    # Clarify tool
    "ClarifyTool",
    "QuestionBuilder",
    # Portal tools
    "PortalTool",
    "PortalWriteTool",
    "OpenPortal",
    "get_open_portals",
    "reset_open_portals",
    # Registration
    "register_core_tools",
    "register_system_tools",
    "register_orchestration_tools",
    "register_all_tools",
]

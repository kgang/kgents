"""
AGENTESE Self REPL Context: REPL state and conversation memory.

CLI v7 Phase 4: The REPL

The self.repl context provides access to REPL session state:
- self.repl.manifest - View REPL status and memory overview
- self.repl.memory - Get conversation memory (last N turns)
- self.repl.history - Get command history
- self.repl.context - Get current navigation context

The REPL is a "conversation partner, not a command executor."
It remembers. It shows who's around.

AGENTESE: self.repl.*

Principle Alignment:
- Composable: REPL state composes with other self.* contexts
- Transparent: Memory utilization is always visible
- Joy-Inducing: "What did I just ask?" should work
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..contract import Response
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger(__name__)

# REPL affordances
REPL_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "memory",
    "history",
    "context",
)


# Contracts for type-safe FE/BE sync
@dataclass
class ReplManifestResponse:
    """REPL manifest response."""

    turn_count: int
    max_turns: int
    utilization: float
    current_path: str
    observer: str
    has_summary: bool
    command_history_length: int


@dataclass
class MemoryResponse:
    """Conversation memory response."""

    turns: list[dict[str, str]]
    total: int
    has_summary: bool
    summary: str | None


@dataclass
class HistoryRequest:
    """Command history request."""

    limit: int = 20
    query: str = ""


@dataclass
class HistoryResponse:
    """Command history response."""

    commands: list[str]
    total: int


@node(
    "self.repl",
    description="REPL session state and conversation memory",
    singleton=True,
    contracts={
        "manifest": Response(ReplManifestResponse),
        "memory": Response(MemoryResponse),
        "history": Response(HistoryResponse),
    },
)
@dataclass
class ReplNode(BaseLogosNode):
    """
    self.repl - REPL session interface.

    Phase 4 (CLI v7): Exposes REPL state via AGENTESE:
    - View current session status
    - Access conversation memory (via ConversationWindow)
    - Query command history
    - See navigation context

    The REPL remembers. This node makes that memory accessible.
    """

    _handle: str = "self.repl"

    # Reference to the active REPL state (injected when REPL starts)
    _repl_state: Any = None

    @property
    def handle(self) -> str:
        return self._handle

    def set_repl_state(self, state: Any) -> None:
        """Inject the active ReplState (called from repl.py)."""
        self._repl_state = state

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """REPL affordances available to all archetypes."""
        return REPL_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View REPL status and memory overview."""
        state = self._repl_state

        if state is None:
            return BasicRendering(
                summary="REPL",
                content="REPL not active. Start with: kg repl",
                metadata={"active": False},
            )

        # Get window stats
        window = state.get_window() if hasattr(state, "get_window") else None
        turn_count = window.turn_count if window else 0
        max_turns = window.max_turns if window else 0
        utilization = window.utilization if window else 0.0
        has_summary = window.has_summary if window else False

        current_path = state.current_path if hasattr(state, "current_path") else ""
        obs = state.observer if hasattr(state, "observer") else "explorer"
        history_len = len(state.history) if hasattr(state, "history") else 0

        content_lines = [
            "REPL: Interactive AGENTESE Navigation",
            "",
            f"  Current path:  {current_path or '[root]'}",
            f"  Observer:      {obs}",
            "",
            "Conversation Memory:",
            f"  Turns:         {turn_count} / {max_turns}",
            f"  Utilization:   {utilization:.0%}",
            f"  Has Summary:   {'yes' if has_summary else 'no'}",
            "",
            f"Command History: {history_len} commands",
            "",
            "Commands:",
            "  /memory        Show conversation memory",
            "  /memory toggle Enable memory indicator in prompt",
            "  /history       Show command history",
        ]

        return BasicRendering(
            summary=f"REPL: {current_path or 'root'} ({turn_count} turns)",
            content="\n".join(content_lines),
            metadata={
                "active": True,
                "turn_count": turn_count,
                "max_turns": max_turns,
                "utilization": utilization,
                "current_path": current_path,
                "observer": obs,
                "has_summary": has_summary,
                "command_history_length": history_len,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle REPL-specific aspects."""
        match aspect:
            case "memory":
                return await self._get_memory(observer, **kwargs)
            case "history":
                return await self._get_history(observer, **kwargs)
            case "context":
                return await self._get_context(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("memory")],
        help="Get conversation memory (recent turns)",
        examples=["self.repl.memory", "self.repl.memory[limit=5]"],
    )
    async def _get_memory(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get conversation memory from ConversationWindow.

        Args:
            limit: Max turns to return (default: 10)

        Returns:
            Recent conversation turns with role and content
        """
        limit = kwargs.get("limit", 10)
        state = self._repl_state

        if state is None:
            return {"error": "REPL not active", "turns": [], "total": 0}

        window = state.get_window() if hasattr(state, "get_window") else None

        if window is None:
            return {"error": "No conversation window", "turns": [], "total": 0}

        messages = window.get_context_messages()

        # Filter to user/assistant only (skip system)
        user_messages = [m for m in messages if m.role != "system"]

        # Apply limit
        recent = user_messages[-limit:]

        return {
            "turns": [
                {
                    "role": m.role,
                    "content": m.content[:500] + "..." if len(m.content) > 500 else m.content,
                }
                for m in recent
            ],
            "total": len(user_messages),
            "has_summary": window.has_summary,
            "summary": window._summary if window.has_summary else None,
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("history")],
        help="Get command history",
        examples=["self.repl.history", "self.repl.history[limit=10]"],
    )
    async def _get_history(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get command history.

        Args:
            limit: Max commands to return (default: 20)
            query: Filter by substring (optional)

        Returns:
            Recent commands
        """
        limit = kwargs.get("limit", 20)
        query = kwargs.get("query", "")
        state = self._repl_state

        if state is None:
            return {"error": "REPL not active", "commands": [], "total": 0}

        history = state.history if hasattr(state, "history") else []

        # Filter by query if provided
        if query:
            history = [h for h in history if query.lower() in h.lower()]

        # Apply limit
        recent = history[-limit:]

        return {
            "commands": recent,
            "total": len(history),
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("context")],
        help="Get current navigation context",
        examples=["self.repl.context"],
    )
    async def _get_context(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get current navigation context.

        Returns:
            Current path, observer, and available affordances
        """
        state = self._repl_state

        if state is None:
            return {"error": "REPL not active"}

        return {
            "path": state.path if hasattr(state, "path") else [],
            "current_path": state.current_path if hasattr(state, "current_path") else "",
            "observer": state.observer if hasattr(state, "observer") else "explorer",
            "running": state.running if hasattr(state, "running") else False,
        }


# Factory function
def create_repl_node() -> ReplNode:
    """Create a ReplNode instance."""
    return ReplNode()


# Singleton instance for injection
_repl_node: ReplNode | None = None


def get_repl_node() -> ReplNode:
    """Get or create the singleton ReplNode."""
    global _repl_node
    if _repl_node is None:
        _repl_node = create_repl_node()
    return _repl_node


__all__ = [
    "ReplNode",
    "REPL_AFFORDANCES",
    "create_repl_node",
    "get_repl_node",
]

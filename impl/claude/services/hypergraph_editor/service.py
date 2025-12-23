"""
HypergraphEditorService - Crown Jewel for typed-hypergraph editing.

The editor service manages editor state and operations. It wraps the
EditorPolynomial state machine and provides the service interface for
AGENTESE node access.

Philosophy:
    "Every cursor is a node. Every selection is a subgraph. Every edit is a morphism."

See: spec/surfaces/hypergraph-editor.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .core.state import (
    EditorState,
    affordances,
    backtrack,
    create_initial_state,
    enter_mode,
    navigate,
)
from .core.types import EditorMode

if TYPE_CHECKING:
    from impl.claude.protocols.exploration.types import ContextNode, Observer


@dataclass
class HypergraphEditorService:
    """
    Crown Jewel service for hypergraph editing.

    The service maintains editor state and executes operations through
    the EditorPolynomial state machine.

    This wraps the pure functional state machine (EditorState + navigate/etc.)
    with a stateful service interface for AGENTESE nodes.
    """

    _state: EditorState | None = field(default=None, init=False)

    @property
    def state(self) -> EditorState:
        """Get current editor state."""
        if self._state is None:
            raise RuntimeError("Editor not initialized - call initialize() first")
        return self._state

    async def initialize(self, focus: "ContextNode", observer: "Observer") -> None:
        """
        Initialize editor with focus on a node.

        Args:
            focus: Initial focus node
            observer: The phenomenological lens
        """
        self._state = create_initial_state(focus, observer)

    async def navigate(self, edge_type: str) -> EditorState:
        """
        Navigate via edge type from current focus.

        Args:
            edge_type: Edge type to follow ("parent", "child", etc.)

        Returns:
            New editor state after navigation

        Raises:
            RuntimeError: If editor not initialized
            ValueError: If edge_type not available from focus
        """
        current = self.state  # Raises if not initialized
        self._state = await navigate(current, edge_type)
        return self._state

    async def enter_mode(self, mode: EditorMode) -> EditorState:
        """
        Enter a new mode.

        Args:
            mode: Target mode

        Returns:
            New editor state in target mode
        """
        current = self.state
        self._state = enter_mode(current, mode)
        return self._state

    async def execute_command(self, command: str) -> dict[str, str]:
        """
        Execute an AGENTESE command or ex command.

        Args:
            command: Command string

        Returns:
            Execution result
        """
        # Stub implementation - full command execution in later phase
        return {
            "success": "false",
            "error": "Command execution not yet implemented",
            "command": command,
        }

    async def focus_node(self, focus: "ContextNode") -> EditorState:
        """
        Focus a specific node directly (not via edge).

        Args:
            focus: Node to focus

        Returns:
            New editor state with updated focus
        """
        current = self.state

        # Direct focus is like a synthetic "focus" edge
        # We update trail to record this jump
        from impl.claude.protocols.exploration.types import Trail

        new_trail = current.trail.add_step(
            node=focus.path,
            edge_taken="focus",  # Synthetic edge type for direct focus
        )

        from dataclasses import replace

        self._state = replace(
            current,
            focus=focus,
            trail=new_trail,
        )

        return self._state

    async def get_affordances(self) -> dict[str, int]:
        """
        Get available affordances from current focus.

        Returns:
            Dict mapping edge types to destination counts
        """
        current = self.state
        return await affordances(current)

    def backtrack(self) -> EditorState:
        """
        Backtrack one step in navigation trail.

        Returns:
            New editor state with previous focus

        Raises:
            ValueError: If trail is empty
        """
        current = self.state
        self._state = backtrack(current)
        return self._state


# =============================================================================
# Module Exports
# =============================================================================

__all__ = ["HypergraphEditorService"]

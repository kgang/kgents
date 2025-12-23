"""
Hypergraph Editor AGENTESE Node: @node("self.editor")

Wraps HypergraphEditorService as an AGENTESE node for universal gateway access.

AGENTESE Paths:
- self.editor.state       → Current EditorState (mode, focus, trail, etc.)
- self.editor.navigate    → Navigate via edge type
- self.editor.mode        → Enter/exit mode
- self.editor.command     → Execute AGENTESE or ex command
- self.editor.focus       → Focus a specific node by path
- self.editor.affordances → Available edge types from focus

The Modal Insight:
    "The editor IS the typed-hypergraph. Cursor position is a node focus.
     Selection is a subgraph. Edit operations are morphisms."

Philosophy:
    "Six modes are polynomial positions, not scattered conditionals."

See: spec/surfaces/hypergraph-editor.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import BaseLogosNode, BasicRendering, Renderable
from protocols.agentese.registry import node

from .contracts import (
    AffordancesRequest,
    AffordancesResponse,
    CommandRequest,
    CommandResponse,
    EditorStateResponse,
    FocusRequest,
    FocusResponse,
    ModeRequest,
    ModeResponse,
    NavigateRequest,
    NavigateResponse,
)
from .core.types import EditorMode

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from protocols.agentese.node import Observer

    from .service import HypergraphEditorService


# =============================================================================
# EditorNode
# =============================================================================


@node(
    "self.editor",
    description="Hypergraph Editor - Modal editing of the typed-hypergraph",
    dependencies=("editor_service",),
    contracts={
        # Perception aspects (Response only)
        "state": Response(EditorStateResponse),
        # Navigation aspects (Contract with request + response)
        "navigate": Contract(NavigateRequest, NavigateResponse),
        "focus": Contract(FocusRequest, FocusResponse),
        "affordances": Contract(AffordancesRequest, AffordancesResponse),
        # Mode aspects
        "mode": Contract(ModeRequest, ModeResponse),
        # Command aspects
        "command": Contract(CommandRequest, CommandResponse),
    },
    examples=[
        ("state", {}, "Get current editor state"),
        ("navigate", {"edge_type": "child"}, "Navigate to child node"),
        ("focus", {"path": "spec/agents/d-gent.md"}, "Focus specific node"),
        ("mode", {"mode": "INSERT"}, "Enter INSERT mode"),
        ("command", {"command": ":w"}, "Execute save command"),
        ("affordances", {}, "Get available edges from focus"),
    ],
)
class EditorNode(BaseLogosNode):
    """
    AGENTESE node for Hypergraph Editor Crown Jewel.

    Exposes HypergraphEditorService through the universal protocol.
    All transports (HTTP, WebSocket, CLI, TUI) collapse to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/self/editor/navigate
        {"edge_type": "child"}

        # Via Logos directly
        await logos.invoke("self.editor.navigate", observer, edge_type="child")

        # Via CLI
        kg editor navigate child

    Teaching:
        gotcha: EditorNode REQUIRES editor_service dependency. Without it,
                instantiation fails with TypeError.
                (Pattern: See BrainNode for DI example)

        gotcha: Mode transitions follow polynomial laws. Not all mode
                transitions are valid. The service enforces transition rules.
                (Evidence: spec/surfaces/hypergraph-editor.md → Laws/Invariants)

        gotcha: Navigation is edge-based, not path-based. You navigate by
                following typed edges (parent, child, definition, etc.), not
                by constructing arbitrary paths.
                (Philosophy: "The file is a lie. There is only the graph.")
    """

    def __init__(self, editor_service: "HypergraphEditorService") -> None:
        """
        Initialize EditorNode.

        Args:
            editor_service: The editor service (injected by container)

        Raises:
            TypeError: If editor_service is not provided (intentional for fallback)
        """
        self._editor = editor_service

    @property
    def handle(self) -> str:
        return "self.editor"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        The editor has different capabilities for different observer archetypes:
        - developer/operator: Full access (all modes, all commands)
        - architect/researcher: Navigation + VISUAL + COMMAND (no INSERT)
        - newcomer/casual: Navigation + basic commands
        - guest: Read-only navigation
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: developers, operators
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return (
                "state",
                "navigate",
                "focus",
                "affordances",
                "mode",
                "command",
            )

        # Architects: Navigation + exploration, no INSERT mode
        if archetype_lower in ("architect", "artist", "researcher", "technical"):
            return (
                "state",
                "navigate",
                "focus",
                "affordances",
                "mode",  # Can use VISUAL, COMMAND, GRAPH modes
            )

        # Newcomers: Basic navigation + commands
        if archetype_lower in ("newcomer", "casual", "reviewer"):
            return (
                "state",
                "navigate",
                "focus",
                "affordances",
            )

        # Guest: Read-only navigation
        return (
            "state",
            "navigate",
            "affordances",
        )

    async def manifest(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        Manifest editor state to observer.

        AGENTESE: self.editor.state

        Returns:
            BasicRendering with current editor state
        """
        try:
            state = self._editor.state
            response = EditorStateResponse(
                mode=state.mode.name,
                focus_path=state.focus.path,
                trail_length=len(state.trail.steps),
                has_kblock=state.kblock is not None,
                selection_count=len(state.selection),
                kblock_id=state.kblock.id if state.kblock else None,
                command_buffer="",  # Not yet implemented
            )

            return BasicRendering(
                summary=f"Editor: {state.mode.name} mode at {state.focus.path}",
                content=f"Mode: {state.mode.name}\nFocus: {state.focus.path}\nTrail depth: {len(state.trail.steps)}",
                metadata={
                    "mode": response.mode,
                    "focus_path": response.focus_path,
                    "trail_length": response.trail_length,
                    "has_kblock": response.has_kblock,
                    "selection_count": response.selection_count,
                    "kblock_id": response.kblock_id,
                    "command_buffer": response.command_buffer,
                },
            )

        except RuntimeError as e:
            # Editor not initialized
            return BasicRendering(
                summary="Editor not initialized",
                content=str(e),
                metadata={"error": "not_initialized"},
            )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to service methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        try:
            if aspect == "state":
                return await self.manifest(observer, **kwargs)

            elif aspect == "navigate":
                edge_type = kwargs.get("edge_type", "")
                if not edge_type:
                    return NavigateResponse(
                        success=False,
                        error="edge_type required",
                    )

                try:
                    new_state = await self._editor.navigate(edge_type)
                    return NavigateResponse(
                        success=True,
                        new_focus=new_state.focus.path,
                        edge_type=edge_type,
                        message=f"Navigated via {edge_type} to {new_state.focus.path}",
                    )
                except Exception as e:
                    return NavigateResponse(
                        success=False,
                        error=f"Navigation failed: {e}",
                        edge_type=edge_type,
                    )

            elif aspect == "focus":
                path = kwargs.get("path", "")
                if not path:
                    return FocusResponse(
                        success=False,
                        error="path required",
                    )

                # Create a ContextNode from the path
                from impl.claude.protocols.exploration.types import ContextNode

                # Extract holon from path (last segment)
                holon = path.split(".")[-1]
                focus_node = ContextNode(path=path, holon=holon)

                try:
                    new_state = await self._editor.focus_node(focus_node)
                    return FocusResponse(
                        success=True,
                        focused_path=new_state.focus.path,
                        message=f"Focused on {path}",
                    )
                except Exception as e:
                    return FocusResponse(
                        success=False,
                        error=f"Focus failed: {e}",
                    )

            elif aspect == "mode":
                mode_str = kwargs.get("mode", "")
                if not mode_str:
                    return ModeResponse(
                        success=False,
                        mode=self._editor.state.mode.name,
                        error="mode required",
                    )

                # Parse mode
                try:
                    mode = EditorMode[mode_str.upper()]
                except KeyError:
                    return ModeResponse(
                        success=False,
                        mode=self._editor.state.mode.name,
                        error=f"Invalid mode: {mode_str}",
                    )

                try:
                    new_state = await self._editor.enter_mode(mode)
                    return ModeResponse(
                        success=True,
                        mode=new_state.mode.name,
                        message=f"Entered {new_state.mode.name} mode",
                    )
                except Exception as e:
                    return ModeResponse(
                        success=False,
                        mode=self._editor.state.mode.name,
                        error=f"Mode transition failed: {e}",
                    )

            elif aspect == "command":
                command = kwargs.get("command", "")
                if not command:
                    return CommandResponse(
                        success=False,
                        error="command required",
                    )

                try:
                    result = await self._editor.execute_command(command)
                    return CommandResponse(
                        success=result.get("success", False) == "true",
                        output=result.get("output", ""),
                        result=result,
                        error=result.get("error"),
                    )
                except Exception as e:
                    return CommandResponse(
                        success=False,
                        error=f"Command execution failed: {e}",
                    )

            elif aspect == "affordances":
                from_path = kwargs.get("from_path")
                current_focus = self._editor.state.focus.path

                # If from_path specified, temporarily focus it (without updating state)
                if from_path and from_path != current_focus:
                    # TODO: Query affordances without changing focus
                    # For now, use current focus
                    pass

                try:
                    affordances = await self._editor.get_affordances()
                    return AffordancesResponse(
                        affordances=affordances,
                        focus_path=current_focus,
                    )
                except Exception as e:
                    return AffordancesResponse(
                        affordances={},
                        focus_path=current_focus,
                    )

            else:
                return {"error": f"Unknown aspect: {aspect}"}

        except RuntimeError as e:
            # Editor not initialized
            return {"error": f"Editor not initialized: {e}"}


# =============================================================================
# Module Exports
# =============================================================================

__all__ = ["EditorNode"]

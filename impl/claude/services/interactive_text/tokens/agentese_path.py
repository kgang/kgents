"""
AGENTESEPath Token Implementation.

The AGENTESEPath token represents a portal to the agent system via the
AGENTESE protocol. It recognizes backtick-wrapped paths like `world.town.citizen`
and provides affordances for navigation, inspection, and invocation.

Affordances:
- hover: Display polynomial state (current position, valid transitions)
- click: Navigate to the path's Habitat (AD-010)
- right-click: Show context menu with invoke, view source, copy options
- drag: Pre-fill the path for invocation in REPL

Ghost Tokens:
When an AGENTESEPath references a non-existent node, it renders as a
"ghost token" with reduced affordances (no invoke, no state display).

See: .kiro/specs/meaning-token-frontend/design.md
Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from services.interactive_text.contracts import (
    Affordance,
    AffordanceAction,
    Observer,
    ObserverRole,
    TokenDefinition,
)
from services.interactive_text.registry import TokenRegistry

from .base import BaseMeaningToken, filter_affordances_by_observer


@dataclass(frozen=True)
class PolynomialState:
    """State information for an AGENTESE node.

    Represents the current position and valid transitions for a node
    in the polynomial state machine.

    Attributes:
        position: Current state/mode of the node
        valid_inputs: Set of valid inputs in current state
        description: Human-readable description of current state
    """

    position: str
    valid_inputs: frozenset[str]
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "position": self.position,
            "valid_inputs": list(self.valid_inputs),
            "description": self.description,
        }


@dataclass(frozen=True)
class HoverInfo:
    """Information displayed on token hover.

    Attributes:
        title: Title for the hover display
        content: Main content (polynomial state, description, etc.)
        actions: Available actions from hover state
        is_ghost: Whether this is a ghost token (non-existent path)
    """

    title: str
    content: Any
    actions: list[str] = field(default_factory=list)
    is_ghost: bool = False

    @classmethod
    def ghost(cls, path: str) -> HoverInfo:
        """Create hover info for a ghost token."""
        return cls(
            title=path,
            content="Path not yet implemented",
            actions=[],
            is_ghost=True,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        content = self.content
        if hasattr(content, "to_dict"):
            content = content.to_dict()
        return {
            "title": self.title,
            "content": content,
            "actions": self.actions,
            "is_ghost": self.is_ghost,
        }


@dataclass(frozen=True)
class NavigationResult:
    """Result of navigating to an AGENTESE path.

    Attributes:
        success: Whether navigation succeeded
        path: The path that was navigated to
        habitat: The habitat/location information
        error: Error message if navigation failed
        is_ghost: Whether this is a ghost token (non-existent path)
        can_create: Whether the path can be created (for ghost tokens)
    """

    success: bool
    path: str
    habitat: dict[str, Any] | None = None
    error: str | None = None
    is_ghost: bool = False
    can_create: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "path": self.path,
            "habitat": self.habitat,
            "error": self.error,
            "is_ghost": self.is_ghost,
            "can_create": self.can_create,
        }


@dataclass(frozen=True)
class ContextMenuResult:
    """Result of showing context menu for an AGENTESE path.

    Attributes:
        path: The AGENTESE path
        options: Available menu options
        is_ghost: Whether this is a ghost token
    """

    path: str
    options: list[dict[str, Any]]
    is_ghost: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "path": self.path,
            "options": self.options,
            "is_ghost": self.is_ghost,
        }


@dataclass(frozen=True)
class DragResult:
    """Result of dragging an AGENTESE path to REPL.

    Attributes:
        path: The AGENTESE path to pre-fill
        template: REPL command template
    """

    path: str
    template: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "path": self.path,
            "template": self.template,
        }


class AGENTESEPathToken(BaseMeaningToken[str]):
    """Token representing an AGENTESE path in text.

    AGENTESEPath tokens are portals to the agent system. They recognize
    backtick-wrapped paths like `world.town.citizen` and provide
    interactive affordances for exploring and invoking the agent system.

    Ghost Tokens:
    When a path references a non-existent node, the token becomes a
    "ghost token" with reduced affordances. Ghost tokens still render
    but cannot be invoked or display state information.

    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
    """

    # Pattern for extracting context and path segments
    PATH_PATTERN = re.compile(r"`((?:world|self|concept|void|time)\.[a-z_][a-z0-9_.]*)`")

    # Capabilities required for certain affordances
    REQUIRED_CAPABILITIES: dict[str, frozenset[str]] = {
        "hover": frozenset(),  # Always available
        "navigate": frozenset(),  # Always available
        "context_menu": frozenset(),  # Always available
        "drag_to_repl": frozenset(),  # Always available
    }

    def __init__(
        self,
        source_text: str,
        source_position: tuple[int, int],
        path: str,
        exists: bool = True,
    ) -> None:
        """Initialize an AGENTESEPath token.

        Args:
            source_text: The original matched text (including backticks)
            source_position: (start, end) position in source document
            path: The AGENTESE path (without backticks)
            exists: Whether the path exists in the registry
        """
        self._source_text = source_text
        self._source_position = source_position
        self._path = path
        self._exists = exists

        # Parse path components
        parts = path.split(".")
        self._context = parts[0] if parts else ""
        self._segments = parts[1:] if len(parts) > 1 else []

    @classmethod
    def from_match(
        cls,
        match: re.Match[str],
        exists: bool = True,
    ) -> AGENTESEPathToken:
        """Create token from regex match.

        Args:
            match: Regex match object from pattern matching
            exists: Whether the path exists in the registry

        Returns:
            New AGENTESEPathToken instance
        """
        return cls(
            source_text=match.group(0),
            source_position=(match.start(), match.end()),
            path=match.group(1),
            exists=exists,
        )

    @property
    def token_type(self) -> str:
        """Token type name from registry."""
        return "agentese_path"

    @property
    def source_text(self) -> str:
        """Original text that was recognized as this token."""
        return self._source_text

    @property
    def source_position(self) -> tuple[int, int]:
        """(start, end) position in source document."""
        return self._source_position

    @property
    def path(self) -> str:
        """The AGENTESE path (without backticks)."""
        return self._path

    @property
    def context(self) -> str:
        """The context (world, self, concept, void, time)."""
        return self._context

    @property
    def segments(self) -> list[str]:
        """Path segments after the context."""
        return self._segments

    @property
    def exists(self) -> bool:
        """Whether this path exists in the registry."""
        return self._exists

    @property
    def is_ghost(self) -> bool:
        """Whether this is a ghost token (non-existent path)."""
        return not self._exists

    async def get_affordances(self, observer: Observer) -> list[Affordance]:
        """Get available affordances for this observer.

        Ghost tokens have reduced affordances - they cannot be invoked
        and don't display state information.

        Args:
            observer: The observer requesting affordances

        Returns:
            List of available affordances

        Requirements: 5.2, 5.3, 5.4, 5.5, 5.6
        """
        definition = self.get_definition()
        if definition is None:
            return []

        affordances = list(definition.affordances)

        # Filter by observer capabilities
        result = filter_affordances_by_observer(
            tuple(affordances),
            observer,
            self.REQUIRED_CAPABILITIES,
        )

        # Ghost tokens have reduced affordances
        if self.is_ghost:
            result = [
                Affordance(
                    name=a.name,
                    action=a.action,
                    handler=a.handler,
                    enabled=a.action in (AffordanceAction.HOVER, AffordanceAction.CLICK),
                    description=f"{a.description} (ghost token)"
                    if a.description
                    else "Ghost token",
                )
                for a in result
            ]

        return result

    async def project(self, target: str, observer: Observer) -> str | dict[str, Any]:
        """Project token to target-specific rendering.

        Args:
            target: Target name (e.g., "cli", "web", "json")
            observer: The observer receiving the projection

        Returns:
            Target-specific rendering of this token
        """
        if target == "cli":
            if self.is_ghost:
                return f"[dim italic]{self._source_text}[/dim italic]"
            return f"[cyan]{self._source_text}[/cyan]"

        elif target == "json":
            return {
                "type": "agentese_path",
                "path": self._path,
                "context": self._context,
                "segments": self._segments,
                "is_ghost": self.is_ghost,
                "source_text": self._source_text,
            }

        else:  # web or default
            return self._source_text

    async def _execute_action(
        self,
        action: AffordanceAction,
        observer: Observer,
        **kwargs: Any,
    ) -> Any:
        """Execute the action for this token.

        Args:
            action: The action being performed
            observer: The observer performing the action
            **kwargs: Additional action-specific arguments

        Returns:
            Action-specific result

        Requirements: 5.2, 5.3, 5.4, 5.5
        """
        if action == AffordanceAction.HOVER:
            return await self._handle_hover(observer)
        elif action == AffordanceAction.CLICK:
            return await self._handle_navigate(observer)
        elif action == AffordanceAction.RIGHT_CLICK:
            return await self._handle_context_menu(observer)
        elif action == AffordanceAction.DRAG:
            return await self._handle_drag(observer)
        else:
            return None

    async def _handle_hover(self, observer: Observer) -> HoverInfo:
        """Handle hover action - display polynomial state.

        Requirements: 5.2
        """
        if self.is_ghost:
            return HoverInfo.ghost(self._path)

        # Get polynomial state from registry (simulated)
        state = await self._get_polynomial_state()

        return HoverInfo(
            title=self._path,
            content=state,
            actions=["invoke", "view_source", "copy"],
        )

    async def _handle_navigate(self, observer: Observer) -> NavigationResult:
        """Handle click action - navigate to path's Habitat.

        Requirements: 5.3, 5.6
        """
        if self.is_ghost:
            return NavigationResult(
                success=False,  # Ghost navigation fails - path does not exist
                path=self._path,
                error=f"Path '{self._path}' does not exist",
                is_ghost=True,
                can_create=True,  # Ghost tokens can be created
            )

        # In full implementation, this would invoke:
        # habitat = await logos.invoke(f"{self._path}.habitat", observer)
        habitat = {
            "path": self._path,
            "context": self._context,
            "type": "node",
        }

        return NavigationResult(
            success=True,
            path=self._path,
            habitat=habitat,
            is_ghost=False,
            can_create=False,
        )

    async def _handle_context_menu(self, observer: Observer) -> ContextMenuResult:
        """Handle right-click action - show context menu.

        Requirements: 5.4
        """
        options = [
            {"action": "copy", "label": "Copy Path", "enabled": True},
        ]

        if not self.is_ghost:
            options.extend(
                [
                    {"action": "invoke", "label": "Invoke", "enabled": True},
                    {"action": "view_source", "label": "View Source", "enabled": True},
                ]
            )

        # Admin-only options
        if observer.role == ObserverRole.ADMIN:
            options.append({"action": "edit", "label": "Edit Node", "enabled": not self.is_ghost})

        return ContextMenuResult(
            path=self._path,
            options=options,
            is_ghost=self.is_ghost,
        )

    async def _handle_drag(self, observer: Observer) -> DragResult:
        """Handle drag action - pre-fill REPL with path.

        Requirements: 5.5
        """
        template = f"kg {self._path}"

        return DragResult(
            path=self._path,
            template=template,
        )

    async def _get_polynomial_state(self) -> PolynomialState:
        """Get the polynomial state for this path.

        In full implementation, this would query the AGENTESE registry.
        For now, returns a simulated state.
        """
        # Simulated polynomial state
        return PolynomialState(
            position="READY",
            valid_inputs=frozenset(["invoke", "manifest", "query"]),
            description=f"Node at {self._path} is ready for interaction",
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        base = super().to_dict()
        base.update(
            {
                "path": self._path,
                "context": self._context,
                "segments": self._segments,
                "exists": self._exists,
                "is_ghost": self.is_ghost,
            }
        )
        return base


# =============================================================================
# Factory Functions
# =============================================================================


def create_agentese_path_token(
    text: str,
    position: tuple[int, int] | None = None,
    check_exists: bool = False,
) -> AGENTESEPathToken | None:
    """Create an AGENTESEPath token from text.

    Args:
        text: Text that may contain an AGENTESE path
        position: Optional (start, end) position override
        check_exists: Whether to check if path exists in registry

    Returns:
        AGENTESEPathToken if text matches pattern, None otherwise
    """
    match = AGENTESEPathToken.PATH_PATTERN.search(text)
    if match is None:
        return None

    # Determine if path exists (simplified check)
    exists = True
    if check_exists:
        # In full implementation, would check AGENTESE registry
        exists = True  # Assume exists for now

    token = AGENTESEPathToken.from_match(match, exists=exists)

    # Override position if provided
    if position is not None:
        return AGENTESEPathToken(
            source_text=token.source_text,
            source_position=position,
            path=token.path,
            exists=exists,
        )

    return token


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "AGENTESEPathToken",
    "PolynomialState",
    "HoverInfo",
    "NavigationResult",
    "ContextMenuResult",
    "DragResult",
    "create_agentese_path_token",
]

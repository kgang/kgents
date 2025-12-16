"""
ComponentRenderer: Transform context state into React-ready props.

The frontend receives ONLY this shape—never prompts or internal state.
This is a pure projection from context to component props.

Frontend Contract:
    interface ContextComponent {
        messages: Message[];      // Display-ready messages
        pressure: number;         // 0.0 to 1.0
        status: Status;          // "ready" | "thinking" | "compressed" | "pressured"
        canSend: boolean;        // Action availability
    }

AGENTESE: self.context.render (future alias from self.stream.*)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .context_window import ContextWindow, Turn


class ContextStatus(str, Enum):
    """UI status for context component."""

    READY = "ready"  # Normal state, can send
    THINKING = "thinking"  # Waiting for response
    COMPRESSED = "compressed"  # Recently compressed
    PRESSURED = "pressured"  # High pressure, needs attention


@dataclass
class MessageProps:
    """
    React-ready message props.

    This is what the frontend receives for each message.
    """

    id: str
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: str  # ISO format
    is_preserved: bool  # Visual indicator for important messages

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "isPreserved": self.is_preserved,
        }


@dataclass
class ContextProps:
    """
    React-ready context component props.

    This is the complete frontend contract.
    """

    messages: list[MessageProps]
    pressure: float
    status: ContextStatus
    can_send: bool
    total_tokens: int
    max_tokens: int
    turn_count: int
    compression_count: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "messages": [m.to_dict() for m in self.messages],
            "pressure": self.pressure,
            "status": self.status.value,
            "canSend": self.can_send,
            "totalTokens": self.total_tokens,
            "maxTokens": self.max_tokens,
            "turnCount": self.turn_count,
            "compressionCount": self.compression_count,
        }


# === ComponentRenderer ===


@dataclass
class ComponentRenderer:
    """
    Render context state as React component props.

    The frontend receives pure data, no prompts or logic.

    Example:
        renderer = ComponentRenderer()
        props = renderer.render_chat(window)
        # props.to_dict() → JSON for frontend

    Usage:
        # From ContextWindow
        props = renderer.render_chat(window)

        # From ContextSession (preferred)
        props = session.render()  # Uses ComponentRenderer internally
    """

    # Filter system messages from display (frontend shouldn't see them)
    hide_system_messages: bool = True

    # Truncate long messages for display
    max_content_length: int = 10000

    def render_chat(
        self,
        window: "ContextWindow",
        status_override: ContextStatus | None = None,
    ) -> ContextProps:
        """
        Render chat component props from a ContextWindow.

        Args:
            window: The context window to render
            status_override: Override computed status (e.g., for "thinking")

        Returns:
            ContextProps ready for frontend
        """
        from .context_window import TurnRole
        from .linearity import ResourceClass

        messages: list[MessageProps] = []

        for turn in window.all_turns():
            # Optionally hide system messages
            if self.hide_system_messages and turn.role == TurnRole.SYSTEM:
                continue

            # Check if preserved
            resource_class = window.get_resource_class(turn)
            is_preserved = resource_class == ResourceClass.PRESERVED

            # Truncate content if needed
            content = turn.content
            if len(content) > self.max_content_length:
                content = content[: self.max_content_length] + "..."

            messages.append(
                MessageProps(
                    id=turn.resource_id,
                    role=turn.role.value,
                    content=content,
                    timestamp=turn.timestamp.isoformat(),
                    is_preserved=is_preserved,
                )
            )

        # Compute status
        status = self._compute_status(window)
        if status_override is not None:
            status = status_override

        # Determine if can send
        can_send = status not in (ContextStatus.PRESSURED, ContextStatus.THINKING)

        return ContextProps(
            messages=messages,
            pressure=window.pressure,
            status=status,
            can_send=can_send,
            total_tokens=window.total_tokens,
            max_tokens=window.max_tokens,
            turn_count=len(window),
            compression_count=window._meta.compression_count,
        )

    def render_message(self, turn: "Turn", is_preserved: bool = False) -> MessageProps:
        """
        Render a single message for display.

        Args:
            turn: The turn to render
            is_preserved: Whether this message is preserved

        Returns:
            MessageProps for frontend
        """
        content = turn.content
        if len(content) > self.max_content_length:
            content = content[: self.max_content_length] + "..."

        return MessageProps(
            id=turn.resource_id,
            role=turn.role.value,
            content=content,
            timestamp=turn.timestamp.isoformat(),
            is_preserved=is_preserved,
        )

    def _compute_status(self, window: "ContextWindow") -> ContextStatus:
        """
        Compute context status from window state.

        Status logic:
        - PRESSURED: pressure > 0.7 and no recent compression
        - COMPRESSED: compression happened recently (within 5 turns)
        - READY: normal state
        """
        # Check if recently compressed
        if window._meta.compression_count > 0:
            # Consider "recent" if within last 5 turns of compression
            # This is a heuristic - could be time-based instead
            if window._meta.last_compression is not None:
                # Check if there's been activity since compression
                if len(window) <= 5:  # Few turns since compression
                    return ContextStatus.COMPRESSED

        # Check pressure
        if window.needs_compression:
            return ContextStatus.PRESSURED

        return ContextStatus.READY


# === Factory Functions ===


def create_component_renderer(
    hide_system_messages: bool = True,
    max_content_length: int = 10000,
) -> ComponentRenderer:
    """
    Create a ComponentRenderer with configuration.

    Args:
        hide_system_messages: Whether to filter system messages
        max_content_length: Max content length before truncation

    Returns:
        Configured ComponentRenderer
    """
    return ComponentRenderer(
        hide_system_messages=hide_system_messages,
        max_content_length=max_content_length,
    )


def render_for_frontend(
    window: "ContextWindow",
    status_override: ContextStatus | None = None,
) -> dict[str, Any]:
    """
    Convenience function to render window for frontend.

    Args:
        window: The context window to render
        status_override: Optional status override

    Returns:
        Dictionary ready for JSON serialization to frontend
    """
    renderer = ComponentRenderer()
    props = renderer.render_chat(window, status_override)
    return props.to_dict()


def render_minimal(window: "ContextWindow") -> dict[str, Any]:
    """
    Render minimal props (just messages and pressure).

    Useful for lightweight updates.
    """
    renderer = ComponentRenderer()
    props = renderer.render_chat(window)
    return {
        "messages": [m.to_dict() for m in props.messages],
        "pressure": props.pressure,
    }

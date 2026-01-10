"""
ChatResolver: Resolver for chat: resources.

Resolves ChatSession and individual turns.

Philosophy:
    "The session is a K-Block. Every turn is witnessed."

See: spec/protocols/portal-resource-system.md §5.1
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from ..resolver import ResolvedResource
from ..uri import PortalURI

if TYPE_CHECKING:
    from services.chat.session import ChatSession


class ChatResolver:
    """
    Resolver for chat: resources.

    Handles:
    - chat:session-abc123         → Full ChatSession metadata
    - chat:session-abc123#turn-5  → Specific turn

    Dependencies:
        session_store: Storage for ChatSession instances
    """

    resource_type = "chat"

    def __init__(self, session_store: Any = None) -> None:
        """
        Initialize ChatResolver.

        Args:
            session_store: Storage provider for chat sessions
        """
        self.session_store = session_store

    def can_resolve(self, uri: PortalURI) -> bool:
        """Check if this resolver can handle the URI."""
        return uri.resource_type == self.resource_type

    async def resolve(self, uri: PortalURI, observer: Any = None) -> ResolvedResource:
        """
        Resolve ChatSession or specific turn.

        Args:
            uri: Parsed portal URI
            observer: Optional observer for access control

        Returns:
            ResolvedResource with session or turn data
        """
        session_id = uri.resource_path
        turn_number = self._parse_turn_number(uri.fragment)

        # Fetch session
        session = await self._get_session(session_id)
        if session is None:
            return ResolvedResource(
                uri=uri.render(),
                resource_type=self.resource_type,
                exists=False,
                title="Session Not Found",
                preview=f"Session not found: {session_id}",
                content=None,
                actions=[],
                metadata={"error": "session_not_found"},
            )

        # If fragment specifies turn, resolve that turn
        if turn_number is not None:
            return self._resolve_turn(uri, session, turn_number)

        # Otherwise, resolve full session
        return self._resolve_session(uri, session)

    def _resolve_session(self, uri: PortalURI, session: ChatSession) -> ResolvedResource:
        """Resolve full ChatSession."""
        # Get session metadata
        turn_count = session.turn_count
        flow_state = (
            session.flow_state.value
            if hasattr(session.flow_state, "value")
            else str(session.flow_state)
        )
        branch_name = getattr(session, "branch_name", None)
        created_at = getattr(session, "created_at", None)
        updated_at = getattr(session, "updated_at", None)

        # Build preview
        preview = f"{turn_count} turns"
        if branch_name:
            preview = f"{branch_name}: {preview}"

        return ResolvedResource(
            uri=uri.render(),
            resource_type=self.resource_type,
            exists=True,
            title=branch_name or session.id,
            preview=preview,
            content={
                "session_id": session.id,
                "branch_name": branch_name,
                "turn_count": turn_count,
                "flow_state": flow_state,
                "created_at": created_at.isoformat() if created_at else None,
                "updated_at": updated_at.isoformat() if updated_at else None,
            },
            actions=["expand", "fork", "resume"],
            metadata={
                "session_id": session.id,
                "branch_name": branch_name,
                "turn_count": turn_count,
                "flow_state": flow_state,
            },
        )

    def _resolve_turn(
        self, uri: PortalURI, session: ChatSession, turn_number: int
    ) -> ResolvedResource:
        """Resolve specific turn from session."""
        # Get turn from context
        turns = session.context.turns
        if turn_number < 0 or turn_number >= len(turns):
            return ResolvedResource(
                uri=uri.render(),
                resource_type="turn",  # Note: resource_type is "turn" for specific turn
                exists=False,
                title="Turn Not Found",
                preview=f"Turn {turn_number} not found (session has {len(turns)} turns)",
                content=None,
                actions=[],
                metadata={"error": "turn_not_found"},
            )

        turn = turns[turn_number]

        return ResolvedResource(
            uri=uri.render(),
            resource_type="turn",
            exists=True,
            title=f"Turn {turn_number}",
            preview=turn.user_message[:100] + "..."
            if len(turn.user_message) > 100
            else turn.user_message,
            content={
                "user_message": turn.user_message,
                "assistant_response": turn.assistant_response or "",
            },
            actions=["expand", "fork_from", "cite"],
            metadata={
                "session_id": session.id,
                "turn_number": turn_number,
                "timestamp": turn.timestamp.isoformat() if hasattr(turn, "timestamp") else None,
            },
        )

    async def _get_session(self, session_id: str) -> ChatSession | None:
        """Fetch session from storage."""
        if self.session_store is None:
            return None

        if hasattr(self.session_store, "get"):
            result = await self.session_store.get(session_id)
            return cast("ChatSession | None", result)
        elif hasattr(self.session_store, "load"):
            result = await self.session_store.load(session_id)
            return cast("ChatSession | None", result)
        else:
            return None

    def _parse_turn_number(self, fragment: str | None) -> int | None:
        """Parse turn number from fragment."""
        if not fragment:
            return None

        if fragment.startswith("turn-"):
            try:
                return int(fragment[5:])
            except ValueError:
                return None

        return None


__all__ = ["ChatResolver"]

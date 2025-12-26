"""
MarkResolver: Resolver for mark: resources.

Resolves ChatMarks with constitutional scores.

Philosophy:
    "The mark IS the witness. The scores ARE the judgment."

See: spec/protocols/portal-resource-system.md §5.2
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..resolver import ResolvedResource
from ..uri import PortalURI

if TYPE_CHECKING:
    from services.chat.session import ChatSession
    from services.chat.witness import ChatMark


class MarkResolver:
    """
    Resolver for mark: resources.

    Handles:
    - mark:session-abc123#turn-5    → ChatMark with constitutional scores

    Dependencies:
        session_store: Storage for ChatSession instances
    """

    resource_type = "mark"

    def __init__(self, session_store: Any = None) -> None:
        """
        Initialize MarkResolver.

        Args:
            session_store: Storage provider for chat sessions
        """
        self.session_store = session_store

    def can_resolve(self, uri: PortalURI) -> bool:
        """Check if this resolver can handle the URI."""
        return uri.resource_type == self.resource_type

    async def resolve(self, uri: PortalURI, observer: Any = None) -> ResolvedResource:
        """
        Resolve ChatMark with constitutional scores.

        Args:
            uri: Parsed portal URI
            observer: Optional observer for access control

        Returns:
            ResolvedResource with mark data
        """
        session_id = uri.resource_path
        turn_number = self._parse_turn_number(uri.fragment)

        if turn_number is None:
            return ResolvedResource(
                uri=uri.render(),
                resource_type=self.resource_type,
                exists=False,
                title="Mark Not Found",
                preview="Fragment must specify turn number (e.g., #turn-5)",
                content=None,
                actions=[],
                metadata={"error": "missing_fragment"},
            )

        # Fetch session
        session = await self._get_session(session_id)
        if session is None:
            return ResolvedResource(
                uri=uri.render(),
                resource_type=self.resource_type,
                exists=False,
                title="Mark Not Found",
                preview=f"Session not found: {session_id}",
                content=None,
                actions=[],
                metadata={"error": "session_not_found"},
            )

        # Get mark from policy trace
        mark = session.policy_trace.get_mark(turn_number)
        if mark is None:
            return ResolvedResource(
                uri=uri.render(),
                resource_type=self.resource_type,
                exists=False,
                title="Mark Not Found",
                preview=f"No mark for turn {turn_number}",
                content=None,
                actions=[],
                metadata={"error": "mark_not_found"},
            )

        return self._resolve_mark(uri, mark, session_id)

    def _resolve_mark(self, uri: PortalURI, mark: ChatMark, session_id: str) -> ResolvedResource:
        """Resolve ChatMark to resource."""
        # Build content dict
        content = {
            "user_message": mark.user_message,
            "assistant_response": mark.assistant_response,
            "tools_used": list(mark.tools_used),
            "reasoning": mark.reasoning,
            "timestamp": mark.timestamp.isoformat(),
        }

        # Add constitutional scores if available
        if mark.constitutional_scores:
            content["constitutional_scores"] = mark.constitutional_scores.to_dict()
            preview = f"Score: {mark.constitutional_scores.weighted_total():.1f}"
        else:
            content["constitutional_scores"] = None
            preview = "No scores available"

        return ResolvedResource(
            uri=uri.render(),
            resource_type=self.resource_type,
            exists=True,
            title=f"Mark: Turn {mark.turn_number}",
            preview=preview,
            content=content,
            actions=["expand", "view_constitutional"],
            metadata={
                "session_id": session_id,
                "turn_number": mark.turn_number,
                "timestamp": mark.timestamp.isoformat(),
                "has_scores": mark.constitutional_scores is not None,
            },
        )

    async def _get_session(self, session_id: str) -> ChatSession | None:
        """Fetch session from storage."""
        if self.session_store is None:
            return None

        if hasattr(self.session_store, "get"):
            return await self.session_store.get(session_id)
        elif hasattr(self.session_store, "load"):
            return await self.session_store.load(session_id)
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


__all__ = ["MarkResolver"]

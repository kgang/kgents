"""
TraceResolver: Resolver for trace: resources.

Resolves PolicyTraces (complete conversation witness trails).

Philosophy:
    "The trace IS the history. The marks ARE the decisions."

See: spec/protocols/portal-resource-system.md §5.5
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..resolver import ResolvedResource
from ..uri import PortalURI

if TYPE_CHECKING:
    from services.chat.session import ChatSession
    from services.chat.witness import ChatPolicyTrace


class TraceResolver:
    """
    Resolver for trace: resources.

    Handles:
    - trace:session-abc123    → Full PolicyTrace with all marks

    Dependencies:
        session_store: Storage for ChatSession instances
    """

    resource_type = "trace"

    def __init__(self, session_store: Any = None) -> None:
        """
        Initialize TraceResolver.

        Args:
            session_store: Storage provider for chat sessions
        """
        self.session_store = session_store

    def can_resolve(self, uri: PortalURI) -> bool:
        """Check if this resolver can handle the URI."""
        return uri.resource_type == self.resource_type

    async def resolve(self, uri: PortalURI, observer: Any = None) -> ResolvedResource:
        """
        Resolve PolicyTrace.

        Args:
            uri: Parsed portal URI
            observer: Optional observer for access control

        Returns:
            ResolvedResource with trace data
        """
        session_id = uri.resource_path

        # Fetch session
        session = await self._get_session(session_id)
        if session is None:
            return ResolvedResource(
                uri=uri.render(),
                resource_type=self.resource_type,
                exists=False,
                title="Trace Not Found",
                preview=f"Session not found: {session_id}",
                content=None,
                actions=[],
                metadata={"error": "session_not_found"},
            )

        trace = session.policy_trace
        return self._resolve_trace(uri, trace, session_id)

    def _resolve_trace(
        self, uri: PortalURI, trace: ChatPolicyTrace, session_id: str
    ) -> ResolvedResource:
        """Resolve PolicyTrace to resource."""
        marks_data = [mark.to_dict() for mark in trace.get_marks()]

        # Get latest timestamp if available
        latest_timestamp = None
        if trace.latest_mark:
            latest_timestamp = trace.latest_mark.timestamp.isoformat()

        return ResolvedResource(
            uri=uri.render(),
            resource_type=self.resource_type,
            exists=True,
            title=f"Trace: {session_id}",
            preview=f"{trace.turn_count} marks",
            content={
                "marks": marks_data,
                "turn_count": trace.turn_count,
                "session_id": trace.session_id,
            },
            actions=["expand", "export", "replay"],
            metadata={
                "session_id": session_id,
                "turn_count": trace.turn_count,
                "latest_timestamp": latest_timestamp,
            },
        )

    async def _get_session(self, session_id: str) -> ChatSession | None:
        """Fetch session from storage."""
        if self.session_store is None:
            return None

        if hasattr(self.session_store, "get"):
            return await self.session_store.get(session_id)  # type: ignore[no-any-return]
        elif hasattr(self.session_store, "load"):
            return await self.session_store.load(session_id)  # type: ignore[no-any-return]
        else:
            return None


__all__ = ["TraceResolver"]

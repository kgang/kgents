"""
ChatSession Persistence: D-gent integration for chat session storage.

This module provides:
- PersistedSession: The persisted form of a chat session
- ChatPersistence: Save/load/list/search sessions via D-gent

Sessions are stored as Datum with:
- ID: chat:session:{session_id}
- Content: JSON-serialized session data
- Metadata: node_path, observer_id, name, tags
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from agents.d import Backend, Datum, DgentRouter

if TYPE_CHECKING:
    from .session import ChatSession, Turn

logger = logging.getLogger(__name__)


# =============================================================================
# PersistedSession: The on-disk representation
# =============================================================================


@dataclass
class PersistedSession:
    """
    Session stored in D-gent memory.

    This is the serialized form of a ChatSession that can be
    saved to and loaded from D-gent storage.
    """

    session_id: str
    node_path: str
    observer_id: str
    created_at: datetime
    updated_at: datetime
    turn_count: int
    total_tokens: int

    # Ground truth - turn history
    turns: list[dict[str, Any]]

    # Compressed context (optional summary)
    summary: str | None = None

    # User-assigned metadata
    name: str | None = None
    tags: list[str] = field(default_factory=list)

    # Session state
    state: str = "waiting"
    entropy: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "session_id": self.session_id,
            "node_path": self.node_path,
            "observer_id": self.observer_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "turn_count": self.turn_count,
            "total_tokens": self.total_tokens,
            "turns": self.turns,
            "summary": self.summary,
            "name": self.name,
            "tags": self.tags,
            "state": self.state,
            "entropy": self.entropy,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PersistedSession:
        """Deserialize from JSON-compatible dict."""
        return cls(
            session_id=data["session_id"],
            node_path=data["node_path"],
            observer_id=data["observer_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            turn_count=data["turn_count"],
            total_tokens=data["total_tokens"],
            turns=data["turns"],
            summary=data.get("summary"),
            name=data.get("name"),
            tags=data.get("tags", []),
            state=data.get("state", "waiting"),
            entropy=data.get("entropy", 1.0),
        )

    @classmethod
    def from_session(cls, session: "ChatSession") -> PersistedSession:
        """Create a PersistedSession from a live ChatSession."""
        session_dict = session.to_dict()
        return cls(
            session_id=session.session_id,
            node_path=session.node_path,
            observer_id=getattr(session.observer, "id", "anonymous"),
            created_at=datetime.fromisoformat(session_dict["created_at"]),
            updated_at=datetime.fromisoformat(session_dict["updated_at"]),
            turn_count=session_dict["turn_count"],
            total_tokens=session_dict["budget"]["total_tokens"],
            turns=session_dict["turns"],
            summary=None,  # Summary computed on demand
            name=session_dict.get("name"),
            tags=session_dict.get("tags", []),
            state=session_dict["state"],
            entropy=session_dict["entropy"],
        )


# =============================================================================
# ChatPersistence: D-gent integration
# =============================================================================


class ChatPersistence:
    """
    Persistence layer for chat sessions using D-gent.

    Provides CRUD operations for chat sessions:
    - save_session: Store session to D-gent
    - load_session: Retrieve session by ID
    - list_sessions: List sessions with filters
    - search_sessions: Full-text search
    - delete_session: Remove session

    Usage:
        persistence = ChatPersistence()
        await persistence.save_session(session)
        loaded = await persistence.load_session("session-123")
        sessions = await persistence.list_sessions(node_path="self.soul")
    """

    PREFIX = "chat:session:"

    def __init__(
        self,
        dgent: DgentRouter | None = None,
        namespace: str = "chat_sessions",
    ):
        """
        Initialize persistence layer.

        Args:
            dgent: D-gent router (auto-created if None)
            namespace: Namespace for session storage
        """
        self._dgent = dgent or DgentRouter(
            namespace=namespace,
            fallback_chain=[Backend.SQLITE, Backend.JSONL, Backend.MEMORY],
        )
        self._namespace = namespace

    def _session_id_to_datum_id(self, session_id: str) -> str:
        """Convert session ID to datum ID."""
        return f"{self.PREFIX}{session_id}"

    def _datum_id_to_session_id(self, datum_id: str) -> str:
        """Extract session ID from datum ID."""
        if datum_id.startswith(self.PREFIX):
            return datum_id[len(self.PREFIX) :]
        return datum_id

    async def save_session(
        self,
        session: "ChatSession",
        *,
        name: str | None = None,
        summary: str | None = None,
    ) -> str:
        """
        Save a chat session to D-gent storage.

        Args:
            session: The ChatSession to persist
            name: Optional user-assigned name
            summary: Optional session summary

        Returns:
            The datum ID of the saved session
        """
        # Create persisted form
        persisted = PersistedSession.from_session(session)

        # Apply overrides
        if name:
            persisted.name = name
        if summary:
            persisted.summary = summary

        # Serialize to bytes
        content = json.dumps(persisted.to_dict()).encode("utf-8")

        # Build metadata for filtering
        metadata: dict[str, str] = {
            "node_path": persisted.node_path,
            "observer_id": persisted.observer_id,
            "turn_count": str(persisted.turn_count),
            "state": persisted.state,
        }
        if persisted.name:
            metadata["name"] = persisted.name
        if persisted.tags:
            metadata["tags"] = ",".join(persisted.tags)

        # Create datum
        datum = Datum.create(
            content=content,
            id=self._session_id_to_datum_id(session.session_id),
            metadata=metadata,
        )

        # Store
        return await self._dgent.put(datum)

    async def load_session(self, session_id: str) -> PersistedSession | None:
        """
        Load a chat session from D-gent storage.

        Args:
            session_id: The session ID to load

        Returns:
            PersistedSession if found, None otherwise
        """
        datum_id = self._session_id_to_datum_id(session_id)
        datum = await self._dgent.get(datum_id)

        if datum is None:
            return None

        try:
            data = json.loads(datum.content.decode("utf-8"))
            return PersistedSession.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            # Corrupted data - log and return None
            logger.warning(f"Failed to load session {session_id}: {e}")
            return None

    async def load_by_name(self, name: str) -> PersistedSession | None:
        """
        Load a chat session by user-assigned name.

        Args:
            name: The session name to search for

        Returns:
            PersistedSession if found, None otherwise
        """
        sessions = await self.list_sessions()
        for session in sessions:
            if session.name == name:
                return session
        return None

    async def list_sessions(
        self,
        *,
        node_path: str | None = None,
        observer_id: str | None = None,
        after: datetime | None = None,
        limit: int = 100,
    ) -> list[PersistedSession]:
        """
        List persisted sessions with optional filters.

        Args:
            node_path: Filter by AGENTESE path (e.g., "self.soul")
            observer_id: Filter by observer
            after: Filter to sessions updated after this time
            limit: Maximum sessions to return

        Returns:
            List of matching PersistedSession objects
        """
        # List all chat session data
        after_timestamp = after.timestamp() if after else None
        data = await self._dgent.list(
            prefix=self.PREFIX,
            after=after_timestamp,
            limit=limit * 2,  # Over-fetch for post-filtering
        )

        sessions: list[PersistedSession] = []
        for datum in data:
            # Filter by metadata
            if node_path and datum.metadata.get("node_path") != node_path:
                continue
            if observer_id and datum.metadata.get("observer_id") != observer_id:
                continue

            try:
                data_dict = json.loads(datum.content.decode("utf-8"))
                session = PersistedSession.from_dict(data_dict)
                sessions.append(session)
            except (json.JSONDecodeError, KeyError):
                continue  # Skip corrupted entries

            if len(sessions) >= limit:
                break

        return sessions

    async def search_sessions(
        self,
        query: str,
        *,
        limit: int = 20,
    ) -> list[PersistedSession]:
        """
        Search sessions by content.

        Searches in:
        - Session name
        - Tags
        - Turn content (user messages and assistant responses)

        Args:
            query: Search query string
            limit: Maximum results

        Returns:
            List of matching sessions
        """
        query_lower = query.lower()
        all_sessions = await self.list_sessions(limit=1000)

        matches: list[tuple[int, PersistedSession]] = []
        for session in all_sessions:
            score = 0

            # Check name
            if session.name and query_lower in session.name.lower():
                score += 10

            # Check tags
            for tag in session.tags:
                if query_lower in tag.lower():
                    score += 5

            # Check summary
            if session.summary and query_lower in session.summary.lower():
                score += 3

            # Check turn content
            for turn in session.turns:
                if query_lower in turn.get("user_message", "").lower():
                    score += 1
                if query_lower in turn.get("assistant_response", "").lower():
                    score += 1

            if score > 0:
                matches.append((score, session))

        # Sort by score descending
        matches.sort(key=lambda x: x[0], reverse=True)

        return [session for _, session in matches[:limit]]

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a persisted session.

        Args:
            session_id: The session ID to delete

        Returns:
            True if deleted, False if not found
        """
        datum_id = self._session_id_to_datum_id(session_id)
        return await self._dgent.delete(datum_id)

    async def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists.

        Args:
            session_id: The session ID to check

        Returns:
            True if session exists
        """
        datum_id = self._session_id_to_datum_id(session_id)
        return await self._dgent.exists(datum_id)

    async def count_sessions(
        self,
        *,
        node_path: str | None = None,
    ) -> int:
        """
        Count persisted sessions.

        Args:
            node_path: Optional filter by path

        Returns:
            Number of matching sessions
        """
        if node_path:
            sessions = await self.list_sessions(node_path=node_path, limit=10000)
            return len(sessions)

        # Count all chat sessions
        data = await self._dgent.list(prefix=self.PREFIX, limit=10000)
        return len(data)

    async def get_recent_sessions(
        self,
        *,
        node_path: str | None = None,
        limit: int = 10,
    ) -> list[PersistedSession]:
        """
        Get most recently updated sessions.

        Args:
            node_path: Optional filter by path
            limit: Maximum sessions

        Returns:
            Sessions sorted by updated_at descending
        """
        sessions = await self.list_sessions(node_path=node_path, limit=limit * 2)

        # Sort by updated_at descending
        sessions.sort(key=lambda s: s.updated_at, reverse=True)

        return sessions[:limit]


# =============================================================================
# Memory Injection: Cross-Session Context
# =============================================================================


class MemoryInjector:
    """
    Injects relevant memories from past sessions into new session context.

    This enables:
    - Entity-specific memory (remembering past conversations with same entity)
    - Topic continuity (recalling relevant past discussions)
    - Observer familiarity (adapting to user patterns)

    Usage:
        injector = MemoryInjector(persistence)
        context = await injector.inject_context(
            node_path="self.soul",
            observer_id="user-123",
            current_message="How do I implement auth?",
        )
    """

    def __init__(
        self,
        persistence: ChatPersistence | None = None,
    ):
        """Initialize memory injector."""
        self._persistence = persistence

    @property
    def persistence(self) -> ChatPersistence:
        """Get persistence instance (lazy)."""
        if self._persistence is None:
            self._persistence = get_persistence()
        return self._persistence

    async def inject_context(
        self,
        node_path: str,
        observer_id: str,
        current_message: str | None = None,
        *,
        max_sessions: int = 3,
        max_turns_per_session: int = 2,
    ) -> str:
        """
        Build context string from relevant past sessions.

        Args:
            node_path: AGENTESE path (e.g., "self.soul")
            observer_id: Observer identifier
            current_message: Current user message (for relevance scoring)
            max_sessions: Maximum past sessions to include
            max_turns_per_session: Maximum turns per session to include

        Returns:
            Context string for injection into system prompt
        """
        # Get past sessions for this node/observer
        sessions = await self.persistence.list_sessions(
            node_path=node_path,
            observer_id=observer_id,
            limit=max_sessions * 2,  # Over-fetch for filtering
        )

        if not sessions:
            return ""

        # Score and rank sessions by relevance
        if current_message:
            sessions = self._rank_by_relevance(sessions, current_message)

        # Take top sessions
        top_sessions = sessions[:max_sessions]

        # Build context
        lines: list[str] = [
            "## Relevant Past Conversations",
            "",
        ]

        for session in top_sessions:
            # Session header
            name = session.name or session.session_id[:8]
            lines.append(f"### {name} ({session.turn_count} turns)")

            # Include recent turns
            recent_turns = session.turns[-max_turns_per_session:]
            for turn in recent_turns:
                user_msg = turn.get("user_message", "")[:100]
                asst_msg = turn.get("assistant_response", "")[:100]
                lines.append(f"- User: {user_msg}...")
                lines.append(f"- Assistant: {asst_msg}...")

            lines.append("")

        return "\n".join(lines)

    def _rank_by_relevance(
        self,
        sessions: list[PersistedSession],
        query: str,
    ) -> list[PersistedSession]:
        """Rank sessions by relevance to query."""
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored: list[tuple[float, PersistedSession]] = []
        for session in sessions:
            score = 0.0

            # Recency bonus (newer = higher)
            age_days = (datetime.now() - session.updated_at).days
            recency_score = max(0, 1.0 - (age_days / 30))  # Decay over 30 days
            score += recency_score * 0.5

            # Content relevance
            content_score = 0.0
            for turn in session.turns:
                turn_text = (
                    turn.get("user_message", "") + " " + turn.get("assistant_response", "")
                ).lower()

                # Word overlap
                turn_words = set(turn_text.split())
                overlap = len(query_words & turn_words)
                content_score += overlap * 0.1

                # Exact substring match
                if query_lower in turn_text:
                    content_score += 0.5

            score += min(content_score, 2.0)  # Cap content score

            scored.append((score, session))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        return [session for _, session in scored]

    async def get_entity_memory(
        self,
        node_path: str,
        *,
        limit: int = 10,
    ) -> dict[str, Any]:
        """
        Get memory summary for an entity (aggregated across sessions).

        Useful for entities like Town citizens that persist across
        multiple conversations.

        Args:
            node_path: AGENTESE path
            limit: Maximum sessions to consider

        Returns:
            Memory summary dict
        """
        sessions = await self.persistence.list_sessions(
            node_path=node_path,
            limit=limit,
        )

        if not sessions:
            return {
                "total_sessions": 0,
                "total_turns": 0,
                "observers_seen": [],
                "recent_topics": [],
            }

        # Aggregate statistics
        total_turns = sum(s.turn_count for s in sessions)
        observers = list(set(s.observer_id for s in sessions))

        # Extract recent topics (from user messages)
        recent_topics: list[str] = []
        for session in sessions[:3]:
            for turn in session.turns[-2:]:
                msg = turn.get("user_message", "")
                if msg and len(msg) > 10:
                    # Extract first sentence as topic
                    topic = msg.split(".")[0][:50]
                    if topic not in recent_topics:
                        recent_topics.append(topic)

        return {
            "total_sessions": len(sessions),
            "total_turns": total_turns,
            "observers_seen": observers[:10],  # Cap at 10
            "recent_topics": recent_topics[:5],  # Cap at 5
        }


# =============================================================================
# Singleton instance
# =============================================================================

_persistence: ChatPersistence | None = None
_injector: MemoryInjector | None = None


def get_persistence() -> ChatPersistence:
    """Get or create the singleton persistence instance."""
    global _persistence
    if _persistence is None:
        _persistence = ChatPersistence()
    return _persistence


def get_memory_injector() -> MemoryInjector:
    """Get or create the singleton memory injector."""
    global _injector
    if _injector is None:
        _injector = MemoryInjector()
    return _injector


def reset_persistence() -> None:
    """Reset the singletons (for testing)."""
    global _persistence, _injector
    _persistence = None
    _injector = None


__all__ = [
    "PersistedSession",
    "ChatPersistence",
    "MemoryInjector",
    "get_persistence",
    "get_memory_injector",
    "reset_persistence",
]

"""
WindowPersistence: D-gent integration for ConversationWindow state.

CLI v7 Phase 2: Deep Conversation

This module provides:
- WindowPersistence: Save/load ConversationWindow state via D-gent
- get_window_persistence: Singleton accessor

The window state is stored separately from ChatSession to allow:
1. Independent window lifecycle (windows can persist across sessions)
2. Bounded history resumption after restarts
3. Summary preservation for continued context

Storage pattern:
- ID: conductor:window:{session_id}
- Content: JSON-serialized window.to_dict()
- Metadata: strategy, turn_count, has_summary

Teaching:
    gotcha: Corrupted JSON data returns None from load_window(), not an exception.
            Always handle the None case when loading - the user may have edited
            the underlying storage or the data may be from an incompatible version.
            (Evidence: test_persistence.py::TestWindowPersistenceLoad::test_load_window_handles_corrupted_data)

    gotcha: Window persistence is independent from ChatSession lifecycle.
            A window can exist in D-gent even after its session is gone.
            Use exists() to check before assuming a load will succeed.
            (Evidence: test_persistence.py::TestWindowPersistenceIntegration::test_exists_check)
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from agents.d import Backend, Datum, DgentRouter

if TYPE_CHECKING:
    from .window import ConversationWindow

logger = logging.getLogger(__name__)


# =============================================================================
# WindowPersistence: D-gent integration
# =============================================================================


class WindowPersistence:
    """
    Persistence layer for ConversationWindow using D-gent.

    Provides save/load operations for window state:
    - save_window: Store window state to D-gent
    - load_window: Retrieve window by session ID
    - delete_window: Remove window state
    - exists: Check if window state exists

    Usage:
        persistence = WindowPersistence()
        await persistence.save_window("session-123", window)
        loaded = await persistence.load_window("session-123")
    """

    PREFIX = "conductor:window:"

    def __init__(
        self,
        dgent: DgentRouter | None = None,
        namespace: str = "conductor_windows",
    ):
        """
        Initialize persistence layer.

        Args:
            dgent: D-gent router (auto-created if None)
            namespace: Namespace for window storage
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

    async def save_window(
        self,
        session_id: str,
        window: "ConversationWindow",
    ) -> str:
        """
        Save a ConversationWindow to D-gent storage.

        Args:
            session_id: The session ID this window belongs to
            window: The ConversationWindow to persist

        Returns:
            The datum ID of the saved window
        """
        # Serialize window state
        data = window.to_dict()
        content = json.dumps(data).encode("utf-8")

        # Build metadata for filtering/observability
        metadata: dict[str, str] = {
            "strategy": window.strategy,
            "turn_count": str(window.turn_count),
            "total_turn_count": str(window.total_turn_count),
            "has_summary": str(window.has_summary).lower(),
            "max_turns": str(window.max_turns),
        }

        # Create datum
        datum = Datum.create(
            content=content,
            id=self._session_id_to_datum_id(session_id),
            metadata=metadata,
        )

        # Store
        datum_id = await self._dgent.put(datum)
        logger.debug(
            f"Saved window for session {session_id[:8]}, "
            f"turns={window.turn_count}, strategy={window.strategy}"
        )
        return datum_id

    async def load_window(
        self,
        session_id: str,
    ) -> "ConversationWindow | None":
        """
        Load a ConversationWindow from D-gent storage.

        Args:
            session_id: The session ID to load window for

        Returns:
            ConversationWindow if found, None otherwise
        """
        from .window import ConversationWindow

        datum_id = self._session_id_to_datum_id(session_id)
        datum = await self._dgent.get(datum_id)

        if datum is None:
            return None

        try:
            data = json.loads(datum.content.decode("utf-8"))
            window = ConversationWindow.from_dict(data)
            logger.debug(
                f"Loaded window for session {session_id[:8]}, "
                f"turns={window.turn_count}, strategy={window.strategy}"
            )
            return window
        except (json.JSONDecodeError, KeyError) as e:
            # Corrupted data - log and return None
            logger.warning(f"Failed to load window for session {session_id}: {e}")
            return None

    async def delete_window(self, session_id: str) -> bool:
        """
        Delete a persisted window.

        Args:
            session_id: The session ID to delete window for

        Returns:
            True if deleted, False if not found
        """
        datum_id = self._session_id_to_datum_id(session_id)
        result = await self._dgent.delete(datum_id)
        if result:
            logger.debug(f"Deleted window for session {session_id[:8]}")
        return result

    async def exists(self, session_id: str) -> bool:
        """
        Check if a window exists for a session.

        Args:
            session_id: The session ID to check

        Returns:
            True if window state exists
        """
        datum_id = self._session_id_to_datum_id(session_id)
        return await self._dgent.exists(datum_id)

    async def list_windows(
        self,
        *,
        limit: int = 100,
    ) -> list[tuple[str, dict[str, str]]]:
        """
        List all persisted windows.

        Returns:
            List of (session_id, metadata) tuples
        """
        data = await self._dgent.list(prefix=self.PREFIX, limit=limit)

        results: list[tuple[str, dict[str, str]]] = []
        for datum in data:
            session_id = self._datum_id_to_session_id(datum.id)
            results.append((session_id, dict(datum.metadata)))

        return results


# =============================================================================
# Singleton instance
# =============================================================================

_persistence: WindowPersistence | None = None


def get_window_persistence() -> WindowPersistence:
    """Get or create the singleton WindowPersistence instance."""
    global _persistence
    if _persistence is None:
        _persistence = WindowPersistence()
    return _persistence


def reset_window_persistence() -> None:
    """Reset the singleton (for testing)."""
    global _persistence
    _persistence = None


__all__ = [
    "WindowPersistence",
    "get_window_persistence",
    "reset_window_persistence",
]

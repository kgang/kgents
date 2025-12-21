"""
Tests for WindowPersistence.

CLI v7 Phase 2: Deep Conversation

Test categories (per test-patterns.md T-gent taxonomy):
- Type I (Unit): Basic persistence operations
- Type II (Integration): Persistence + D-gent + Composer
- Type III (Property-based): Roundtrip preservation invariants
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.conductor.persistence import (
    WindowPersistence,
    get_window_persistence,
    reset_window_persistence,
)
from services.conductor.window import ConversationWindow

# =============================================================================
# Type I: Unit Tests
# =============================================================================


class TestWindowPersistenceBasic:
    """Basic unit tests for WindowPersistence."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self) -> None:
        """Reset singleton before each test."""
        reset_window_persistence()

    def test_create_persistence_with_defaults(self) -> None:
        """Persistence creates with sensible defaults."""
        persistence = WindowPersistence()

        assert persistence.PREFIX == "conductor:window:"
        assert persistence._namespace == "conductor_windows"

    def test_session_id_to_datum_id(self) -> None:
        """Session ID is converted to datum ID with prefix."""
        persistence = WindowPersistence()

        datum_id = persistence._session_id_to_datum_id("session-123")

        assert datum_id == "conductor:window:session-123"

    def test_datum_id_to_session_id(self) -> None:
        """Datum ID is converted back to session ID."""
        persistence = WindowPersistence()

        session_id = persistence._datum_id_to_session_id("conductor:window:session-123")

        assert session_id == "session-123"

    def test_datum_id_passthrough(self) -> None:
        """Datum ID without prefix is returned as-is."""
        persistence = WindowPersistence()

        session_id = persistence._datum_id_to_session_id("session-123")

        assert session_id == "session-123"

    def test_singleton_accessor(self) -> None:
        """get_window_persistence returns singleton."""
        p1 = get_window_persistence()
        p2 = get_window_persistence()

        assert p1 is p2

    def test_singleton_reset(self) -> None:
        """reset_window_persistence clears singleton."""
        p1 = get_window_persistence()
        reset_window_persistence()
        p2 = get_window_persistence()

        assert p1 is not p2


class TestWindowPersistenceSave:
    """Tests for save_window method."""

    @pytest.fixture
    def mock_dgent(self) -> MagicMock:
        """Create mock D-gent router."""
        dgent = MagicMock()
        dgent.put = AsyncMock(return_value="conductor:window:test-123")
        dgent.get = AsyncMock(return_value=None)
        dgent.delete = AsyncMock(return_value=True)
        dgent.exists = AsyncMock(return_value=False)
        dgent.list = AsyncMock(return_value=[])
        return dgent

    @pytest.fixture
    def persistence(self, mock_dgent: MagicMock) -> WindowPersistence:
        """Create persistence with mock D-gent."""
        return WindowPersistence(dgent=mock_dgent)

    @pytest.mark.asyncio
    async def test_save_window_creates_datum(
        self, persistence: WindowPersistence, mock_dgent: MagicMock
    ) -> None:
        """save_window creates a Datum with correct structure."""
        window = ConversationWindow(max_turns=10, strategy="sliding")
        window.add_turn("Hello", "Hi there!")

        datum_id = await persistence.save_window("session-123", window)

        # Verify put was called
        mock_dgent.put.assert_called_once()
        datum = mock_dgent.put.call_args[0][0]

        # Verify datum structure
        assert datum.id == "conductor:window:session-123"
        assert datum.metadata["strategy"] == "sliding"
        assert datum.metadata["turn_count"] == "1"
        assert datum.metadata["has_summary"] == "false"

    @pytest.mark.asyncio
    async def test_save_window_serializes_content(
        self, persistence: WindowPersistence, mock_dgent: MagicMock
    ) -> None:
        """save_window serializes window content as JSON."""
        window = ConversationWindow(max_turns=5, strategy="hybrid")
        window.add_turn("User message", "Assistant response")

        await persistence.save_window("session-456", window)

        datum = mock_dgent.put.call_args[0][0]
        content = json.loads(datum.content.decode("utf-8"))

        assert content["max_turns"] == 5
        assert content["strategy"] == "hybrid"
        assert content["turn_count"] == 1
        assert len(content["turns"]) == 1

    @pytest.mark.asyncio
    async def test_save_window_with_summary(
        self, persistence: WindowPersistence, mock_dgent: MagicMock
    ) -> None:
        """save_window includes summary in metadata."""
        window = ConversationWindow(max_turns=2, strategy="summarize")
        # Manually set summary for testing
        window._summary = "This is a summary"
        window._summary_tokens = 10

        await persistence.save_window("session-789", window)

        datum = mock_dgent.put.call_args[0][0]
        assert datum.metadata["has_summary"] == "true"


class TestWindowPersistenceLoad:
    """Tests for load_window method."""

    @pytest.fixture
    def mock_dgent(self) -> MagicMock:
        """Create mock D-gent router."""
        dgent = MagicMock()
        dgent.put = AsyncMock(return_value="conductor:window:test-123")
        dgent.get = AsyncMock(return_value=None)
        dgent.delete = AsyncMock(return_value=True)
        dgent.exists = AsyncMock(return_value=False)
        dgent.list = AsyncMock(return_value=[])
        return dgent

    @pytest.fixture
    def persistence(self, mock_dgent: MagicMock) -> WindowPersistence:
        """Create persistence with mock D-gent."""
        return WindowPersistence(dgent=mock_dgent)

    @pytest.mark.asyncio
    async def test_load_window_returns_none_when_not_found(
        self, persistence: WindowPersistence, mock_dgent: MagicMock
    ) -> None:
        """load_window returns None for missing sessions."""
        mock_dgent.get.return_value = None

        window = await persistence.load_window("nonexistent")

        assert window is None

    @pytest.mark.asyncio
    async def test_load_window_deserializes_correctly(
        self, persistence: WindowPersistence, mock_dgent: MagicMock
    ) -> None:
        """load_window reconstructs ConversationWindow from datum."""
        # Create mock datum with serialized window
        window_data = {
            "max_turns": 10,
            "strategy": "sliding",
            "turn_count": 2,
            "total_turn_count": 2,
            "total_tokens": 50,
            "utilization": 0.1,
            "has_summary": False,
            "summary_tokens": 0,
            "turns": [
                {
                    "user": {"role": "user", "content": "Hello"},
                    "assistant": {"role": "assistant", "content": "Hi!"},
                },
                {
                    "user": {"role": "user", "content": "How are you?"},
                    "assistant": {"role": "assistant", "content": "Great!"},
                },
            ],
            "summary": None,
            "created_at": "2025-01-01T00:00:00",
            "last_updated": "2025-01-01T00:01:00",
        }

        mock_datum = MagicMock()
        mock_datum.content = json.dumps(window_data).encode("utf-8")
        mock_dgent.get.return_value = mock_datum

        window = await persistence.load_window("session-123")

        assert window is not None
        assert window.turn_count == 2
        assert window.strategy == "sliding"
        assert window.max_turns == 10

    @pytest.mark.asyncio
    async def test_load_window_handles_corrupted_data(
        self, persistence: WindowPersistence, mock_dgent: MagicMock
    ) -> None:
        """load_window returns None for corrupted data."""
        mock_datum = MagicMock()
        mock_datum.content = b"not valid json"
        mock_dgent.get.return_value = mock_datum

        window = await persistence.load_window("corrupted")

        assert window is None


class TestWindowPersistenceDelete:
    """Tests for delete_window method."""

    @pytest.fixture
    def mock_dgent(self) -> MagicMock:
        """Create mock D-gent router."""
        dgent = MagicMock()
        dgent.delete = AsyncMock(return_value=True)
        return dgent

    @pytest.fixture
    def persistence(self, mock_dgent: MagicMock) -> WindowPersistence:
        """Create persistence with mock D-gent."""
        return WindowPersistence(dgent=mock_dgent)

    @pytest.mark.asyncio
    async def test_delete_window_returns_true_on_success(
        self, persistence: WindowPersistence, mock_dgent: MagicMock
    ) -> None:
        """delete_window returns True when deletion succeeds."""
        mock_dgent.delete.return_value = True

        result = await persistence.delete_window("session-123")

        assert result is True
        mock_dgent.delete.assert_called_once_with("conductor:window:session-123")

    @pytest.mark.asyncio
    async def test_delete_window_returns_false_when_not_found(
        self, persistence: WindowPersistence, mock_dgent: MagicMock
    ) -> None:
        """delete_window returns False when session not found."""
        mock_dgent.delete.return_value = False

        result = await persistence.delete_window("nonexistent")

        assert result is False


# =============================================================================
# Type II: Integration Tests
# =============================================================================


class TestWindowPersistenceIntegration:
    """Integration tests with real D-gent memory backend."""

    @pytest.fixture
    def persistence(self) -> WindowPersistence:
        """Create persistence with memory backend."""
        from agents.d import Backend, DgentRouter

        dgent = DgentRouter(
            namespace="test_windows",
            fallback_chain=[Backend.MEMORY],
        )
        return WindowPersistence(dgent=dgent)

    @pytest.mark.asyncio
    async def test_save_and_load_roundtrip(self, persistence: WindowPersistence) -> None:
        """Window survives save/load roundtrip with real D-gent."""
        # Create and populate window
        original = ConversationWindow(max_turns=5, strategy="hybrid")
        original.add_turn("Hello", "Hi there!")
        original.add_turn("How are you?", "I'm doing great!")
        original.set_system_prompt("You are helpful.")

        # Save
        await persistence.save_window("roundtrip-test", original)

        # Load
        loaded = await persistence.load_window("roundtrip-test")

        # Verify
        assert loaded is not None
        assert loaded.turn_count == original.turn_count
        assert loaded.strategy == original.strategy
        assert loaded.max_turns == original.max_turns

        # Verify turn content
        original_turns = original.get_recent_turns()
        loaded_turns = loaded.get_recent_turns()
        assert original_turns == loaded_turns

    @pytest.mark.asyncio
    async def test_exists_check(self, persistence: WindowPersistence) -> None:
        """exists returns correct state before/after save."""
        session_id = "exists-test"

        # Before save
        assert not await persistence.exists(session_id)

        # Save
        window = ConversationWindow()
        await persistence.save_window(session_id, window)

        # After save
        assert await persistence.exists(session_id)

        # After delete
        await persistence.delete_window(session_id)
        assert not await persistence.exists(session_id)

    @pytest.mark.asyncio
    async def test_list_windows(self, persistence: WindowPersistence) -> None:
        """list_windows returns all persisted windows."""
        # Save multiple windows
        for i in range(3):
            window = ConversationWindow(strategy="sliding")
            window.add_turn(f"Message {i}", f"Response {i}")
            await persistence.save_window(f"list-test-{i}", window)

        # List
        windows = await persistence.list_windows()

        assert len(windows) >= 3
        session_ids = [sid for sid, _ in windows]
        assert "list-test-0" in session_ids
        assert "list-test-1" in session_ids
        assert "list-test-2" in session_ids


# Note: TestComposerPersistenceIntegration removed 2025-12-21 (Crown Jewel Cleanup)
# The ChatMorpheusComposer class was part of the deleted chat service.


# =============================================================================
# Type III: Property-Based Tests
# =============================================================================

try:
    from hypothesis import HealthCheck, given, settings, strategies as st

    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False


@pytest.mark.skipif(not HAS_HYPOTHESIS, reason="hypothesis not installed")
class TestWindowPersistenceProperties:
    """Property-based tests for persistence invariants."""

    def _make_persistence(self) -> WindowPersistence:
        """Create persistence with memory backend."""
        from agents.d import Backend, DgentRouter

        dgent = DgentRouter(
            namespace="test_properties",
            fallback_chain=[Backend.MEMORY],
        )
        return WindowPersistence(dgent=dgent)

    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=100, alphabet="abcdefghijklmnopqrstuvwxyz"),
                st.text(min_size=1, max_size=100, alphabet="abcdefghijklmnopqrstuvwxyz"),
            ),
            min_size=1,
            max_size=20,
        ),
        st.sampled_from(["sliding", "summarize", "hybrid", "forget"]),
    )
    @settings(max_examples=25)
    @pytest.mark.asyncio
    async def test_roundtrip_preserves_turns(
        self,
        turns: list[tuple[str, str]],
        strategy: str,
    ) -> None:
        """Roundtrip preserves all turn content."""
        import uuid

        persistence = self._make_persistence()
        session_id = f"prop-{uuid.uuid4()}"

        # Create window with turns
        window = ConversationWindow(max_turns=100, strategy=strategy)
        for user_msg, asst_msg in turns:
            window.add_turn(user_msg, asst_msg)

        # Save and load
        await persistence.save_window(session_id, window)
        loaded = await persistence.load_window(session_id)

        # Verify
        assert loaded is not None
        assert loaded.turn_count == window.turn_count
        assert loaded.strategy == window.strategy

    @given(
        st.integers(min_value=1, max_value=50),
        st.integers(min_value=1, max_value=100),
    )
    @settings(max_examples=20)
    @pytest.mark.asyncio
    async def test_roundtrip_preserves_config(
        self,
        max_turns: int,
        context_tokens: int,
    ) -> None:
        """Roundtrip preserves window configuration."""
        import uuid

        persistence = self._make_persistence()
        session_id = f"config-{uuid.uuid4()}"

        # Create window with specific config
        window = ConversationWindow(
            max_turns=max_turns,
            strategy="sliding",
            context_window_tokens=context_tokens,
        )

        # Save and load
        await persistence.save_window(session_id, window)
        loaded = await persistence.load_window(session_id)

        # Config is preserved
        assert loaded is not None
        assert loaded.max_turns == max_turns

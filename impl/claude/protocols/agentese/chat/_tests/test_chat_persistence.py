"""
Tests for Chat Session Persistence (Phase 4).

Tests:
- PersistedSession serialization/deserialization
- ChatSessionPersistence CRUD operations
- Session search functionality
- D-gent integration
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytest

from agents.d import DgentRouter, MemoryBackend
from protocols.agentese.chat.config import ChatConfig
from protocols.agentese.chat.persistence import (
    ChatSessionPersistence,
    MemoryInjector,
    PersistedSession,
    get_memory_injector,
    get_persistence,
    reset_persistence,
)
from protocols.agentese.chat.session import ChatSession, ChatSessionState, Message, Turn

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def memory_backend() -> MemoryBackend:
    """Create a fresh in-memory backend for testing."""
    return MemoryBackend()


@pytest.fixture
def persistence(memory_backend: MemoryBackend) -> ChatSessionPersistence:
    """Create persistence layer with in-memory backend."""
    router = DgentRouter(namespace="test_chat")
    router._backend = memory_backend
    router._selected = True  # Mark as selected
    return ChatSessionPersistence(dgent=router)


@pytest.fixture
def mock_umwelt() -> Any:
    """Create a mock Umwelt for testing."""

    class MockUmwelt:
        id = "test-observer-123"
        archetype = "tester"

    return MockUmwelt()


@pytest.fixture
def sample_session(mock_umwelt: Any) -> ChatSession:
    """Create a sample ChatSession for testing."""
    config = ChatConfig(
        context_window=8000,
        max_turns=50,
        entropy_budget=1.0,
    )
    session = ChatSession(
        session_id="test-session-abc123",
        node_path="self.soul",
        observer=mock_umwelt,
        config=config,
    )
    session.activate()
    return session


@pytest.fixture
def session_with_turns(sample_session: ChatSession) -> ChatSession:
    """Create a session with some conversation turns."""
    # Add some turns manually for testing
    for i in range(3):
        user_msg = Message(role="user", content=f"Test message {i + 1}")
        assistant_msg = Message(role="assistant", content=f"Test response {i + 1}")
        turn = Turn(
            turn_number=i + 1,
            user_message=user_msg,
            assistant_response=assistant_msg,
            started_at=datetime.now() - timedelta(minutes=5 - i),
            completed_at=datetime.now() - timedelta(minutes=4 - i),
            tokens_in=10,
            tokens_out=20,
            context_before=100,
            context_after=130,
        )
        sample_session._turns.append(turn)

    sample_session._current_turn = 3
    return sample_session


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset singleton persistence instance before each test."""
    reset_persistence()
    yield
    reset_persistence()


# =============================================================================
# PersistedSession Tests
# =============================================================================


class TestPersistedSession:
    """Tests for PersistedSession dataclass."""

    def test_to_dict_roundtrip(self):
        """Test serialization/deserialization roundtrip."""
        now = datetime.now()
        session = PersistedSession(
            session_id="test-123",
            node_path="self.soul",
            observer_id="user-456",
            created_at=now,
            updated_at=now,
            turn_count=5,
            total_tokens=1000,
            turns=[
                {"turn_number": 1, "user_message": "hello", "assistant_response": "hi"},
            ],
            summary="Test summary",
            name="my-session",
            tags=["test", "demo"],
            state="waiting",
            entropy=0.8,
        )

        # Serialize
        data = session.to_dict()
        assert data["session_id"] == "test-123"
        assert data["name"] == "my-session"
        assert data["entropy"] == 0.8

        # Deserialize
        restored = PersistedSession.from_dict(data)
        assert restored.session_id == session.session_id
        assert restored.name == session.name
        assert restored.entropy == session.entropy
        assert restored.turn_count == session.turn_count

    def test_from_session(self, session_with_turns: ChatSession):
        """Test creating PersistedSession from ChatSession."""
        persisted = PersistedSession.from_session(session_with_turns)

        assert persisted.session_id == session_with_turns.session_id
        assert persisted.node_path == session_with_turns.node_path
        assert persisted.turn_count == 3
        assert len(persisted.turns) == 3

    def test_from_session_without_turns(self, sample_session: ChatSession):
        """Test creating PersistedSession from empty session."""
        persisted = PersistedSession.from_session(sample_session)

        assert persisted.session_id == sample_session.session_id
        assert persisted.turn_count == 0
        assert persisted.turns == []


# =============================================================================
# ChatSessionPersistence Tests
# =============================================================================


class TestChatSessionPersistence:
    """Tests for ChatSessionPersistence class."""

    @pytest.mark.asyncio
    async def test_save_and_load_session(
        self,
        persistence: ChatSessionPersistence,
        session_with_turns: ChatSession,
    ):
        """Test saving and loading a session."""
        # Save
        datum_id = await persistence.save_session(session_with_turns)
        assert datum_id is not None

        # Load
        loaded = await persistence.load_session(session_with_turns.session_id)
        assert loaded is not None
        assert loaded.session_id == session_with_turns.session_id
        assert loaded.turn_count == 3

    @pytest.mark.asyncio
    async def test_save_with_name(
        self,
        persistence: ChatSessionPersistence,
        session_with_turns: ChatSession,
    ):
        """Test saving session with a custom name."""
        await persistence.save_session(session_with_turns, name="my-planning-session")

        # Load by name
        loaded = await persistence.load_by_name("my-planning-session")
        assert loaded is not None
        assert loaded.name == "my-planning-session"

    @pytest.mark.asyncio
    async def test_list_sessions(
        self,
        persistence: ChatSessionPersistence,
        mock_umwelt: Any,
    ):
        """Test listing sessions."""
        # Create and save multiple sessions
        for i in range(3):
            config = ChatConfig()
            session = ChatSession(
                session_id=f"session-{i}",
                node_path="self.soul",
                observer=mock_umwelt,
                config=config,
            )
            session.activate()
            await persistence.save_session(session, name=f"session-{i}")

        # List all
        sessions = await persistence.list_sessions()
        assert len(sessions) == 3

    @pytest.mark.asyncio
    async def test_list_sessions_with_node_filter(
        self,
        persistence: ChatSessionPersistence,
        mock_umwelt: Any,
    ):
        """Test listing sessions filtered by node path."""
        # Create sessions with different paths (unique IDs)
        paths_and_ids = [
            ("self.soul", "session-soul-1"),
            ("self.soul", "session-soul-2"),
            ("world.town.citizen.elara", "session-elara-1"),
        ]
        for path, session_id in paths_and_ids:
            config = ChatConfig()
            session = ChatSession(
                session_id=session_id,
                node_path=path,
                observer=mock_umwelt,
                config=config,
            )
            session.activate()
            await persistence.save_session(session)

        # Filter by path
        soul_sessions = await persistence.list_sessions(node_path="self.soul")
        assert len(soul_sessions) == 2

        citizen_sessions = await persistence.list_sessions(node_path="world.town.citizen.elara")
        assert len(citizen_sessions) == 1

    @pytest.mark.asyncio
    async def test_search_sessions(
        self,
        persistence: ChatSessionPersistence,
        mock_umwelt: Any,
    ):
        """Test searching sessions by content."""
        # Create sessions with different content
        config = ChatConfig()

        # Session 1: about authentication
        session1 = ChatSession(
            session_id="session-auth",
            node_path="self.soul",
            observer=mock_umwelt,
            config=config,
        )
        session1.activate()
        session1._turns.append(
            Turn(
                turn_number=1,
                user_message=Message(role="user", content="How do I implement authentication?"),
                assistant_response=Message(role="assistant", content="Use OAuth or JWT"),
                started_at=datetime.now(),
                completed_at=datetime.now(),
                tokens_in=10,
                tokens_out=20,
                context_before=0,
                context_after=30,
            )
        )
        await persistence.save_session(session1)

        # Session 2: about testing
        session2 = ChatSession(
            session_id="session-testing",
            node_path="self.soul",
            observer=mock_umwelt,
            config=config,
        )
        session2.activate()
        session2._turns.append(
            Turn(
                turn_number=1,
                user_message=Message(role="user", content="How do I write unit tests?"),
                assistant_response=Message(role="assistant", content="Use pytest fixtures"),
                started_at=datetime.now(),
                completed_at=datetime.now(),
                tokens_in=10,
                tokens_out=20,
                context_before=0,
                context_after=30,
            )
        )
        await persistence.save_session(session2)

        # Search for authentication
        auth_results = await persistence.search_sessions("authentication")
        assert len(auth_results) >= 1
        assert any("auth" in s.session_id for s in auth_results)

        # Search for testing
        test_results = await persistence.search_sessions("pytest")
        assert len(test_results) >= 1

    @pytest.mark.asyncio
    async def test_delete_session(
        self,
        persistence: ChatSessionPersistence,
        session_with_turns: ChatSession,
    ):
        """Test deleting a session."""
        # Save first
        await persistence.save_session(session_with_turns)

        # Verify exists
        exists = await persistence.session_exists(session_with_turns.session_id)
        assert exists

        # Delete
        deleted = await persistence.delete_session(session_with_turns.session_id)
        assert deleted

        # Verify gone
        exists = await persistence.session_exists(session_with_turns.session_id)
        assert not exists

    @pytest.mark.asyncio
    async def test_delete_nonexistent_session(
        self,
        persistence: ChatSessionPersistence,
    ):
        """Test deleting a session that doesn't exist."""
        deleted = await persistence.delete_session("nonexistent-id")
        assert not deleted

    @pytest.mark.asyncio
    async def test_count_sessions(
        self,
        persistence: ChatSessionPersistence,
        mock_umwelt: Any,
    ):
        """Test counting sessions."""
        # Initially empty
        count = await persistence.count_sessions()
        assert count == 0

        # Add sessions
        for i in range(5):
            config = ChatConfig()
            session = ChatSession(
                session_id=f"count-session-{i}",
                node_path="self.soul",
                observer=mock_umwelt,
                config=config,
            )
            session.activate()
            await persistence.save_session(session)

        count = await persistence.count_sessions()
        assert count == 5

    @pytest.mark.asyncio
    async def test_get_recent_sessions(
        self,
        persistence: ChatSessionPersistence,
        mock_umwelt: Any,
    ):
        """Test getting most recent sessions."""
        # Create sessions at different times
        for i in range(5):
            config = ChatConfig()
            session = ChatSession(
                session_id=f"recent-session-{i}",
                node_path="self.soul",
                observer=mock_umwelt,
                config=config,
            )
            session.activate()
            # Simulate different update times by modifying _updated_at
            session._updated_at = datetime.now() - timedelta(minutes=5 - i)
            await persistence.save_session(session)

        # Get recent
        recent = await persistence.get_recent_sessions(limit=3)
        assert len(recent) == 3

    @pytest.mark.asyncio
    async def test_update_existing_session(
        self,
        persistence: ChatSessionPersistence,
        session_with_turns: ChatSession,
    ):
        """Test updating an existing session."""
        # Save initial
        await persistence.save_session(session_with_turns)

        # Add more turns
        session_with_turns._turns.append(
            Turn(
                turn_number=4,
                user_message=Message(role="user", content="New message"),
                assistant_response=Message(role="assistant", content="New response"),
                started_at=datetime.now(),
                completed_at=datetime.now(),
                tokens_in=10,
                tokens_out=20,
                context_before=0,
                context_after=30,
            )
        )

        # Save again (update)
        await persistence.save_session(session_with_turns)

        # Load and verify
        loaded = await persistence.load_session(session_with_turns.session_id)
        assert loaded is not None
        assert loaded.turn_count == 4
        assert len(loaded.turns) == 4


# =============================================================================
# Singleton Tests
# =============================================================================


class TestPersistenceSingleton:
    """Tests for singleton pattern."""

    def test_get_persistence_returns_singleton(self):
        """Test that get_persistence returns the same instance."""
        p1 = get_persistence()
        p2 = get_persistence()
        assert p1 is p2

    def test_reset_persistence_clears_singleton(self):
        """Test that reset_persistence clears the singleton."""
        p1 = get_persistence()
        reset_persistence()
        p2 = get_persistence()
        assert p1 is not p2


# =============================================================================
# Edge Cases
# =============================================================================


class TestPersistenceEdgeCases:
    """Edge case and error handling tests."""

    @pytest.mark.asyncio
    async def test_load_nonexistent_session(
        self,
        persistence: ChatSessionPersistence,
    ):
        """Test loading a session that doesn't exist."""
        loaded = await persistence.load_session("nonexistent-id")
        assert loaded is None

    @pytest.mark.asyncio
    async def test_load_by_name_nonexistent(
        self,
        persistence: ChatSessionPersistence,
    ):
        """Test loading by name that doesn't exist."""
        loaded = await persistence.load_by_name("nonexistent-name")
        assert loaded is None

    @pytest.mark.asyncio
    async def test_search_empty_results(
        self,
        persistence: ChatSessionPersistence,
    ):
        """Test search with no matches."""
        results = await persistence.search_sessions("xyz123nonexistent")
        assert results == []

    @pytest.mark.asyncio
    async def test_list_with_limit(
        self,
        persistence: ChatSessionPersistence,
        mock_umwelt: Any,
    ):
        """Test listing with limit."""
        # Create 10 sessions
        for i in range(10):
            config = ChatConfig()
            session = ChatSession(
                session_id=f"limit-session-{i}",
                node_path="self.soul",
                observer=mock_umwelt,
                config=config,
            )
            session.activate()
            await persistence.save_session(session)

        # List with limit
        sessions = await persistence.list_sessions(limit=5)
        assert len(sessions) == 5


# =============================================================================
# Memory Injector Tests
# =============================================================================


class TestMemoryInjector:
    """Tests for MemoryInjector class."""

    @pytest.fixture
    def injector(self, persistence: ChatSessionPersistence) -> MemoryInjector:
        """Create injector with test persistence."""
        return MemoryInjector(persistence=persistence)

    @pytest.mark.asyncio
    async def test_inject_context_empty(
        self,
        injector: MemoryInjector,
    ):
        """Test context injection with no past sessions."""
        context = await injector.inject_context(
            node_path="self.soul",
            observer_id="user-123",
        )
        assert context == ""

    @pytest.mark.asyncio
    async def test_inject_context_with_sessions(
        self,
        injector: MemoryInjector,
        persistence: ChatSessionPersistence,
        mock_umwelt: Any,
    ):
        """Test context injection with past sessions."""
        # Create a session with turns
        config = ChatConfig()
        session = ChatSession(
            session_id="past-session-1",
            node_path="self.soul",
            observer=mock_umwelt,
            config=config,
        )
        session.activate()
        session._turns.append(
            Turn(
                turn_number=1,
                user_message=Message(role="user", content="How do I implement auth?"),
                assistant_response=Message(role="assistant", content="Use OAuth or JWT tokens"),
                started_at=datetime.now(),
                completed_at=datetime.now(),
                tokens_in=10,
                tokens_out=20,
                context_before=0,
                context_after=30,
            )
        )
        await persistence.save_session(session)

        # Inject context
        context = await injector.inject_context(
            node_path="self.soul",
            observer_id=mock_umwelt.id,
            current_message="Tell me about authentication",
        )

        assert "Past Conversations" in context
        assert "auth" in context.lower()

    @pytest.mark.asyncio
    async def test_inject_context_relevance_ranking(
        self,
        injector: MemoryInjector,
        persistence: ChatSessionPersistence,
        mock_umwelt: Any,
    ):
        """Test that sessions are ranked by relevance."""
        config = ChatConfig()

        # Create irrelevant session
        irrelevant = ChatSession(
            session_id="irrelevant-session",
            node_path="self.soul",
            observer=mock_umwelt,
            config=config,
        )
        irrelevant.activate()
        irrelevant._turns.append(
            Turn(
                turn_number=1,
                user_message=Message(role="user", content="What's the weather?"),
                assistant_response=Message(role="assistant", content="I don't know"),
                started_at=datetime.now() - timedelta(days=10),
                completed_at=datetime.now() - timedelta(days=10),
                tokens_in=10,
                tokens_out=20,
                context_before=0,
                context_after=30,
            )
        )
        await persistence.save_session(irrelevant)

        # Create relevant session
        relevant = ChatSession(
            session_id="relevant-session",
            node_path="self.soul",
            observer=mock_umwelt,
            config=config,
        )
        relevant.activate()
        relevant._turns.append(
            Turn(
                turn_number=1,
                user_message=Message(role="user", content="How do databases work?"),
                assistant_response=Message(role="assistant", content="SQL queries fetch data"),
                started_at=datetime.now(),
                completed_at=datetime.now(),
                tokens_in=10,
                tokens_out=20,
                context_before=0,
                context_after=30,
            )
        )
        await persistence.save_session(relevant)

        # Query about databases - should rank relevant higher
        context = await injector.inject_context(
            node_path="self.soul",
            observer_id=mock_umwelt.id,
            current_message="Tell me about databases",
            max_sessions=1,
        )

        assert "database" in context.lower()

    @pytest.mark.asyncio
    async def test_get_entity_memory_empty(
        self,
        injector: MemoryInjector,
    ):
        """Test entity memory with no sessions."""
        memory = await injector.get_entity_memory("self.soul")

        assert memory["total_sessions"] == 0
        assert memory["total_turns"] == 0
        assert memory["observers_seen"] == []

    @pytest.mark.asyncio
    async def test_get_entity_memory_with_sessions(
        self,
        injector: MemoryInjector,
        persistence: ChatSessionPersistence,
        mock_umwelt: Any,
    ):
        """Test entity memory aggregation."""
        config = ChatConfig()

        # Create multiple sessions
        for i in range(3):
            session = ChatSession(
                session_id=f"entity-session-{i}",
                node_path="world.town.citizen.elara",
                observer=mock_umwelt,
                config=config,
            )
            session.activate()
            session._turns.append(
                Turn(
                    turn_number=1,
                    user_message=Message(role="user", content=f"Question {i}"),
                    assistant_response=Message(role="assistant", content=f"Answer {i}"),
                    started_at=datetime.now(),
                    completed_at=datetime.now(),
                    tokens_in=10,
                    tokens_out=20,
                    context_before=0,
                    context_after=30,
                )
            )
            await persistence.save_session(session)

        memory = await injector.get_entity_memory("world.town.citizen.elara")

        assert memory["total_sessions"] == 3
        assert memory["total_turns"] == 3
        assert mock_umwelt.id in memory["observers_seen"]


class TestMemoryInjectorSingleton:
    """Tests for memory injector singleton."""

    def test_get_memory_injector_returns_singleton(self):
        """Test singleton behavior."""
        i1 = get_memory_injector()
        i2 = get_memory_injector()
        assert i1 is i2


__all__ = [
    "TestPersistedSession",
    "TestChatSessionPersistence",
    "TestPersistenceSingleton",
    "TestPersistenceEdgeCases",
    "TestMemoryInjector",
    "TestMemoryInjectorSingleton",
]

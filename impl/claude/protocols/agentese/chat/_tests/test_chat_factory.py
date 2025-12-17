"""
Tests for ChatSessionFactory.

Tests the factory pattern for creating chat sessions:
- Session creation and caching
- Configuration resolution
- System prompt generation
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from protocols.agentese.chat.config import (
    CITIZEN_CHAT_CONFIG,
    SOUL_CHAT_CONFIG,
    ChatConfig,
)
from protocols.agentese.chat.factory import (
    ChatSessionFactory,
    SystemPromptContext,
    generate_session_id,
)
from protocols.agentese.chat.session import ChatSession, ChatSessionState

# === Fixtures ===


@pytest.fixture
def mock_observer() -> MagicMock:
    """Create a mock observer umwelt."""
    observer = MagicMock()
    observer.meta.name = "test_user"
    observer.meta.archetype = "developer"
    return observer


@pytest.fixture
def factory() -> ChatSessionFactory:
    """Create a basic factory."""
    return ChatSessionFactory()


# === Session ID Generation Tests ===


class TestSessionIdGeneration:
    """Tests for generate_session_id()."""

    def test_session_id_format(self) -> None:
        """Test session ID has expected format."""
        session_id = generate_session_id("self.soul", "test_user")

        # Format: <prefix>_<timestamp>_<hash>
        parts = session_id.split("_")
        assert len(parts) >= 3

    def test_session_id_unique(self) -> None:
        """Test session IDs are unique."""
        id1 = generate_session_id("self.soul", "user1")
        id2 = generate_session_id("self.soul", "user2")

        assert id1 != id2

    def test_session_id_different_nodes(self) -> None:
        """Test different nodes get different IDs."""
        id1 = generate_session_id("self.soul", "user")
        id2 = generate_session_id("world.town.citizen.elara", "user")

        assert id1 != id2


# === SystemPromptContext Tests ===


class TestSystemPromptContext:
    """Tests for SystemPromptContext."""

    def test_context_defaults(self) -> None:
        """Test context has sensible defaults."""
        ctx = SystemPromptContext(node_path="self.soul")

        assert ctx.node_path == "self.soul"
        assert ctx.observer_name == "user"
        assert ctx.warmth == 0.7

    def test_context_custom_values(self) -> None:
        """Test context with custom values."""
        ctx = SystemPromptContext(
            node_path="world.town.citizen.elara",
            citizen_name="Elara",
            citizen_archetype="mystic",
        )

        assert ctx.citizen_name == "Elara"
        assert ctx.citizen_archetype == "mystic"


# === Factory Configuration Resolution Tests ===


class TestFactoryConfigResolution:
    """Tests for ChatSessionFactory._resolve_config()."""

    def test_explicit_config_preferred(self, factory: ChatSessionFactory) -> None:
        """Test explicit config takes precedence."""
        custom_config = ChatConfig(context_window=2000)

        resolved = factory._resolve_config("self.soul", custom_config)

        assert resolved.context_window == 2000

    def test_soul_default_config(self, factory: ChatSessionFactory) -> None:
        """Test soul gets SOUL_CHAT_CONFIG defaults."""
        resolved = factory._resolve_config("self.soul", None)

        assert resolved.context_window == SOUL_CHAT_CONFIG.context_window

    def test_citizen_default_config(self, factory: ChatSessionFactory) -> None:
        """Test citizen gets CITIZEN_CHAT_CONFIG defaults."""
        resolved = factory._resolve_config("world.town.citizen.elara", None)

        assert resolved.context_window == CITIZEN_CHAT_CONFIG.context_window


# === Factory System Prompt Tests ===


class TestFactorySystemPrompt:
    """Tests for system prompt generation."""

    @pytest.mark.asyncio
    async def test_soul_prompt_generated(
        self, factory: ChatSessionFactory, mock_observer: MagicMock
    ) -> None:
        """Test soul prompt is generated."""
        config = ChatConfig()  # No explicit prompt
        prompt = await factory._build_system_prompt("self.soul", mock_observer, config)

        assert "K-gent" in prompt
        assert "consciousness" in prompt.lower()

    @pytest.mark.asyncio
    async def test_citizen_prompt_generated(
        self, factory: ChatSessionFactory, mock_observer: MagicMock
    ) -> None:
        """Test citizen prompt is generated."""
        config = ChatConfig()
        prompt = await factory._build_system_prompt(
            "world.town.citizen.elara", mock_observer, config
        )

        assert "citizen" in prompt.lower()

    @pytest.mark.asyncio
    async def test_explicit_prompt_used(
        self, factory: ChatSessionFactory, mock_observer: MagicMock
    ) -> None:
        """Test explicit prompt is used when provided."""
        config = ChatConfig(system_prompt="Custom system prompt")
        prompt = await factory._build_system_prompt("self.soul", mock_observer, config)

        assert prompt == "Custom system prompt"

    @pytest.mark.asyncio
    async def test_custom_prompt_factory(self, mock_observer: MagicMock) -> None:
        """Test custom prompt factory is used."""

        def custom_factory(ctx: SystemPromptContext) -> str:
            return f"Custom prompt for {ctx.node_path}"

        factory = ChatSessionFactory(system_prompt_factory=custom_factory)
        config = ChatConfig()
        prompt = await factory._build_system_prompt("self.soul", mock_observer, config)

        assert prompt == "Custom prompt for self.soul"


# === Factory Session Creation Tests ===


class TestFactorySessionCreation:
    """Tests for ChatSessionFactory.create_session()."""

    @pytest.mark.asyncio
    async def test_create_session_basic(
        self, factory: ChatSessionFactory, mock_observer: MagicMock
    ) -> None:
        """Test basic session creation."""
        session = await factory.create_session("self.soul", mock_observer)

        assert isinstance(session, ChatSession)
        assert session.node_path == "self.soul"
        assert session.state == ChatSessionState.READY

    @pytest.mark.asyncio
    async def test_create_session_with_config(
        self, factory: ChatSessionFactory, mock_observer: MagicMock
    ) -> None:
        """Test session creation with custom config."""
        config = ChatConfig(max_turns=5)
        session = await factory.create_session(
            "self.soul", mock_observer, config=config
        )

        assert session.config.max_turns == 5

    @pytest.mark.asyncio
    async def test_session_caching(
        self, factory: ChatSessionFactory, mock_observer: MagicMock
    ) -> None:
        """Test sessions are cached by (node_path, observer_id)."""
        session1 = await factory.create_session("self.soul", mock_observer)
        session2 = await factory.create_session("self.soul", mock_observer)

        # Same observer, same node -> same session
        assert session1.session_id == session2.session_id

    @pytest.mark.asyncio
    async def test_force_new_session(
        self, factory: ChatSessionFactory, mock_observer: MagicMock
    ) -> None:
        """Test force_new creates a new session."""
        session1 = await factory.create_session("self.soul", mock_observer)
        session2 = await factory.create_session(
            "self.soul", mock_observer, force_new=True
        )

        assert session1.session_id != session2.session_id

    @pytest.mark.asyncio
    async def test_different_observers_different_sessions(
        self, factory: ChatSessionFactory
    ) -> None:
        """Test different observers get different sessions."""
        observer1 = MagicMock()
        observer1.meta.name = "user1"

        observer2 = MagicMock()
        observer2.meta.name = "user2"

        session1 = await factory.create_session("self.soul", observer1)
        session2 = await factory.create_session("self.soul", observer2)

        assert session1.session_id != session2.session_id

    @pytest.mark.asyncio
    async def test_different_nodes_different_sessions(
        self, factory: ChatSessionFactory, mock_observer: MagicMock
    ) -> None:
        """Test different nodes get different sessions."""
        session1 = await factory.create_session("self.soul", mock_observer)
        session2 = await factory.create_session(
            "world.town.citizen.elara", mock_observer
        )

        assert session1.session_id != session2.session_id


# === Factory Session Retrieval Tests ===


class TestFactorySessionRetrieval:
    """Tests for session retrieval methods."""

    @pytest.mark.asyncio
    async def test_get_session(
        self, factory: ChatSessionFactory, mock_observer: MagicMock
    ) -> None:
        """Test get_session() retrieves cached session."""
        created = await factory.create_session("self.soul", mock_observer)
        retrieved = factory.get_session("self.soul", mock_observer)

        assert retrieved is not None
        assert retrieved.session_id == created.session_id

    @pytest.mark.asyncio
    async def test_get_session_not_found(
        self, factory: ChatSessionFactory, mock_observer: MagicMock
    ) -> None:
        """Test get_session() returns None when not found."""
        retrieved = factory.get_session("nonexistent.path", mock_observer)

        assert retrieved is None

    @pytest.mark.asyncio
    async def test_get_session_by_id(
        self, factory: ChatSessionFactory, mock_observer: MagicMock
    ) -> None:
        """Test get_session_by_id() retrieves by ID."""
        created = await factory.create_session("self.soul", mock_observer)
        retrieved = factory.get_session_by_id(created.session_id)

        assert retrieved is not None
        assert retrieved.session_id == created.session_id

    @pytest.mark.asyncio
    async def test_list_sessions(
        self, factory: ChatSessionFactory, mock_observer: MagicMock
    ) -> None:
        """Test list_sessions() returns matching sessions."""
        await factory.create_session("self.soul", mock_observer)
        await factory.create_session("world.town.citizen.elara", mock_observer)

        # List all
        all_sessions = factory.list_sessions()
        assert len(all_sessions) == 2

        # List by node path
        soul_sessions = factory.list_sessions(node_path="self.soul")
        assert len(soul_sessions) == 1


# === Factory Session Lifecycle Tests ===


class TestFactorySessionLifecycle:
    """Tests for session lifecycle management."""

    @pytest.mark.asyncio
    async def test_close_session(
        self, factory: ChatSessionFactory, mock_observer: MagicMock
    ) -> None:
        """Test close_session() collapses and removes session."""
        session = await factory.create_session("self.soul", mock_observer)
        factory.close_session(session)

        assert session.is_collapsed
        assert factory.get_session("self.soul", mock_observer) is None

    @pytest.mark.asyncio
    async def test_cached_collapsed_session_replaced(
        self, factory: ChatSessionFactory, mock_observer: MagicMock
    ) -> None:
        """Test that collapsed cached sessions are replaced."""
        session1 = await factory.create_session("self.soul", mock_observer)
        session1.collapse("manual")

        # Creating new session should replace collapsed one
        session2 = await factory.create_session("self.soul", mock_observer)

        assert session2.session_id != session1.session_id
        assert session2.is_active


# === Factory Integration Tests ===


class TestFactoryIntegration:
    """Integration tests for ChatSessionFactory."""

    @pytest.mark.asyncio
    async def test_full_workflow(self, mock_observer: MagicMock) -> None:
        """Test complete factory workflow."""
        factory = ChatSessionFactory()

        # Create session
        session = await factory.create_session("self.soul", mock_observer)
        assert session.is_active

        # Use session
        await session.send("Hello")
        assert session.turn_count == 1

        # Retrieve same session
        same_session = await factory.create_session("self.soul", mock_observer)
        assert same_session.session_id == session.session_id
        assert same_session.turn_count == 1

        # Create a different session type
        citizen_session = await factory.create_session(
            "world.town.citizen.elara", mock_observer
        )
        assert citizen_session.turn_count == 0

        # List sessions (should have 2: soul and citizen)
        sessions = factory.list_sessions()
        assert len(sessions) == 2

        # Force new soul session (replaces old one)
        new_session = await factory.create_session(
            "self.soul", mock_observer, force_new=True
        )
        assert new_session.turn_count == 0
        assert new_session.session_id != session.session_id

        # Still have 2 sessions (new soul + citizen)
        sessions = factory.list_sessions()
        assert len(sessions) == 2

        # Close the citizen session
        factory.close_session(citizen_session)
        assert len(factory.list_sessions()) == 1

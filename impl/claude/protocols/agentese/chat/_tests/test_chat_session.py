"""
Tests for ChatSession state machine and turn protocol.

Tests the core ChatSession class:
- State machine transitions
- Turn protocol (atomic turns)
- Budget tracking
- Entropy management
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from protocols.agentese.chat.config import ChatConfig, ContextStrategy
from protocols.agentese.chat.session import (
    ChatSession,
    ChatSessionState,
    Message,
    SessionBudget,
    Turn,
)

# === Fixtures ===


@pytest.fixture
def mock_observer() -> MagicMock:
    """Create a mock observer umwelt."""
    observer = MagicMock()
    observer.meta.name = "test_observer"
    observer.meta.archetype = "developer"
    return observer


@pytest.fixture
def basic_config() -> ChatConfig:
    """Create a basic chat config."""
    return ChatConfig(
        context_window=4000,
        context_strategy=ContextStrategy.SLIDING,
        max_turns=10,
        entropy_budget=1.0,
        entropy_decay_per_turn=0.1,
    )


@pytest.fixture
def session(mock_observer: MagicMock, basic_config: ChatConfig) -> ChatSession:
    """Create a basic chat session."""
    return ChatSession(
        session_id="test_session_001",
        node_path="self.soul",
        observer=mock_observer,
        config=basic_config,
    )


# === Message Tests ===


class TestMessage:
    """Tests for the Message dataclass."""

    def test_message_creation(self) -> None:
        """Test basic message creation."""
        msg = Message(role="user", content="Hello world")
        assert msg.role == "user"
        assert msg.content == "Hello world"
        assert msg.tokens > 0  # Auto-calculated

    def test_message_token_estimation(self) -> None:
        """Test token estimation (4 chars ~= 1 token)."""
        msg = Message(role="user", content="12345678")  # 8 chars
        assert msg.tokens == 2  # 8 // 4

    def test_message_explicit_tokens(self) -> None:
        """Test explicit token count override."""
        msg = Message(role="user", content="Hello", tokens=100)
        assert msg.tokens == 100

    def test_message_timestamp(self) -> None:
        """Test message has timestamp."""
        before = datetime.now()
        msg = Message(role="user", content="test")
        after = datetime.now()
        assert before <= msg.timestamp <= after


# === Turn Tests ===


class TestTurn:
    """Tests for the Turn dataclass."""

    def test_turn_creation(self) -> None:
        """Test basic turn creation."""
        user_msg = Message(role="user", content="Hello")
        response_msg = Message(role="assistant", content="Hi there!")
        started = datetime.now()
        completed = datetime.now()

        turn = Turn(
            turn_number=1,
            user_message=user_msg,
            assistant_response=response_msg,
            started_at=started,
            completed_at=completed,
            tokens_in=10,
            tokens_out=15,
            context_before=100,
            context_after=125,
        )

        assert turn.turn_number == 1
        assert turn.total_tokens == 25
        assert turn.duration >= 0

    def test_turn_to_dict(self) -> None:
        """Test turn serialization."""
        turn = Turn(
            turn_number=1,
            user_message=Message(role="user", content="Hello"),
            assistant_response=Message(role="assistant", content="Hi"),
            started_at=datetime.now(),
            completed_at=datetime.now(),
            tokens_in=5,
            tokens_out=5,
            context_before=0,
            context_after=10,
        )

        data = turn.to_dict()
        assert data["turn_number"] == 1
        assert data["tokens_in"] == 5
        assert data["tokens_out"] == 5
        assert "started_at" in data


# === SessionBudget Tests ===


class TestSessionBudget:
    """Tests for the SessionBudget class."""

    def test_budget_creation(self) -> None:
        """Test budget creation with defaults."""
        budget = SessionBudget()
        assert budget.tokens_in_total == 0
        assert budget.tokens_out_total == 0
        assert budget.estimated_cost_usd == 0.0

    def test_budget_record_turn(self) -> None:
        """Test recording a turn."""
        budget = SessionBudget()
        turn = Turn(
            turn_number=1,
            user_message=Message(role="user", content="Hello"),
            assistant_response=Message(role="assistant", content="Hi"),
            started_at=datetime.now(),
            completed_at=datetime.now(),
            tokens_in=100,
            tokens_out=200,
            context_before=0,
            context_after=300,
        )

        budget.record_turn(turn)
        assert budget.tokens_in_total == 100
        assert budget.tokens_out_total == 200
        assert budget.total_tokens == 300
        assert budget.turn_count == 1
        assert budget.estimated_cost_usd > 0

    def test_budget_multiple_turns(self) -> None:
        """Test recording multiple turns."""
        budget = SessionBudget()

        for i in range(3):
            turn = Turn(
                turn_number=i + 1,
                user_message=Message(role="user", content="msg"),
                assistant_response=Message(role="assistant", content="response"),
                started_at=datetime.now(),
                completed_at=datetime.now(),
                tokens_in=100,
                tokens_out=200,
                context_before=0,
                context_after=0,
            )
            budget.record_turn(turn)

        assert budget.turn_count == 3
        assert budget.tokens_in_total == 300
        assert budget.tokens_out_total == 600


# === ChatSession State Machine Tests ===


class TestChatSessionStateMachine:
    """Tests for ChatSession state transitions."""

    def test_initial_state_dormant(self, session: ChatSession) -> None:
        """Test session starts in DORMANT state."""
        assert session.state == ChatSessionState.DORMANT

    def test_activate_transition(self, session: ChatSession) -> None:
        """Test DORMANT -> READY transition."""
        session.activate()
        assert session.state == ChatSessionState.READY

    def test_invalid_transition_raises(self, session: ChatSession) -> None:
        """Test invalid transition raises ValueError."""
        with pytest.raises(ValueError):
            session._transition(ChatSessionState.STREAMING)  # Can't go directly

    def test_collapse_from_any_state(self, session: ChatSession) -> None:
        """Test collapse can happen from any state."""
        session.activate()
        session.collapse("test")
        assert session.state == ChatSessionState.COLLAPSED

    def test_collapsed_is_terminal(self, session: ChatSession) -> None:
        """Test collapsed is a terminal state."""
        session.collapse("test")
        assert session.is_collapsed

    def test_is_active_states(self, session: ChatSession) -> None:
        """Test is_active for various states."""
        assert not session.is_active  # DORMANT

        session.activate()
        assert session.is_active  # READY

        session.collapse("test")
        assert not session.is_active  # COLLAPSED


# === ChatSession Send Tests ===


class TestChatSessionSend:
    """Tests for ChatSession.send() method."""

    @pytest.mark.asyncio
    async def test_send_activates_dormant_session(self, session: ChatSession) -> None:
        """Test send() activates a dormant session."""
        assert session.state == ChatSessionState.DORMANT
        await session.send("Hello")
        # Should transition through STREAMING to WAITING
        assert session.state == ChatSessionState.WAITING

    @pytest.mark.asyncio
    async def test_send_records_turn(self, session: ChatSession) -> None:
        """Test send() records a turn."""
        await session.send("Hello world")
        assert session.turn_count == 1
        turn = session.get_history()[0]
        assert turn.user_message.content == "Hello world"

    @pytest.mark.asyncio
    async def test_send_decays_entropy(self, mock_observer: MagicMock) -> None:
        """Test send() decays entropy."""
        config = ChatConfig(entropy_budget=1.0, entropy_decay_per_turn=0.1)
        session = ChatSession(
            session_id="test",
            node_path="self.soul",
            observer=mock_observer,
            config=config,
        )

        assert session.entropy == 1.0
        await session.send("Hello")
        assert session.entropy == 0.9

    @pytest.mark.asyncio
    async def test_send_collapses_on_entropy_depletion(
        self, mock_observer: MagicMock
    ) -> None:
        """Test session collapses when entropy depletes."""
        config = ChatConfig(entropy_budget=0.05, entropy_decay_per_turn=0.1)
        session = ChatSession(
            session_id="test",
            node_path="self.soul",
            observer=mock_observer,
            config=config,
        )

        await session.send("Hello")
        assert session.is_collapsed

    @pytest.mark.asyncio
    async def test_send_enforces_max_turns(self, mock_observer: MagicMock) -> None:
        """Test max_turns enforcement."""
        config = ChatConfig(max_turns=2, entropy_budget=10.0)
        session = ChatSession(
            session_id="test",
            node_path="self.soul",
            observer=mock_observer,
            config=config,
        )

        await session.send("Turn 1")
        await session.send("Turn 2")

        with pytest.raises(RuntimeError, match="Max turns"):
            await session.send("Turn 3")

    @pytest.mark.asyncio
    async def test_send_fails_on_collapsed_session(self, session: ChatSession) -> None:
        """Test send() fails on collapsed session."""
        session.collapse("test")

        with pytest.raises(RuntimeError, match="collapsed"):
            await session.send("Hello")


# === ChatSession Stream Tests ===


class TestChatSessionStream:
    """Tests for ChatSession.stream() method."""

    @pytest.mark.asyncio
    async def test_stream_yields_tokens(self, session: ChatSession) -> None:
        """Test stream() yields tokens."""
        tokens = []
        async for token in session.stream("Hello"):
            tokens.append(token)

        assert len(tokens) > 0
        assert session.turn_count == 1

    @pytest.mark.asyncio
    async def test_stream_records_turn(self, session: ChatSession) -> None:
        """Test stream() records a turn."""
        async for _ in session.stream("Hello"):
            pass

        assert session.turn_count == 1

    @pytest.mark.asyncio
    async def test_stream_decays_entropy(self, mock_observer: MagicMock) -> None:
        """Test stream() decays entropy."""
        config = ChatConfig(entropy_budget=1.0, entropy_decay_per_turn=0.2)
        session = ChatSession(
            session_id="test",
            node_path="self.soul",
            observer=mock_observer,
            config=config,
        )

        async for _ in session.stream("Hello"):
            pass

        assert session.entropy == 0.8


# === ChatSession History Tests ===


class TestChatSessionHistory:
    """Tests for ChatSession history methods."""

    @pytest.mark.asyncio
    async def test_get_history_returns_all_turns(self, session: ChatSession) -> None:
        """Test get_history() returns all turns."""
        await session.send("Turn 1")
        await session.send("Turn 2")
        await session.send("Turn 3")

        history = session.get_history()
        assert len(history) == 3

    @pytest.mark.asyncio
    async def test_get_history_with_limit(self, session: ChatSession) -> None:
        """Test get_history() with limit."""
        await session.send("Turn 1")
        await session.send("Turn 2")
        await session.send("Turn 3")

        history = session.get_history(limit=2)
        assert len(history) == 2
        # Should be most recent
        assert history[0].turn_number == 2
        assert history[1].turn_number == 3

    @pytest.mark.asyncio
    async def test_get_messages_flattens_turns(self, session: ChatSession) -> None:
        """Test get_messages() returns flattened messages."""
        await session.send("Hello")

        messages = session.get_messages()
        assert len(messages) == 2  # user + assistant
        assert messages[0].role == "user"
        assert messages[1].role == "assistant"


# === ChatSession Metrics Tests ===


class TestChatSessionMetrics:
    """Tests for ChatSession.get_metrics()."""

    def test_metrics_empty_session(self, session: ChatSession) -> None:
        """Test metrics for empty session."""
        metrics = session.get_metrics()
        assert metrics["turns_completed"] == 0
        assert metrics["tokens_in"] == 0
        assert metrics["tokens_out"] == 0

    @pytest.mark.asyncio
    async def test_metrics_after_turns(self, session: ChatSession) -> None:
        """Test metrics after turns."""
        await session.send("Hello")
        await session.send("How are you?")

        metrics = session.get_metrics()
        assert metrics["turns_completed"] == 2
        assert metrics["tokens_in"] > 0
        assert metrics["entropy"] < 1.0


# === ChatSession Reset Tests ===


class TestChatSessionReset:
    """Tests for ChatSession.reset()."""

    @pytest.mark.asyncio
    async def test_reset_clears_history(self, session: ChatSession) -> None:
        """Test reset() clears turn history."""
        await session.send("Hello")
        assert session.turn_count == 1

        session.reset()
        assert session.turn_count == 0

    @pytest.mark.asyncio
    async def test_reset_restores_entropy(self, mock_observer: MagicMock) -> None:
        """Test reset() restores entropy."""
        config = ChatConfig(entropy_budget=1.0, entropy_decay_per_turn=0.2)
        session = ChatSession(
            session_id="test",
            node_path="self.soul",
            observer=mock_observer,
            config=config,
        )

        await session.send("Hello")
        assert session.entropy < 1.0

        session.reset()
        assert session.entropy == 1.0

    @pytest.mark.asyncio
    async def test_reset_sets_state_to_ready(self, session: ChatSession) -> None:
        """Test reset() sets state to READY."""
        await session.send("Hello")
        session.reset()
        assert session.state == ChatSessionState.READY


# === ChatSession Serialization Tests ===


class TestChatSessionSerialization:
    """Tests for ChatSession.to_dict()."""

    @pytest.mark.asyncio
    async def test_to_dict_includes_all_fields(self, session: ChatSession) -> None:
        """Test to_dict() includes all required fields."""
        await session.send("Hello")

        data = session.to_dict()
        assert "session_id" in data
        assert "node_path" in data
        assert "state" in data
        assert "turns" in data
        assert "entropy" in data
        assert "budget" in data

    def test_to_dict_empty_session(self, session: ChatSession) -> None:
        """Test to_dict() on empty session."""
        data = session.to_dict()
        assert data["turn_count"] == 0
        assert data["turns"] == []


# === Integration Tests ===


class TestChatSessionIntegration:
    """Integration tests for ChatSession."""

    @pytest.mark.asyncio
    async def test_full_conversation_flow(self, mock_observer: MagicMock) -> None:
        """Test a full conversation flow."""
        config = ChatConfig(
            max_turns=5,
            entropy_budget=1.0,
            entropy_decay_per_turn=0.1,
        )
        session = ChatSession(
            session_id="integration_test",
            node_path="self.soul",
            observer=mock_observer,
            config=config,
        )

        # Start conversation
        assert session.state == ChatSessionState.DORMANT

        # First turn
        response1 = await session.send("Hello")
        assert session.turn_count == 1
        assert session.state == ChatSessionState.WAITING

        # Second turn
        response2 = await session.send("How are you?")
        assert session.turn_count == 2

        # Check metrics
        metrics = session.get_metrics()
        assert metrics["turns_completed"] == 2
        assert metrics["entropy"] == 0.8

        # Reset and continue
        session.reset()
        assert session.turn_count == 0
        assert session.entropy == 1.0

        # Can continue after reset
        await session.send("New conversation")
        assert session.turn_count == 1

"""
Tests for ChatMorpheusComposer.

Per spec/protocols/chat-morpheus-synergy.md:
- Composition preserves both coalgebra states
- Transforms messages without re-parsing
- Maintains observer context throughout
- Graceful degradation on errors
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.chat.composer import (
    ChatMorpheusComposer,
    TurnResult,
    create_composer,
)
from services.chat.model_selector import MorpheusConfig


def _make_observer(archetype: str = "developer") -> MagicMock:
    """Create a mock observer umwelt."""
    observer = MagicMock()
    observer.meta.archetype = archetype
    observer.meta.name = "test_user"
    return observer


def _make_session(node_path: str = "self.soul") -> MagicMock:
    """Create a mock ChatSession."""
    session = MagicMock()
    session.node_path = node_path
    session.get_messages.return_value = []
    session.config.system_prompt = "You are a helpful assistant."
    return session


def _make_morpheus_result(content: str = "Hello!", tokens_in: int = 10, tokens_out: int = 5) -> MagicMock:
    """Create a mock CompletionResult."""
    result = MagicMock()
    result.response.choices = [MagicMock(message=MagicMock(content=content))]
    result.response.usage = MagicMock(
        prompt_tokens=tokens_in,
        completion_tokens=tokens_out,
    )
    result.latency_ms = 100.0
    return result


@pytest.fixture
def mock_morpheus() -> MagicMock:
    """Create mock MorpheusPersistence."""
    morpheus = MagicMock()
    morpheus.complete = AsyncMock()
    morpheus.stream = AsyncMock()
    return morpheus


@pytest.fixture
def composer(mock_morpheus: MagicMock) -> ChatMorpheusComposer:
    """Create ChatMorpheusComposer with mock Morpheus."""
    return ChatMorpheusComposer(morpheus=mock_morpheus)


class TestComposeTurn:
    """Tests for compose_turn method."""

    @pytest.mark.asyncio
    async def test_transforms_messages_without_parsing(
        self, composer: ChatMorpheusComposer, mock_morpheus: MagicMock
    ) -> None:
        """Verify we pass structured messages, not strings."""
        mock_morpheus.complete.return_value = _make_morpheus_result("Hello!")

        session = _make_session()
        observer = _make_observer()

        result = await composer.compose_turn(session, "Hi", observer)

        # Verify result
        assert result.content == "Hello!"
        assert result.tokens_in == 10
        assert result.tokens_out == 5
        assert result.latency_ms == 100.0

        # Verify Morpheus was called with ChatRequest, not string
        call_args = mock_morpheus.complete.call_args
        request = call_args[0][0]
        assert hasattr(request, "messages")
        assert request.messages[-1].content == "Hi"
        assert request.messages[-1].role == "user"

    @pytest.mark.asyncio
    async def test_observer_affects_model_selection(
        self, mock_morpheus: MagicMock
    ) -> None:
        """Verify different observers get different models."""
        composer = ChatMorpheusComposer(morpheus=mock_morpheus)

        # Guest observer
        guest = _make_observer(archetype="guest")
        config = composer.model_selector(guest, "self.soul")
        assert "haiku" in config.model.lower()

        # Developer observer
        dev = _make_observer(archetype="developer")
        config = composer.model_selector(dev, "self.soul")
        assert "sonnet" in config.model.lower()

        # System observer
        system = _make_observer(archetype="system")
        config = composer.model_selector(system, "self.soul")
        assert "opus" in config.model.lower()

    @pytest.mark.asyncio
    async def test_graceful_degradation_on_error(
        self, composer: ChatMorpheusComposer, mock_morpheus: MagicMock
    ) -> None:
        """Verify errors return graceful fallback."""
        mock_morpheus.complete.side_effect = Exception("LLM unavailable")

        session = _make_session()
        observer = _make_observer()

        result = await composer.compose_turn(session, "Hi", observer)

        assert "[LLM Error]" in result.content
        assert result.error is not None
        assert result.fallback is True
        assert result.tokens_in == 0
        assert result.tokens_out == 0

    @pytest.mark.asyncio
    async def test_returns_actual_token_counts(
        self, composer: ChatMorpheusComposer, mock_morpheus: MagicMock
    ) -> None:
        """Verify actual token counts from gateway are returned."""
        mock_morpheus.complete.return_value = _make_morpheus_result(
            content="Response",
            tokens_in=150,
            tokens_out=50,
        )

        session = _make_session()
        observer = _make_observer()

        result = await composer.compose_turn(session, "Question", observer)

        assert result.tokens_in == 150
        assert result.tokens_out == 50
        assert result.total_tokens == 200

    @pytest.mark.asyncio
    async def test_includes_system_prompt(
        self, composer: ChatMorpheusComposer, mock_morpheus: MagicMock
    ) -> None:
        """Verify system prompt is included in request."""
        mock_morpheus.complete.return_value = _make_morpheus_result()

        session = _make_session()
        session.config.system_prompt = "You are K-gent."
        observer = _make_observer()

        await composer.compose_turn(session, "Hi", observer)

        call_args = mock_morpheus.complete.call_args
        request = call_args[0][0]

        # First message should be system
        assert request.messages[0].role == "system"
        assert "K-gent" in request.messages[0].content

    @pytest.mark.asyncio
    async def test_includes_context_messages(
        self, composer: ChatMorpheusComposer, mock_morpheus: MagicMock
    ) -> None:
        """Verify conversation context is included."""
        mock_morpheus.complete.return_value = _make_morpheus_result()

        session = _make_session()
        # Simulate existing conversation
        from services.chat.session import Message
        session.get_messages.return_value = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi there!"),
        ]
        observer = _make_observer()

        await composer.compose_turn(session, "How are you?", observer)

        call_args = mock_morpheus.complete.call_args
        request = call_args[0][0]

        # Should have: system + 2 context messages + new user message = 4
        assert len(request.messages) == 4


class TestComposeStream:
    """Tests for streaming composition."""

    @pytest.mark.asyncio
    async def test_yields_tokens_from_morpheus(
        self, composer: ChatMorpheusComposer, mock_morpheus: MagicMock
    ) -> None:
        """Verify tokens are yielded as they arrive."""
        # Setup mock streaming
        async def mock_stream(*args, **kwargs):
            for word in ["Hello", " ", "world", "!"]:
                chunk = MagicMock()
                chunk.choices = [MagicMock(delta=MagicMock(content=word))]
                yield chunk

        mock_morpheus.stream = mock_stream

        session = _make_session()
        observer = _make_observer()

        tokens = []
        async for token in composer.compose_stream(session, "Hi", observer):
            tokens.append(token)

        assert tokens == ["Hello", " ", "world", "!"]

    @pytest.mark.asyncio
    async def test_stream_error_yields_error_message(
        self, composer: ChatMorpheusComposer, mock_morpheus: MagicMock
    ) -> None:
        """Verify streaming errors yield error message."""
        async def mock_stream_error(*args, **kwargs):
            yield MagicMock(choices=[MagicMock(delta=MagicMock(content="Start"))])
            raise Exception("Stream interrupted")

        mock_morpheus.stream = mock_stream_error

        session = _make_session()
        observer = _make_observer()

        tokens = []
        async for token in composer.compose_stream(session, "Hi", observer):
            tokens.append(token)

        assert "Start" in tokens
        assert any("[Streaming Error]" in t for t in tokens)


class TestTurnResult:
    """Tests for TurnResult dataclass."""

    def test_success_property(self) -> None:
        """Success is True when no error."""
        result = TurnResult(content="Hello", tokens_in=10, tokens_out=5)
        assert result.success is True

        result_with_error = TurnResult(content="Error", error="Something failed")
        assert result_with_error.success is False

    def test_total_tokens(self) -> None:
        """Total tokens sums in and out."""
        result = TurnResult(content="Hello", tokens_in=100, tokens_out=50)
        assert result.total_tokens == 150


class TestCreateComposer:
    """Tests for create_composer factory function."""

    def test_creates_with_default_selector(self, mock_morpheus: MagicMock) -> None:
        """Factory creates composer with default model selector."""
        composer = create_composer(mock_morpheus)

        assert composer.morpheus is mock_morpheus
        # Should use default selector
        observer = _make_observer(archetype="guest")
        config = composer.model_selector(observer, "test")
        assert "haiku" in config.model.lower()

    def test_creates_with_custom_selector(self, mock_morpheus: MagicMock) -> None:
        """Factory accepts custom model selector."""
        custom_selector = MagicMock(return_value=MorpheusConfig(model="custom"))
        composer = create_composer(mock_morpheus, model_selector=custom_selector)

        config = composer.model_selector(MagicMock(), "test")
        assert config.model == "custom"

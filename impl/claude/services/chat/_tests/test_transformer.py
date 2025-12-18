"""
Tests for Chat-Morpheus transform functions.

Per spec/protocols/chat-morpheus-synergy.md Part II §2.3:
Transform functions are natural transformations between Chat and Morpheus categories.
"""

from unittest.mock import MagicMock

import pytest

from services.chat.model_selector import MorpheusConfig
from services.chat.session import Message
from services.chat.transformer import (
    extract_usage,
    from_morpheus_response,
    to_morpheus_request,
    to_streaming_request,
)


@pytest.fixture
def config() -> MorpheusConfig:
    """Create test MorpheusConfig."""
    return MorpheusConfig(
        model="claude-sonnet-4-20250514",
        temperature=0.7,
        max_tokens=4096,
    )


class TestToMorpheusRequest:
    """Tests for to_morpheus_request transform."""

    def test_creates_request_with_user_message(self, config: MorpheusConfig) -> None:
        """Basic transform adds user message."""
        request = to_morpheus_request([], "Hello!", config)

        assert request.model == "claude-sonnet-4-20250514"
        assert request.temperature == 0.7
        assert request.max_tokens == 4096
        assert len(request.messages) == 1
        assert request.messages[0].role == "user"
        assert request.messages[0].content == "Hello!"

    def test_includes_context_messages(self, config: MorpheusConfig) -> None:
        """Transform preserves conversation context."""
        context = [
            Message(role="user", content="Hi"),
            Message(role="assistant", content="Hello!"),
        ]

        request = to_morpheus_request(context, "How are you?", config)

        assert len(request.messages) == 3
        assert request.messages[0].role == "user"
        assert request.messages[0].content == "Hi"
        assert request.messages[1].role == "assistant"
        assert request.messages[1].content == "Hello!"
        assert request.messages[2].role == "user"
        assert request.messages[2].content == "How are you?"

    def test_includes_system_prompt(self, config: MorpheusConfig) -> None:
        """Transform prepends system prompt."""
        request = to_morpheus_request(
            [],
            "Hello!",
            config,
            system_prompt="You are K-gent.",
        )

        assert len(request.messages) == 2
        assert request.messages[0].role == "system"
        assert request.messages[0].content == "You are K-gent."
        assert request.messages[1].role == "user"
        assert request.messages[1].content == "Hello!"

    def test_maps_unknown_roles_to_user(self, config: MorpheusConfig) -> None:
        """Unknown roles default to user."""
        context = [Message(role="tool", content="Tool output")]

        request = to_morpheus_request(context, "Continue", config)

        assert request.messages[0].role == "user"
        assert request.messages[0].content == "Tool output"

    def test_no_stream_by_default(self, config: MorpheusConfig) -> None:
        """Default request is not streaming."""
        request = to_morpheus_request([], "Hello!", config)

        assert request.stream is False


class TestFromMorpheusResponse:
    """Tests for from_morpheus_response transform."""

    def test_extracts_content(self) -> None:
        """Extract content from result."""
        result = MagicMock()
        result.response.choices = [MagicMock(message=MagicMock(content="Hello from Claude!"))]

        content = from_morpheus_response(result)

        assert content == "Hello from Claude!"

    def test_empty_choices_returns_empty_string(self) -> None:
        """Empty choices return empty string."""
        result = MagicMock()
        result.response.choices = []

        content = from_morpheus_response(result)

        assert content == ""


class TestExtractUsage:
    """Tests for extract_usage transform."""

    def test_extracts_token_counts(self) -> None:
        """Extract token counts from result."""
        result = MagicMock()
        result.response.usage = MagicMock(
            prompt_tokens=100,
            completion_tokens=50,
        )

        tokens_in, tokens_out = extract_usage(result)

        assert tokens_in == 100
        assert tokens_out == 50

    def test_no_usage_returns_zeros(self) -> None:
        """Missing usage returns zeros."""
        result = MagicMock()
        result.response.usage = None

        tokens_in, tokens_out = extract_usage(result)

        assert tokens_in == 0
        assert tokens_out == 0


class TestToStreamingRequest:
    """Tests for streaming request transform."""

    def test_creates_streaming_request(self, config: MorpheusConfig) -> None:
        """Streaming request has stream=True."""
        request = to_streaming_request([], "Hello!", config)

        assert request.stream is True
        assert request.model == config.model

    def test_includes_all_transform_features(self, config: MorpheusConfig) -> None:
        """Streaming request includes context and system prompt."""
        context = [Message(role="user", content="Previous")]
        request = to_streaming_request(
            context,
            "Current",
            config,
            system_prompt="System",
        )

        assert request.stream is True
        assert len(request.messages) == 3
        assert request.messages[0].role == "system"
        assert request.messages[1].content == "Previous"
        assert request.messages[2].content == "Current"

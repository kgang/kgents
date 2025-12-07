"""Tests for runtime/messages.py"""

import pytest

from runtime.messages import (
    Message,
    TokenUsage,
    CompletionResult,
    user,
    assistant,
    system,
)


class TestMessage:
    def test_user_message(self):
        msg = user("Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_assistant_message(self):
        msg = assistant("Hi there")
        assert msg.role == "assistant"
        assert msg.content == "Hi there"

    def test_system_message(self):
        msg = system("You are helpful")
        assert msg.role == "system"
        assert msg.content == "You are helpful"

    def test_message_is_frozen(self):
        msg = Message(role="user", content="test")
        with pytest.raises(AttributeError):
            msg.content = "changed"


class TestTokenUsage:
    def test_total_tokens(self):
        usage = TokenUsage(input_tokens=100, output_tokens=50)
        assert usage.total_tokens == 150

    def test_frozen(self):
        usage = TokenUsage(input_tokens=10, output_tokens=5)
        with pytest.raises(AttributeError):
            usage.input_tokens = 20


class TestCompletionResult:
    def test_creation(self):
        usage = TokenUsage(input_tokens=10, output_tokens=20)
        result = CompletionResult(
            content="Hello",
            model="claude-sonnet-4",
            usage=usage,
        )
        assert result.content == "Hello"
        assert result.model == "claude-sonnet-4"
        assert result.cached is False

    def test_repr(self):
        usage = TokenUsage(input_tokens=10, output_tokens=20)
        result = CompletionResult(content="Hi", model="test", usage=usage)
        assert "tokens=30" in repr(result)

    def test_cached_repr(self):
        usage = TokenUsage(input_tokens=10, output_tokens=20)
        result = CompletionResult(content="Hi", model="test", usage=usage, cached=True)
        assert "(cached)" in repr(result)

"""Tests for Morpheus Gateway types."""

import pytest
from infra.morpheus.types import (
    ChatChoice,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    MorpheusError,
    Usage,
)


class TestChatMessage:
    """Tests for ChatMessage."""

    def test_user_message(self) -> None:
        """Test creating a user message."""
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.name is None

    def test_system_message(self) -> None:
        """Test creating a system message."""
        msg = ChatMessage(role="system", content="You are helpful.")
        assert msg.role == "system"
        assert msg.content == "You are helpful."

    def test_to_dict(self) -> None:
        """Test converting to dict."""
        msg = ChatMessage(role="user", content="Hello")
        d = msg.to_dict()
        assert d == {"role": "user", "content": "Hello"}

    def test_to_dict_with_name(self) -> None:
        """Test to_dict includes name when present."""
        msg = ChatMessage(role="assistant", content="Hi", name="helper")
        d = msg.to_dict()
        assert d == {"role": "assistant", "content": "Hi", "name": "helper"}


class TestChatRequest:
    """Tests for ChatRequest."""

    def test_from_dict_minimal(self) -> None:
        """Test creating from minimal dict."""
        data = {
            "model": "claude-sonnet",
            "messages": [{"role": "user", "content": "Hello"}],
        }
        req = ChatRequest.from_dict(data)
        assert req.model == "claude-sonnet"
        assert len(req.messages) == 1
        assert req.messages[0].content == "Hello"
        assert req.temperature == 0.7  # default

    def test_from_dict_full(self) -> None:
        """Test creating from full dict."""
        data = {
            "model": "claude-opus",
            "messages": [
                {"role": "system", "content": "Be helpful."},
                {"role": "user", "content": "Hello"},
            ],
            "temperature": 0.5,
            "max_tokens": 2000,
            "stream": False,
        }
        req = ChatRequest.from_dict(data)
        assert req.model == "claude-opus"
        assert len(req.messages) == 2
        assert req.temperature == 0.5
        assert req.max_tokens == 2000

    def test_defaults(self) -> None:
        """Test default values."""
        req = ChatRequest(
            model="test",
            messages=[ChatMessage(role="user", content="Hi")],
        )
        assert req.temperature == 0.7
        assert req.max_tokens == 4096
        assert req.stream is False
        assert req.n == 1


class TestChatResponse:
    """Tests for ChatResponse."""

    def test_from_text(self) -> None:
        """Test creating response from text."""
        resp = ChatResponse.from_text(
            text="Hello there!",
            model="claude-sonnet",
            prompt_tokens=10,
            completion_tokens=5,
        )
        assert resp.model == "claude-sonnet"
        assert len(resp.choices) == 1
        assert resp.choices[0].message.content == "Hello there!"
        assert resp.choices[0].finish_reason == "stop"
        assert resp.usage is not None
        assert resp.usage.total_tokens == 15

    def test_to_dict(self) -> None:
        """Test converting to dict."""
        resp = ChatResponse.from_text(
            text="Hi",
            model="test-model",
            prompt_tokens=5,
            completion_tokens=2,
        )
        d = resp.to_dict()
        assert d["model"] == "test-model"
        assert d["object"] == "chat.completion"
        assert "id" in d
        assert "created" in d
        assert len(d["choices"]) == 1
        assert d["choices"][0]["message"]["content"] == "Hi"
        assert d["usage"]["total_tokens"] == 7


class TestUsage:
    """Tests for Usage."""

    def test_to_dict(self) -> None:
        """Test converting to dict."""
        usage = Usage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        d = usage.to_dict()
        assert d == {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        }


class TestMorpheusError:
    """Tests for MorpheusError."""

    def test_to_dict(self) -> None:
        """Test error dict format."""
        err = MorpheusError(
            message="Model not found",
            type="invalid_request_error",
        )
        d = err.to_dict()
        assert d == {
            "error": {
                "message": "Model not found",
                "type": "invalid_request_error",
            }
        }

    def test_to_dict_with_code(self) -> None:
        """Test error dict with code."""
        err = MorpheusError(
            message="Rate limit exceeded",
            type="rate_limit_error",
            code="rate_limit",
        )
        d = err.to_dict()
        assert d["error"]["code"] == "rate_limit"

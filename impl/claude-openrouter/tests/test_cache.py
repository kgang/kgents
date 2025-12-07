"""Tests for runtime/cache.py"""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from runtime.cache import ResponseCache, get_cache, reset_cache
from runtime.config import RuntimeConfig
from runtime.messages import Message, TokenUsage, CompletionResult


class TestResponseCache:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = RuntimeConfig(
            cache_dir=Path(self.temp_dir),
            enable_cache=True,
            cache_ttl_seconds=3600,
        )
        self.cache = ResponseCache(self.config)

    def test_cache_miss(self):
        messages = [Message(role="user", content="Hello")]
        result = self.cache.get(messages, "test-model")
        assert result is None

    def test_cache_hit(self):
        messages = [Message(role="user", content="Hello")]
        original = CompletionResult(
            content="Hi there",
            model="test-model",
            usage=TokenUsage(10, 20),
        )

        self.cache.set(messages, "test-model", original)
        cached = self.cache.get(messages, "test-model")

        assert cached is not None
        assert cached.content == "Hi there"
        assert cached.cached is True

    def test_cache_with_system(self):
        messages = [Message(role="user", content="Hello")]
        original = CompletionResult(
            content="Response",
            model="test-model",
            usage=TokenUsage(10, 20),
        )

        self.cache.set(messages, "test-model", original, system="Be helpful")
        cached = self.cache.get(messages, "test-model", system="Be helpful")

        assert cached is not None
        assert cached.content == "Response"

    def test_cache_different_system(self):
        messages = [Message(role="user", content="Hello")]
        original = CompletionResult(
            content="Response",
            model="test-model",
            usage=TokenUsage(10, 20),
        )

        self.cache.set(messages, "test-model", original, system="System A")
        cached = self.cache.get(messages, "test-model", system="System B")

        assert cached is None

    def test_cache_disabled(self):
        config = RuntimeConfig(
            cache_dir=Path(self.temp_dir),
            enable_cache=False,
        )
        cache = ResponseCache(config)

        messages = [Message(role="user", content="Hello")]
        original = CompletionResult(
            content="Response",
            model="test-model",
            usage=TokenUsage(10, 20),
        )

        cache.set(messages, "test-model", original)
        cached = cache.get(messages, "test-model")

        assert cached is None

    def test_clear(self):
        messages = [Message(role="user", content="Hello")]
        original = CompletionResult(
            content="Response",
            model="test-model",
            usage=TokenUsage(10, 20),
        )

        self.cache.set(messages, "test-model", original)
        count = self.cache.clear()

        assert count == 1
        assert self.cache.get(messages, "test-model") is None

    def test_clear_expired(self):
        messages = [Message(role="user", content="Hello")]
        original = CompletionResult(
            content="Response",
            model="test-model",
            usage=TokenUsage(10, 20),
        )

        # Set with 0 TTL (immediately expired)
        config = RuntimeConfig(
            cache_dir=Path(self.temp_dir),
            enable_cache=True,
            cache_ttl_seconds=0,
        )
        cache = ResponseCache(config)
        cache.set(messages, "test-model", original)

        count = cache.clear_expired()
        assert count == 1


class TestGetCache:
    def setup_method(self):
        reset_cache()

    def test_singleton(self):
        c1 = get_cache()
        c2 = get_cache()
        assert c1 is c2

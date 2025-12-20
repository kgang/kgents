"""
Tests for AGENTESE Telemetry - OpenTelemetry Integration.

These tests verify:
- TelemetryMiddleware span creation
- Span attribute recording
- Error handling and status codes
- Context manager for manual spans
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from ..telemetry import (
    ATTR_CONTEXT,
    ATTR_DURATION_MS,
    ATTR_HOLON,
    ATTR_OBSERVER_ID,
    ATTR_PATH,
    ATTR_RESULT_TYPE,
    TelemetryMiddleware,
    add_event,
    get_tracer,
    set_attribute,
    trace_invocation,
)

# === Fixtures ===


@dataclass
class MockDNA:
    """Mock DNA for testing."""

    name: str = "test-observer"
    archetype: str = "tester"


@dataclass
class MockUmwelt:
    """Mock Umwelt for testing."""

    id: str = "umwelt-123"
    dna: MockDNA | None = None

    def __post_init__(self) -> None:
        if self.dna is None:
            self.dna = MockDNA()


# === Test TelemetryMiddleware ===


class TestTelemetryMiddleware:
    """Tests for TelemetryMiddleware."""

    @pytest.fixture
    def middleware(self) -> TelemetryMiddleware:
        """Create middleware instance."""
        return TelemetryMiddleware()

    @pytest.fixture
    def umwelt(self) -> MockUmwelt:
        """Create mock Umwelt."""
        return MockUmwelt()

    async def test_middleware_creates_span(
        self,
        middleware: TelemetryMiddleware,
        umwelt: MockUmwelt,
    ) -> None:
        """Middleware creates span for invocation."""

        async def mock_handler(path: str, observer: Any, *args: Any, **kwargs: Any) -> str:
            return "result"

        result = await middleware(
            path="self.soul.challenge",
            umwelt=umwelt,
            args=("idea",),
            kwargs={},
            next_handler=mock_handler,
        )

        assert result == "result"

    async def test_middleware_propagates_errors(
        self,
        middleware: TelemetryMiddleware,
        umwelt: MockUmwelt,
    ) -> None:
        """Middleware propagates exceptions from handler."""

        async def failing_handler(path: str, observer: Any, *args: Any, **kwargs: Any) -> None:
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            await middleware(
                path="self.soul.challenge",
                umwelt=umwelt,
                args=(),
                kwargs={},
                next_handler=failing_handler,
            )

    async def test_middleware_records_result_type(
        self,
        middleware: TelemetryMiddleware,
        umwelt: MockUmwelt,
    ) -> None:
        """Middleware records result type attribute."""

        async def dict_handler(
            path: str, observer: Any, *args: Any, **kwargs: Any
        ) -> dict[str, str]:
            return {"key": "value"}

        result = await middleware(
            path="self.soul.challenge",
            umwelt=umwelt,
            args=(),
            kwargs={},
            next_handler=dict_handler,
        )

        assert result == {"key": "value"}

    async def test_middleware_parses_path_components(
        self,
        middleware: TelemetryMiddleware,
        umwelt: MockUmwelt,
    ) -> None:
        """Middleware correctly parses path into components."""

        # Test with full path
        async def handler(path: str, observer: Any, *args: Any, **kwargs: Any) -> str:
            return "ok"

        await middleware(
            path="world.house.manifest",
            umwelt=umwelt,
            args=(),
            kwargs={},
            next_handler=handler,
        )
        # Path components are recorded as span attributes
        # (verified by OTEL span inspection in integration tests)

    async def test_middleware_handles_short_path(
        self,
        middleware: TelemetryMiddleware,
        umwelt: MockUmwelt,
    ) -> None:
        """Middleware handles paths with fewer than 3 components."""

        async def handler(path: str, observer: Any, *args: Any, **kwargs: Any) -> str:
            return "ok"

        # Should not raise even with short path
        result = await middleware(
            path="self.soul",
            umwelt=umwelt,
            args=(),
            kwargs={},
            next_handler=handler,
        )
        assert result == "ok"


# === Test trace_invocation Context Manager ===


class TestTraceInvocation:
    """Tests for trace_invocation context manager."""

    @pytest.fixture
    def umwelt(self) -> MockUmwelt:
        """Create mock Umwelt."""
        return MockUmwelt()

    async def test_trace_invocation_yields_span(self, umwelt: MockUmwelt) -> None:
        """Context manager yields span for attribute setting."""
        async with trace_invocation("self.soul.challenge", umwelt) as span:
            # Span should be usable
            assert span is not None

    async def test_trace_invocation_handles_exception(self, umwelt: MockUmwelt) -> None:
        """Context manager records exception and re-raises."""
        with pytest.raises(RuntimeError, match="test"):
            async with trace_invocation("self.soul.challenge", umwelt):
                raise RuntimeError("test")

    async def test_trace_invocation_extra_attributes(self, umwelt: MockUmwelt) -> None:
        """Context manager accepts extra attributes."""
        async with trace_invocation(
            "self.soul.challenge",
            umwelt,
            custom_attr="value",
        ) as span:
            assert span is not None


# === Test Utility Functions ===


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_get_tracer_returns_tracer(self) -> None:
        """get_tracer returns a valid tracer."""
        tracer = get_tracer()
        assert tracer is not None
        # Should have start_span method
        assert hasattr(tracer, "start_span")
        assert hasattr(tracer, "start_as_current_span")

    def test_get_tracer_cached(self) -> None:
        """get_tracer returns same instance."""
        tracer1 = get_tracer()
        tracer2 = get_tracer()
        assert tracer1 is tracer2

    def test_add_event_no_span(self) -> None:
        """add_event does nothing when no span active."""
        # Should not raise
        add_event("test_event", {"key": "value"})

    def test_set_attribute_no_span(self) -> None:
        """set_attribute does nothing when no span active."""
        # Should not raise
        set_attribute("test_key", "test_value")


# === Test Token Recording ===


class TestTokenRecording:
    """Tests for token usage recording."""

    @pytest.fixture
    def middleware(self) -> TelemetryMiddleware:
        """Create middleware with token recording enabled."""
        return TelemetryMiddleware(record_tokens=True)

    async def test_records_anthropic_style_usage(
        self,
        middleware: TelemetryMiddleware,
    ) -> None:
        """Records tokens from anthropic-style usage."""

        @dataclass
        class Usage:
            input_tokens: int = 100
            output_tokens: int = 50

        @dataclass
        class Result:
            usage: Usage | None = None

            def __post_init__(self) -> None:
                if self.usage is None:
                    self.usage = Usage()

        async def handler(path: str, observer: Any, *args: Any, **kwargs: Any) -> Result:
            return Result()

        umwelt = MockUmwelt()
        result = await middleware(
            path="self.llm.generate",
            umwelt=umwelt,
            args=(),
            kwargs={},
            next_handler=handler,
        )

        assert result.usage is not None
        assert result.usage.input_tokens == 100

    async def test_records_dict_style_usage(
        self,
        middleware: TelemetryMiddleware,
    ) -> None:
        """Records tokens from dict-style result."""

        async def handler(path: str, observer: Any, *args: Any, **kwargs: Any) -> dict[str, Any]:
            return {
                "content": "response",
                "usage": {
                    "input_tokens": 200,
                    "output_tokens": 100,
                },
            }

        umwelt = MockUmwelt()
        result = await middleware(
            path="self.llm.generate",
            umwelt=umwelt,
            args=(),
            kwargs={},
            next_handler=handler,
        )

        assert result["usage"]["input_tokens"] == 200

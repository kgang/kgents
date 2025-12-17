"""
Tests for Chat Observability (Phase 5).

Tests:
- ChatTelemetry context managers
- Metrics recording functions
- Summary aggregation
- Span attribute verification
- Error handling
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from protocols.agentese.chat.config import ChatConfig
from protocols.agentese.chat.observability import (
    ATTR_CONTEXT_UTILIZATION,
    ATTR_NODE_PATH,
    ATTR_SESSION_ID,
    ATTR_TOKENS_IN,
    ATTR_TOKENS_OUT,
    ATTR_TURN_NUMBER,
    ChatMetricsState,
    ChatTelemetry,
    get_active_session_count,
    get_chat_meter,
    get_chat_metrics_summary,
    get_chat_tracer,
    record_error,
    record_session_event,
    record_turn,
    reset_chat_metrics,
)
from protocols.agentese.chat.session import (
    ChatSession,
    ChatSessionState,
    Message,
    Turn,
)

# =============================================================================
# Fixtures
# =============================================================================


@dataclass
class MockObserver:
    """Mock observer for tests."""

    id: str = "test-observer-123"
    archetype: str = "user"


@dataclass
class MockUmwelt:
    """Mock umwelt for tests."""

    id: str = "test-umwelt"


@pytest.fixture
def mock_session() -> ChatSession:
    """Create a mock ChatSession for testing."""
    observer = MockUmwelt()
    session = ChatSession(
        session_id="test-session-abc",
        node_path="self.soul",
        observer=observer,
        config=ChatConfig(),
    )
    session.activate()
    return session


@pytest.fixture
def mock_session_with_turns(mock_session: ChatSession) -> ChatSession:
    """Create a mock session with pre-populated turns."""
    # Add a few mock turns
    for i in range(3):
        turn = Turn(
            turn_number=i + 1,
            user_message=Message(role="user", content=f"Message {i}"),
            assistant_response=Message(role="assistant", content=f"Response {i}"),
            started_at=datetime.now(),
            completed_at=datetime.now(),
            tokens_in=50 + i * 10,
            tokens_out=100 + i * 20,
            context_before=200 * i,
            context_after=200 * (i + 1),
        )
        mock_session._turns.append(turn)
        mock_session._budget.record_turn(turn)

    mock_session._current_turn = 3
    return mock_session


@pytest.fixture(autouse=True)
def reset_metrics_state():
    """Reset metrics state before each test."""
    reset_chat_metrics()
    yield
    reset_chat_metrics()


# =============================================================================
# Test: Tracer and Meter Singletons
# =============================================================================


class TestTracerMeterSingletons:
    """Tests for tracer and meter singleton access."""

    def test_get_chat_tracer_returns_tracer(self):
        """get_chat_tracer returns a valid tracer."""
        tracer = get_chat_tracer()
        assert tracer is not None
        # Call again - should be cached
        tracer2 = get_chat_tracer()
        assert tracer is tracer2

    def test_get_chat_meter_returns_meter(self):
        """get_chat_meter returns a valid meter."""
        meter = get_chat_meter()
        assert meter is not None
        # Call again - should be cached
        meter2 = get_chat_meter()
        assert meter is meter2


# =============================================================================
# Test: Record Turn
# =============================================================================


class TestRecordTurn:
    """Tests for record_turn function."""

    def test_record_turn_basic(self):
        """record_turn updates metrics state."""
        record_turn(
            node_path="self.soul",
            turn_number=1,
            duration_s=1.5,
            tokens_in=100,
            tokens_out=200,
            success=True,
        )

        summary = get_chat_metrics_summary()
        assert summary["total_turns"] == 1
        assert summary["total_tokens_in"] == 100
        assert summary["total_tokens_out"] == 200
        assert summary["total_duration_s"] > 0

    def test_record_turn_multiple(self):
        """record_turn accumulates across calls."""
        for i in range(5):
            record_turn(
                node_path="self.soul",
                turn_number=i + 1,
                duration_s=0.5,
                tokens_in=50,
                tokens_out=100,
                success=True,
            )

        summary = get_chat_metrics_summary()
        assert summary["total_turns"] == 5
        assert summary["total_tokens_in"] == 250
        assert summary["total_tokens_out"] == 500

    def test_record_turn_with_error(self):
        """record_turn tracks errors."""
        record_turn(
            node_path="self.soul",
            turn_number=1,
            duration_s=0.5,
            tokens_in=100,
            tokens_out=0,
            success=False,
        )

        summary = get_chat_metrics_summary()
        assert summary["total_turns"] == 1
        assert summary["total_errors"] == 1
        assert summary["error_rate"] == 1.0

    def test_record_turn_by_node(self):
        """record_turn tracks metrics by node path."""
        record_turn(
            node_path="self.soul",
            turn_number=1,
            duration_s=0.5,
            tokens_in=100,
            tokens_out=200,
            success=True,
        )
        record_turn(
            node_path="world.town.citizen.elara",
            turn_number=1,
            duration_s=0.3,
            tokens_in=50,
            tokens_out=100,
            success=True,
        )

        summary = get_chat_metrics_summary()
        assert summary["top_nodes_by_turns"]["self.soul"] == 1
        assert summary["top_nodes_by_turns"]["world.town.citizen.elara"] == 1

    def test_record_turn_with_context_utilization(self):
        """record_turn records context utilization."""
        record_turn(
            node_path="self.soul",
            turn_number=1,
            duration_s=0.5,
            tokens_in=100,
            tokens_out=200,
            success=True,
            context_utilization=0.75,
        )

        summary = get_chat_metrics_summary()
        assert summary["total_turns"] == 1

    def test_record_turn_with_cost(self):
        """record_turn tracks estimated cost."""
        record_turn(
            node_path="self.soul",
            turn_number=1,
            duration_s=0.5,
            tokens_in=100,
            tokens_out=200,
            success=True,
            estimated_cost_usd=0.001,
        )

        summary = get_chat_metrics_summary()
        assert summary["total_cost_usd"] == 0.001


# =============================================================================
# Test: Record Session Event
# =============================================================================


class TestRecordSessionEvent:
    """Tests for record_session_event function."""

    def test_record_session_started(self):
        """record_session_event tracks session starts."""
        record_session_event("self.soul", "started")

        summary = get_chat_metrics_summary()
        assert summary["total_sessions"] == 1
        assert summary["active_sessions"]["self.soul"] == 1

    def test_record_session_ended(self):
        """record_session_event tracks session ends."""
        record_session_event("self.soul", "started")
        record_session_event("self.soul", "ended")

        summary = get_chat_metrics_summary()
        assert summary["total_sessions"] == 1
        assert summary["active_sessions"]["self.soul"] == 0

    def test_record_session_collapsed(self):
        """record_session_event handles collapsed sessions."""
        record_session_event("self.soul", "started")
        record_session_event("self.soul", "collapsed")

        summary = get_chat_metrics_summary()
        assert summary["active_sessions"]["self.soul"] == 0

    def test_record_multiple_sessions(self):
        """record_session_event tracks multiple sessions."""
        record_session_event("self.soul", "started")
        record_session_event("self.soul", "started")
        record_session_event("world.town.citizen.elara", "started")

        summary = get_chat_metrics_summary()
        assert summary["total_sessions"] == 3
        assert summary["sessions_by_node"]["self.soul"] == 2
        assert summary["sessions_by_node"]["world.town.citizen.elara"] == 1
        assert summary["active_sessions"]["self.soul"] == 2


# =============================================================================
# Test: Record Error
# =============================================================================


class TestRecordError:
    """Tests for record_error function."""

    def test_record_error_basic(self):
        """record_error tracks errors."""
        record_error("self.soul", "RuntimeError")

        summary = get_chat_metrics_summary()
        assert summary["total_errors"] == 1

    def test_record_error_multiple(self):
        """record_error accumulates errors."""
        record_error("self.soul", "RuntimeError")
        record_error("self.soul", "ValueError")
        record_error("world.town.citizen.elara", "RuntimeError")

        summary = get_chat_metrics_summary()
        assert summary["total_errors"] == 3


# =============================================================================
# Test: Get Active Session Count
# =============================================================================


class TestGetActiveSessionCount:
    """Tests for get_active_session_count function."""

    def test_get_active_session_count_empty(self):
        """get_active_session_count returns 0 when no sessions."""
        assert get_active_session_count() == 0

    def test_get_active_session_count_all(self):
        """get_active_session_count returns total when no path filter."""
        record_session_event("self.soul", "started")
        record_session_event("world.town.citizen.elara", "started")

        assert get_active_session_count() == 2

    def test_get_active_session_count_filtered(self):
        """get_active_session_count filters by node path."""
        record_session_event("self.soul", "started")
        record_session_event("self.soul", "started")
        record_session_event("world.town.citizen.elara", "started")

        assert get_active_session_count("self.soul") == 2
        assert get_active_session_count("world.town.citizen.elara") == 1
        assert get_active_session_count("nonexistent") == 0


# =============================================================================
# Test: Metrics Summary
# =============================================================================


class TestMetricsSummary:
    """Tests for get_chat_metrics_summary function."""

    def test_summary_empty(self):
        """get_chat_metrics_summary returns empty state correctly."""
        summary = get_chat_metrics_summary()

        assert summary["total_turns"] == 0
        assert summary["total_sessions"] == 0
        assert summary["total_errors"] == 0
        assert summary["error_rate"] == 0.0
        assert summary["total_tokens_in"] == 0
        assert summary["total_tokens_out"] == 0
        assert summary["avg_tokens_per_turn"] == 0.0
        assert summary["avg_turn_duration_s"] == 0.0

    def test_summary_comprehensive(self):
        """get_chat_metrics_summary aggregates all metrics."""
        # Record some activity
        record_session_event("self.soul", "started")
        record_turn("self.soul", 1, 1.0, 100, 200, True, 0.5, 0.001)
        record_turn("self.soul", 2, 0.8, 80, 160, True, 0.6, 0.0008)
        record_turn("self.soul", 3, 0.5, 50, 100, False, 0.7, 0.0005)

        summary = get_chat_metrics_summary()

        assert summary["total_turns"] == 3
        assert summary["total_sessions"] == 1
        assert summary["total_errors"] == 1
        assert abs(summary["error_rate"] - 0.333) < 0.01
        assert summary["total_tokens_in"] == 230
        assert summary["total_tokens_out"] == 460
        assert summary["total_tokens"] == 690
        assert summary["avg_tokens_per_turn"] == 230.0
        assert abs(summary["total_duration_s"] - 2.3) < 0.01
        assert abs(summary["avg_turn_duration_s"] - 0.767) < 0.01

    def test_summary_top_nodes(self):
        """get_chat_metrics_summary identifies top nodes."""
        # Soul with 5 turns
        for i in range(5):
            record_turn("self.soul", i + 1, 0.5, 50, 100, True)

        # Citizen with 3 turns
        for i in range(3):
            record_turn("world.town.citizen.elara", i + 1, 0.5, 50, 100, True)

        summary = get_chat_metrics_summary()

        top_nodes = summary["top_nodes_by_turns"]
        assert top_nodes["self.soul"] == 5
        assert top_nodes["world.town.citizen.elara"] == 3


# =============================================================================
# Test: Reset Metrics
# =============================================================================


class TestResetMetrics:
    """Tests for reset_chat_metrics function."""

    def test_reset_clears_state(self):
        """reset_chat_metrics clears all in-memory state."""
        # Add some data
        record_session_event("self.soul", "started")
        record_turn("self.soul", 1, 1.0, 100, 200, True)
        record_error("self.soul", "RuntimeError")

        # Verify data exists
        assert get_chat_metrics_summary()["total_turns"] > 0

        # Reset
        reset_chat_metrics()

        # Verify cleared
        summary = get_chat_metrics_summary()
        assert summary["total_turns"] == 0
        assert summary["total_sessions"] == 0
        assert summary["total_errors"] == 0


# =============================================================================
# Test: ChatTelemetry
# =============================================================================


class TestChatTelemetry:
    """Tests for ChatTelemetry class."""

    @pytest.fixture
    def telemetry(self) -> ChatTelemetry:
        """Create a ChatTelemetry instance."""
        return ChatTelemetry()

    @pytest.mark.asyncio
    async def test_trace_session_basic(
        self, telemetry: ChatTelemetry, mock_session: ChatSession
    ):
        """trace_session creates a session span."""
        async with telemetry.trace_session(mock_session) as span:
            assert span is not None
            # Session event recorded
            summary = get_chat_metrics_summary()
            assert summary["total_sessions"] == 1
            assert summary["active_sessions"]["self.soul"] == 1

        # After context exit, session ended
        summary = get_chat_metrics_summary()
        assert summary["active_sessions"]["self.soul"] == 0

    @pytest.mark.asyncio
    async def test_trace_session_with_error(
        self, telemetry: ChatTelemetry, mock_session: ChatSession
    ):
        """trace_session handles errors gracefully."""
        with pytest.raises(ValueError):
            async with telemetry.trace_session(mock_session) as span:
                raise ValueError("Test error")

        # Error recorded
        summary = get_chat_metrics_summary()
        assert summary["total_errors"] == 1

    @pytest.mark.asyncio
    async def test_trace_turn_basic(
        self, telemetry: ChatTelemetry, mock_session: ChatSession
    ):
        """trace_turn creates a turn span."""
        async with telemetry.trace_turn(mock_session, "Hello") as span:
            # Manually add a turn to simulate send()
            turn = Turn(
                turn_number=1,
                user_message=Message(role="user", content="Hello"),
                assistant_response=Message(role="assistant", content="Hi there!"),
                started_at=datetime.now(),
                completed_at=datetime.now(),
                tokens_in=10,
                tokens_out=20,
                context_before=0,
                context_after=30,
            )
            mock_session._turns.append(turn)
            mock_session._budget.record_turn(turn)

        # Turn recorded
        summary = get_chat_metrics_summary()
        assert summary["total_turns"] == 1

    @pytest.mark.asyncio
    async def test_trace_turn_with_error(
        self, telemetry: ChatTelemetry, mock_session: ChatSession
    ):
        """trace_turn handles errors gracefully."""
        with pytest.raises(RuntimeError):
            async with telemetry.trace_turn(mock_session, "Hello") as span:
                raise RuntimeError("LLM error")

        # Turn error recorded
        summary = get_chat_metrics_summary()
        assert summary["total_turns"] == 1
        assert summary["total_errors"] == 1

    @pytest.mark.asyncio
    async def test_trace_context_render(
        self, telemetry: ChatTelemetry, mock_session: ChatSession
    ):
        """trace_context_render creates a context render span."""
        async with telemetry.trace_context_render(mock_session) as span:
            assert span is not None
            # Simulate context rendering work
            pass

    @pytest.mark.asyncio
    async def test_trace_llm_call(
        self, telemetry: ChatTelemetry, mock_session: ChatSession
    ):
        """trace_llm_call creates an LLM call span."""
        async with telemetry.trace_llm_call(
            mock_session, model="claude-3-haiku"
        ) as span:
            assert span is not None
            # Simulate LLM call
            pass

    @pytest.mark.asyncio
    async def test_trace_nested_spans(
        self, telemetry: ChatTelemetry, mock_session_with_turns: ChatSession
    ):
        """Nested tracing (session > turn > context_render > llm_call)."""
        session = mock_session_with_turns

        async with telemetry.trace_session(session):
            async with telemetry.trace_turn(session, "What's up?"):
                async with telemetry.trace_context_render(session):
                    pass
                async with telemetry.trace_llm_call(session, model="claude-3-haiku"):
                    # Add turn
                    turn = Turn(
                        turn_number=4,
                        user_message=Message(role="user", content="What's up?"),
                        assistant_response=Message(
                            role="assistant", content="All good!"
                        ),
                        started_at=datetime.now(),
                        completed_at=datetime.now(),
                        tokens_in=20,
                        tokens_out=30,
                        context_before=600,
                        context_after=650,
                    )
                    session._turns.append(turn)
                    session._budget.record_turn(turn)

        summary = get_chat_metrics_summary()
        assert summary["total_sessions"] == 1
        assert summary["total_turns"] == 1


# =============================================================================
# Test: Utility Functions
# =============================================================================


class TestUtilityFunctions:
    """Tests for utility tracing functions."""

    def test_create_turn_span(self):
        """create_turn_span creates a valid span."""
        from protocols.agentese.chat.observability import create_turn_span

        span = create_turn_span(
            session_id="test-123",
            node_path="self.soul",
            turn_number=1,
            custom_attr="value",
        )
        assert span is not None

    def test_add_turn_event(self):
        """add_turn_event doesn't fail (no active span)."""
        from protocols.agentese.chat.observability import add_turn_event

        # Should not raise even with no active span
        add_turn_event("test_event", {"key": "value"})

    def test_set_turn_attribute(self):
        """set_turn_attribute doesn't fail (no active span)."""
        from protocols.agentese.chat.observability import set_turn_attribute

        # Should not raise even with no active span
        set_turn_attribute("test_key", "test_value")
        set_turn_attribute("chat.other_key", "other_value")


# =============================================================================
# Test: Attribute Constants
# =============================================================================


class TestAttributeConstants:
    """Tests for attribute constant definitions."""

    def test_session_attributes_defined(self):
        """Session attributes are properly defined."""
        assert ATTR_SESSION_ID == "chat.session_id"
        assert ATTR_NODE_PATH == "chat.node_path"

    def test_turn_attributes_defined(self):
        """Turn attributes are properly defined."""
        assert ATTR_TURN_NUMBER == "chat.turn_number"
        assert ATTR_TOKENS_IN == "chat.tokens_in"
        assert ATTR_TOKENS_OUT == "chat.tokens_out"

    def test_context_attributes_defined(self):
        """Context attributes are properly defined."""
        assert ATTR_CONTEXT_UTILIZATION == "chat.context_utilization"


# =============================================================================
# Test: Thread Safety
# =============================================================================


class TestThreadSafety:
    """Tests for thread safety of metrics state."""

    def test_concurrent_record_turn(self):
        """record_turn is thread-safe."""
        import threading

        def record_turns():
            for i in range(100):
                record_turn(
                    node_path="self.soul",
                    turn_number=i,
                    duration_s=0.01,
                    tokens_in=10,
                    tokens_out=20,
                    success=True,
                )

        threads = [threading.Thread(target=record_turns) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        summary = get_chat_metrics_summary()
        assert summary["total_turns"] == 400
        assert summary["total_tokens_in"] == 4000
        assert summary["total_tokens_out"] == 8000

    def test_concurrent_session_events(self):
        """record_session_event is thread-safe."""
        import threading

        def start_end_sessions():
            for i in range(50):
                record_session_event("self.soul", "started")
                record_session_event("self.soul", "ended")

        threads = [threading.Thread(target=start_end_sessions) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        summary = get_chat_metrics_summary()
        assert summary["total_sessions"] == 200
        # All sessions ended
        assert summary["active_sessions"]["self.soul"] == 0

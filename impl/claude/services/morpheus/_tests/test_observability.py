"""
Tests for Morpheus observability (telemetry integration).
"""

import pytest

from services.morpheus import (
    ChatMessage,
    ChatRequest,
    MorpheusGateway,
    MorpheusPersistence,
)
from services.morpheus.adapters.mock import MockAdapter
from services.morpheus.observability import (
    MorpheusTelemetry,
    get_morpheus_metrics_summary,
    record_completion,
    record_rate_limit,
    reset_morpheus_metrics,
)


@pytest.fixture(autouse=True)
def reset_metrics():
    """Reset metrics before each test."""
    reset_morpheus_metrics()
    yield
    reset_morpheus_metrics()


@pytest.fixture
def persistence_with_telemetry() -> MorpheusPersistence:
    """Persistence with telemetry enabled."""
    gateway = MorpheusGateway()
    gateway.register_provider("mock", MockAdapter(), prefix="mock-")
    return MorpheusPersistence(gateway=gateway, telemetry_enabled=True)


class TestRecordCompletion:
    """Tests for record_completion function."""

    def test_record_completion_updates_counts(self):
        """Recording a completion should update counters."""
        record_completion(
            model="test-model",
            provider="test-provider",
            archetype="developer",
            duration_s=1.5,
            tokens_in=100,
            tokens_out=50,
            success=True,
        )

        summary = get_morpheus_metrics_summary()
        assert summary["total_requests"] == 1
        assert summary["total_tokens_in"] == 100
        assert summary["total_tokens_out"] == 50

    def test_record_completion_tracks_errors(self):
        """Failed completions should be tracked."""
        record_completion(
            model="test-model",
            provider="test-provider",
            archetype="guest",
            duration_s=0.5,
            tokens_in=50,
            tokens_out=0,
            success=False,
        )

        summary = get_morpheus_metrics_summary()
        assert summary["total_errors"] == 1

    def test_record_completion_by_model(self):
        """Completions should be tracked by model."""
        record_completion(
            model="claude-sonnet",
            provider="claude",
            archetype="developer",
            duration_s=1.0,
            tokens_in=100,
            tokens_out=100,
            success=True,
        )
        record_completion(
            model="claude-sonnet",
            provider="claude",
            archetype="developer",
            duration_s=1.0,
            tokens_in=100,
            tokens_out=100,
            success=True,
        )
        record_completion(
            model="gpt-4",
            provider="openai",
            archetype="developer",
            duration_s=1.0,
            tokens_in=100,
            tokens_out=100,
            success=True,
        )

        summary = get_morpheus_metrics_summary()
        assert summary["top_models"]["claude-sonnet"] == 2
        assert summary["top_models"]["gpt-4"] == 1

    def test_record_completion_by_archetype(self):
        """Completions should be tracked by archetype."""
        record_completion(
            model="test",
            provider="test",
            archetype="admin",
            duration_s=1.0,
            tokens_in=100,
            tokens_out=50,
            success=True,
        )
        record_completion(
            model="test",
            provider="test",
            archetype="guest",
            duration_s=1.0,
            tokens_in=100,
            tokens_out=50,
            success=True,
        )

        summary = get_morpheus_metrics_summary()
        assert summary["requests_by_archetype"]["admin"] == 1
        assert summary["requests_by_archetype"]["guest"] == 1

    def test_record_streaming_completion(self):
        """Streaming completions should be tracked."""
        record_completion(
            model="test",
            provider="test",
            archetype="developer",
            duration_s=2.0,
            tokens_in=100,
            tokens_out=200,
            success=True,
            streaming=True,
        )

        summary = get_morpheus_metrics_summary()
        assert summary["total_streaming"] == 1


class TestRecordRateLimit:
    """Tests for record_rate_limit function."""

    def test_record_rate_limit_updates_count(self):
        """Rate limit hits should be counted."""
        record_rate_limit("guest", "test-model")
        record_rate_limit("guest", "test-model")

        summary = get_morpheus_metrics_summary()
        assert summary["total_rate_limits"] == 2


class TestMetricsSummary:
    """Tests for get_morpheus_metrics_summary function."""

    def test_empty_summary(self):
        """Empty state should return zero counts."""
        summary = get_morpheus_metrics_summary()

        assert summary["total_requests"] == 0
        assert summary["total_errors"] == 0
        assert summary["total_tokens_in"] == 0
        assert summary["total_tokens_out"] == 0
        assert summary["error_rate"] == 0.0

    def test_summary_calculations(self):
        """Summary should calculate averages correctly."""
        for _ in range(10):
            record_completion(
                model="test",
                provider="test",
                archetype="developer",
                duration_s=1.0,
                tokens_in=100,
                tokens_out=200,
                success=True,
            )

        summary = get_morpheus_metrics_summary()

        assert summary["total_requests"] == 10
        assert summary["total_tokens"] == 3000
        assert summary["avg_tokens_per_request"] == 300.0
        assert summary["avg_request_duration_s"] == 1.0


class TestResetMetrics:
    """Tests for reset_morpheus_metrics function."""

    def test_reset_clears_all_counters(self):
        """Reset should clear all metrics."""
        record_completion(
            model="test",
            provider="test",
            archetype="developer",
            duration_s=1.0,
            tokens_in=100,
            tokens_out=50,
            success=True,
        )
        record_rate_limit("guest")

        reset_morpheus_metrics()

        summary = get_morpheus_metrics_summary()
        assert summary["total_requests"] == 0
        assert summary["total_rate_limits"] == 0


class TestMorpheusTelemetry:
    """Tests for MorpheusTelemetry context manager."""

    async def test_trace_completion_creates_span(self):
        """trace_completion should create a span."""
        request = ChatRequest(
            model="test-model",
            messages=[ChatMessage(role="user", content="test")],
        )
        telemetry = MorpheusTelemetry()

        async with telemetry.trace_completion(request, "developer", "test-provider"):
            pass  # Span should be created

        # If we get here without error, span was created successfully

    async def test_trace_stream_creates_span(self):
        """trace_stream should create a span."""
        request = ChatRequest(
            model="test-model",
            messages=[ChatMessage(role="user", content="test")],
        )
        telemetry = MorpheusTelemetry()

        async with telemetry.trace_stream(request, "developer", "test-provider"):
            pass  # Span should be created


class TestPersistenceTelemetryIntegration:
    """Tests for MorpheusPersistence telemetry integration."""

    async def test_complete_records_metrics(
        self, persistence_with_telemetry: MorpheusPersistence
    ):
        """Completion should record metrics."""
        request = ChatRequest(
            model="mock-test",
            messages=[ChatMessage(role="user", content="test")],
        )

        await persistence_with_telemetry.complete(request, archetype="developer")

        summary = get_morpheus_metrics_summary()
        assert summary["total_requests"] >= 1
        assert "mock" in summary["requests_by_provider"]

    async def test_complete_returns_span_id(
        self, persistence_with_telemetry: MorpheusPersistence
    ):
        """Completion result should include span ID."""
        request = ChatRequest(
            model="mock-test",
            messages=[ChatMessage(role="user", content="test")],
        )

        result = await persistence_with_telemetry.complete(request)

        # telemetry_span_id should be set
        assert result.telemetry_span_id is not None
        assert len(result.telemetry_span_id) == 16  # 8 bytes = 16 hex chars

    async def test_stream_records_metrics(
        self, persistence_with_telemetry: MorpheusPersistence
    ):
        """Streaming should record metrics."""
        request = ChatRequest(
            model="mock-test",
            messages=[ChatMessage(role="user", content="test")],
        )

        async for _ in persistence_with_telemetry.stream(request, archetype="admin"):
            pass

        summary = get_morpheus_metrics_summary()
        assert summary["total_streaming"] >= 1

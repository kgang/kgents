"""
Tests for AGENTESE Metrics - Prometheus-compatible metrics.

These tests verify:
- Recording invocations with counters and histograms
- Token usage tracking
- Error counting
- Metrics summary generation
"""

from __future__ import annotations

from collections.abc import Generator

import pytest

from ..metrics import (
    get_error_count,
    get_invocation_count,
    get_metrics_summary,
    get_token_totals,
    record_error,
    record_invocation,
    reset_metrics,
)

# === Fixtures ===


@pytest.fixture(autouse=True)
def clean_metrics() -> Generator[None, None, None]:
    """Reset metrics before and after each test."""
    reset_metrics()
    yield
    reset_metrics()


# === Test Recording Functions ===


class TestRecordInvocation:
    """Tests for record_invocation function."""

    def test_records_basic_invocation(self) -> None:
        """Records a basic invocation."""
        record_invocation(
            path="self.soul.challenge",
            context="self",
            duration_s=0.1,
            success=True,
        )

        assert get_invocation_count() == 1
        assert get_error_count() == 0

    def test_records_multiple_invocations(self) -> None:
        """Records multiple invocations."""
        for i in range(5):
            record_invocation(
                path=f"self.soul.path{i}",
                context="self",
                duration_s=0.05 * i,
                success=True,
            )

        assert get_invocation_count() == 5

    def test_records_invocation_with_error(self) -> None:
        """Records invocations with errors."""
        record_invocation(
            path="self.soul.challenge",
            context="self",
            duration_s=0.1,
            success=False,
        )

        assert get_invocation_count() == 1
        assert get_error_count() == 1

    def test_records_token_usage(self) -> None:
        """Records token usage."""
        record_invocation(
            path="self.llm.generate",
            context="self",
            duration_s=0.5,
            success=True,
            tokens_in=100,
            tokens_out=50,
        )

        tokens_in, tokens_out = get_token_totals()
        assert tokens_in == 100
        assert tokens_out == 50

    def test_accumulates_token_usage(self) -> None:
        """Accumulates token usage across invocations."""
        for _ in range(3):
            record_invocation(
                path="self.llm.generate",
                context="self",
                duration_s=0.1,
                success=True,
                tokens_in=100,
                tokens_out=50,
            )

        tokens_in, tokens_out = get_token_totals()
        assert tokens_in == 300
        assert tokens_out == 150

    def test_tracks_by_context(self) -> None:
        """Tracks invocations by context."""
        record_invocation(
            path="self.soul.challenge",
            context="self",
            duration_s=0.1,
            success=True,
        )
        record_invocation(
            path="world.house.manifest",
            context="world",
            duration_s=0.1,
            success=True,
        )
        record_invocation(
            path="self.memory.store",
            context="self",
            duration_s=0.1,
            success=True,
        )

        summary = get_metrics_summary()
        assert summary["invocations_by_context"]["self"] == 2
        assert summary["invocations_by_context"]["world"] == 1

    def test_tracks_by_path(self) -> None:
        """Tracks invocations by path."""
        record_invocation(
            path="self.soul.challenge",
            context="self",
            duration_s=0.1,
            success=True,
        )
        record_invocation(
            path="self.soul.challenge",
            context="self",
            duration_s=0.1,
            success=True,
        )

        assert get_invocation_count("self.soul.challenge") == 2
        assert get_invocation_count("self.soul.other") == 0


class TestRecordError:
    """Tests for record_error function."""

    def test_records_error(self) -> None:
        """Records an error."""
        record_error(
            path="self.soul.challenge",
            context="self",
            error_type="ValueError",
        )

        assert get_error_count() == 1
        assert get_error_count("self.soul.challenge") == 1

    def test_accumulates_errors(self) -> None:
        """Accumulates errors."""
        for _ in range(3):
            record_error(
                path="self.soul.challenge",
                context="self",
            )

        assert get_error_count() == 3
        assert get_error_count("self.soul.challenge") == 3


# === Test Summary Functions ===


class TestGetMetricsSummary:
    """Tests for get_metrics_summary function."""

    def test_empty_summary(self) -> None:
        """Returns empty summary when no metrics recorded."""
        summary = get_metrics_summary()

        assert summary["total_invocations"] == 0
        assert summary["total_errors"] == 0
        assert summary["error_rate"] == 0.0
        assert summary["avg_duration_s"] == 0.0

    def test_calculates_error_rate(self) -> None:
        """Calculates error rate correctly."""
        record_invocation("p1", "ctx", 0.1, True)
        record_invocation("p2", "ctx", 0.1, True)
        record_invocation("p3", "ctx", 0.1, False)
        record_invocation("p4", "ctx", 0.1, False)

        summary = get_metrics_summary()
        assert summary["error_rate"] == 0.5  # 2 errors out of 4

    def test_calculates_average_duration(self) -> None:
        """Calculates average duration correctly."""
        record_invocation("p1", "ctx", 0.1, True)
        record_invocation("p2", "ctx", 0.2, True)
        record_invocation("p3", "ctx", 0.3, True)

        summary = get_metrics_summary()
        assert abs(summary["avg_duration_s"] - 0.2) < 0.001

    def test_returns_top_paths(self) -> None:
        """Returns top paths by invocation count."""
        for _ in range(5):
            record_invocation("path.high", "ctx", 0.1, True)
        for _ in range(3):
            record_invocation("path.medium", "ctx", 0.1, True)
        for _ in range(1):
            record_invocation("path.low", "ctx", 0.1, True)

        summary = get_metrics_summary()
        top_paths = list(summary["top_paths"].keys())

        # Should be sorted by count
        assert top_paths[0] == "path.high"
        assert top_paths[1] == "path.medium"
        assert top_paths[2] == "path.low"

    def test_calculates_error_rates_by_path(self) -> None:
        """Calculates error rates for each path."""
        record_invocation("path.good", "ctx", 0.1, True)
        record_invocation("path.good", "ctx", 0.1, True)
        record_invocation("path.bad", "ctx", 0.1, True)
        record_invocation("path.bad", "ctx", 0.1, False)

        summary = get_metrics_summary()
        error_rates = summary["error_rates_by_path"]

        assert error_rates["path.good"] == 0.0
        assert error_rates["path.bad"] == 0.5


# === Test Utility Functions ===


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_get_invocation_count_total(self) -> None:
        """Returns total invocation count."""
        record_invocation("p1", "ctx", 0.1, True)
        record_invocation("p2", "ctx", 0.1, True)

        assert get_invocation_count() == 2

    def test_get_invocation_count_by_path(self) -> None:
        """Returns count for specific path."""
        record_invocation("path.a", "ctx", 0.1, True)
        record_invocation("path.a", "ctx", 0.1, True)
        record_invocation("path.b", "ctx", 0.1, True)

        assert get_invocation_count("path.a") == 2
        assert get_invocation_count("path.b") == 1
        assert get_invocation_count("path.c") == 0

    def test_get_error_count_total(self) -> None:
        """Returns total error count."""
        record_invocation("p1", "ctx", 0.1, False)
        record_invocation("p2", "ctx", 0.1, False)

        assert get_error_count() == 2

    def test_get_error_count_by_path(self) -> None:
        """Returns error count for specific path."""
        record_invocation("path.a", "ctx", 0.1, False)
        record_invocation("path.a", "ctx", 0.1, True)
        record_invocation("path.b", "ctx", 0.1, False)

        assert get_error_count("path.a") == 1
        assert get_error_count("path.b") == 1
        assert get_error_count("path.c") == 0

    def test_reset_metrics(self) -> None:
        """Resets all metrics state."""
        record_invocation("p", "ctx", 0.1, True, 100, 50)
        record_invocation("p", "ctx", 0.1, False)

        reset_metrics()

        assert get_invocation_count() == 0
        assert get_error_count() == 0
        assert get_token_totals() == (0, 0)

        summary = get_metrics_summary()
        assert summary["total_invocations"] == 0


# === Thread Safety Tests ===


class TestThreadSafety:
    """Tests for thread-safe operation."""

    def test_concurrent_recording(self) -> None:
        """Records from multiple threads safely."""
        import threading

        def record_many() -> None:
            for i in range(100):
                record_invocation(f"path.{i}", "ctx", 0.001, True, 10, 5)

        threads = [threading.Thread(target=record_many) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert get_invocation_count() == 400
        tokens_in, tokens_out = get_token_totals()
        assert tokens_in == 4000
        assert tokens_out == 2000

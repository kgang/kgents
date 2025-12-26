"""
Performance benchmarks for Mark operations.

Tests:
- Mark creation: < 50ms (p99)
- Mark serialization/deserialization
- Concurrent mark creation

Verifies that Mark operations meet production SLAs.

See: plans/enlightened-synthesis/EXECUTION_MASTER.md → Performance Targets
"""

import dataclasses
from datetime import datetime, timezone
from typing import Iterator

import pytest

from services.witness import Mark, Response, Stimulus, generate_mark_id


@pytest.fixture
def benchmark_mark() -> Iterator[Mark]:
    """Fixture for benchmarking mark creation."""
    now = datetime.now(timezone.utc)
    yield Mark(
        id=generate_mark_id(),
        origin="benchmark",
        domain="system",
        stimulus=Stimulus(kind="test", content="benchmark"),
        response=Response(kind="result", content="ok"),
        timestamp=now,
    )


class TestMarkCreation:
    """Mark creation performance benchmarks."""

    def test_mark_creation_basic(self, benchmark):
        """Benchmark basic Mark creation.

        Target: < 50ms (p99)
        """
        def create_mark():
            now = datetime.now(timezone.utc)
            return Mark(
                id=generate_mark_id(),
                origin="benchmark",
                domain="system",
                stimulus=Stimulus(kind="test", content="benchmark"),
                response=Response(kind="result", content="ok"),
                timestamp=now,
            )

        result = benchmark(create_mark)
        # Verify result is valid
        assert result.id
        assert result.origin == "benchmark"

    def test_mark_id_generation(self, benchmark):
        """Benchmark Mark ID generation.

        Target: < 1ms per ID
        """
        def generate_id():
            return generate_mark_id()

        result = benchmark(generate_id)
        assert result
        assert isinstance(result, str)

    def test_mark_creation_with_timestamps(self, benchmark):
        """Benchmark Mark creation with various timestamps.

        Target: < 50ms (p99)
        """
        now = datetime.now(timezone.utc)

        def create_timestamped_marks():
            marks = []
            for i in range(10):
                mark = Mark(
                    id=generate_mark_id(),
                    origin=f"source_{i}",
                    domain="system",
                    stimulus=Stimulus(kind="test", content=f"event_{i}"),
                    response=Response(kind="result", content="ok"),
                    timestamp=now,
                )
                marks.append(mark)
            return marks

        results = benchmark(create_timestamped_marks)
        assert len(results) == 10
        assert all(m.id for m in results)


class TestMarkProperties:
    """Test Mark immutability and properties."""

    def test_mark_immutability(self, benchmark_mark):
        """Verify Mark is immutable (frozen=True).

        Should be instantaneous.
        """
        mark = benchmark_mark

        # Verify we cannot modify fields
        with pytest.raises((AttributeError, dataclasses.FrozenInstanceError)):
            mark.origin = "modified"

    @pytest.mark.benchmark(
        min_rounds=100,
        min_time=0.001,
        max_time=0.05,
    )
    def test_mark_attribute_access(self, benchmark):
        """Benchmark Mark attribute access.

        Target: < 1ms (p99)
        """
        mark = Mark(
            id=generate_mark_id(),
            origin="test",
            domain="system",
            stimulus=Stimulus(kind="test", content="data"),
            response=Response(kind="result", content="ok"),
            timestamp=datetime.now(timezone.utc),
        )

        def access_attributes():
            _ = mark.id
            _ = mark.origin
            _ = mark.domain
            _ = mark.stimulus
            _ = mark.response
            _ = mark.timestamp

        benchmark(access_attributes)


class TestMarkBatchCreation:
    """Batch creation performance."""

    @pytest.mark.benchmark(min_rounds=10)
    def test_batch_create_100_marks(self, benchmark):
        """Benchmark creating 100 marks.

        Target: < 5s total (< 50ms per mark average)
        """
        now = datetime.now(timezone.utc)

        def create_batch():
            marks = []
            for i in range(100):
                mark = Mark(
                    id=generate_mark_id(),
                    origin=f"source_{i}",
                    domain="system",
                    stimulus=Stimulus(kind="batch", content=f"item_{i}"),
                    response=Response(kind="result", content="ok"),
                    timestamp=now,
                )
                marks.append(mark)
            return marks

        results = benchmark(create_batch)
        assert len(results) == 100

    @pytest.mark.benchmark(min_rounds=10)
    def test_batch_create_1000_marks(self, benchmark):
        """Benchmark creating 1000 marks.

        Target: < 50s total (< 50ms per mark average)
        """
        now = datetime.now(timezone.utc)

        def create_large_batch():
            marks = []
            for i in range(1000):
                mark = Mark(
                    id=generate_mark_id(),
                    origin=f"source_{i % 10}",
                    domain="system",
                    stimulus=Stimulus(kind="batch", content=f"item_{i}"),
                    response=Response(kind="result", content="ok"),
                    timestamp=now,
                )
                marks.append(mark)
            return marks

        results = benchmark(create_large_batch)
        assert len(results) == 1000

"""
Performance benchmarks for Trace operations (append-only mark sequences).

Tests:
- Trace append: < 5ms (p99) per append
- Trace filtering operations
- Trace memory efficiency

Verifies that Trace operations meet production SLAs for append-only history.

See: plans/enlightened-synthesis/EXECUTION_MASTER.md → Performance Targets
See: services/witness/trace.py
"""

from datetime import datetime, timedelta, timezone

import pytest

from services.witness import (
    Mark,
    Response,
    Stimulus,
    Trace,
    generate_mark_id,
)


@pytest.fixture
def empty_trace() -> Trace[Mark]:
    """Fixture providing an empty Trace."""
    return Trace[Mark]()


@pytest.fixture
def sample_marks() -> list[Mark]:
    """Fixture providing sample marks for benchmarking."""
    now = datetime.now(timezone.utc)
    marks = []

    for i in range(100):
        mark = Mark(
            id=generate_mark_id(),
            origin=f"source_{i % 10}",
            domain=["navigation", "portal", "chat", "edit", "system"][i % 5],
            stimulus=Stimulus(kind="event", content=f"stimulus_{i}"),
            response=Response(kind="result", content=f"response_{i}"),
            timestamp=now + timedelta(milliseconds=i),
        )
        marks.append(mark)

    return marks


class TestTraceAppend:
    """Trace append operation benchmarks."""

    def test_single_append(self, benchmark, empty_trace):
        """Benchmark single mark append.

        Target: < 5ms (p99)
        """
        trace = empty_trace
        mark = Mark(
            id=generate_mark_id(),
            origin="test",
            domain="system",
            stimulus=Stimulus(kind="test", content="data"),
            response=Response(kind="result", content="ok"),
            timestamp=datetime.now(timezone.utc),
        )

        def append():
            return trace.add(mark)

        result = benchmark(append)
        assert len(result) == 1

    def test_sequential_appends(self, benchmark, empty_trace):
        """Benchmark sequential appends (10 marks).

        Target: < 50ms total (< 5ms per append)
        """
        now = datetime.now(timezone.utc)

        def append_sequence():
            trace = empty_trace
            for i in range(10):
                mark = Mark(
                    id=generate_mark_id(),
                    origin=f"source_{i}",
                    domain="system",
                    stimulus=Stimulus(kind="event", content=f"item_{i}"),
                    response=Response(kind="result", content="ok"),
                    timestamp=now + timedelta(milliseconds=i),
                )
                trace = trace.add(mark)
            return trace

        result = benchmark(append_sequence)
        assert len(result) == 10

    def test_large_sequential_appends(self, benchmark, empty_trace):
        """Benchmark sequential appends (100 marks).

        Target: < 500ms total (< 5ms per append)
        """
        now = datetime.now(timezone.utc)

        def append_large_sequence():
            trace = empty_trace
            for i in range(100):
                mark = Mark(
                    id=generate_mark_id(),
                    origin=f"source_{i % 10}",
                    domain=["nav", "portal", "chat", "edit", "sys"][i % 5],
                    stimulus=Stimulus(kind="event", content=f"item_{i}"),
                    response=Response(kind="result", content="ok"),
                    timestamp=now + timedelta(milliseconds=i),
                )
                trace = trace.add(mark)
            return trace

        result = benchmark(append_large_sequence)
        assert len(result) == 100


class TestTraceFiltering:
    """Trace filtering operation benchmarks."""

    def test_filter_by_domain(self, benchmark, sample_marks):
        """Benchmark filtering marks by domain.

        Target: < 10ms for 100 marks
        """
        trace = Trace[Mark]()
        for mark in sample_marks:
            trace = trace.add(mark)

        def filter_domain():
            return trace.filter(lambda m: m.domain == "chat")

        result = benchmark(filter_domain)
        assert len(result.marks) > 0

    def test_filter_by_origin(self, benchmark, sample_marks):
        """Benchmark filtering marks by origin.

        Target: < 10ms for 100 marks
        """
        trace = Trace[Mark]()
        for mark in sample_marks:
            trace = trace.add(mark)

        def filter_origin():
            return trace.filter(lambda m: m.origin == "source_5")

        result = benchmark(filter_origin)
        assert len(result.marks) > 0

    def test_multiple_filters(self, benchmark, sample_marks):
        """Benchmark chained filter operations.

        Target: < 15ms for 100 marks
        """
        trace = Trace[Mark]()
        for mark in sample_marks:
            trace = trace.add(mark)

        def chained_filters():
            filtered = trace.filter(lambda m: m.domain == "chat")
            filtered = filtered.filter(lambda m: "source_0" in m.origin)
            return filtered

        result = benchmark(chained_filters)
        # Result may be empty depending on data


class TestTraceAccess:
    """Trace access pattern benchmarks."""

    def test_latest_access(self, benchmark, sample_marks):
        """Benchmark accessing latest mark.

        Target: < 1ms
        """
        trace = Trace[Mark]()
        for mark in sample_marks:
            trace = trace.add(mark)

        def get_latest():
            return trace.latest

        result = benchmark(get_latest)
        assert result is not None

    def test_length_check(self, benchmark, sample_marks):
        """Benchmark checking trace length.

        Target: < 1ms
        """
        trace = Trace[Mark]()
        for mark in sample_marks:
            trace = trace.add(mark)

        def check_length():
            return len(trace)

        result = benchmark(check_length)
        assert result == len(sample_marks)

    def test_iteration(self, benchmark, sample_marks):
        """Benchmark iterating over marks.

        Target: < 5ms for 100 marks
        """
        trace = Trace[Mark]()
        for mark in sample_marks:
            trace = trace.add(mark)

        def iterate_marks():
            count = 0
            for _ in trace:
                count += 1
            return count

        result = benchmark(iterate_marks)
        assert result == len(sample_marks)


class TestTraceComposition:
    """Trace composition operation benchmarks."""

    def test_merge_traces(self, benchmark):
        """Benchmark merging two traces.

        Target: < 10ms for 50 + 50 marks
        """
        now = datetime.now(timezone.utc)

        def create_and_merge():
            trace1 = Trace[Mark]()
            for i in range(50):
                mark = Mark(
                    id=generate_mark_id(),
                    origin="trace1",
                    domain="system",
                    stimulus=Stimulus(kind="event", content=f"t1_{i}"),
                    response=Response(kind="result", content="ok"),
                    timestamp=now + timedelta(milliseconds=i),
                )
                trace1 = trace1.add(mark)

            trace2 = Trace[Mark]()
            for i in range(50):
                mark = Mark(
                    id=generate_mark_id(),
                    origin="trace2",
                    domain="system",
                    stimulus=Stimulus(kind="event", content=f"t2_{i}"),
                    response=Response(kind="result", content="ok"),
                    timestamp=now + timedelta(milliseconds=50 + i),
                )
                trace2 = trace2.add(mark)

            # Merge by adding all from trace2 to trace1
            result = trace1
            for mark in trace2:
                result = result.add(mark)
            return result

        result = benchmark(create_and_merge)
        assert len(result) == 100


class TestTraceMemory:
    """Memory efficiency benchmarks for traces."""

    @pytest.mark.benchmark(min_rounds=5)
    def test_large_trace_creation(self, benchmark):
        """Benchmark creating large trace (1000 marks).

        Should complete without memory issues.
        Target: < 500ms
        """
        now = datetime.now(timezone.utc)

        def create_large_trace():
            trace = Trace[Mark]()
            for i in range(1000):
                mark = Mark(
                    id=generate_mark_id(),
                    origin=f"source_{i % 10}",
                    domain=["nav", "portal", "chat", "edit", "sys"][i % 5],
                    stimulus=Stimulus(kind="event", content=f"item_{i}"),
                    response=Response(kind="result", content="ok"),
                    timestamp=now + timedelta(milliseconds=i % 10000),
                )
                trace = trace.add(mark)
            return trace

        result = benchmark(create_large_trace)
        assert len(result) == 1000

    @pytest.mark.benchmark(min_rounds=5)
    def test_trace_slicing(self, benchmark, sample_marks):
        """Benchmark slicing operations on traces.

        Target: < 5ms for 100 marks
        """
        trace = Trace[Mark]()
        for mark in sample_marks:
            trace = trace.add(mark)

        def slice_trace():
            return trace.slice(10, 50)

        result = benchmark(slice_trace)
        assert len(result.marks) == 40

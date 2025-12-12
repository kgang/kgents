"""Tests for flux sources."""

import asyncio
import time

import pytest
from agents.flux.sources import (
    batched,
    countdown,
    empty,
    filtered,
    from_iterable,
    from_stream,
    mapped,
    merged,
    periodic,
    skip,
    take,
    tick,
)
from agents.flux.sources.events import range_source, repeat, single


class TestFromIterable:
    """Test from_iterable() source."""

    @pytest.mark.asyncio
    async def test_list(self):
        results = []
        async for item in from_iterable([1, 2, 3]):
            results.append(item)

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_tuple(self):
        results = []
        async for item in from_iterable((1, 2, 3)):
            results.append(item)

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_empty_list(self):
        results: list[int] = []
        empty_list: list[int] = []
        async for item in from_iterable(empty_list):
            results.append(item)

        assert results == []

    @pytest.mark.asyncio
    async def test_strings(self):
        results = []
        async for item in from_iterable(["a", "b", "c"]):
            results.append(item)

        assert results == ["a", "b", "c"]

    @pytest.mark.asyncio
    async def test_generator(self):
        def gen():
            yield 1
            yield 2
            yield 3

        results = []
        async for item in from_iterable(gen()):
            results.append(item)

        assert results == [1, 2, 3]


class TestFromStream:
    """Test from_stream() source."""

    @pytest.mark.asyncio
    async def test_pass_through(self):
        async def gen():
            yield 1
            yield 2

        results = []
        async for item in from_stream(gen()):
            results.append(item)

        assert results == [1, 2]


class TestEmpty:
    """Test empty() source."""

    @pytest.mark.asyncio
    async def test_empty_yields_nothing(self):
        results = []
        async for item in empty():
            results.append(item)

        assert results == []


class TestSingle:
    """Test single() source."""

    @pytest.mark.asyncio
    async def test_single_value(self):
        results = []
        async for item in single(42):
            results.append(item)

        assert results == [42]


class TestRepeat:
    """Test repeat() source."""

    @pytest.mark.asyncio
    async def test_repeat_finite(self):
        results = []
        async for item in repeat("x", times=3):
            results.append(item)

        assert results == ["x", "x", "x"]

    @pytest.mark.asyncio
    async def test_repeat_zero(self):
        results = []
        async for item in repeat("x", times=0):
            results.append(item)

        assert results == []


class TestRangeSource:
    """Test range_source()."""

    @pytest.mark.asyncio
    async def test_basic_range(self):
        results = []
        async for item in range_source(0, 5):
            results.append(item)

        assert results == [0, 1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_range_with_step(self):
        results = []
        async for item in range_source(0, 10, 2):
            results.append(item)

        assert results == [0, 2, 4, 6, 8]


class TestPeriodic:
    """Test periodic() source."""

    @pytest.mark.asyncio
    async def test_periodic_emits_timestamps(self):
        results = []
        count = 0
        async for ts in periodic(0.01):
            results.append(ts)
            count += 1
            if count >= 3:
                break

        assert len(results) == 3
        assert all(isinstance(t, float) for t in results)
        # Timestamps should be increasing
        assert results[0] < results[1] < results[2]


class TestCountdown:
    """Test countdown() source."""

    @pytest.mark.asyncio
    async def test_countdown(self):
        results = []
        async for n in countdown(3, interval=0.01):
            results.append(n)

        assert results == [3, 2, 1, 0]


class TestTick:
    """Test tick() source."""

    @pytest.mark.asyncio
    async def test_tick_finite(self):
        results = []
        async for n in tick(0.01, count=5):
            results.append(n)

        assert results == [0, 1, 2, 3, 4]


class TestFiltered:
    """Test filtered() combinator."""

    @pytest.mark.asyncio
    async def test_filter_sync_predicate(self):
        source = from_iterable([1, 2, 3, 4, 5, 6])

        results = []
        async for item in filtered(source, lambda x: x % 2 == 0):
            results.append(item)

        assert results == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_filter_async_predicate(self):
        source = from_iterable([1, 2, 3, 4])

        async def is_even(x):
            return x % 2 == 0

        results = []
        async for item in filtered(source, is_even):
            results.append(item)

        assert results == [2, 4]


class TestMapped:
    """Test mapped() combinator."""

    @pytest.mark.asyncio
    async def test_map_sync_transform(self):
        source = from_iterable([1, 2, 3])

        results = []
        async for item in mapped(source, lambda x: x * 2):
            results.append(item)

        assert results == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_map_async_transform(self):
        source = from_iterable([1, 2, 3])

        async def double(x):
            return x * 2

        results = []
        async for item in mapped(source, double):
            results.append(item)

        assert results == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_map_type_change(self):
        source = from_iterable([1, 2, 3])

        results = []
        async for item in mapped(source, str):
            results.append(item)

        assert results == ["1", "2", "3"]


class TestBatched:
    """Test batched() combinator."""

    @pytest.mark.asyncio
    async def test_exact_batches(self):
        source = from_iterable([1, 2, 3, 4, 5, 6])

        results = []
        async for batch in batched(source, size=2):
            results.append(batch)

        assert results == [[1, 2], [3, 4], [5, 6]]

    @pytest.mark.asyncio
    async def test_partial_batch(self):
        source = from_iterable([1, 2, 3, 4, 5])

        results = []
        async for batch in batched(source, size=2):
            results.append(batch)

        assert results == [[1, 2], [3, 4], [5]]

    @pytest.mark.asyncio
    async def test_single_item_batches(self):
        source = from_iterable([1, 2, 3])

        results = []
        async for batch in batched(source, size=1):
            results.append(batch)

        assert results == [[1], [2], [3]]


class TestTake:
    """Test take() combinator."""

    @pytest.mark.asyncio
    async def test_take_less_than_source(self):
        source = from_iterable([1, 2, 3, 4, 5])

        results = []
        async for item in take(source, 3):
            results.append(item)

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_take_more_than_source(self):
        source = from_iterable([1, 2])

        results = []
        async for item in take(source, 10):
            results.append(item)

        assert results == [1, 2]

    @pytest.mark.asyncio
    async def test_take_zero(self):
        source = from_iterable([1, 2, 3])

        results = []
        async for item in take(source, 0):
            results.append(item)

        assert results == []


class TestSkip:
    """Test skip() combinator."""

    @pytest.mark.asyncio
    async def test_skip(self):
        source = from_iterable([1, 2, 3, 4, 5])

        results = []
        async for item in skip(source, 2):
            results.append(item)

        assert results == [3, 4, 5]

    @pytest.mark.asyncio
    async def test_skip_all(self):
        source = from_iterable([1, 2, 3])

        results = []
        async for item in skip(source, 10):
            results.append(item)

        assert results == []

    @pytest.mark.asyncio
    async def test_skip_none(self):
        source = from_iterable([1, 2, 3])

        results = []
        async for item in skip(source, 0):
            results.append(item)

        assert results == [1, 2, 3]


class TestMerged:
    """Test merged() combinator."""

    @pytest.mark.asyncio
    async def test_merge_two_sources(self):
        source_a = from_iterable([1, 2, 3])
        source_b = from_iterable([4, 5, 6])

        results = []
        async for item in merged(source_a, source_b):
            results.append(item)

        # All items from both sources
        assert sorted(results) == [1, 2, 3, 4, 5, 6]

    @pytest.mark.asyncio
    async def test_merge_empty(self):
        results: list[int] = []
        async for item in merged():  # type: ignore[var-annotated]
            results.append(item)

        assert results == []

    @pytest.mark.asyncio
    async def test_merge_single_source(self):
        source = from_iterable([1, 2, 3])

        results = []
        async for item in merged(source):
            results.append(item)

        assert results == [1, 2, 3]


class TestCombinatorChaining:
    """Test chaining multiple combinators."""

    @pytest.mark.asyncio
    async def test_filter_then_map(self):
        source = from_iterable([1, 2, 3, 4, 5, 6])

        # Filter evens, then double
        filtered_source = filtered(source, lambda x: x % 2 == 0)
        mapped_source = mapped(filtered_source, lambda x: x * 2)

        results = []
        async for item in mapped_source:
            results.append(item)

        assert results == [4, 8, 12]

    @pytest.mark.asyncio
    async def test_take_then_map(self):
        source = from_iterable([1, 2, 3, 4, 5])

        # Take 3, then square
        taken = take(source, 3)
        squared = mapped(taken, lambda x: x * x)

        results = []
        async for item in squared:
            results.append(item)

        assert results == [1, 4, 9]

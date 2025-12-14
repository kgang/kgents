"""
Tests for FluxStream Operators and Composition (C14, C15).

These tests verify:
- Stream operators (map, filter, take, tap)
- Stream composition (chain, merge, zip, collect)
- Lazy evaluation
- Metadata passthrough
"""

from __future__ import annotations

import asyncio
from typing import AsyncIterator

import pytest
from agents.k.flux import FluxEvent, FluxStream
from agents.k.llm import StreamingLLMResponse

# =============================================================================
# Test Fixtures
# =============================================================================


async def data_source(values: list[str]) -> AsyncIterator[FluxEvent[str]]:
    """Create a simple data source from a list of strings."""
    for value in values:
        yield FluxEvent.data(value)


async def data_source_with_metadata(
    values: list[str], tokens: int = 100
) -> AsyncIterator[FluxEvent[str]]:
    """Create a data source that ends with a metadata event."""
    for value in values:
        yield FluxEvent.data(value)
    yield FluxEvent.metadata(
        StreamingLLMResponse(
            text="".join(values),
            tokens_used=tokens,
            model="test",
            raw_metadata={},
        )
    )


async def slow_source(
    values: list[str], delay: float = 0.01
) -> AsyncIterator[FluxEvent[str]]:
    """Create a slow data source with delays."""
    for value in values:
        await asyncio.sleep(delay)
        yield FluxEvent.data(value)


# =============================================================================
# C14: FluxStream Operators Tests
# =============================================================================


class TestFluxStreamMap:
    """Test FluxStream.map() operator."""

    @pytest.mark.asyncio
    async def test_map_transforms_data_events(self) -> None:
        """map() should transform data events."""
        source = FluxStream(data_source(["hello", "world"]))

        result = source.map(
            lambda e: FluxEvent.data(e.value.upper()) if e.is_data else e
        )

        values = await result.collect()
        assert values == ["HELLO", "WORLD"]

    @pytest.mark.asyncio
    async def test_map_preserves_metadata(self) -> None:
        """map() should pass metadata events through unchanged."""
        source = FluxStream(data_source_with_metadata(["a", "b"], tokens=50))

        result = source.map(
            lambda e: FluxEvent.data(e.value.upper()) if e.is_data else e
        )

        events = []
        async for event in result:
            events.append(event)

        # Should have 2 data + 1 metadata
        assert len(events) == 3
        assert events[0].is_data and events[0].value == "A"
        assert events[1].is_data and events[1].value == "B"
        assert events[2].is_metadata
        assert events[2].value.tokens_used == 50

    @pytest.mark.asyncio
    async def test_map_is_lazy(self) -> None:
        """map() should not consume source until iterated."""
        call_count = 0

        async def counting_source() -> AsyncIterator[FluxEvent[str]]:
            nonlocal call_count
            for i in range(3):
                call_count += 1
                yield FluxEvent.data(str(i))

        source = FluxStream(counting_source())

        # Just creating the mapped stream shouldn't consume
        _ = source.map(lambda e: e)

        assert call_count == 0  # Not consumed yet


class TestFluxStreamFilter:
    """Test FluxStream.filter() operator."""

    @pytest.mark.asyncio
    async def test_filter_removes_non_matching_events(self) -> None:
        """filter() should remove events that don't match predicate."""
        source = FluxStream(data_source(["a", "bb", "c", "ddd"]))

        result = source.filter(lambda e: e.is_data and len(e.value) > 1)

        values = await result.collect()
        assert values == ["bb", "ddd"]

    @pytest.mark.asyncio
    async def test_filter_preserves_metadata(self) -> None:
        """filter() should always pass metadata through."""
        source = FluxStream(data_source_with_metadata(["a", "b", "c"], tokens=75))

        # Filter that would reject all data events
        result = source.filter(lambda e: e.is_data and len(e.value) > 10)

        events = []
        async for event in result:
            events.append(event)

        # Should have 0 data (all filtered) + 1 metadata (passed through)
        assert len(events) == 1
        assert events[0].is_metadata
        assert events[0].value.tokens_used == 75

    @pytest.mark.asyncio
    async def test_filter_empty_stream(self) -> None:
        """filter() on empty stream should return empty."""
        source = FluxStream(data_source([]))
        result = source.filter(lambda e: True)

        values = await result.collect()
        assert values == []


class TestFluxStreamTake:
    """Test FluxStream.take() operator."""

    @pytest.mark.asyncio
    async def test_take_limits_data_events(self) -> None:
        """take() should limit to first n data events."""
        source = FluxStream(data_source(["a", "b", "c", "d", "e"]))

        result = source.take(3)

        values = await result.collect()
        assert values == ["a", "b", "c"]

    @pytest.mark.asyncio
    async def test_take_preserves_metadata(self) -> None:
        """take() should pass metadata through regardless of limit."""
        source = FluxStream(data_source_with_metadata(["a", "b", "c"], tokens=100))

        result = source.take(1)

        events = []
        async for event in result:
            events.append(event)

        # Should have 1 data (limited) + 1 metadata (passed through)
        assert len(events) == 2
        assert events[0].is_data and events[0].value == "a"
        assert events[1].is_metadata

    @pytest.mark.asyncio
    async def test_take_zero(self) -> None:
        """take(0) should return no data events."""
        source = FluxStream(data_source(["a", "b", "c"]))

        result = source.take(0)

        values = await result.collect()
        assert values == []

    @pytest.mark.asyncio
    async def test_take_more_than_available(self) -> None:
        """take(n) where n > stream length should return all."""
        source = FluxStream(data_source(["a", "b"]))

        result = source.take(100)

        values = await result.collect()
        assert values == ["a", "b"]


class TestFluxStreamTap:
    """Test FluxStream.tap() operator."""

    @pytest.mark.asyncio
    async def test_tap_executes_side_effects(self) -> None:
        """tap() should execute side effect function."""
        seen: list[str] = []
        source = FluxStream(data_source(["x", "y", "z"]))

        result = source.tap(lambda e: seen.append(e.value) if e.is_data else None)

        values = await result.collect()

        # Side effects executed
        assert seen == ["x", "y", "z"]
        # Stream unchanged
        assert values == ["x", "y", "z"]

    @pytest.mark.asyncio
    async def test_tap_does_not_modify_events(self) -> None:
        """tap() should not modify events."""
        source = FluxStream(data_source_with_metadata(["a"], tokens=25))

        result = source.tap(lambda e: None)  # No-op side effect

        events = []
        async for event in result:
            events.append(event)

        assert events[0].is_data and events[0].value == "a"
        assert events[1].is_metadata and events[1].value.tokens_used == 25


class TestFluxStreamOperatorChaining:
    """Test chaining multiple operators."""

    @pytest.mark.asyncio
    async def test_chain_filter_map_take(self) -> None:
        """Operators should chain correctly."""
        source = FluxStream(data_source(["", "a", "", "bb", "ccc", "d", ""]))

        result = (
            source.filter(lambda e: e.is_data and len(e.value.strip()) > 0)
            .map(lambda e: FluxEvent.data(e.value.upper()) if e.is_data else e)
            .take(3)
        )

        values = await result.collect()
        assert values == ["A", "BB", "CCC"]

    @pytest.mark.asyncio
    async def test_complex_pipeline_preserves_metadata(self) -> None:
        """Complex pipelines should preserve metadata."""
        source = FluxStream(data_source_with_metadata(["a", "b", "c", "d"], tokens=200))

        tapped: list[str] = []
        result = (
            source.tap(lambda e: tapped.append(e.value) if e.is_data else None)
            .filter(lambda e: e.is_data and e.value != "b")
            .map(lambda e: FluxEvent.data(f"[{e.value}]") if e.is_data else e)
            .take(2)
        )

        events = []
        async for event in result:
            events.append(event)

        # Data events transformed and limited
        assert events[0].is_data and events[0].value == "[a]"
        assert events[1].is_data and events[1].value == "[c]"
        # Metadata preserved
        assert events[2].is_metadata and events[2].value.tokens_used == 200
        # Tap saw all events before filter
        assert tapped == ["a", "b", "c", "d"]


# =============================================================================
# C15: FluxStream Composition Tests
# =============================================================================


class TestFluxStreamChain:
    """Test FluxStream.chain() composition."""

    @pytest.mark.asyncio
    async def test_chain_concatenates_streams(self) -> None:
        """chain() should concatenate streams in order."""
        s1 = FluxStream(data_source(["a", "b"]))
        s2 = FluxStream(data_source(["c", "d"]))
        s3 = FluxStream(data_source(["e"]))

        result = FluxStream.chain(s1, s2, s3)

        values = await result.collect()
        assert values == ["a", "b", "c", "d", "e"]

    @pytest.mark.asyncio
    async def test_chain_preserves_metadata(self) -> None:
        """chain() should preserve metadata from all streams."""
        s1 = FluxStream(data_source_with_metadata(["a"], tokens=10))
        s2 = FluxStream(data_source_with_metadata(["b"], tokens=20))

        result = FluxStream.chain(s1, s2)

        events = []
        async for event in result:
            events.append(event)

        # Should have: a, meta(10), b, meta(20)
        assert len(events) == 4
        metadata_events = [e for e in events if e.is_metadata]
        assert len(metadata_events) == 2
        assert metadata_events[0].value.tokens_used == 10
        assert metadata_events[1].value.tokens_used == 20

    @pytest.mark.asyncio
    async def test_chain_empty_stream(self) -> None:
        """chain() with empty stream should work."""
        s1 = FluxStream(data_source(["a"]))
        s2 = FluxStream(data_source([]))
        s3 = FluxStream(data_source(["b"]))

        result = FluxStream.chain(s1, s2, s3)

        values = await result.collect()
        assert values == ["a", "b"]


class TestFluxStreamMerge:
    """Test FluxStream.merge() composition."""

    @pytest.mark.asyncio
    async def test_merge_interleaves_streams(self) -> None:
        """merge() should interleave events from streams."""
        s1 = FluxStream(data_source(["a", "b"]))
        s2 = FluxStream(data_source(["1", "2"]))

        result = FluxStream.merge(s1, s2)

        values = await result.collect()

        # All values present (order may vary due to interleaving)
        assert sorted(values) == ["1", "2", "a", "b"]

    @pytest.mark.asyncio
    async def test_merge_aggregates_metadata(self) -> None:
        """merge() should aggregate metadata token counts."""
        s1 = FluxStream(data_source_with_metadata(["a"], tokens=10))
        s2 = FluxStream(data_source_with_metadata(["b"], tokens=20))

        result = FluxStream.merge(s1, s2)

        events = []
        async for event in result:
            events.append(event)

        # Should have data events + one aggregate metadata
        data_events = [e for e in events if e.is_data]
        metadata_events = [e for e in events if e.is_metadata]

        assert len(data_events) == 2
        assert len(metadata_events) == 1
        assert metadata_events[0].value.tokens_used == 30  # 10 + 20

    @pytest.mark.asyncio
    async def test_merge_single_stream(self) -> None:
        """merge() with single stream should work."""
        s1 = FluxStream(data_source(["a", "b", "c"]))

        result = FluxStream.merge(s1)

        values = await result.collect()
        assert values == ["a", "b", "c"]


class TestFluxStreamZip:
    """Test FluxStream.zip() composition."""

    @pytest.mark.asyncio
    async def test_zip_pairs_events(self) -> None:
        """zip() should pair events from two streams."""
        s1 = FluxStream(data_source(["a", "b", "c"]))
        s2 = FluxStream(data_source(["1", "2", "3"]))

        result = s1.zip(s2)

        values = await result.collect()
        assert values == [("a", "1"), ("b", "2"), ("c", "3")]

    @pytest.mark.asyncio
    async def test_zip_stops_at_shorter_stream(self) -> None:
        """zip() should stop when either stream exhausts."""
        s1 = FluxStream(data_source(["a", "b", "c", "d", "e"]))
        s2 = FluxStream(data_source(["1", "2"]))

        result = s1.zip(s2)

        values = await result.collect()
        assert values == [("a", "1"), ("b", "2")]

    @pytest.mark.asyncio
    async def test_zip_preserves_metadata(self) -> None:
        """zip() should pass metadata through."""
        s1 = FluxStream(data_source_with_metadata(["a", "b"], tokens=50))
        s2 = FluxStream(data_source_with_metadata(["1", "2"], tokens=75))

        result = s1.zip(s2)

        events = []
        async for event in result:
            events.append(event)

        # Should have paired data + both metadata
        data_events = [e for e in events if e.is_data]
        metadata_events = [e for e in events if e.is_metadata]

        assert len(data_events) == 2
        assert len(metadata_events) == 2


class TestFluxStreamCollect:
    """Test FluxStream.collect() materialization."""

    @pytest.mark.asyncio
    async def test_collect_returns_data_values(self) -> None:
        """collect() should return list of data values."""
        source = FluxStream(data_source(["a", "b", "c"]))

        values = await source.collect()
        assert values == ["a", "b", "c"]

    @pytest.mark.asyncio
    async def test_collect_ignores_metadata(self) -> None:
        """collect() should ignore metadata events."""
        source = FluxStream(data_source_with_metadata(["a", "b"], tokens=100))

        values = await source.collect()
        assert values == ["a", "b"]

    @pytest.mark.asyncio
    async def test_collect_empty_stream(self) -> None:
        """collect() on empty stream returns empty list."""
        source = FluxStream(data_source([]))

        values = await source.collect()
        assert values == []


# =============================================================================
# CP6 Verification Test
# =============================================================================


class TestCP6Verification:
    """CP6 checkpoint verification tests."""

    @pytest.mark.asyncio
    async def test_flux_operators_compose(self) -> None:
        """
        CP6 Verification: Stream operators compose correctly.

        Tests the exact scenario from the checkpoint:
        - Filter empty chunks
        - Map to uppercase
        - Take first 5
        """
        # Create source with various chunks
        chunks = ["", "hello", " ", "world", "", "foo", "bar", "baz", ""]

        async def mock_source() -> AsyncIterator[FluxEvent[str]]:
            for chunk in chunks:
                yield FluxEvent.data(chunk)
            yield FluxEvent.metadata(
                StreamingLLMResponse(
                    text="".join(chunks),
                    tokens_used=len(chunks) * 10,
                    model="test",
                    raw_metadata={},
                )
            )

        # Chain operators: filter empty, map to uppercase, take first 5
        stream = (
            FluxStream(mock_source())
            .filter(lambda e: e.is_data and len(e.value.strip()) > 0)
            .map(lambda e: FluxEvent.data(e.value.upper()) if e.is_data else e)
            .take(5)
        )

        collected: list[str] = []
        async for event in stream:
            if event.is_data:
                collected.append(event.value)

        # Verify constraints
        assert len(collected) <= 5
        assert all(c.isupper() for c in collected if c.strip())

        # Verify actual values
        assert collected == ["HELLO", "WORLD", "FOO", "BAR", "BAZ"]

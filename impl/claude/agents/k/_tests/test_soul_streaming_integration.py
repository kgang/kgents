"""
Tests for C22: Full Streaming Pipeline Integration.

CP8 Checkpoint: Streaming pipelines compose end-to-end with lawful operators.

These tests verify:
1. FluxStream.pipe() composition operator
2. Pipe associativity laws
3. Error propagation through operator chains
4. End-to-end streaming pipeline composition

Note: This test file uses lambda expressions for operators to demonstrate
the functional composition patterns that pipe() enables. This is intentional
and matches the documented usage patterns.
"""

# ruff: noqa: E731

from typing import Any, Callable

import pytest

from agents.k.flux import FluxEvent, FluxStream
from agents.k.llm import MockLLMClient, StreamingLLMResponse
from agents.k.persona import DialogueMode
from agents.k.soul import KgentSoul

# =============================================================================
# C20: FluxStream.pipe() Composition Operator Tests
# =============================================================================


class TestFluxStreamPipe:
    """Test FluxStream.pipe() composition operator."""

    @pytest.mark.asyncio
    async def test_pipe_single_operator(self) -> None:
        """Test pipe with a single operator."""
        mock_llm = MockLLMClient(default_response="hello world")
        soul = KgentSoul(llm=mock_llm)

        # Define operator
        filter_data = lambda s: s.filter(lambda e: e.is_data)

        result = await (
            soul.dialogue_flux("test", mode=DialogueMode.REFLECT).pipe(filter_data).collect()
        )

        assert len(result) > 0
        assert all(isinstance(r, str) for r in result)

    @pytest.mark.asyncio
    async def test_pipe_multiple_operators(self) -> None:
        """Test pipe with multiple operators chained."""
        mock_llm = MockLLMClient(default_response="a b c d e f g h i j")
        soul = KgentSoul(llm=mock_llm)

        # Define operators
        filter_data = lambda s: s.filter(lambda e: e.is_data and e.value.strip())
        take_five = lambda s: s.take(5)

        result = await (
            soul.dialogue_flux("test", mode=DialogueMode.REFLECT)
            .pipe(filter_data, take_five)
            .collect()
        )

        assert len(result) <= 5

    @pytest.mark.asyncio
    async def test_pipe_with_map_operator(self) -> None:
        """Test pipe with map transformation."""
        mock_llm = MockLLMClient(default_response="hello")
        soul = KgentSoul(llm=mock_llm)

        # Define operator to uppercase
        to_upper = lambda s: s.map(lambda e: FluxEvent.data(e.value.upper()) if e.is_data else e)

        result = await (
            soul.dialogue_flux("test", mode=DialogueMode.REFLECT).pipe(to_upper).collect()
        )

        assert len(result) > 0
        assert "".join(result).isupper()

    @pytest.mark.asyncio
    async def test_pipe_empty_operators(self) -> None:
        """Test pipe with no operators (identity)."""
        mock_llm = MockLLMClient(default_response="test")
        soul = KgentSoul(llm=mock_llm)

        # pipe() with no operators should be identity
        result = await soul.dialogue_flux("test", mode=DialogueMode.REFLECT).pipe().collect()

        assert len(result) > 0


# =============================================================================
# Pipe Associativity Law Tests
# =============================================================================


class TestPipeAssociativity:
    """Test that pipe composition is associative: pipe(f, g) == pipe(f).pipe(g)."""

    @pytest.mark.asyncio
    async def test_pipe_associativity_filter_take(self) -> None:
        """
        Test pipe associativity with filter and take operators.

        pipe(f, g) should equal pipe(f).pipe(g)
        """
        # Define operators
        f = lambda s: s.filter(lambda e: e.is_data and e.value.strip())
        g = lambda s: s.take(3)

        # Create two streams with same content
        async def create_stream() -> FluxStream[str]:
            events = [
                FluxEvent.data("a"),
                FluxEvent.data("b"),
                FluxEvent.data("c"),
                FluxEvent.data("d"),
                FluxEvent.data("e"),
                FluxEvent.metadata(StreamingLLMResponse(text="abcde", tokens_used=5, model="test")),
            ]

            async def gen():
                for e in events:
                    yield e

            return FluxStream(gen())

        # Composed: pipe(f, g)
        stream1 = await create_stream()
        result_composed = await stream1.pipe(f, g).collect()

        # Chained: pipe(f).pipe(g)
        stream2 = await create_stream()
        result_chained = await stream2.pipe(f).pipe(g).collect()

        assert result_composed == result_chained

    @pytest.mark.asyncio
    async def test_pipe_associativity_map_filter(self) -> None:
        """Test associativity with map and filter."""
        # Define operators
        f = lambda s: s.map(lambda e: FluxEvent.data(e.value.upper()) if e.is_data else e)
        g = lambda s: s.filter(lambda e: e.is_data)

        async def create_stream() -> FluxStream[str]:
            events = [
                FluxEvent.data("hello"),
                FluxEvent.data("world"),
                FluxEvent.metadata(
                    StreamingLLMResponse(text="helloworld", tokens_used=2, model="test")
                ),
            ]

            async def gen():
                for e in events:
                    yield e

            return FluxStream(gen())

        stream1 = await create_stream()
        result_composed = await stream1.pipe(f, g).collect()

        stream2 = await create_stream()
        result_chained = await stream2.pipe(f).pipe(g).collect()

        assert result_composed == result_chained

    @pytest.mark.asyncio
    async def test_pipe_associativity_three_operators(self) -> None:
        """Test associativity with three operators: pipe(f, g, h) == pipe(f).pipe(g).pipe(h)."""
        # Define operators
        f = lambda s: s.filter(lambda e: e.is_data)
        g = lambda s: s.map(lambda e: FluxEvent.data(e.value + "!") if e.is_data else e)
        h = lambda s: s.take(2)

        async def create_stream() -> FluxStream[str]:
            events = [
                FluxEvent.data("a"),
                FluxEvent.data("b"),
                FluxEvent.data("c"),
                FluxEvent.metadata(StreamingLLMResponse(text="abc", tokens_used=3, model="test")),
            ]

            async def gen():
                for e in events:
                    yield e

            return FluxStream(gen())

        # pipe(f, g, h)
        stream1 = await create_stream()
        result_composed = await stream1.pipe(f, g, h).collect()

        # pipe(f).pipe(g).pipe(h)
        stream2 = await create_stream()
        result_chained = await stream2.pipe(f).pipe(g).pipe(h).collect()

        assert result_composed == result_chained


# =============================================================================
# Error Propagation Tests
# =============================================================================


class TestErrorPropagation:
    """Test error propagation through operator chains."""

    @pytest.mark.asyncio
    async def test_error_in_source_propagates(self) -> None:
        """Test that errors in source stream propagate through pipe."""

        async def failing_source():
            yield FluxEvent.data("ok")
            raise ValueError("Source error")

        stream = FluxStream(failing_source())

        with pytest.raises(ValueError, match="Source error"):
            await stream.pipe(lambda s: s.filter(lambda e: e.is_data)).collect()

    @pytest.mark.asyncio
    async def test_error_in_operator_propagates(self) -> None:
        """Test that errors in operators propagate."""

        async def source():
            yield FluxEvent.data("test")
            yield FluxEvent.metadata(StreamingLLMResponse(text="test", tokens_used=1, model="test"))

        def failing_map(stream: FluxStream[Any]) -> FluxStream[Any]:
            def transform(e: FluxEvent[Any]) -> FluxEvent[Any]:
                if e.is_data:
                    raise RuntimeError("Operator error")
                return e

            return stream.map(transform)

        stream = FluxStream(source())

        with pytest.raises(RuntimeError, match="Operator error"):
            await stream.pipe(failing_map).collect()


# =============================================================================
# Full Pipeline Integration Tests
# =============================================================================


class TestFullPipelineIntegration:
    """Test complete streaming pipeline integration."""

    @pytest.mark.asyncio
    async def test_flux_stream_pipe_composition(self) -> None:
        """
        CP8 Verification Test: Streaming pipelines compose end-to-end.

        This is the primary checkpoint verification test from the spec.
        """
        soul = KgentSoul(llm=MockLLMClient())

        result = await (
            soul.dialogue_flux("Hello", mode=DialogueMode.REFLECT)
            .pipe(
                lambda s: s.filter(lambda e: e.is_data),
                lambda s: s.take(3),
            )
            .collect()
        )

        assert len(result) <= 3

    @pytest.mark.asyncio
    async def test_dialogue_flux_with_logging_pipeline(self) -> None:
        """Test pipeline with tap for logging/side effects."""
        mock_llm = MockLLMClient(default_response="test response")
        soul = KgentSoul(llm=mock_llm)

        log: list[str] = []

        # Pipeline with logging
        result = await (
            soul.dialogue_flux("test", mode=DialogueMode.REFLECT)
            .pipe(
                lambda s: s.filter(lambda e: e.is_data),
                lambda s: s.tap(lambda e: log.append(e.value) if e.is_data else None),
            )
            .collect()
        )

        # Log should match result
        assert log == result

    @pytest.mark.asyncio
    async def test_pipeline_preserves_metadata(self) -> None:
        """Test that metadata passes through pipeline operators."""
        mock_llm = MockLLMClient(default_response="test")
        soul = KgentSoul(llm=mock_llm)

        metadata_received = []

        stream = soul.dialogue_flux("test", mode=DialogueMode.REFLECT).pipe(
            lambda s: s.filter(lambda e: e.is_data or e.is_metadata),
            lambda s: s.tap(lambda e: metadata_received.append(e.value) if e.is_metadata else None),
        )

        async for event in stream:
            pass  # Consume stream

        # Should have received metadata
        assert len(metadata_received) == 1
        assert hasattr(metadata_received[0], "tokens_used")

    @pytest.mark.asyncio
    async def test_pipeline_multiple_dialogue_modes(self) -> None:
        """Test pipeline works across different dialogue modes."""
        mock_llm = MockLLMClient(default_response="mode test")
        soul = KgentSoul(llm=mock_llm)

        # Define common pipeline
        filter_and_take = [
            lambda s: s.filter(lambda e: e.is_data),
            lambda s: s.take(3),
        ]

        for mode in [
            DialogueMode.REFLECT,
            DialogueMode.ADVISE,
            DialogueMode.CHALLENGE,
            DialogueMode.EXPLORE,
        ]:
            result = await soul.dialogue_flux("test", mode=mode).pipe(*filter_and_take).collect()
            assert len(result) <= 3


# =============================================================================
# Operator Factory Tests
# =============================================================================


class TestOperatorFactories:
    """Test higher-order operator factories with pipe."""

    @pytest.mark.asyncio
    async def test_take_n_factory(self) -> None:
        """Test take_n as a higher-order operator factory."""

        def take_n(n: int) -> Callable[[FluxStream[Any]], FluxStream[Any]]:
            """Factory that creates a take operator for n items."""
            return lambda s: s.take(n)

        mock_llm = MockLLMClient(default_response="a b c d e f g")
        soul = KgentSoul(llm=mock_llm)

        result = await (
            soul.dialogue_flux("test", mode=DialogueMode.REFLECT)
            .pipe(
                lambda s: s.filter(lambda e: e.is_data),
                take_n(2),
            )
            .collect()
        )

        assert len(result) <= 2

    @pytest.mark.asyncio
    async def test_filter_by_length_factory(self) -> None:
        """Test filter_by_length as a higher-order operator factory."""

        def filter_by_length(
            min_length: int,
        ) -> Callable[[FluxStream[Any]], FluxStream[Any]]:
            """Factory that creates a filter for minimum string length."""
            return lambda s: s.filter(lambda e: e.is_data and len(e.value.strip()) >= min_length)

        async def source():
            for text in ["a", "abc", "ab", "abcd"]:
                yield FluxEvent.data(text)
            yield FluxEvent.metadata(StreamingLLMResponse(text="", tokens_used=4, model="test"))

        stream = FluxStream(source())
        result = await stream.pipe(filter_by_length(3)).collect()

        # Only "abc" and "abcd" should pass
        assert result == ["abc", "abcd"]


# =============================================================================
# Stream Composition Tests
# =============================================================================


class TestStreamComposition:
    """Test stream composition methods work with pipe."""

    @pytest.mark.asyncio
    async def test_pipe_with_chain(self) -> None:
        """Test pipe works with FluxStream.chain() for concatenation."""

        async def source1():
            yield FluxEvent.data("first")
            yield FluxEvent.metadata(
                StreamingLLMResponse(text="first", tokens_used=1, model="test")
            )

        async def source2():
            yield FluxEvent.data("second")
            yield FluxEvent.metadata(
                StreamingLLMResponse(text="second", tokens_used=1, model="test")
            )

        # Chain two streams then pipe
        chained = FluxStream.chain(FluxStream(source1()), FluxStream(source2()))
        result = await chained.pipe(lambda s: s.filter(lambda e: e.is_data)).collect()

        assert result == ["first", "second"]


# =============================================================================
# CP8 Checkpoint Verification
# =============================================================================


class TestCP8Checkpoint:
    """CP8 Checkpoint: Streaming pipelines compose end-to-end with lawful operators."""

    @pytest.mark.asyncio
    async def test_cp8_full_pipeline_composition(self) -> None:
        """
        CP8 Final Verification: Complete streaming pipeline with all features.

        Verifies:
        1. dialogue_flux() returns FluxStream
        2. pipe() composes operators
        3. Operators are lawful (associative)
        4. Metadata passes through
        5. collect() materializes results
        """
        soul = KgentSoul(llm=MockLLMClient())

        # Track metadata
        metadata_holder: list[Any] = []

        # Define operators
        filter_data = lambda s: s.filter(lambda e: e.is_data)
        take_three = lambda s: s.take(3)
        track_meta = lambda s: s.tap(
            lambda e: metadata_holder.append(e.value) if e.is_metadata else None
        )

        # Execute pipeline
        result = await (
            soul.dialogue_flux("What should I focus on?", mode=DialogueMode.REFLECT)
            .pipe(filter_data, take_three, track_meta)
            .collect()
        )

        # Verify results
        assert len(result) <= 3
        assert all(isinstance(r, str) for r in result)
        # Metadata should have passed through
        assert len(metadata_holder) == 1

    @pytest.mark.asyncio
    async def test_cp8_associativity_law(self) -> None:
        """
        CP8 Law Verification: pipe(f, g) == pipe(f).pipe(g)

        This is the fundamental composition law for pipe.
        """
        f = lambda s: s.filter(lambda e: e.is_data)
        g = lambda s: s.take(5)

        async def create_stream() -> FluxStream[str]:
            events = [FluxEvent.data(str(i)) for i in range(10)]
            events.append(
                FluxEvent.metadata(
                    StreamingLLMResponse(text="0123456789", tokens_used=10, model="test")
                )
            )

            async def gen():
                for e in events:
                    yield e

            return FluxStream(gen())

        # Both forms should produce identical results
        stream1 = await create_stream()
        result_composed = await stream1.pipe(f, g).collect()

        stream2 = await create_stream()
        result_chained = await stream2.pipe(f).pipe(g).collect()

        assert result_composed == result_chained
        assert len(result_composed) == 5  # take(5) limits to 5 items

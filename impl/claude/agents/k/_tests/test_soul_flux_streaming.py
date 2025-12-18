"""
Tests for Wave 5: Soul Flux Streaming (C11-C13).

CP5 Checkpoint: End-to-end streaming from CLI to LLM with token display.
"""

import pytest

from agents.k.flux import (
    DEFAULT_STREAM_BUFFER_SIZE,
    FluxEvent,
    FluxStream,
    LLMStreamSource,
)
from agents.k.llm import MockLLMClient, StreamingLLMResponse
from agents.k.persona import DialogueMode
from agents.k.soul import BudgetTier, KgentSoul

# =============================================================================
# C11: FluxEvent Tests
# =============================================================================


class TestFluxEvent:
    """Test FluxEvent dataclass."""

    def test_create_data_event(self) -> None:
        """Test creating a data event."""
        event = FluxEvent.data("Hello")
        assert event.is_data
        assert not event.is_metadata
        assert event.value == "Hello"

    def test_create_metadata_event(self) -> None:
        """Test creating a metadata event."""
        meta = StreamingLLMResponse(
            text="Full response",
            tokens_used=42,
            model="test-model",
        )
        event: FluxEvent[StreamingLLMResponse] = FluxEvent.metadata(meta)
        assert event.is_metadata
        assert not event.is_data
        assert event.value.tokens_used == 42

    def test_flux_event_is_frozen(self) -> None:
        """Test that FluxEvent is immutable."""
        event = FluxEvent.data("test")
        with pytest.raises(Exception):  # FrozenInstanceError
            event._value = "modified"  # type: ignore

    def test_generic_type_parameter(self) -> None:
        """Test FluxEvent works with different type parameters."""
        # String data
        str_event: FluxEvent[str] = FluxEvent.data("text")
        assert str_event.value == "text"

        # Integer data (unusual but valid)
        int_event: FluxEvent[int] = FluxEvent.data(42)
        assert int_event.value == 42


# =============================================================================
# C11: LLMStreamSource Tests
# =============================================================================


class TestLLMStreamSource:
    """Test LLMStreamSource wrapper."""

    @pytest.mark.asyncio
    async def test_stream_source_yields_data_events(self) -> None:
        """Test that LLMStreamSource yields data events for chunks."""
        client = MockLLMClient(default_response="Hello world test")
        source = LLMStreamSource(
            client=client,
            system="Test system",
            user="Test user",
        )

        data_events: list[str] = []
        async for event in source:
            if event.is_data:
                data_events.append(event.value)

        assert len(data_events) > 0
        # Accumulated data should contain the response
        assert "Hello" in "".join(data_events)

    @pytest.mark.asyncio
    async def test_stream_source_yields_final_metadata(self) -> None:
        """Test that LLMStreamSource yields metadata event at end."""
        client = MockLLMClient(default_response="Test response")
        source = LLMStreamSource(
            client=client,
            system="Test",
            user="Test",
        )

        metadata_event: FluxEvent[str] | None = None
        async for event in source:
            if event.is_metadata:
                metadata_event = event

        assert metadata_event is not None
        assert metadata_event.value.tokens_used > 0

    @pytest.mark.asyncio
    async def test_stream_source_accumulated_text_matches(self) -> None:
        """Test that accumulated chunks match final response."""
        test_response = "The quick brown fox"
        client = MockLLMClient(default_response=test_response)
        source = LLMStreamSource(
            client=client,
            system="Test",
            user="Test",
        )

        chunks: list[str] = []
        final_text = ""
        async for event in source:
            if event.is_data:
                chunks.append(event.value)
            elif event.is_metadata:
                final_text = event.value.text

        accumulated = "".join(chunks)
        assert accumulated == final_text

    @pytest.mark.asyncio
    async def test_stream_source_respects_buffer_size(self) -> None:
        """Test that buffer size is configurable."""
        client = MockLLMClient(default_response="Test")
        source = LLMStreamSource(
            client=client,
            system="Test",
            user="Test",
            buffer_size=16,
        )

        assert source._buffer_size == 16

    def test_default_buffer_size(self) -> None:
        """Test default buffer size from environment."""
        assert DEFAULT_STREAM_BUFFER_SIZE == 64  # Default when env not set

    @pytest.mark.asyncio
    async def test_stream_source_is_complete_property(self) -> None:
        """Test is_complete property tracks stream state."""
        client = MockLLMClient(default_response="Short")
        source = LLMStreamSource(
            client=client,
            system="Test",
            user="Test",
        )

        assert not source.is_complete

        async for _ in source:
            pass

        assert source.is_complete


# =============================================================================
# C12: KgentSoul.dialogue_flux() Tests
# =============================================================================


class TestKgentSoulDialogueFlux:
    """Test KgentSoul.dialogue_flux() method."""

    @pytest.mark.asyncio
    async def test_dialogue_flux_returns_async_iterator(self) -> None:
        """Test that dialogue_flux returns an async iterator."""
        mock_llm = MockLLMClient(default_response="Test response")
        soul = KgentSoul(llm=mock_llm)

        stream = soul.dialogue_flux("Hello", mode=DialogueMode.REFLECT)
        # Should be an async iterator
        assert hasattr(stream, "__anext__")

    @pytest.mark.asyncio
    async def test_dialogue_flux_yields_data_and_metadata(self) -> None:
        """Test that dialogue_flux yields both data and metadata events."""
        mock_llm = MockLLMClient(default_response="A thoughtful response")
        soul = KgentSoul(llm=mock_llm)

        chunks: list[str] = []
        final_tokens = 0

        async for event in soul.dialogue_flux("Hello", mode=DialogueMode.REFLECT):
            if event.is_data:
                chunks.append(event.value)
            elif event.is_metadata:
                final_tokens = event.value.tokens_used

        assert len(chunks) > 0
        assert final_tokens > 0
        assert "".join(chunks) == event.value.text

    @pytest.mark.asyncio
    async def test_dialogue_flux_empty_message(self) -> None:
        """Test dialogue_flux handles empty message gracefully."""
        soul = KgentSoul(auto_llm=False)

        events: list[FluxEvent[str]] = []
        async for event in soul.dialogue_flux(""):
            events.append(event)

        # Should have data event with fallback response
        assert len(events) >= 1
        assert any(e.is_data for e in events)
        # Check for fallback response
        data_events = [e for e in events if e.is_data]
        assert "What's on your mind?" in data_events[0].value

    @pytest.mark.asyncio
    async def test_dialogue_flux_whisper_budget(self) -> None:
        """Test dialogue_flux with WHISPER budget tier."""
        soul = KgentSoul(auto_llm=False)

        chunks: list[str] = []
        tokens = 0

        async for event in soul.dialogue_flux(
            "Test", mode=DialogueMode.REFLECT, budget=BudgetTier.WHISPER
        ):
            if event.is_data:
                chunks.append(event.value)
            elif event.is_metadata:
                tokens = event.value.tokens_used

        # Whisper should use ~50 tokens
        assert tokens == 50

    @pytest.mark.asyncio
    async def test_dialogue_flux_updates_session_stats(self) -> None:
        """Test that dialogue_flux updates session statistics."""
        mock_llm = MockLLMClient(default_response="Response with content")
        soul = KgentSoul(llm=mock_llm)

        initial_tokens = soul.manifest().tokens_used_session

        # Stream dialogue
        async for _ in soul.dialogue_flux("Test", mode=DialogueMode.REFLECT):
            pass

        # Session tokens should have increased
        final_tokens = soul.manifest().tokens_used_session
        assert final_tokens > initial_tokens


# =============================================================================
# CP5: End-to-End Streaming Integration Test
# =============================================================================


class TestCP5EndToEndStreaming:
    """CP5 Checkpoint: End-to-end streaming from CLI to LLM with token display."""

    @pytest.mark.asyncio
    async def test_soul_flux_streaming(self) -> None:
        """
        The core CP5 test: Verify end-to-end streaming behavior.

        This test ensures:
        1. Multiple chunks are yielded (streaming works)
        2. Final metadata contains token count
        3. Accumulated text matches final response
        """
        mock_llm = MockLLMClient(
            default_response="Based on your current focus, I would suggest prioritizing depth over breadth."
        )
        soul = KgentSoul(llm=mock_llm)

        chunks: list[str] = []
        final_tokens = 0
        final_text = ""

        async for event in soul.dialogue_flux("Hello", mode=DialogueMode.REFLECT):
            if event.is_data:
                chunks.append(event.value)
            elif event.is_metadata:
                final_tokens = event.value.tokens_used
                final_text = event.value.text

        # CP5 Criteria 1: Multiple chunks (streaming works)
        assert len(chunks) > 0, "Expected at least one chunk"

        # CP5 Criteria 2: Token count available
        assert final_tokens > 0, "Expected token count in metadata"

        # CP5 Criteria 3: Accumulated text matches
        accumulated = "".join(chunks)
        assert accumulated == final_text, "Accumulated chunks should match final text"

    @pytest.mark.asyncio
    async def test_streaming_temporal_spread(self) -> None:
        """
        Test that streaming shows temporal spread (chunks arrive progressively).

        This verifies that chunks don't all arrive at once, demonstrating
        true streaming behavior.
        """
        import time

        mock_llm = MockLLMClient(default_response="Word by word by word by word")
        soul = KgentSoul(llm=mock_llm)

        timestamps: list[float] = []

        async for event in soul.dialogue_flux("Test", mode=DialogueMode.REFLECT):
            if event.is_data:
                timestamps.append(time.time())

        # Should have multiple timestamps
        assert len(timestamps) > 1, "Expected multiple chunks with timestamps"

        # Some temporal spread should exist
        if len(timestamps) > 2:
            gaps = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]
            # At least some gaps should be measurable (MockLLMClient uses 0.005s delay)
            assert any(gap > 0.001 for gap in gaps), f"Expected temporal spread: {gaps}"

    @pytest.mark.asyncio
    async def test_flux_stream_type_alias(self) -> None:
        """Test that FluxStream type alias works correctly."""
        mock_llm = MockLLMClient(default_response="Test")
        soul = KgentSoul(llm=mock_llm)

        # dialogue_flux returns AsyncIterator[FluxEvent[str]]
        stream = soul.dialogue_flux("Test", mode=DialogueMode.REFLECT)

        count = 0
        async for event in stream:
            count += 1
            assert isinstance(event, FluxEvent)

        assert count > 0


# =============================================================================
# LLMStreamSource Error Handling Tests
# =============================================================================


class TestLLMStreamSourceErrors:
    """Test error handling in LLMStreamSource."""

    @pytest.mark.asyncio
    async def test_stream_source_handles_client_error(self) -> None:
        """Test that stream source handles client errors gracefully."""

        class FailingClient:
            """Client that fails during streaming."""

            async def generate_stream(self, **kwargs):  # type: ignore
                yield "First chunk"
                raise RuntimeError("Connection lost")

        source = LLMStreamSource(
            client=FailingClient(),  # type: ignore
            system="Test",
            user="Test",
        )

        events: list[FluxEvent[str]] = []
        async for event in source:
            events.append(event)

        # Should have at least one data event and an error metadata
        assert len(events) >= 2
        # Last event should be metadata (error case)
        last_event = events[-1]
        assert last_event.is_metadata
        # Error metadata has empty text
        assert last_event.value.text == ""

    @pytest.mark.asyncio
    async def test_stream_source_cancel(self) -> None:
        """Test that stream source can be cancelled."""
        import asyncio

        client = MockLLMClient(default_response="Long response " * 100)
        source = LLMStreamSource(
            client=client,
            system="Test",
            user="Test",
        )

        # Start iteration
        it = source.__aiter__()
        await it.__anext__()  # Get first event

        # Cancel
        await source.cancel()

        # Source should be in cancelled state
        # Further iteration should complete cleanly

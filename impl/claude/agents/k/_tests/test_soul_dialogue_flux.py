"""
Tests for C17: KgentSoul.dialogue_flux() Method.

CP7 Checkpoint: End-to-end streaming from soul to CLI and WebSocket clients.
"""

import pytest

from agents.k.flux import FluxEvent, FluxStream
from agents.k.llm import MockLLMClient, StreamingLLMResponse
from agents.k.persona import DialogueMode
from agents.k.soul import BudgetTier, KgentSoul

# =============================================================================
# C17: dialogue_flux() Returns FluxStream
# =============================================================================


class TestDialogueFluxReturnsFluxStream:
    """Test that dialogue_flux() returns a proper FluxStream."""

    def test_dialogue_flux_returns_flux_stream_type(self) -> None:
        """Test that dialogue_flux returns FluxStream, not AsyncIterator."""
        mock_llm = MockLLMClient(default_response="Test response")
        soul = KgentSoul(llm=mock_llm)

        stream = soul.dialogue_flux("Hello", mode=DialogueMode.REFLECT)

        # Should be FluxStream, not just AsyncIterator
        assert isinstance(stream, FluxStream)

    @pytest.mark.asyncio
    async def test_soul_dialogue_flux_returns_stream(self) -> None:
        """
        CP7 Test: dialogue_flux returns a stream with chunks.

        This is the primary verification test from the spec.
        """
        soul = KgentSoul(llm=MockLLMClient())

        stream = soul.dialogue_flux("What should I focus on?", mode=DialogueMode.REFLECT)

        chunks: list[str] = []
        async for event in stream:
            if event.is_data:
                chunks.append(event.value)

        assert len(chunks) > 0
        assert "".join(chunks)  # Non-empty response

    @pytest.mark.asyncio
    async def test_dialogue_flux_yields_data_and_metadata(self) -> None:
        """Test that dialogue_flux yields both data and metadata events."""
        mock_llm = MockLLMClient(default_response="A thoughtful response")
        soul = KgentSoul(llm=mock_llm)

        data_events: list[FluxEvent[str]] = []
        metadata_events: list[FluxEvent[str]] = []

        async for event in soul.dialogue_flux("Hello", mode=DialogueMode.REFLECT):
            if event.is_data:
                data_events.append(event)
            elif event.is_metadata:
                metadata_events.append(event)

        assert len(data_events) > 0, "Should have data events"
        assert len(metadata_events) == 1, "Should have exactly one metadata event"
        assert metadata_events[0].value.tokens_used > 0

    @pytest.mark.asyncio
    async def test_dialogue_flux_accumulated_matches_metadata(self) -> None:
        """Test that accumulated chunks match the final metadata text."""
        test_response = "This is a test response with multiple words"
        mock_llm = MockLLMClient(default_response=test_response)
        soul = KgentSoul(llm=mock_llm)

        chunks: list[str] = []
        final_text = ""

        async for event in soul.dialogue_flux("Test", mode=DialogueMode.REFLECT):
            if event.is_data:
                chunks.append(event.value)
            elif event.is_metadata:
                final_text = event.value.text

        accumulated = "".join(chunks)
        assert accumulated == final_text


# =============================================================================
# C17: FluxStream Operator Chaining
# =============================================================================


class TestDialogueFluxOperators:
    """Test operator chaining on FluxStream from dialogue_flux()."""

    @pytest.mark.asyncio
    async def test_soul_dialogue_flux_with_operators(self) -> None:
        """
        CP7 Test: dialogue_flux works with operator chaining.

        This verifies the FluxStream operators work correctly.
        """
        soul = KgentSoul(llm=MockLLMClient())

        stream = (
            soul.dialogue_flux("Hello", mode=DialogueMode.REFLECT)
            .filter(lambda e: e.is_data and e.value.strip())
            .take(3)
        )

        values = await stream.collect()
        assert len(values) <= 3

    @pytest.mark.asyncio
    async def test_dialogue_flux_filter_operator(self) -> None:
        """Test filter operator on dialogue_flux stream."""
        mock_llm = MockLLMClient(default_response="one two three four five")
        soul = KgentSoul(llm=mock_llm)

        # Filter to only non-whitespace data events
        stream = soul.dialogue_flux("Test", mode=DialogueMode.REFLECT).filter(
            lambda e: e.is_data and len(e.value.strip()) > 0
        )

        chunks: list[str] = []
        async for event in stream:
            if event.is_data:
                chunks.append(event.value)

        # All chunks should be non-empty (after strip)
        assert all(c.strip() for c in chunks)

    @pytest.mark.asyncio
    async def test_dialogue_flux_take_operator(self) -> None:
        """Test take operator limits data events."""
        mock_llm = MockLLMClient(default_response="a b c d e f g h i j")
        soul = KgentSoul(llm=mock_llm)

        # Take only first 3 data events
        stream = soul.dialogue_flux("Test", mode=DialogueMode.REFLECT).take(3)

        data_count = 0
        async for event in stream:
            if event.is_data:
                data_count += 1

        assert data_count <= 3

    @pytest.mark.asyncio
    async def test_dialogue_flux_map_operator(self) -> None:
        """Test map operator transforms events."""
        mock_llm = MockLLMClient(default_response="hello world")
        soul = KgentSoul(llm=mock_llm)

        # Map to uppercase
        stream = soul.dialogue_flux("Test", mode=DialogueMode.REFLECT).map(
            lambda e: FluxEvent.data(e.value.upper()) if e.is_data else e
        )

        chunks: list[str] = []
        async for event in stream:
            if event.is_data:
                chunks.append(event.value)

        accumulated = "".join(chunks)
        assert accumulated.isupper()

    @pytest.mark.asyncio
    async def test_dialogue_flux_tap_operator(self) -> None:
        """Test tap operator for side effects."""
        mock_llm = MockLLMClient(default_response="test")
        soul = KgentSoul(llm=mock_llm)

        side_effect_log: list[str] = []

        # Tap to log chunks
        stream = soul.dialogue_flux("Test", mode=DialogueMode.REFLECT).tap(
            lambda e: side_effect_log.append(e.value) if e.is_data else None
        )

        # Consume stream
        async for _ in stream:
            pass

        # Side effects should have been recorded
        assert len(side_effect_log) > 0

    @pytest.mark.asyncio
    async def test_dialogue_flux_collect(self) -> None:
        """Test collect() materializes stream to list."""
        mock_llm = MockLLMClient(default_response="one two three")
        soul = KgentSoul(llm=mock_llm)

        stream = soul.dialogue_flux("Test", mode=DialogueMode.REFLECT)
        values = await stream.collect()

        # Should have collected data values (not metadata)
        assert len(values) > 0
        assert all(isinstance(v, str) for v in values)


# =============================================================================
# Token Tracking
# =============================================================================


class TestDialogueFluxTokenTracking:
    """Test token tracking through dialogue_flux."""

    @pytest.mark.asyncio
    async def test_dialogue_flux_tracks_tokens(self) -> None:
        """Test that dialogue_flux provides token count in metadata."""
        mock_llm = MockLLMClient(default_response="Response with tokens")
        soul = KgentSoul(llm=mock_llm)

        final_tokens = 0
        async for event in soul.dialogue_flux("Test", mode=DialogueMode.REFLECT):
            if event.is_metadata:
                final_tokens = event.value.tokens_used

        assert final_tokens > 0

    @pytest.mark.asyncio
    async def test_dialogue_flux_updates_session_stats(self) -> None:
        """Test that dialogue_flux updates session statistics."""
        mock_llm = MockLLMClient(default_response="Response with content")
        soul = KgentSoul(llm=mock_llm)

        initial_tokens = soul.manifest().tokens_used_session

        # Consume stream
        async for _ in soul.dialogue_flux("Test", mode=DialogueMode.REFLECT):
            pass

        final_tokens = soul.manifest().tokens_used_session
        assert final_tokens > initial_tokens


# =============================================================================
# Budget Tier Behavior
# =============================================================================


class TestDialogueFluxBudgetTiers:
    """Test dialogue_flux behavior across budget tiers."""

    @pytest.mark.asyncio
    async def test_dialogue_flux_whisper_budget(self) -> None:
        """Test dialogue_flux with WHISPER budget tier."""
        soul = KgentSoul(auto_llm=False)

        tokens = 0
        async for event in soul.dialogue_flux(
            "Test", mode=DialogueMode.REFLECT, budget=BudgetTier.WHISPER
        ):
            if event.is_metadata:
                tokens = event.value.tokens_used

        # Whisper should use ~50 tokens
        assert tokens == 50

    @pytest.mark.asyncio
    async def test_dialogue_flux_empty_message(self) -> None:
        """Test dialogue_flux handles empty message gracefully."""
        soul = KgentSoul(auto_llm=False)

        events: list[FluxEvent[str]] = []
        async for event in soul.dialogue_flux(""):
            events.append(event)

        # Should have data event with fallback response
        assert any(e.is_data for e in events)
        data_events = [e for e in events if e.is_data]
        assert "What's on your mind?" in data_events[0].value

    @pytest.mark.asyncio
    async def test_dialogue_flux_no_llm_fallback(self) -> None:
        """Test dialogue_flux fallback when no LLM available."""
        soul = KgentSoul(auto_llm=False)

        chunks: list[str] = []
        async for event in soul.dialogue_flux("Test message", mode=DialogueMode.REFLECT):
            if event.is_data:
                chunks.append(event.value)

        # Should have a fallback response
        response = "".join(chunks)
        assert len(response) > 0


# =============================================================================
# Mode Handling
# =============================================================================


class TestDialogueFluxModes:
    """Test dialogue_flux handles different dialogue modes."""

    @pytest.mark.asyncio
    async def test_dialogue_flux_reflect_mode(self) -> None:
        """Test dialogue_flux in REFLECT mode."""
        mock_llm = MockLLMClient(default_response="Reflection response")
        soul = KgentSoul(llm=mock_llm)

        stream = soul.dialogue_flux("Test", mode=DialogueMode.REFLECT)
        values = await stream.collect()

        assert len(values) > 0

    @pytest.mark.asyncio
    async def test_dialogue_flux_challenge_mode(self) -> None:
        """Test dialogue_flux in CHALLENGE mode."""
        mock_llm = MockLLMClient(default_response="Challenge response")
        soul = KgentSoul(llm=mock_llm)

        stream = soul.dialogue_flux("Test", mode=DialogueMode.CHALLENGE)
        values = await stream.collect()

        assert len(values) > 0

    @pytest.mark.asyncio
    async def test_dialogue_flux_advise_mode(self) -> None:
        """Test dialogue_flux in ADVISE mode."""
        mock_llm = MockLLMClient(default_response="Advice response")
        soul = KgentSoul(llm=mock_llm)

        stream = soul.dialogue_flux("Test", mode=DialogueMode.ADVISE)
        values = await stream.collect()

        assert len(values) > 0

    @pytest.mark.asyncio
    async def test_dialogue_flux_uses_default_mode(self) -> None:
        """Test dialogue_flux uses default mode when none specified."""
        mock_llm = MockLLMClient(default_response="Default response")
        soul = KgentSoul(llm=mock_llm)
        soul.active_mode = DialogueMode.EXPLORE

        # Don't specify mode
        stream = soul.dialogue_flux("Test")
        values = await stream.collect()

        assert len(values) > 0
        # Mode should have been used from soul's active_mode
        assert soul.active_mode == DialogueMode.EXPLORE

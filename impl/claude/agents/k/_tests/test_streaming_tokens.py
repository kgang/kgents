"""Tests for Wave 4: Morpheus Native Streaming with token counts.

CP4 Checkpoint: Verify streaming with accurate token counts.
"""

import pytest
from agents.k.llm import MockLLMClient, StreamingLLMResponse
from agents.k.persona import DialogueInput, DialogueMode, KgentAgent
from agents.k.soul import KgentSoul


class TestStreamingLLMResponse:
    """Test StreamingLLMResponse dataclass."""

    def test_create_response(self) -> None:
        """Test creating a StreamingLLMResponse."""
        response = StreamingLLMResponse(
            text="Hello world",
            tokens_used=100,
            model="test-model",
            prompt_tokens=50,
            completion_tokens=50,
        )
        assert response.text == "Hello world"
        assert response.tokens_used == 100
        assert response.model == "test-model"
        assert response.prompt_tokens == 50
        assert response.completion_tokens == 50

    def test_default_values(self) -> None:
        """Test default values in StreamingLLMResponse."""
        response = StreamingLLMResponse(
            text="Test",
            tokens_used=10,
        )
        assert response.model == ""
        assert response.prompt_tokens == 0
        assert response.completion_tokens == 0
        assert response.raw_metadata is None


class TestMockLLMClientStreaming:
    """Test MockLLMClient streaming with token counts."""

    @pytest.mark.asyncio
    async def test_generate_stream_yields_chunks(self) -> None:
        """Test that generate_stream yields text chunks."""
        client = MockLLMClient(default_response="Hello world test")
        chunks: list[str] = []
        final_response: StreamingLLMResponse | None = None

        async for item in client.generate_stream(
            system="Test system",
            user="Test user",
        ):
            if isinstance(item, str):
                chunks.append(item)
            else:
                final_response = item

        # Should have text chunks
        assert len(chunks) > 0
        # Should have final response
        assert final_response is not None
        assert isinstance(final_response, StreamingLLMResponse)

    @pytest.mark.asyncio
    async def test_generate_stream_final_has_tokens(self) -> None:
        """Test that final StreamingLLMResponse has token counts."""
        client = MockLLMClient(default_response="Hello world")
        final_response: StreamingLLMResponse | None = None

        async for item in client.generate_stream(
            system="Test",
            user="Test",
        ):
            if isinstance(item, StreamingLLMResponse):
                final_response = item

        assert final_response is not None
        assert final_response.tokens_used > 0
        assert final_response.text == "Hello world"

    @pytest.mark.asyncio
    async def test_generate_stream_text_matches(self) -> None:
        """Test that accumulated chunks match final text."""
        test_response = "The quick brown fox jumps over the lazy dog"
        client = MockLLMClient(default_response=test_response)
        chunks: list[str] = []
        final_response: StreamingLLMResponse | None = None

        async for item in client.generate_stream(
            system="Test",
            user="Test",
        ):
            if isinstance(item, str):
                chunks.append(item)
            else:
                final_response = item

        accumulated = "".join(chunks)
        assert final_response is not None
        assert accumulated == final_response.text


class TestKgentAgentInvokeStream:
    """Test KgentAgent.invoke_stream with token counts."""

    @pytest.mark.asyncio
    async def test_invoke_stream_yields_tokens(self) -> None:
        """Test that invoke_stream returns token counts in final tuple."""
        mock_llm = MockLLMClient(default_response="Test response")
        agent = KgentAgent(llm=mock_llm)

        input_data = DialogueInput(
            message="Test message",
            mode=DialogueMode.REFLECT,
        )

        chunks: list[str] = []
        final_tokens = 0

        async for chunk, is_final, tokens in agent.invoke_stream(input_data):
            if chunk:
                chunks.append(chunk)
            if is_final:
                final_tokens = tokens

        assert len(chunks) > 0
        assert final_tokens > 0

    @pytest.mark.asyncio
    async def test_invoke_stream_without_llm(self) -> None:
        """Test that invoke_stream works without LLM (template fallback)."""
        agent = KgentAgent(llm=None)  # No LLM

        input_data = DialogueInput(
            message="Test message",
            mode=DialogueMode.REFLECT,
        )

        chunks: list[str] = []
        final_tokens = 0

        async for chunk, is_final, tokens in agent.invoke_stream(input_data):
            if chunk:
                chunks.append(chunk)
            if is_final:
                final_tokens = tokens

        # Should have one chunk (template response)
        assert len(chunks) == 1
        # Should have estimated tokens
        assert final_tokens > 0


class TestKgentSoulStreamingBudget:
    """Test KgentSoul streaming with budget awareness."""

    @pytest.mark.asyncio
    async def test_dialogue_with_streaming_captures_tokens(self) -> None:
        """Test that dialogue() with streaming captures actual token counts."""
        mock_llm = MockLLMClient(default_response="A streaming response with content")
        soul = KgentSoul(llm=mock_llm)

        chunks_received: list[str] = []

        def on_chunk(chunk: str) -> None:
            chunks_received.append(chunk)

        output = await soul.dialogue(
            "Test message",
            mode=DialogueMode.REFLECT,
            on_chunk=on_chunk,
        )

        # Should have received chunks
        assert len(chunks_received) > 0
        # Should have token count from streaming
        assert output.tokens_used > 0
        # Response should match accumulated chunks
        assert output.response == "".join(chunks_received)

    @pytest.mark.asyncio
    async def test_dialogue_without_streaming_estimates_tokens(self) -> None:
        """Test that dialogue() without streaming estimates tokens."""
        mock_llm = MockLLMClient(default_response="A non-streaming response")
        soul = KgentSoul(llm=mock_llm)

        # No on_chunk callback = no streaming
        output = await soul.dialogue(
            "Test message",
            mode=DialogueMode.REFLECT,
        )

        # Should have estimated token count
        assert output.tokens_used > 0
        # Should have response
        assert len(output.response) > 0

    @pytest.mark.asyncio
    async def test_session_tracks_streaming_tokens(self) -> None:
        """Test that session stats track tokens from streaming."""
        mock_llm = MockLLMClient(
            responses=["First response", "Second response", "Third response"]
        )
        soul = KgentSoul(llm=mock_llm)

        # Initial state
        assert soul.manifest().tokens_used_session == 0

        chunks: list[str] = []

        # First dialogue with streaming
        await soul.dialogue("First", on_chunk=lambda c: chunks.append(c))
        first_tokens = soul.manifest().tokens_used_session

        # Second dialogue with streaming
        await soul.dialogue("Second", on_chunk=lambda c: chunks.append(c))
        second_tokens = soul.manifest().tokens_used_session

        # Session should accumulate tokens
        assert first_tokens > 0
        assert second_tokens > first_tokens

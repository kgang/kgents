"""
Tests for Morpheus streaming support.
"""

import pytest

from services.morpheus import (
    ChatMessage,
    ChatRequest,
    MorpheusGateway,
    MorpheusPersistence,
    StreamChunk,
)
from services.morpheus.adapters.mock import MockAdapter


@pytest.fixture
def gateway_with_streaming() -> MorpheusGateway:
    """Gateway with streaming-enabled mock adapter."""
    gateway = MorpheusGateway()
    adapter = MockAdapter(streaming_enabled=True, chunk_size=5)
    gateway.register_provider("mock", adapter, prefix="mock-")
    return gateway


@pytest.fixture
def persistence_with_streaming(
    gateway_with_streaming: MorpheusGateway,
) -> MorpheusPersistence:
    """Persistence layer with streaming support."""
    return MorpheusPersistence(gateway=gateway_with_streaming, telemetry_enabled=False)


class TestMockAdapterStreaming:
    """Tests for MockAdapter streaming."""

    async def test_stream_returns_chunks(self):
        """Stream should yield multiple chunks."""
        adapter = MockAdapter(chunk_size=5)
        adapter.queue_response("Hello World!")

        request = ChatRequest(
            model="mock-test",
            messages=[ChatMessage(role="user", content="test")],
        )

        chunks = []
        async for chunk in adapter.stream(request):
            chunks.append(chunk)

        # Should have content chunks + final chunk
        assert len(chunks) > 1
        # Last chunk should have finish_reason
        assert chunks[-1].choices[0].finish_reason == "stop"

    async def test_stream_content_matches(self):
        """Streaming content should match queued response."""
        adapter = MockAdapter(chunk_size=3)
        adapter.queue_response("Hello")

        request = ChatRequest(
            model="mock-test",
            messages=[ChatMessage(role="user", content="test")],
        )

        content = ""
        async for chunk in adapter.stream(request):
            if chunk.choices and chunk.choices[0].delta.content:
                content += chunk.choices[0].delta.content

        assert content == "Hello"

    async def test_supports_streaming_true(self):
        """MockAdapter should report streaming support."""
        adapter = MockAdapter(streaming_enabled=True)
        assert adapter.supports_streaming() is True

    async def test_supports_streaming_false(self):
        """MockAdapter can disable streaming."""
        adapter = MockAdapter(streaming_enabled=False)
        assert adapter.supports_streaming() is False


class TestGatewayStreaming:
    """Tests for MorpheusGateway streaming."""

    async def test_gateway_stream_routes_correctly(
        self, gateway_with_streaming: MorpheusGateway
    ):
        """Gateway should route streaming requests to correct provider."""
        request = ChatRequest(
            model="mock-test",
            messages=[ChatMessage(role="user", content="test")],
        )

        chunks = []
        async for chunk in gateway_with_streaming.stream(request):
            chunks.append(chunk)

        assert len(chunks) > 0

    async def test_gateway_stream_unknown_model_yields_error(
        self, gateway_with_streaming: MorpheusGateway
    ):
        """Gateway should yield error for unknown model."""
        request = ChatRequest(
            model="unknown-model",
            messages=[ChatMessage(role="user", content="test")],
        )

        chunks = []
        async for chunk in gateway_with_streaming.stream(request):
            chunks.append(chunk)

        # Should have error message in first chunk
        assert len(chunks) >= 1
        first_content = chunks[0].choices[0].delta.content
        assert "No provider found" in first_content

    async def test_gateway_stream_no_streaming_support_yields_error(self):
        """Gateway should yield error for non-streaming provider."""
        gateway = MorpheusGateway()
        adapter = MockAdapter(streaming_enabled=False)
        gateway.register_provider("mock", adapter, prefix="mock-")

        request = ChatRequest(
            model="mock-test",
            messages=[ChatMessage(role="user", content="test")],
        )

        chunks = []
        async for chunk in gateway.stream(request):
            chunks.append(chunk)

        assert len(chunks) >= 1
        first_content = chunks[0].choices[0].delta.content
        assert "does not support streaming" in first_content


class TestPersistenceStreaming:
    """Tests for MorpheusPersistence streaming."""

    async def test_persistence_stream_yields_chunks(
        self, persistence_with_streaming: MorpheusPersistence
    ):
        """Persistence should yield streaming chunks."""
        request = ChatRequest(
            model="mock-test",
            messages=[ChatMessage(role="user", content="test")],
        )

        chunks = []
        async for chunk in persistence_with_streaming.stream(request):
            chunks.append(chunk)

        assert len(chunks) > 0


class TestStreamChunk:
    """Tests for StreamChunk type."""

    def test_from_text_creates_chunk(self):
        """from_text should create a content chunk."""
        chunk = StreamChunk.from_text("Hello", "test-id", "test-model")

        assert chunk.id == "test-id"
        assert chunk.model == "test-model"
        assert len(chunk.choices) == 1
        assert chunk.choices[0].delta.content == "Hello"
        assert chunk.choices[0].finish_reason is None

    def test_final_creates_finish_chunk(self):
        """final should create a chunk with finish_reason."""
        chunk = StreamChunk.final("test-id", "test-model")

        assert chunk.id == "test-id"
        assert len(chunk.choices) == 1
        assert chunk.choices[0].delta.content is None
        assert chunk.choices[0].finish_reason == "stop"

    def test_to_sse_format(self):
        """to_sse should format as Server-Sent Events."""
        chunk = StreamChunk.from_text("Hi", "test-id", "test-model")
        sse = chunk.to_sse()

        assert sse.startswith("data: ")
        assert sse.endswith("\n\n")
        assert '"content": "Hi"' in sse

    def test_to_dict_serialization(self):
        """to_dict should create serializable dict."""
        chunk = StreamChunk.from_text("Test", "id", "model")
        d = chunk.to_dict()

        assert d["id"] == "id"
        assert d["object"] == "chat.completion.chunk"
        assert d["model"] == "model"
        assert d["choices"][0]["delta"]["content"] == "Test"

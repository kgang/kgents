"""
Tests for K-gent Bridge: Chat LLM integration.

Verifies:
- K-gent Soul integration for chat responses
- Streaming SSE format
- Witness mark creation for each turn
- Graceful fallback when LLM unavailable
"""

import pytest

from agents.k import BudgetTier, DialogueMode, MockLLMClient
from services.chat import ChatContext, KgentBridge
from services.witness import MarkQuery, get_mark_store, reset_mark_store


@pytest.fixture
def mark_store():
    """Provide a clean mark store for each test."""
    reset_mark_store()
    store = get_mark_store()
    yield store
    reset_mark_store()


@pytest.fixture
def mock_bridge(mark_store):
    """Create a K-gent bridge with mock LLM."""
    from agents.k import KgentSoul

    # Create mock LLM client
    mock_llm = MockLLMClient(
        responses=["This is a helpful response from K-gent about your question."]
    )

    # Create soul with mock LLM
    soul = KgentSoul(llm=mock_llm, auto_llm=False)

    # Create bridge
    bridge = KgentBridge(soul=soul, mark_store=mark_store)

    return bridge


@pytest.mark.asyncio
async def test_bridge_streaming_response(mock_bridge):
    """Test that bridge streams response via K-gent."""
    context = ChatContext(
        session_id="test-session-1",
        turn_number=1,
        user_message="What is the best architectural pattern for agents?",
        mode=DialogueMode.ADVISE,
        budget=BudgetTier.DIALOGUE,
    )

    chunks = []
    async for chunk in mock_bridge.stream_response(context):
        chunks.append(chunk)

    # Should have received chunks
    assert len(chunks) > 0

    # Last chunk should be "done" type
    last_chunk = chunks[-1]
    assert "done" in last_chunk or "error" in last_chunk

    # Should have content chunks
    content_chunks = [c for c in chunks if '"type": "content"' in c]
    assert len(content_chunks) > 0


@pytest.mark.asyncio
async def test_bridge_creates_witness_mark(mock_bridge, mark_store):
    """Test that bridge creates a witness mark for each turn."""
    context = ChatContext(
        session_id="test-session-2",
        turn_number=1,
        user_message="How should I structure my code?",
    )

    # Initially no marks
    marks_before = list(mark_store.all())
    assert len(marks_before) == 0

    # Stream response
    chunks = []
    async for chunk in mock_bridge.stream_response(context):
        chunks.append(chunk)

    # Should have created a witness mark
    marks_after = list(mark_store.all())
    assert len(marks_after) == 1

    # Verify mark contains session context
    mark = marks_after[0]
    assert mark.stimulus.metadata["session_id"] == "test-session-2"
    assert mark.stimulus.metadata["turn_number"] == 1
    assert mark.stimulus.content == "How should I structure my code?"


@pytest.mark.asyncio
async def test_bridge_sse_format(mock_bridge):
    """Test that bridge outputs valid SSE format."""
    context = ChatContext(
        session_id="test-session-3",
        turn_number=1,
        user_message="Tell me about SSE",
    )

    chunks = []
    async for chunk in mock_bridge.stream_response(context):
        chunks.append(chunk)

    # All chunks should be valid SSE format
    for chunk in chunks:
        # SSE format: "data: {json}\n\n"
        assert chunk.startswith("data: ")
        assert chunk.endswith("\n\n")

        # Should be valid JSON
        import json

        json_str = chunk[6:].strip()
        if json_str:
            data = json.loads(json_str)
            assert "type" in data
            assert data["type"] in ["content", "done", "error"]


@pytest.mark.asyncio
async def test_bridge_without_llm(mark_store):
    """Test that bridge gracefully handles missing LLM."""
    from agents.k import KgentSoul

    # Create soul without LLM
    soul = KgentSoul(llm=None, auto_llm=False)
    bridge = KgentBridge(soul=soul, mark_store=mark_store)

    context = ChatContext(
        session_id="test-session-4",
        turn_number=1,
        user_message="This should fallback gracefully",
    )

    chunks = []
    async for chunk in bridge.stream_response(context):
        chunks.append(chunk)

    # Should have chunks (fallback message)
    assert len(chunks) > 0

    # Should indicate fallback in done event
    import json

    done_chunk = chunks[-1]
    data = json.loads(done_chunk[6:].strip())
    # Either error or done with fallback flag
    assert data["type"] in ["done", "error"]


@pytest.mark.asyncio
async def test_bridge_preserves_context(mock_bridge, mark_store):
    """Test that bridge preserves session context across turns."""
    # Turn 1
    context1 = ChatContext(
        session_id="test-session-5",
        turn_number=1,
        user_message="First question",
    )

    chunks1 = []
    async for chunk in mock_bridge.stream_response(context1):
        chunks1.append(chunk)

    # Turn 2
    context2 = ChatContext(
        session_id="test-session-5",
        turn_number=2,
        user_message="Second question",
    )

    chunks2 = []
    async for chunk in mock_bridge.stream_response(context2):
        chunks2.append(chunk)

    # Should have two marks
    marks = list(mark_store.all())
    assert len(marks) == 2

    # Both marks should be from same session
    assert marks[0].stimulus.metadata["session_id"] == "test-session-5"
    assert marks[1].stimulus.metadata["session_id"] == "test-session-5"

    # But different turn numbers
    assert marks[0].stimulus.metadata["turn_number"] == 1
    assert marks[1].stimulus.metadata["turn_number"] == 2

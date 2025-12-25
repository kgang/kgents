"""
Integration test for real LLM streaming in chat.

This test verifies that when LLM credentials are available,
the chat system properly streams responses from K-gent Soul.

IMPORTANT: This test requires either:
- MORPHEUS_URL environment variable set to a Morpheus Gateway endpoint
- Claude CLI installed and authenticated

To run:
    MORPHEUS_URL=http://localhost:8080/v1 pytest services/chat/_tests/test_llm_integration.py -v
"""

import pytest

from agents.k import has_llm_credentials
from services.chat import ChatContext, create_kgent_bridge


@pytest.mark.skipif(
    not has_llm_credentials(),
    reason="No LLM credentials available (set MORPHEUS_URL or install claude CLI)",
)
@pytest.mark.asyncio
async def test_real_llm_streaming():
    """Test that real LLM streaming works end-to-end."""
    bridge = create_kgent_bridge()

    # Verify LLM is available
    assert bridge.has_llm, "Bridge should have LLM when credentials are available"

    context = ChatContext(
        session_id="integration-test-1",
        turn_number=1,
        user_message="What is 2+2? Answer with just the number.",
    )

    chunks = []
    content = ""

    async for chunk in bridge.stream_response(context):
        chunks.append(chunk)

        # Extract content from SSE format
        if chunk.startswith("data: "):
            import json

            try:
                data = json.loads(chunk[6:].strip())
                if data.get("type") == "content":
                    content = data.get("content", "")
            except json.JSONDecodeError:
                pass

    # Should have received chunks
    assert len(chunks) > 0, "Should receive streaming chunks"

    # Should have accumulated content
    assert len(content) > 0, "Should have accumulated content from LLM"

    # Last chunk should be done type
    import json

    last_chunk = chunks[-1]
    last_data = json.loads(last_chunk[6:].strip())
    assert last_data["type"] == "done", "Last chunk should be done type"

    # Should have turn data
    turn_data = last_data.get("turn")
    assert turn_data is not None, "Done chunk should include turn data"
    assert turn_data["turn_number"] == 1
    assert turn_data["session_id"] == "integration-test-1"
    assert "mark_id" in turn_data, "Turn should have witness mark ID"

    print(f"\n✓ LLM Response: {content[:100]}...")
    print(f"✓ Received {len(chunks)} chunks")
    print(f"✓ Mark ID: {turn_data['mark_id']}")


@pytest.mark.skipif(
    has_llm_credentials(),
    reason="Test fallback behavior when no LLM available",
)
@pytest.mark.asyncio
async def test_fallback_without_credentials():
    """Test that system gracefully falls back when no LLM available."""
    bridge = create_kgent_bridge()

    # Should not have LLM
    assert not bridge.has_llm, "Bridge should not have LLM without credentials"

    context = ChatContext(
        session_id="fallback-test-1",
        turn_number=1,
        user_message="This should fallback gracefully",
    )

    chunks = []
    content = ""

    async for chunk in bridge.stream_response(context):
        chunks.append(chunk)

        if chunk.startswith("data: "):
            import json

            try:
                data = json.loads(chunk[6:].strip())
                if data.get("type") == "content":
                    content = data.get("content", "")
            except json.JSONDecodeError:
                pass

    # Should have received fallback message
    assert len(chunks) > 0
    assert "LLM credentials" in content or "MORPHEUS_URL" in content
    assert "Claude CLI" in content

    print(f"\n✓ Fallback message: {content}")

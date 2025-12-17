"""
Mock Adapter: Testing adapter with queued responses.

Provides a mock LLM backend for testing without real API calls.
Supports queued responses, request history tracking, and streaming.
"""

from __future__ import annotations

import uuid
from typing import Any, AsyncIterator, Optional

from ..types import ChatRequest, ChatResponse, StreamChunk


class MockAdapter:
    """Mock adapter for testing without real LLM calls."""

    def __init__(
        self,
        responses: Optional[list[str]] = None,
        default_response: str = "Mock response from Morpheus",
        *,
        streaming_enabled: bool = True,
        chunk_size: int = 10,  # Characters per chunk for streaming
    ) -> None:
        self._responses = list(responses) if responses else []
        self._default_response = default_response
        self._request_count = 0
        self._history: list[ChatRequest] = []
        self._streaming_enabled = streaming_enabled
        self._chunk_size = chunk_size

    async def complete(self, request: ChatRequest) -> ChatResponse:
        """Return mock response."""
        self._request_count += 1
        self._history.append(request)

        if self._responses:
            text = self._responses.pop(0)
        else:
            text = self._default_response

        return ChatResponse.from_text(
            text=text,
            model=request.model,
            prompt_tokens=100,
            completion_tokens=50,
        )

    async def stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        """Stream mock response in chunks."""
        self._request_count += 1
        self._history.append(request)

        if self._responses:
            text = self._responses.pop(0)
        else:
            text = self._default_response

        chunk_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"

        # Yield content in chunks
        for i in range(0, len(text), self._chunk_size):
            chunk_text = text[i : i + self._chunk_size]
            yield StreamChunk.from_text(chunk_text, chunk_id, request.model)

        # Yield final chunk with finish_reason
        yield StreamChunk.final(chunk_id, request.model)

    def is_available(self) -> bool:
        return True

    def supports_streaming(self) -> bool:
        return self._streaming_enabled

    def health_check(self) -> dict[str, Any]:
        return {
            "adapter": "mock",
            "available": True,
            "total_requests": self._request_count,
            "supports_streaming": self._streaming_enabled,
        }

    @property
    def history(self) -> list[ChatRequest]:
        """Request history for testing assertions."""
        return self._history

    def queue_response(self, response: str) -> None:
        """Add a response to the queue."""
        self._responses.append(response)

    def clear_history(self) -> None:
        """Clear request history."""
        self._history.clear()


__all__ = ["MockAdapter"]

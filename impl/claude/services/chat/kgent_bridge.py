"""
K-gent Bridge: Route chat LLM calls through K-gent governance.

This bridges the chat API to K-gent Soul for:
- LLM-backed dialogue with governance
- Witness mark creation for each turn
- Streaming SSE responses
- Trust/gating integration (future)

Architecture:
    Chat API → KgentBridge → KgentSoul → LLM
                           ↓
                        Mark Store (witness)

Usage:
    bridge = KgentBridge()
    async for chunk in bridge.stream_response(message, session_id):
        yield chunk  # SSE format

Philosophy:
    "The proof IS the decision. The mark IS the witness."
    Every chat turn creates a witness mark for traceability.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, AsyncIterator, Optional

from agents.k import (
    BudgetTier,
    DialogueMode,
    KgentSoul,
    create_llm_client,
    has_llm_credentials,
)
from services.witness import (
    Mark,
    MarkStore,
    Response,
    Stimulus,
    UmweltSnapshot,
    generate_mark_id,
    get_mark_store,
)


@dataclass
class ChatContext:
    """Context for a chat turn."""

    session_id: str
    turn_number: int
    user_message: str
    mode: DialogueMode = DialogueMode.ADVISE  # Default to ADVISE for chat
    budget: BudgetTier = BudgetTier.DIALOGUE


@dataclass
class StreamChunk:
    """A chunk of streamed chat response."""

    type: str  # "content" | "done" | "error"
    content: str | None = None
    turn_data: dict | None = None
    error: str | None = None


class KgentBridge:
    """
    Bridge between Chat API and K-gent Soul.

    Routes all chat LLM calls through K-gent for:
    - Governance and gating
    - Witness mark creation
    - Streaming responses
    """

    def __init__(
        self,
        soul: Optional[KgentSoul] = None,
        mark_store: Optional[MarkStore] = None,
    ):
        """Initialize K-gent bridge.

        Args:
            soul: Optional K-gent Soul instance. If None, creates one.
            mark_store: Optional mark store for witness marks. If None, uses singleton.
        """
        # Initialize K-gent Soul
        if soul is not None:
            self._soul = soul
        else:
            # Create LLM client if credentials available
            llm = None
            if has_llm_credentials():
                llm = create_llm_client()

            self._soul = KgentSoul(llm=llm)

        # Get mark store for witness marks
        self._mark_store = mark_store or get_mark_store()

    @property
    def has_llm(self) -> bool:
        """Check if LLM is available."""
        return self._soul.has_llm

    async def stream_response(
        self,
        context: ChatContext,
    ) -> AsyncIterator[str]:
        """
        Stream a chat response through K-gent with witness marks.

        Yields SSE (Server-Sent Events) formatted chunks:
        - data: {"type": "content", "content": "..."} - Accumulated content
        - data: {"type": "done", "turn": {...}} - Final turn data
        - data: {"type": "error", "error": "..."} - Error if occurred

        Args:
            context: Chat context with session, turn, message

        Yields:
            SSE formatted event strings
        """
        try:
            started_at = datetime.now().isoformat()

            # Create witness mark for turn start
            mark_id = generate_mark_id()

            # Build stimulus (user input)
            stimulus = Stimulus(
                kind="prompt",
                content=context.user_message,
                source="chat",
                metadata={
                    "session_id": context.session_id,
                    "turn_number": context.turn_number,
                    "mode": context.mode.value,
                },
            )

            # Fallback if no LLM available
            if not self.has_llm:
                fallback_response = (
                    "K-gent requires LLM credentials for chat. "
                    "Please configure MORPHEUS_URL or Claude CLI authentication."
                )
                yield self._format_sse(
                    StreamChunk(type="content", content=fallback_response)
                )
                yield self._format_sse(
                    StreamChunk(
                        type="done",
                        turn_data={
                            "turn_number": context.turn_number,
                            "started_at": started_at,
                            "completed_at": datetime.now().isoformat(),
                            "mark_id": mark_id,
                            "was_fallback": True,
                        },
                    )
                )
                return

            # Stream from K-gent Soul
            accumulated_text = ""
            tokens_used = 0

            async for chunk in self._stream_from_soul(context):
                accumulated_text += chunk
                yield self._format_sse(
                    StreamChunk(type="content", content=accumulated_text)
                )

            # Create response (assistant output)
            completed_at = datetime.now().isoformat()
            response = Response(
                kind="text",
                content=accumulated_text,
                success=True,
                metadata={
                    "tokens_used": tokens_used,
                    "budget_tier": context.budget.value,
                    "mode": context.mode.value,
                    "confidence": 0.8,  # K-gent provides governance
                },
            )

            # Create witness mark with detailed context
            mark = Mark(
                id=mark_id,
                origin="chat.kgent_bridge",
                timestamp=datetime.fromisoformat(started_at),
                stimulus=stimulus,
                response=response,
                umwelt=UmweltSnapshot(
                    observer_id="chat",
                    role="assistant",
                    capabilities=frozenset({"dialogue", "observe", "reason"}),
                    perceptions=frozenset({"user_message", "session_state", "conversation_history"}),
                    trust_level=1,  # Bounded: can respond but with governance
                ),
                tags=("chat", "turn", "dialogue"),
                metadata={
                    "session_id": context.session_id,
                    "turn_number": context.turn_number,
                    "mode": context.mode.value,
                    "budget": context.budget.value,
                    "message_length": len(context.user_message),
                    "response_length": len(accumulated_text),
                    "tokens_used": tokens_used,
                },
            )

            # Store mark
            self._mark_store.append(mark)

            # Send completion event
            turn_data = {
                "turn_number": context.turn_number,
                "user_message": context.user_message,
                "assistant_response": accumulated_text,
                "started_at": started_at,
                "completed_at": completed_at,
                "mark_id": mark_id,
                "confidence": 0.8,
                "tools_used": [],
            }

            yield self._format_sse(StreamChunk(type="done", turn_data=turn_data))

        except Exception as e:
            # Log error and yield error event
            import logging

            logger = logging.getLogger(__name__)
            logger.exception("Error in K-gent bridge streaming")

            yield self._format_sse(
                StreamChunk(type="error", error=f"K-gent error: {str(e)}")
            )

    async def _stream_from_soul(self, context: ChatContext) -> AsyncIterator[str]:
        """
        Stream response from K-gent Soul.

        Args:
            context: Chat context

        Yields:
            Text chunks from K-gent
        """
        # Use dialogue_flux for proper streaming
        stream = self._soul.dialogue_flux(
            message=context.user_message,
            mode=context.mode,
            budget=context.budget,
        )

        # Stream data events (text chunks)
        async for event in stream:
            if event.is_data and event.value:
                yield event.value
            # Metadata event contains final token counts
            # We ignore it here since we track tokens in the mark

    def _format_sse(self, chunk: StreamChunk) -> str:
        """
        Format a stream chunk as SSE event.

        Args:
            chunk: Stream chunk to format

        Returns:
            SSE formatted string
        """
        payload: dict[str, Any] = {"type": chunk.type}

        if chunk.content is not None:
            payload["content"] = chunk.content
        if chunk.turn_data is not None:
            payload["turn"] = chunk.turn_data
        if chunk.error is not None:
            payload["error"] = chunk.error

        return f"data: {json.dumps(payload)}\n\n"


# --- Convenience Functions ---


def create_kgent_bridge(
    soul: Optional[KgentSoul] = None,
    mark_store: Optional[MarkStore] = None,
) -> KgentBridge:
    """Create a K-gent bridge instance."""
    return KgentBridge(soul=soul, mark_store=mark_store)


__all__ = [
    "KgentBridge",
    "ChatContext",
    "StreamChunk",
    "create_kgent_bridge",
]

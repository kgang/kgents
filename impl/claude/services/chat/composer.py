"""
ChatMorpheusComposer: Functor composition of Chat and Morpheus.

Per spec/protocols/chat-morpheus-synergy.md Part II & IV:

This is NOT an adapter. It's a composition that:
1. Preserves both coalgebra states (Chat state × Morpheus state)
2. Transforms messages without re-parsing
3. Maintains observer context throughout
4. Updates session state with actual token counts

The composition is horizontal (parallel state), not vertical (sequential):
    (ChatCoalgebra ⊗ MorpheusCoalgebra) : (S_chat × S_morpheus) × Message → (S_chat × S_morpheus) × Response

Lives in services/chat/ per AD-009 (Metaphysical Fullstack).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, AsyncIterator, Callable

from .model_selector import MorpheusConfig, default_model_selector
from .transformer import (
    to_morpheus_request,
    from_morpheus_response,
    extract_usage,
    to_streaming_request,
)

if TYPE_CHECKING:
    from .session import ChatSession, Message
    from services.morpheus.persistence import MorpheusPersistence
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger(__name__)


# === Result Types ===


@dataclass
class TurnResult:
    """
    Result of a composed turn.

    Contains the response content plus metadata from both coalgebras.
    """

    content: str
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0
    model: str = ""
    error: str | None = None
    fallback: bool = False

    @property
    def success(self) -> bool:
        """Whether the turn completed without errors."""
        return self.error is None

    @property
    def total_tokens(self) -> int:
        """Total tokens used in this turn."""
        return self.tokens_in + self.tokens_out


# === The Composer ===


@dataclass
class ChatMorpheusComposer:
    """
    Composes ChatSession with MorpheusPersistence.

    Lives in services/chat/ per AD-009 (Metaphysical Fullstack).

    The composer:
    1. Transforms ChatMessage → MorpheusRequest
    2. Preserves observer context through the chain
    3. Transforms MorpheusResponse → ChatResponse
    4. Returns actual token counts from gateway
    """

    morpheus: "MorpheusPersistence"
    model_selector: Callable[["Umwelt", str], MorpheusConfig] = field(
        default=default_model_selector
    )

    async def compose_turn(
        self,
        session: "ChatSession",
        message: str,
        observer: "Umwelt",
    ) -> TurnResult:
        """
        Execute a complete turn through the composition.

        ChatSession.send() delegates here; we don't replace ChatSession.

        Args:
            session: The chat session (provides context)
            message: User's message
            observer: The observer's umwelt (affects model selection)

        Returns:
            TurnResult with response and metadata
        """
        # 1. Get working context from session (structured, not string)
        context = self._get_context_messages(session)

        # 2. Select model based on observer
        config = self.model_selector(observer, session.node_path)
        logger.debug(
            f"Selected model {config.model} for observer archetype, path {session.node_path}"
        )

        # 3. Transform to Morpheus request (no parsing!)
        system_prompt = session.config.system_prompt if session.config else None
        request = to_morpheus_request(context, message, config, system_prompt)

        # 4. Get observer archetype for rate limiting
        archetype = self._get_archetype(observer)

        # 5. Invoke through Morpheus (preserves its state)
        try:
            result = await self.morpheus.complete(request, archetype)

            # 6. Transform back to chat response
            response_content = from_morpheus_response(result)
            tokens_in, tokens_out = extract_usage(result)

            # 7. Return result with actual tokens
            return TurnResult(
                content=response_content,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                latency_ms=result.latency_ms,
                model=config.model,
            )

        except Exception as e:
            # Graceful degradation: return error as content
            logger.warning(f"Morpheus composition failed: {e}")
            return TurnResult(
                content=f"[LLM Error] {e}",
                tokens_in=0,
                tokens_out=0,
                latency_ms=0,
                model=config.model,
                error=str(e),
                fallback=True,
            )

    async def compose_stream(
        self,
        session: "ChatSession",
        message: str,
        observer: "Umwelt",
    ) -> AsyncIterator[str]:
        """
        Streaming composition.

        Yields tokens as they arrive from Morpheus.

        Args:
            session: The chat session
            message: User's message
            observer: The observer's umwelt

        Yields:
            Individual tokens/chunks as strings
        """
        # 1. Get context and config
        context = self._get_context_messages(session)
        config = self.model_selector(observer, session.node_path)
        system_prompt = session.config.system_prompt if session.config else None

        # 2. Create streaming request
        request = to_streaming_request(context, message, config, system_prompt)

        # 3. Get archetype
        archetype = self._get_archetype(observer)

        # 4. Stream from Morpheus
        try:
            async for chunk in self.morpheus.stream(request, archetype):
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.warning(f"Morpheus streaming failed: {e}")
            yield f"\n[Streaming Error] {e}"

    def _get_context_messages(self, session: "ChatSession") -> list["Message"]:
        """Get context messages from session."""
        # Use session's get_messages() which returns Message objects
        return session.get_messages()

    def _get_archetype(self, observer: "Umwelt") -> str:
        """Extract archetype from observer for rate limiting."""
        try:
            meta = observer.meta
            return getattr(meta, "archetype", "guest")
        except Exception:
            return "guest"


# === Factory Helper ===


def create_composer(
    morpheus: "MorpheusPersistence",
    model_selector: Callable[["Umwelt", str], MorpheusConfig] | None = None,
) -> ChatMorpheusComposer:
    """
    Create a ChatMorpheusComposer.

    Convenience factory for dependency injection.

    Args:
        morpheus: The Morpheus persistence service
        model_selector: Optional custom model selector

    Returns:
        Configured ChatMorpheusComposer
    """
    return ChatMorpheusComposer(
        morpheus=morpheus,
        model_selector=model_selector or default_model_selector,
    )


__all__ = [
    "ChatMorpheusComposer",
    "TurnResult",
    "create_composer",
]

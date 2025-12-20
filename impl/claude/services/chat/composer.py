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

CLI v7 Phase 2 Enhancement:
- Now uses ConversationWindow for bounded context (Pattern #8)
- Supports context strategies: sliding, summarize, hybrid
- Integrates with Summarizer for LLM-powered compression
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, AsyncIterator, Callable

from .model_selector import MorpheusConfig, default_model_selector
from .transformer import (
    extract_usage,
    from_morpheus_response,
    to_morpheus_request,
    to_streaming_request,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from services.conductor.persistence import WindowPersistence
    from services.conductor.summarizer import Summarizer
    from services.conductor.window import ConversationWindow
    from services.morpheus.persistence import MorpheusPersistence

    from .session import ChatSession, Message

logger = logging.getLogger(__name__)


# === Result Types ===


@dataclass
class TurnResult:
    """
    Result of a composed turn.

    Contains the response content plus metadata from both coalgebras.

    CLI v7: Now includes context_preview for visibility into what the LLM sees.
    """

    content: str
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0
    model: str = ""
    error: str | None = None
    fallback: bool = False

    # CLI v7: Context visibility - what was sent to the LLM
    context_preview: list[dict[str, str]] = field(default_factory=list)
    context_message_count: int = 0
    context_has_summary: bool = False

    @property
    def success(self) -> bool:
        """Whether the turn completed without errors."""
        return self.error is None

    @property
    def total_tokens(self) -> int:
        """Total tokens used in this turn."""
        return self.tokens_in + self.tokens_out

    def format_context(self) -> str:
        """
        Format context preview for display.

        CLI v7: Human-readable view of what the LLM received.

        Returns:
            Formatted string showing context messages
        """
        if not self.context_preview:
            return "(no context captured)"

        lines = [
            f"=== Context ({self.context_message_count} messages) ===",
            f"Has summary: {self.context_has_summary}",
            "",
        ]

        for msg in self.context_preview:
            role = msg.get("role", "?").upper()
            content = msg.get("content", "")
            # Truncate long content
            if len(content) > 200:
                content = content[:200] + "..."
            lines.append(f"[{role}] {content}")
            lines.append("")

        return "\n".join(lines)


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

    CLI v7 Phase 2: Deep Conversation
    5. Uses ConversationWindow for bounded context (Pattern #8)
    6. Applies context strategies (sliding, summarize, hybrid)
    7. Integrates with Summarizer for LLM-powered compression
    """

    morpheus: "MorpheusPersistence"
    model_selector: Callable[["Umwelt", str], MorpheusConfig] = field(
        default=default_model_selector
    )

    # CLI v7 Phase 2: ConversationWindow integration
    # Window is created per-session, managed by composer
    _windows: dict[str, "ConversationWindow"] = field(default_factory=dict)
    _summarizer: "Summarizer | None" = field(default=None)
    _window_persistence: "WindowPersistence | None" = field(default=None)

    def set_summarizer(self, summarizer: "Summarizer") -> None:
        """
        Inject summarizer for context compression.

        Called by factory to wire up summarization.
        """
        self._summarizer = summarizer

    def set_window_persistence(self, persistence: "WindowPersistence") -> None:
        """
        Inject window persistence for D-gent storage.

        CLI v7 Phase 2: Enables window state to survive across sessions.
        Called by factory to wire up persistence.
        """
        self._window_persistence = persistence

    async def get_or_create_window_async(
        self,
        session: "ChatSession",
    ) -> "ConversationWindow":
        """
        Get or create a ConversationWindow for a session (async version).

        CLI v7 Phase 2: Tries to load from D-gent persistence first.

        The window is bounded and applies the session's context strategy.

        Args:
            session: The ChatSession to get window for

        Returns:
            ConversationWindow for the session
        """
        session_id = session.session_id

        if session_id not in self._windows:
            from services.conductor.window import ConversationWindow

            # CLI v7 Phase 2: Try to load from D-gent first
            if self._window_persistence is not None:
                try:
                    window = await self._window_persistence.load_window(session_id)
                    if window is not None:
                        # Wire summarizer if available
                        if self._summarizer is not None:
                            window.set_summarizer(self._summarizer.summarize_sync)
                        self._windows[session_id] = window
                        logger.debug(
                            f"Loaded window from D-gent for session {session_id[:8]}, "
                            f"turns={window.turn_count}"
                        )
                        return window
                except Exception as e:
                    logger.warning(f"Failed to load window from D-gent: {e}")

            # Create new window with session config
            config = session.config
            window = ConversationWindow(
                max_turns=config.max_turns or 35,
                strategy=config.context_strategy.value,
                context_window_tokens=config.context_window,
                summarization_threshold=config.summarization_threshold,
            )

            # Set system prompt if configured
            if config.system_prompt:
                window.set_system_prompt(config.system_prompt)

            # Wire summarizer if available
            if self._summarizer is not None:
                window.set_summarizer(self._summarizer.summarize_sync)

            self._windows[session_id] = window

            # Populate window with existing session history
            for turn in session.get_history():
                window.add_turn(
                    turn.user_message.content,
                    turn.assistant_response.content,
                )

            logger.debug(
                f"Created window for session {session_id[:8]}, "
                f"strategy={config.context_strategy.value}"
            )

        return self._windows[session_id]

    def get_or_create_window(
        self,
        session: "ChatSession",
    ) -> "ConversationWindow":
        """
        Get or create a ConversationWindow for a session (sync version).

        This is the synchronous version that doesn't try to load from D-gent.
        Used internally when we're already in a sync context.

        For persistence-aware loading, use get_or_create_window_async().

        Args:
            session: The ChatSession to get window for

        Returns:
            ConversationWindow for the session
        """
        session_id = session.session_id

        if session_id not in self._windows:
            from services.conductor.window import ConversationWindow

            # Create new window with session config
            config = session.config
            window = ConversationWindow(
                max_turns=config.max_turns or 35,
                strategy=config.context_strategy.value,
                context_window_tokens=config.context_window,
                summarization_threshold=config.summarization_threshold,
            )

            # Set system prompt if configured
            if config.system_prompt:
                window.set_system_prompt(config.system_prompt)

            # Wire summarizer if available
            if self._summarizer is not None:
                window.set_summarizer(self._summarizer.summarize_sync)

            self._windows[session_id] = window

            # Populate window with existing session history
            for turn in session.get_history():
                window.add_turn(
                    turn.user_message.content,
                    turn.assistant_response.content,
                )

            logger.debug(
                f"Created window for session {session_id[:8]}, "
                f"strategy={config.context_strategy.value}"
            )

        return self._windows[session_id]

    async def update_window_async(
        self,
        session: "ChatSession",
        user_message: str,
        assistant_response: str,
    ) -> None:
        """
        Update the window after a completed turn (async version with auto-save).

        CLI v7 Phase 2: Saves to D-gent after each update.

        Args:
            session: The ChatSession
            user_message: User's message content
            assistant_response: Assistant's response content
        """
        window = self.get_or_create_window(session)
        window.add_turn(user_message, assistant_response)

        # Auto-save to D-gent
        if self._window_persistence is not None:
            try:
                await self._window_persistence.save_window(session.session_id, window)
            except Exception as e:
                # Log but don't fail the turn
                logger.warning(f"Failed to save window to D-gent: {e}")

    def update_window(
        self,
        session: "ChatSession",
        user_message: str,
        assistant_response: str,
    ) -> None:
        """
        Update the window after a completed turn (sync version, fire-and-forget save).

        Called after successful LLM response to keep window in sync.

        Args:
            session: The ChatSession
            user_message: User's message content
            assistant_response: Assistant's response content
        """
        window = self.get_or_create_window(session)
        window.add_turn(user_message, assistant_response)

        # Fire-and-forget save to D-gent (non-blocking)
        if self._window_persistence is not None:
            asyncio.create_task(self._save_window_async(session.session_id, window))

    async def _save_window_async(
        self,
        session_id: str,
        window: "ConversationWindow",
    ) -> None:
        """Internal async save helper for fire-and-forget pattern."""
        try:
            if self._window_persistence is not None:
                await self._window_persistence.save_window(session_id, window)
        except Exception as e:
            logger.warning(f"Background window save failed: {e}")

    def clear_window(self, session_id: str) -> None:
        """Clear the window for a session (e.g., on reset)."""
        if session_id in self._windows:
            del self._windows[session_id]

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

        # CLI v7: Capture context preview for visibility
        context_preview = [{"role": m.role, "content": m.content} for m in context]
        context_has_summary = any("summary" in m.role.lower() for m in context) or any(
            "Summary:" in m.content for m in context
        )

        # Log context for debugging
        logger.debug(f"Context for LLM: {len(context)} messages, has_summary={context_has_summary}")
        for i, m in enumerate(context):
            logger.debug(f"  [{i}] {m.role}: {m.content[:100]}...")

        # 2. Select model based on observer (with session override support)
        config = self.model_selector(observer, session.node_path)

        # Check for session model override
        if session.model_override:
            config = MorpheusConfig(
                model=session.model_override,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )
            logger.debug(f"Using session model override: {session.model_override}")
        else:
            logger.debug(
                f"Selected model {config.model} for observer archetype, path {session.node_path}"
            )

        # 3. Transform to Morpheus request (no parsing!)
        # CLI v7 Phase 2: ConversationWindow already includes system prompt in context,
        # so we don't pass it again to avoid duplication
        context_has_system = any(m.role == "system" for m in context)
        system_prompt = (
            None
            if context_has_system
            else (session.config.system_prompt if session.config else None)
        )
        request = to_morpheus_request(context, message, config, system_prompt)

        # 4. Get observer archetype for rate limiting
        archetype = self._get_archetype(observer)

        # 5. Invoke through Morpheus (preserves its state)
        try:
            result = await self.morpheus.complete(request, archetype)

            # 6. Transform back to chat response
            response_content = from_morpheus_response(result)
            tokens_in, tokens_out = extract_usage(result)

            # 7. CLI v7 Phase 2: Update window with completed turn
            # This keeps the bounded window in sync with session history
            self.update_window(session, message, response_content)

            # 8. Return result with actual tokens and context visibility
            return TurnResult(
                content=response_content,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                latency_ms=result.latency_ms,
                model=config.model,
                context_preview=context_preview,
                context_message_count=len(context),
                context_has_summary=context_has_summary,
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
                # Still include context for debugging
                context_preview=context_preview,
                context_message_count=len(context),
                context_has_summary=context_has_summary,
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

        # Check for session model override
        if session.model_override:
            config = MorpheusConfig(
                model=session.model_override,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )

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
        """
        Get context messages using ConversationWindow.

        CLI v7 Phase 2: Now uses bounded window with context strategies
        instead of returning all messages from session.

        Falls back to session.get_messages() if window not available.
        """
        try:
            # Use ConversationWindow for bounded context
            window = self.get_or_create_window(session)
            context_msgs = window.get_context_messages()

            # Convert ContextMessage to Message format
            from .session import Message

            messages = []
            for ctx_msg in context_msgs:
                messages.append(
                    Message(
                        role=ctx_msg.role,
                        content=ctx_msg.content,
                        tokens=ctx_msg.tokens,
                    )
                )

            logger.debug(
                f"Window context: {len(messages)} messages, "
                f"{window.total_tokens} tokens, "
                f"utilization={window.utilization:.1%}"
            )

            return messages

        except Exception as e:
            # Fallback to full session history on error
            logger.warning(f"Window context failed, using full history: {e}")
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

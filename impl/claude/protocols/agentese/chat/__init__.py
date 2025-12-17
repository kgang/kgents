"""
AGENTESE Chat Protocol: Conversational Affordances

DEPRECATED: This module re-exports from services.chat for backward compatibility.
New code should import directly from services.chat.

Chat is not a separate system - it is a composable affordance that any
AGENTESE node can expose. Any node decorated with @chatty exposes:

- <node>.chat.send[message="..."]  - Send message, get response
- <node>.chat.stream[message="..."] - Streaming response
- <node>.chat.history               - Turn history
- <node>.chat.context               - Working context
- <node>.chat.metrics               - Token counts, latency
- <node>.chat.reset                 - Clear session

See: spec/protocols/chat.md

Usage:
    # Preferred: Import from services.chat
    from services.chat import ChatSession, ChatSessionFactory, ChatConfig

    # Legacy: This still works but is deprecated
    from protocols.agentese.chat import ChatSession, ChatSessionFactory, ChatConfig

    # Create a session
    factory = ChatSessionFactory()
    session = await factory.create_session("self.soul", observer)

    # Send messages
    response = await session.send("Hello")

    # Stream responses
    async for token in session.stream("Tell me more"):
        print(token, end="", flush=True)
"""

import warnings

# Re-export from canonical location
from services.chat import (
    # Config
    ChatConfig,
    # Node
    ChatNode,
    ChatPersistence,
    # Session
    ChatSession,
    # Factory
    ChatSessionFactory,
    ChatSessionState,
    # Observability
    ChatTelemetry,
    ContextStrategy,
    MemoryInjector,
    Message,
    # Persistence
    PersistedSession,
    SessionBudget,
    Turn,
    # Context
    WorkingContextProjector,
    get_active_session_count,
    get_chat_meter,
    get_chat_metrics_summary,
    get_chat_tracer,
    get_memory_injector,
    get_persistence,
    record_error,
    record_session_event,
    record_turn,
    reset_chat_metrics,
    reset_persistence,
)

# Backward compatibility alias
ChatSessionPersistence = ChatPersistence


def __getattr__(name: str) -> object:
    """Emit deprecation warning for direct access."""
    if name in __all__:
        warnings.warn(
            f"Importing {name} from protocols.agentese.chat is deprecated. "
            "Import from services.chat instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return globals().get(name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Config
    "ChatConfig",
    "ContextStrategy",
    # Session
    "ChatSession",
    "ChatSessionState",
    "Turn",
    "Message",
    "SessionBudget",
    # Factory
    "ChatSessionFactory",
    # Context
    "WorkingContextProjector",
    # Persistence
    "PersistedSession",
    "ChatPersistence",
    "ChatSessionPersistence",  # Legacy alias
    "MemoryInjector",
    "get_persistence",
    "get_memory_injector",
    "reset_persistence",
    # Observability
    "ChatTelemetry",
    "record_turn",
    "record_session_event",
    "record_error",
    "get_chat_metrics_summary",
    "get_active_session_count",
    "reset_chat_metrics",
    "get_chat_tracer",
    "get_chat_meter",
    # Node
    "ChatNode",
]

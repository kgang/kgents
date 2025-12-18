"""
Chat Crown Jewel: Conversational Affordances.

Chat is a composable affordance that any AGENTESE node can expose.
Just as `manifest` reveals state and `refine` enables dialectics,
`chat` enables turn-based conversation with any entity that can converse.

AGENTESE Paths (via @node("self.chat")):
- self.chat.manifest     - Chat service status
- self.chat.sessions     - List active sessions
- self.chat.session      - Get specific session by ID
- self.chat.create       - Create new session for path
- self.chat.send         - Send message to session
- self.chat.history      - Get session history
- self.chat.save         - Persist session
- self.chat.search       - Search sessions

The Metaphysical Fullstack Pattern (AD-009):
- ChatNode wraps ChatPersistence as AGENTESE node
- Universal gateway auto-exposes all aspects
- No explicit routes needed

Dual-Track Storage:
- D-gent datums - Semantic content and associations
- SQLAlchemy tables (models/chat.py) - Fast queries by metadata

See: docs/skills/metaphysical-fullstack.md
See: spec/protocols/chat.md
"""

from .composer import ChatMorpheusComposer, TurnResult, create_composer
from .config import ChatConfig, ContextStrategy
from .context_projector import WorkingContextProjector
from .factory import (
    ChatServiceFactory,
    ChatSessionFactory,
    SystemPromptContext,
    generate_session_id,
    get_chat_factory,
    reset_chat_factory,
    set_chat_factory,
)
from .model_selector import (
    TIER_BUDGETS,
    ModelSelector,
    MorpheusConfig,
    TokenBudget,
    budget_aware_selector,
    default_model_selector,
)
from .node import (
    ChatManifestRendering,
    ChatNode,
    ChatResponseRendering,
    SessionDetailRendering,
    SessionListRendering,
)
from .observability import (
    ChatTelemetry,
    get_active_session_count,
    get_chat_meter,
    get_chat_metrics_summary,
    get_chat_tracer,
    record_error,
    record_session_event,
    record_turn,
    reset_chat_metrics,
)
from .persistence import (
    ChatPersistence,
    MemoryInjector,
    PersistedSession,
    get_memory_injector,
    get_persistence,
    reset_persistence,
)
from .session import ChatSession, ChatSessionState, Message, SessionBudget, Turn
from .transformer import (
    extract_usage,
    from_morpheus_response,
    to_morpheus_request,
    to_streaming_request,
)

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
    "ChatServiceFactory",
    "SystemPromptContext",
    "generate_session_id",
    "get_chat_factory",
    "set_chat_factory",
    "reset_chat_factory",
    # Morpheus Composition (NEW)
    "ChatMorpheusComposer",
    "TurnResult",
    "create_composer",
    # Model Selection (NEW)
    "MorpheusConfig",
    "ModelSelector",
    "default_model_selector",
    "budget_aware_selector",
    "TokenBudget",
    "TIER_BUDGETS",
    # Transformer (NEW)
    "to_morpheus_request",
    "from_morpheus_response",
    "extract_usage",
    "to_streaming_request",
    # Context
    "WorkingContextProjector",
    # Persistence
    "PersistedSession",
    "ChatPersistence",
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
    # Node (AGENTESE interface)
    "ChatNode",
    "ChatManifestRendering",
    "SessionListRendering",
    "SessionDetailRendering",
    "ChatResponseRendering",
]

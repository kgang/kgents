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

from .config import ChatConfig, ContextStrategy
from .session import ChatSession, ChatSessionState, Turn, Message, SessionBudget
from .factory import (
    ChatSessionFactory,
    ChatServiceFactory,
    SystemPromptContext,
    generate_session_id,
    get_chat_factory,
    set_chat_factory,
    reset_chat_factory,
)
from .composer import ChatMorpheusComposer, TurnResult, create_composer
from .model_selector import (
    MorpheusConfig,
    ModelSelector,
    default_model_selector,
    budget_aware_selector,
    TokenBudget,
    TIER_BUDGETS,
)
from .transformer import (
    to_morpheus_request,
    from_morpheus_response,
    extract_usage,
    to_streaming_request,
)
from .context_projector import WorkingContextProjector
from .persistence import (
    PersistedSession,
    ChatPersistence,
    MemoryInjector,
    get_persistence,
    get_memory_injector,
    reset_persistence,
)
from .observability import (
    ChatTelemetry,
    record_turn,
    record_session_event,
    record_error,
    get_chat_metrics_summary,
    get_active_session_count,
    reset_chat_metrics,
    get_chat_tracer,
    get_chat_meter,
)
from .node import (
    ChatNode,
    ChatManifestRendering,
    SessionListRendering,
    SessionDetailRendering,
    ChatResponseRendering,
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

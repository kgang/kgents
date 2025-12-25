"""
Chat Crown Jewel: Web-Native Chat Protocol with K-Block Semantics.

The Chat service provides:
- ChatSession: K-Block-based conversation management
- ChatEvidence: Bayesian evidence accumulation per turn
- WorkingContext: Incremental context compression
- Branching: Fork/merge/checkpoint/rewind operations
- ChatPersistence: D-gent-backed persistent storage (survives restarts)

Philosophy:
    "The session is a K-Block. The turn is a Mark. The conversation is a proof."

See: spec/protocols/chat-web.md
See: docs/skills/metaphysical-fullstack.md
See: MIGRATION.md for persistence migration guide
"""

from .context import (
    LinearityTag,
    WorkingContext,
)
from .evidence import (
    BetaPrior,
    ChatEvidence,
    StoppingDecision,
    TurnResult,
)
from .kgent_bridge import (
    ChatContext,
    KgentBridge,
    StreamChunk,
    create_kgent_bridge,
)
from .persistence import (
    ChatPersistence,
)
from .session import (
    BranchError,
    ChatSession,
    MergeStrategy,
    SessionNode,
    generate_session_id,
)

__all__ = [
    # Session
    "BranchError",
    "ChatSession",
    "MergeStrategy",
    "SessionNode",
    "generate_session_id",
    # Evidence
    "BetaPrior",
    "ChatEvidence",
    "StoppingDecision",
    "TurnResult",
    # Context
    "LinearityTag",
    "WorkingContext",
    # K-gent Bridge
    "ChatContext",
    "KgentBridge",
    "StreamChunk",
    "create_kgent_bridge",
    # Persistence
    "ChatPersistence",
]

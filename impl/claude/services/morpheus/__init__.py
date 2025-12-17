"""
Morpheus Crown Jewel: LLM Gateway as Metaphysical Fullstack Agent.

Transform LLM routing from infrastructure plumbing to first-class AGENTESE citizen.

AGENTESE: world.morpheus.*
- world.morpheus.manifest    - Gateway health status
- world.morpheus.complete    - Chat completion (non-streaming)
- world.morpheus.stream      - Chat completion (streaming)
- world.morpheus.providers   - List available providers
- world.morpheus.metrics     - Request/error counts
- world.morpheus.health      - Provider health checks
- world.morpheus.rate_limit  - Rate limit status

Architecture:
    Any Transport -> AGENTESE Protocol -> MorpheusNode -> MorpheusPersistence -> Gateway -> Adapter -> LLM

Observer-Dependent Behavior:
- admin: See all providers, metrics, configure (1000 rpm)
- developer: See enabled providers, metrics (100 rpm)
- guest: Basic completion only, public providers (20 rpm)

Services (Metaphysical Fullstack AD-009):
- types.py         - OpenAI-compatible request/response schemas
- gateway.py       - Routing logic (no HTTP coupling)
- persistence.py   - Domain semantics layer
- node.py          - AGENTESE @node("world.morpheus")
- observability.py - OTEL spans and metrics
- adapters/        - LLM backend implementations
"""

from .node import (
    CompletionRendering,
    MorpheusManifestRendering,
    MorpheusNode,
    ProvidersRendering,
)
from .persistence import (
    CompletionResult,
    MorpheusPersistence,
    MorpheusStatus,
    ProviderStatus,
)
from .gateway import (
    GatewayConfig,
    MorpheusGateway,
    ProviderConfig,
    RateLimitError,
    RateLimitState,
)
from .types import (
    ChatChoice,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    MorpheusError,
    StreamChunk,
    StreamChoice,
    StreamDelta,
    Usage,
)
from .observability import (
    MorpheusTelemetry,
    get_morpheus_metrics_summary,
    record_completion,
    reset_morpheus_metrics,
)

__all__ = [
    # Node
    "MorpheusNode",
    "MorpheusManifestRendering",
    "CompletionRendering",
    "ProvidersRendering",
    # Persistence
    "MorpheusPersistence",
    "MorpheusStatus",
    "ProviderStatus",
    "CompletionResult",
    # Gateway
    "MorpheusGateway",
    "GatewayConfig",
    "ProviderConfig",
    "RateLimitError",
    "RateLimitState",
    # Types
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "ChatChoice",
    "Usage",
    "MorpheusError",
    "StreamChunk",
    "StreamChoice",
    "StreamDelta",
    # Observability
    "MorpheusTelemetry",
    "get_morpheus_metrics_summary",
    "record_completion",
    "reset_morpheus_metrics",
]

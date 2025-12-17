# Morpheus Legacy (DEPRECATED)

This directory contains the original Morpheus infrastructure implementation.
It has been superseded by the Metaphysical Fullstack implementation.

## Migration

Morpheus has been transformed from infrastructure router to first-class AGENTESE citizen.

### New Location

```
services/morpheus/
├── __init__.py           # Public API
├── node.py               # @node("world.morpheus")
├── persistence.py        # Domain semantics layer
├── gateway.py            # Routing logic (no HTTP coupling)
├── types.py              # OpenAI-compatible types
└── adapters/             # LLM backend implementations
```

### Import Changes

```python
# Old (deprecated)
from infra.morpheus import MorpheusGateway, ChatRequest, ChatResponse

# New
from services.morpheus import MorpheusGateway, ChatRequest, ChatResponse
```

### API Changes

```
# Old
POST /v1/chat/completions → MorpheusGateway.chat_completion()

# New
POST /agentese/world/morpheus/complete → MorpheusNode._invoke_aspect("complete")

# Legacy endpoint redirects with 307
POST /v1/chat/completions → 307 → /agentese/world/morpheus/complete
```

### Key Improvements

1. **AGENTESE Integration**: `@node("world.morpheus")` enables universal gateway access
2. **Observer-Dependent Behavior**: Admin sees all providers, guest sees public only
3. **Effect Composition**: Can be chained with other AGENTESE paths
4. **No HTTP Coupling**: Gateway logic is transport-agnostic
5. **Telemetry Ready**: Built-in span tracking and metrics

## Sunset Date

The legacy `/v1/chat/completions` endpoint will be removed on **2025-06-01**.

## Files

- `server.py` - Original FastAPI application (routes removed)
- `adapter.py` - Original adapter implementations (split into adapters/)
- `types.py` - OpenAI-compatible types (copied to services/morpheus/)
- `k8s/` - Kubernetes manifests (may need updates for new paths)

# AGENTESE Universal Protocol (AUP) - Crown Jewel Execution

## Context

You are implementing the **AGENTESE Universal Protocol (AUP)** - a Crown Jewel project that creates a JSON/WebSocket API layer for AGENTESE, enabling any frontend (React, Vue, mobile, CLI) to speak AGENTESE over HTTP.

**Plan**: `plans/agentese-universal-protocol.md`
**Philosophy**: "Expose, Don't Build" - API is the product, UIs are projections
**Key Insight**: Same `AgenteseBridge` powers both marimo notebooks AND HTTP API

## Current Phase: IMPLEMENT (Wave 1: Core Bridge)

### Your Mission

Build the foundational `AgenteseBridge` that translates HTTP/WebSocket requests into `logos.invoke()` calls.

### Files to Create

```
impl/claude/protocols/api/
├── __init__.py              # Package exports
├── bridge.py                # AgenteseBridge: Logos ↔ HTTP translation
├── serializers.py           # Pydantic models for request/response
├── exceptions.py            # HTTP-aware error handling
└── _tests/
    ├── __init__.py
    ├── test_bridge.py       # Unit tests for bridge
    └── test_serializers.py  # Schema validation tests
```

### Implementation Guidelines

#### 1. AgenteseBridge (`bridge.py`)

Core class that handles the translation:

```python
@dataclass
class AgenteseBridge:
    """
    The bridge between HTTP/WS and AGENTESE Logos.

    This is the SAME bridge used by:
    - HTTP API endpoints
    - WebSocket handlers
    - marimo notebooks (via shared instance)
    - CLI (for remote gardens)

    One bridge, many projections.
    """

    logos: Logos
    telemetry_enabled: bool = True

    @classmethod
    def from_default_logos(cls) -> "AgenteseBridge":
        """Create bridge with default Logos configuration."""
        from impl.claude.protocols.agentese.logos import create_logos
        return cls(logos=create_logos())

    async def invoke(
        self,
        handle: str,
        observer: "ObserverContext",
        **kwargs: Any,
    ) -> "AgenteseResponse":
        """
        Core invocation method.

        Maps HTTP request → logos.invoke() → HTTP response.
        """
        ...

    async def manifest(
        self,
        context: str,
        holon: str,
        observer: "ObserverContext",
    ) -> "AgenteseResponse":
        """Convenience for manifest operations."""
        return await self.invoke(f"{context}.{holon}.manifest", observer)

    async def affordances(
        self,
        context: str,
        holon: str,
        observer: "ObserverContext",
    ) -> list[str]:
        """Get available affordances for observer."""
        ...

    async def compose(
        self,
        paths: list[str],
        observer: "ObserverContext",
        initial_input: Any = None,
        emit_law_check: bool = True,
    ) -> "CompositionResponse":
        """Execute a composition pipeline."""
        ...
```

#### 2. Serializers (`serializers.py`)

Pydantic models for type-safe request/response:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any

class ObserverContext(BaseModel):
    """Observer context from HTTP headers or request body."""
    archetype: str = "viewer"
    id: str = "anonymous"
    capabilities: list[str] = Field(default_factory=list)

    def to_umwelt(self) -> "MockUmwelt":
        """Convert to AGENTESE-compatible Umwelt."""
        from impl.claude.agents.i.marimo.logos_bridge import MockUmwelt
        return MockUmwelt(
            name=self.id,
            archetype=self.archetype,
            capabilities=tuple(self.capabilities),
        )

class ResponseMeta(BaseModel):
    """Metadata attached to every response."""
    observer: str
    span_id: str | None = None
    timestamp: datetime
    duration_ms: int | None = None

class AgenteseResponse(BaseModel):
    """Standard response envelope."""
    handle: str
    result: Any
    meta: ResponseMeta

class CompositionRequest(BaseModel):
    """Request body for pipeline composition."""
    paths: list[str]
    initial_input: Any = None
    emit_law_check: bool = True

class CompositionResponse(BaseModel):
    """Response for pipeline composition."""
    result: Any
    pipeline_trace: list[dict[str, Any]]
    laws_verified: list[str]

class ErrorDetail(BaseModel):
    """Sympathetic error detail."""
    error: str
    code: str
    path: str | None = None
    suggestion: str | None = None
    available: list[str] | None = None
```

#### 3. Exceptions (`exceptions.py`)

HTTP-aware error handling that preserves AGENTESE's sympathetic errors:

```python
from impl.claude.protocols.agentese.exceptions import (
    AffordanceError,
    PathNotFoundError,
    ObserverRequiredError,
    PathSyntaxError,
)

class APIError(Exception):
    """Base API error with HTTP status code."""
    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def to_detail(self) -> dict[str, Any]:
        """Convert to ErrorDetail dict."""
        ...

class AffordanceDeniedError(APIError):
    """403: Observer lacks permission."""
    status_code = 403
    code = "AFFORDANCE_DENIED"

class HandleNotFoundError(APIError):
    """404: AGENTESE path not found."""
    status_code = 404
    code = "PATH_NOT_FOUND"

class ObserverMissingError(APIError):
    """401: No observer context provided."""
    status_code = 401
    code = "OBSERVER_REQUIRED"

class SyntaxError(APIError):
    """400: Malformed AGENTESE path."""
    status_code = 400
    code = "SYNTAX_ERROR"

def translate_agentese_error(e: Exception) -> APIError:
    """Translate AGENTESE exceptions to API exceptions."""
    if isinstance(e, AffordanceError):
        return AffordanceDeniedError(...)
    elif isinstance(e, PathNotFoundError):
        return HandleNotFoundError(...)
    # etc.
```

### Integration with Existing Marimo Bridge

The existing `impl/claude/agents/i/marimo/logos_bridge.py` already has:
- `LogosCell` for wrapping handles
- `ObserverState` for managing observer context
- `MockUmwelt` for lightweight Umwelt

**Reuse these!** The API bridge should use the same primitives:

```python
# In bridge.py
from impl.claude.agents.i.marimo.logos_bridge import MockUmwelt, invoke_sync

class AgenteseBridge:
    async def invoke(self, handle: str, observer: ObserverContext, **kwargs):
        umwelt = observer.to_umwelt()  # Returns MockUmwelt
        result = await self.logos.invoke(handle, umwelt, **kwargs)
        ...
```

### Test Requirements

#### test_bridge.py
- `test_manifest_invokes_logos` - Verify manifest calls logos.invoke
- `test_affordance_check` - Verify affordances are returned correctly
- `test_observer_conversion` - Verify ObserverContext → MockUmwelt
- `test_composition_pipeline` - Verify compose executes in order
- `test_error_translation` - Verify AGENTESE errors become API errors

#### test_serializers.py
- `test_observer_context_defaults` - Default values work
- `test_response_serialization` - AgenteseResponse serializes to JSON
- `test_error_detail_structure` - ErrorDetail has all fields

### Success Criteria for Wave 1

1. `AgenteseBridge.invoke()` successfully calls `logos.invoke()`
2. `ObserverContext.to_umwelt()` produces valid MockUmwelt
3. All five contexts work: world, self, concept, void, time
4. Error translation preserves sympathetic messages
5. Composition pipelines execute in order
6. All tests pass, mypy clean

### Next Waves (Don't Implement Yet)

- Wave 2: FastAPI server + HTTP endpoints
- Wave 3: WebSocket + SSE streaming
- Wave 4: OpenAPI spec + React examples

## Commands

```bash
# Run tests
cd impl/claude && uv run pytest protocols/api/_tests/ -v

# Type check
cd impl/claude && uv run mypy protocols/api/

# Verify integration with existing logos
cd impl/claude && uv run pytest protocols/agentese/_tests/ -v
```

## Constraints

- No FastAPI/Starlette yet (Wave 2)
- No WebSocket yet (Wave 3)
- Reuse existing marimo bridge primitives
- Follow existing test patterns in `protocols/agentese/_tests/`
- Sympathetic errors: always include `suggestion` field

## Questions to Answer During Implementation

1. Should `AgenteseBridge` cache Logos instances or create fresh?
2. How do we handle streaming results (e.g., soul.challenge)?
3. Should composition trace include intermediate results?

## Epilogue Template

When complete, write epilogue to:
`impl/claude/plans/_epilogues/2025-12-14-agentese-universal-protocol-wave1.md`

Include:
- Files created
- Test counts
- Key learnings
- Cross-synergies discovered
- Next wave preparation notes

---

*"The bridge does not create meaning. It carries meaning across the void."*

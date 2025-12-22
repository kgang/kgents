# Morpheus Gateway Specification

> *"The noun is a lie. Morpheus is the shape-shifter—one protocol, many backends."*

**AGENTESE Path**: `world.morpheus.*`
**Status**: Implemented (Metaphysical Fullstack)
**Implementation**: `impl/claude/services/morpheus/`

---

## Part I: Core Concept

Morpheus is an LLM gateway transformed into a first-class AGENTESE citizen. It routes requests to multiple backends based on model prefix while providing observer-dependent behavior and universal protocol access.

### The Evolution

| Era | Pattern | Entry Point |
|-----|---------|-------------|
| v1 (Infra) | FastAPI routes | `POST /v1/chat/completions` |
| v2 (Metaphysical) | AGENTESE node | `logos.invoke("world.morpheus.complete", observer, ...)` |

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  Any Transport (CLI, HTTP, WS)                   │
│                            ↓                                     │
│              AGENTESE Universal Protocol                         │
│                            ↓                                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              @node("world.morpheus")                        ││
│  │                                                             ││
│  │  Aspects:                                                   ││
│  │    .manifest   - Gateway status                             ││
│  │    .complete   - Non-streaming completion                   ││
│  │    .stream     - Streaming completion (SSE)                 ││
│  │    .providers  - List providers (observer-filtered)         ││
│  │    .metrics    - Request/error counts (privileged)          ││
│  │    .health     - Provider health checks                     ││
│  │    .route      - Model routing info                         ││
│  └─────────────────────────────────────────────────────────────┘│
│                            ↓                                     │
│              MorpheusPersistence (domain semantics)              │
│                            ↓                                     │
│              MorpheusGateway (routing logic)                     │
│                            ↓                                     │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐     │
│  │ ClaudeCLI   │ Anthropic   │ OpenRouter  │ Ollama      │     │
│  │ Adapter     │ API         │ Adapter     │ Adapter     │     │
│  └─────────────┴─────────────┴─────────────┴─────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part II: AGENTESE Paths

| Path | Category | Effects | Description |
|------|----------|---------|-------------|
| `world.morpheus.manifest` | PERCEPTION | READS(state) | Gateway health status |
| `world.morpheus.complete` | MUTATION | CALLS(llm), CHARGES(tokens) | Chat completion |
| `world.morpheus.stream` | MUTATION | CALLS(llm), CHARGES(tokens) | Streaming completion |
| `world.morpheus.providers` | PERCEPTION | READS(config) | List available providers |
| `world.morpheus.metrics` | PERCEPTION | READS(metrics) | Request/error statistics |
| `world.morpheus.health` | PERCEPTION | READS(state) | Provider health checks |
| `world.morpheus.route` | INTROSPECTION | READS(config) | Model→provider routing info |

### Invocation Examples

```python
# Via Logos (universal)
result = await logos.invoke(
    "world.morpheus.complete",
    observer,
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Hello"}],
)

# Via HTTP (auto-exposed by gateway)
POST /agentese/world/morpheus/complete
X-Observer-Archetype: developer
{"model": "claude-sonnet-4-20250514", "messages": [...]}

# Via CLI
kg morpheus complete --model claude-sonnet-4-20250514 --message "Hello"
```

---

## Part III: Observer-Dependent Behavior

### Affordance Matrix

| Archetype | complete | stream | health | providers | metrics | route | configure |
|-----------|----------|--------|--------|-----------|---------|-------|-----------|
| admin     | ✓        | ✓      | ✓      | all       | ✓       | ✓     | ✓         |
| system    | ✓        | ✓      | ✓      | all       | ✓       | ✓     | ✓         |
| developer | ✓        | ✓      | ✓      | enabled   | ✓       | ✓     | ✗         |
| guest     | ✓        | ✓      | ✓      | public    | ✗       | ✗     | ✗         |

### Provider Visibility

```python
# Admin sees all providers (enabled, disabled, public, private)
world.morpheus.providers → filter="all"

# Developer sees enabled providers
world.morpheus.providers → filter="enabled"

# Guest sees public providers only
world.morpheus.providers → filter="public"
```

---

## Part IV: Request/Response Types

### ChatRequest (OpenAI-compatible)

```python
@dataclass
class ChatRequest:
    model: str                           # e.g., "claude-sonnet-4-20250514"
    messages: list[ChatMessage]          # Conversation history
    temperature: float = 0.7             # Sampling temperature
    max_tokens: int = 4096               # Max response tokens
    top_p: float = 1.0                   # Nucleus sampling
    stream: bool = False                 # Enable streaming
    stop: Optional[list[str]] = None     # Stop sequences
```

### ChatResponse (OpenAI-compatible)

```python
@dataclass
class ChatResponse:
    id: str                              # e.g., "chatcmpl-abc123"
    object: str = "chat.completion"
    created: int                         # Unix timestamp
    model: str                           # Model used
    choices: list[ChatChoice]            # Response choices
    usage: Optional[Usage]               # Token counts
```

### CompletionResult (Morpheus-enriched)

```python
@dataclass
class CompletionResult:
    response: ChatResponse               # OpenAI response
    provider_name: str                   # Which provider handled it
    latency_ms: float                    # Request latency
    telemetry_span_id: Optional[str]     # Telemetry trace ID
```

---

## Part V: Adapter Protocol

```python
class Adapter(Protocol):
    """Protocol for LLM adapters."""

    async def complete(self, request: ChatRequest) -> ChatResponse:
        """Process a chat completion request."""
        ...

    def is_available(self) -> bool:
        """Check if adapter can handle requests."""
        ...

    def health_check(self) -> dict[str, Any]:
        """Return health status for monitoring."""
        ...
```

### Built-in Adapters

| Adapter | Prefix | Backend | Auth |
|---------|--------|---------|------|
| `ClaudeCLIAdapter` | `claude-*` | `claude -p` subprocess | CLI OAuth |
| `MockAdapter` | any | In-memory queue | None |

### Adding Adapters

```python
from services.morpheus import MorpheusGateway
from services.morpheus.adapters import Adapter

class AnthropicAPIAdapter:
    """Direct Anthropic API adapter."""

    def __init__(self, api_key: str):
        self._client = anthropic.Anthropic(api_key=api_key)

    async def complete(self, request: ChatRequest) -> ChatResponse:
        # Transform and call Anthropic API
        ...

# Register
gateway.register_provider(
    name="anthropic-api",
    adapter=AnthropicAPIAdapter(api_key="sk-..."),
    prefix="claude-api-",
    public=True,
)
```

---

## Part VI: Integration Points

### With Bootstrap (DI)

```python
# In services/bootstrap.py
if name == "morpheus_persistence":
    gateway = MorpheusGateway()
    gateway.register_provider(
        name="claude-cli",
        adapter=ClaudeCLIAdapter(),
        prefix="claude-",
    )
    return MorpheusPersistence(gateway=gateway)
```

### With AGENTESE Gateway (Auto-exposure)

```python
# Auto-exposed at app startup via @node decorator
# No explicit route registration needed

GET  /agentese/world/morpheus/manifest
POST /agentese/world/morpheus/complete
GET  /agentese/world/morpheus/providers
```

### With Other Crown Jewels (Effect Composition)

```python
# Future: Chain operations via lens()
pipeline = (
    logos.lens("world.doc.load") >>
    logos.lens("world.morpheus.complete") >>
    logos.lens("self.memory.engram")
)

result = await pipeline.invoke(observer, path="research.pdf", prompt="Summarize")
```

---

## Part VII: Backward Compatibility

### Legacy Endpoint

```
POST /v1/chat/completions
  → 307 Temporary Redirect
  → /agentese/world/morpheus/complete
```

Headers on redirect:
```
Deprecation: true
Sunset: 2025-06-01
Link: </agentese/world/morpheus/complete>; rel="successor-version"
```

### Migration Path

```python
# Old (deprecated)
from infra.morpheus import MorpheusGateway

# New
from services.morpheus import MorpheusGateway
```

---

## Part VIII: File Structure

```
services/morpheus/
├── __init__.py           # Public API exports
├── node.py               # @node("world.morpheus") - AGENTESE node
├── persistence.py        # Service semantics layer
├── gateway.py            # Routing logic (transport-agnostic)
├── types.py              # OpenAI-compatible request/response types
├── adapters/
│   ├── __init__.py       # Adapter exports
│   ├── base.py           # Adapter Protocol
│   ├── claude_cli.py     # ClaudeCLIAdapter
│   └── mock.py           # MockAdapter
├── _tests/
│   ├── __init__.py
│   └── test_node.py      # 18 tests for MorpheusNode
└── AUDIT_PROMPT.md       # Self-audit prompt

# Archived
infra/_archived/morpheus-legacy/  # Original implementation (deprecated)
```

---

## Part IX: Design Principles

### 1. The Protocol IS the API (AD-009)

No explicit HTTP routes. AGENTESE gateway auto-exposes all aspects.

### 2. Transport Agnostic

Gateway has no HTTP coupling. Can be invoked via:
- HTTP (via AGENTESE gateway)
- WebSocket (via Logos)
- CLI (via kg command)
- Direct Python (via logos.invoke)

### 3. Observer-Dependent

Different archetypes see different providers and have different capabilities.

### 4. Stateless Gateway

Morpheus doesn't persist state to database. Each request is independent.
(Telemetry and logging are separate concerns.)

### 5. Thin Adapter

~600 lines total. Router, not platform.

---

## Part X: Future Work

| Feature | Status | Description |
|---------|--------|-------------|
| Streaming | Planned | SSE via `world.morpheus.stream` |
| Telemetry | Planned | OpenTelemetry spans + Prometheus metrics |
| Rate Limiting | Planned | Per-provider, per-observer limits |
| Caching | Planned | Response cache for deterministic queries |
| Anthropic Adapter | Planned | Direct API without CLI subprocess |
| OpenRouter Adapter | Planned | Access to 100+ models |
| Effect Composition | Planned | `lens()` method for pipeline chaining |

---

*Last Updated: 2025-12-17*
*Spec Version: 2.0 (Metaphysical Fullstack)*

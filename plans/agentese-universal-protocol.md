---
path: plans/agentese-universal-protocol
status: active
progress: 0
last_touched: 2025-12-14
touched_by: opus-4.5
blocking: []
enables: [marimo-integration, deployment/permanent-kgent-chatbot, interfaces/dashboard-overhaul]
session_notes: |
  NEW CROWN JEWEL: The AGENTESE Universal Protocol (AUP)
  Unifies TUI, marimo, and any future frontend via JSON/WebSocket API.
  Key insight: "Expose, Don't Build" - API is the product, UIs are projections.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: pending
  STRATEGIZE: touched
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.12
  spent: 0.05
  returned: 0.0
---

# AGENTESE Universal Protocol (AUP)

> *"The API is the product. The UI is merely a projection."*

## The Vision

AGENTESE is already a complete ontology for agent-world interaction. What's missing is **the wire format**—a way for any client (TUI, marimo, React, mobile, CLI) to speak AGENTESE over HTTP/WebSocket.

This Crown Jewel creates **the lingua franca layer**: a JSON protocol that exposes every AGENTESE operation with:
- Full type safety (OpenAPI 3.1 spec)
- Real-time subscriptions (WebSocket)
- Server-Sent Events for streaming
- Observability integration (span IDs in responses)
- Category-law preservation (compositions serialize correctly)

**The Enlightened Move**: Instead of building a React app, we expose an API so beautiful that React developers *want* to build clients for it. We maintain zero JavaScript. We ship:
1. OpenAPI spec
2. Example React components (not a full app)
3. Integration tests proving the API works
4. marimo as our "reference web UI"

---

## The Categorical Foundation

```
                    ┌─────────────────────────────────────────┐
                    │         AGENTESE ONTOLOGY              │
                    │  (Five Contexts, Seven Aspects, Laws)   │
                    └──────────────────┬──────────────────────┘
                                       │
                              logos.invoke()
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                        AGENTESE UNIVERSAL PROTOCOL                           │
│                                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                │
│  │   HTTP/REST    │  │   WebSocket    │  │     SSE        │                │
│  │   (Request)    │  │   (Bidir)      │  │   (Stream)     │                │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘                │
│          │                   │                   │                          │
│          └───────────────────┼───────────────────┘                          │
│                              │                                              │
│                    ┌─────────▼─────────┐                                    │
│                    │  AgenteseBridge   │  ← Python FastAPI/Starlette        │
│                    └─────────┬─────────┘                                    │
│                              │                                              │
└──────────────────────────────┼──────────────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌─────────┐      ┌─────────┐      ┌─────────┐
        │   TUI   │      │ marimo  │      │  React  │
        │(Textual)│      │notebook │      │ (yours) │
        └─────────┘      └─────────┘      └─────────┘
```

**The Functor Guarantee**: Every client sees the same AGENTESE, just rendered differently. The API is the morphism between the agent world and the display world.

---

## Protocol Design

### 1. HTTP Endpoints

#### Core Operations

```
GET  /api/v1/{context}/{holon}/manifest
POST /api/v1/{context}/{holon}/{aspect}
GET  /api/v1/{context}/{holon}/affordances
POST /api/v1/{context}/{holon}/compose
```

#### Examples

```http
# Manifest (GET with observer context in headers)
GET /api/v1/world/field/manifest
X-Observer-Archetype: architect
X-Observer-Id: user-123

Response: {
  "handle": "world.field.manifest",
  "result": { ... observer-specific rendering ... },
  "meta": {
    "observer": "architect",
    "span_id": "abc123",
    "timestamp": "2025-12-14T10:30:00Z"
  }
}

# Invoke with aspect
POST /api/v1/concept/justice/refine
X-Observer-Archetype: philosopher
Content-Type: application/json

{
  "challenge": "What about edge cases?",
  "entropy": 0.07
}

Response: {
  "handle": "concept.justice.refine",
  "result": {
    "thesis": "...",
    "antithesis": "...",
    "synthesis": "..."
  },
  "meta": { ... }
}

# Composition (pipeline execution)
POST /api/v1/compose
{
  "paths": [
    "world.document.manifest",
    "concept.summary.refine",
    "self.memory.engram"
  ],
  "initial_input": null,
  "emit_law_check": true
}

Response: {
  "result": { ... final result ... },
  "pipeline_trace": [
    {"path": "world.document.manifest", "span_id": "a1", "duration_ms": 45},
    {"path": "concept.summary.refine", "span_id": "a2", "duration_ms": 120},
    {"path": "self.memory.engram", "span_id": "a3", "duration_ms": 30}
  ],
  "laws_verified": ["associativity", "identity"]
}
```

### 2. WebSocket Protocol

Real-time bidirectional communication for live gardens.

```typescript
// Client → Server messages
interface Subscribe {
  type: "subscribe";
  channel: "garden" | "agent" | "dialectic";
  filter?: { agent_id?: string; context?: string };
}

interface Invoke {
  type: "invoke";
  id: string;  // Client-generated request ID
  handle: string;  // Full AGENTESE path
  observer: { archetype: string; id: string; capabilities: string[] };
  kwargs?: Record<string, unknown>;
}

interface Unsubscribe {
  type: "unsubscribe";
  channel: string;
}

// Server → Client messages
interface StateUpdate {
  type: "state_update";
  channel: string;
  data: {
    entities: Entity[];
    pheromones: Pheromone[];
    entropy: number;
    timestamp: string;
  };
}

interface InvokeResult {
  type: "invoke_result";
  id: string;  // Matches request ID
  success: boolean;
  result?: unknown;
  error?: { code: string; message: string; suggestion?: string };
  meta: { span_id: string; duration_ms: number };
}

interface DialecticEvent {
  type: "dialectic_event";
  phase: "thesis" | "antithesis" | "synthesis";
  content: string;
  agent_id: string;
}
```

### 3. Server-Sent Events (SSE)

For streaming results (e.g., LLM responses, long traces).

```http
GET /api/v1/self/soul/challenge?prompt=What%20is%20justice%3F
Accept: text/event-stream
X-Observer-Archetype: philosopher

Response stream:
event: chunk
data: {"type": "thinking", "content": "Considering..."}

event: chunk
data: {"type": "response", "content": "Justice is", "partial": true}

event: chunk
data: {"type": "response", "content": " a complex concept", "partial": true}

event: done
data: {"result": "Justice is a complex concept...", "span_id": "xyz789"}
```

---

## Implementation Architecture

### Module Structure

```
impl/claude/protocols/api/
├── __init__.py
├── bridge.py           # AgenteseBridge: Logos ↔ HTTP translation
├── server.py           # FastAPI/Starlette application
├── websocket.py        # WebSocket handler + subscriptions
├── sse.py              # SSE streaming utilities
├── serializers.py      # Pydantic models for request/response
├── middleware.py       # Auth, CORS, telemetry
├── openapi.py          # OpenAPI spec generation
└── _tests/
    ├── test_bridge.py
    ├── test_endpoints.py
    ├── test_websocket.py
    └── test_sse.py
```

### Core Classes

#### AgenteseBridge

```python
@dataclass
class AgenteseBridge:
    """
    The bridge between HTTP/WS and AGENTESE Logos.

    Responsibilities:
    1. Parse incoming requests into Umwelt + handle
    2. Invoke Logos with proper observer context
    3. Serialize results to JSON
    4. Handle streaming for SSE
    5. Manage WebSocket subscriptions
    """

    logos: Logos
    telemetry_enabled: bool = True

    async def invoke_http(
        self,
        context: str,
        holon: str,
        aspect: str,
        observer: ObserverContext,
        kwargs: dict[str, Any],
    ) -> AgentseResponse:
        """
        HTTP invocation path.

        Maps:
          GET /api/v1/world/field/manifest
          → logos.invoke("world.field.manifest", observer_umwelt)
        """
        handle = f"{context}.{holon}.{aspect}"
        umwelt = self._context_to_umwelt(observer)

        with self._create_span(handle, observer) as span:
            try:
                result = await self.logos.invoke(handle, umwelt, **kwargs)
                return AgenteseResponse(
                    handle=handle,
                    result=self._serialize(result),
                    meta=ResponseMeta(
                        observer=observer.archetype,
                        span_id=span.span_id,
                        timestamp=datetime.utcnow(),
                    ),
                )
            except AffordanceError as e:
                raise HTTPException(403, detail=e.to_dict())
            except PathNotFoundError as e:
                raise HTTPException(404, detail=e.to_dict())

    async def stream_invoke(
        self,
        handle: str,
        observer: ObserverContext,
        kwargs: dict[str, Any],
    ) -> AsyncIterator[SSEEvent]:
        """
        SSE streaming invocation for long-running operations.
        """
        umwelt = self._context_to_umwelt(observer)

        # For soul/challenge, we need streaming
        if "soul" in handle and "challenge" in handle:
            async for chunk in self._stream_soul_challenge(umwelt, kwargs):
                yield SSEEvent(event="chunk", data=chunk)
        else:
            # Regular invoke, single response
            result = await self.logos.invoke(handle, umwelt, **kwargs)
            yield SSEEvent(event="done", data={"result": result})

    def subscribe(
        self,
        channel: str,
        filter_: SubscriptionFilter | None,
    ) -> Subscription:
        """
        Create a WebSocket subscription.

        Channels:
        - "garden": All entity movement + pheromone updates
        - "agent:{id}": Single agent state changes
        - "dialectic": Dialectic phase events
        """
        ...
```

#### Serialization (Pydantic Models)

```python
from pydantic import BaseModel, Field
from typing import Any, Literal
from datetime import datetime

class ObserverContext(BaseModel):
    """Observer context from HTTP headers or request body."""
    archetype: str = "viewer"
    id: str = "anonymous"
    capabilities: list[str] = []

class ResponseMeta(BaseModel):
    """Metadata attached to every response."""
    observer: str
    span_id: str
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

class ErrorResponse(BaseModel):
    """Sympathetic error response."""
    error: str
    code: str
    path: str | None = None
    suggestion: str | None = None
    available: list[str] | None = None
```

---

## OpenAPI Specification

The API is self-documenting via OpenAPI 3.1:

```yaml
openapi: 3.1.0
info:
  title: AGENTESE Universal Protocol
  version: 1.0.0
  description: |
    The lingua franca for agent-world interaction.
    Every UI is a projection of this API.

paths:
  /api/v1/{context}/{holon}/manifest:
    get:
      summary: Manifest an entity to observer's perception
      description: |
        Collapse the entity to the observer's view.
        Different observers receive different renderings (Polymorphic Principle).
      parameters:
        - name: context
          in: path
          required: true
          schema:
            type: string
            enum: [world, self, concept, void, time]
        - name: holon
          in: path
          required: true
          schema:
            type: string
        - name: X-Observer-Archetype
          in: header
          schema:
            type: string
            default: viewer
        - name: X-Observer-Id
          in: header
          schema:
            type: string
      responses:
        '200':
          description: Successful manifest
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AgenteseResponse'
        '403':
          description: Affordance denied
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '404':
          description: Path not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /api/v1/{context}/{holon}/{aspect}:
    post:
      summary: Invoke an aspect on an entity
      description: |
        Execute an affordance. Observer must have permission.
        Returns aspect-specific result.
      # ... parameters and responses ...

  /api/v1/compose:
    post:
      summary: Execute a composition pipeline
      description: |
        Chain multiple AGENTESE paths into a pipeline.
        Preserves category laws (identity, associativity).
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CompositionRequest'
      # ... responses ...

  /api/v1/ws/garden:
    get:
      summary: WebSocket connection for real-time garden state
      description: |
        Bidirectional WebSocket for live updates.
        Subscribe to channels: garden, agent:{id}, dialectic
      # ... WebSocket documentation ...

components:
  schemas:
    AgenteseResponse:
      type: object
      properties:
        handle:
          type: string
          example: "world.field.manifest"
        result:
          description: Observer-specific result
        meta:
          $ref: '#/components/schemas/ResponseMeta'

    ErrorResponse:
      type: object
      properties:
        error:
          type: string
        code:
          type: string
          enum: [AFFORDANCE_DENIED, PATH_NOT_FOUND, OBSERVER_REQUIRED, SYNTAX_ERROR]
        suggestion:
          type: string
        available:
          type: array
          items:
            type: string
```

---

## Integration with Marimo

The marimo integration already has `LogosCell` and `invoke_sync`. The API layer shares the same bridge:

```python
# In marimo notebook
import marimo as mo
from impl.claude.protocols.api.bridge import AgenteseBridge

@app.cell
def setup():
    bridge = AgenteseBridge.from_default_logos()
    return bridge

@app.cell
async def manifest_field(bridge):
    # Same invocation path as HTTP API
    response = await bridge.invoke_http(
        context="world",
        holon="field",
        aspect="manifest",
        observer=ObserverContext(archetype="architect"),
        kwargs={},
    )
    return mo.md(f"**Result**: {response.result}")

# OR use the native marimo widgets
@app.cell
def stigmergic_view(bridge):
    from impl.claude.agents.i.marimo import StigmergicFieldWidget
    return StigmergicFieldWidget(bridge=bridge)
```

**The Unification**: marimo notebooks use the same `AgenteseBridge` that powers the HTTP API. One codebase, multiple projections.

---

## Example React Components (Not a Full App)

We ship example components, not a maintained React codebase:

```typescript
// examples/react/AgentseClient.ts
export class AgenteseClient {
  constructor(private baseUrl: string) {}

  async manifest(
    context: string,
    holon: string,
    observer: Observer
  ): Promise<AgenteseResponse> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/${context}/${holon}/manifest`,
      {
        headers: {
          'X-Observer-Archetype': observer.archetype,
          'X-Observer-Id': observer.id,
        },
      }
    );
    return response.json();
  }

  async invoke(
    handle: string,
    observer: Observer,
    kwargs: Record<string, unknown> = {}
  ): Promise<AgenteseResponse> {
    const [context, holon, aspect] = handle.split('.');
    const response = await fetch(
      `${this.baseUrl}/api/v1/${context}/${holon}/${aspect}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Observer-Archetype': observer.archetype,
          'X-Observer-Id': observer.id,
        },
        body: JSON.stringify(kwargs),
      }
    );
    return response.json();
  }

  subscribeToGarden(onUpdate: (state: GardenState) => void): () => void {
    const ws = new WebSocket(`${this.baseUrl.replace('http', 'ws')}/api/v1/ws/garden`);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'state_update') {
        onUpdate(data.data);
      }
    };
    return () => ws.close();
  }
}

// examples/react/StigmergicField.tsx
import { useEffect, useState } from 'react';
import { AgenteseClient, GardenState } from './AgenteseClient';

export function StigmergicField({ client }: { client: AgenteseClient }) {
  const [garden, setGarden] = useState<GardenState | null>(null);

  useEffect(() => {
    const unsubscribe = client.subscribeToGarden(setGarden);
    return unsubscribe;
  }, [client]);

  if (!garden) return <div>Loading garden...</div>;

  return (
    <svg viewBox="0 0 800 600">
      {garden.pheromones.map((p, i) => (
        <circle
          key={i}
          cx={p.x}
          cy={p.y}
          r={p.radius}
          fill={`rgba(${p.color}, ${p.intensity * 0.3})`}
        />
      ))}
      {garden.entities.map((e) => (
        <text
          key={e.id}
          x={e.x}
          y={e.y}
          fill={e.color}
          fontSize="20"
        >
          {e.glyph}
        </text>
      ))}
    </svg>
  );
}
```

**Shipping Strategy**:
- `examples/react/` → Example components (MIT licensed)
- `examples/react/README.md` → "Build your own client" guide
- No React in our dependencies. No maintenance burden.

---

## The Four Waves

### Wave 1: Core Bridge (Foundation)

| Task | Files | Tests |
|------|-------|-------|
| AgenteseBridge class | `api/bridge.py` | Unit tests for all invoke paths |
| Pydantic serializers | `api/serializers.py` | Schema validation tests |
| Error handling | `api/exceptions.py` | Sympathetic error tests |

**Exit Criteria**: `bridge.invoke_http()` works for all five contexts.

### Wave 2: HTTP Layer

| Task | Files | Tests |
|------|-------|-------|
| FastAPI app | `api/server.py` | Integration tests |
| All REST endpoints | `api/routes/` | Endpoint tests |
| OpenAPI generation | `api/openapi.py` | Spec validation |
| Middleware (CORS, auth) | `api/middleware.py` | Middleware tests |

**Exit Criteria**: `uvicorn api.server:app` serves working API. OpenAPI spec validates.

### Wave 3: Real-Time Layer

| Task | Files | Tests |
|------|-------|-------|
| WebSocket handler | `api/websocket.py` | WS integration tests |
| Subscription system | `api/subscriptions.py` | Pub/sub tests |
| SSE streaming | `api/sse.py` | Stream tests |
| Garden state updates | Integration with StigmergicField | Live update tests |

**Exit Criteria**: WebSocket clients receive live garden updates. SSE streams soul challenges.

### Wave 4: Documentation & Examples

| Task | Files | Tests |
|------|-------|-------|
| OpenAPI spec polish | `docs/api/openapi.yaml` | — |
| React examples | `examples/react/` | — |
| TypeScript types | `examples/react/types.ts` | — |
| Integration guide | `docs/api/README.md` | — |
| marimo bridge docs | `docs/api/marimo.md` | — |

**Exit Criteria**: Developer can build React client using only docs + examples.

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Coverage | 100% of AGENTESE aspects callable | Endpoint count |
| Response Time | <50ms for manifest, <200ms for refine | Profiling |
| OpenAPI Validity | Zero spec errors | `openapi-spec-validator` |
| Type Coverage | 100% Pydantic models | mypy |
| WebSocket Latency | <100ms for state updates | Client timing |
| External Adoption | 1+ external React client built | Community |

---

## Cross-Synergies

### AUP + Marimo
- marimo notebooks use same AgenteseBridge
- WASM export still works (static site hits live API)
- marimo becomes "reference client"

### AUP + K-gent Chatbot Deployment
- Chatbot frontend consumes API
- WebSocket for streaming responses
- SSE for LLM token streaming

### AUP + TUI
- TUI can optionally use API (for remote gardens)
- Enables "headless" kgents server

### AUP + Observability
- Span IDs in responses enable distributed tracing
- Prometheus metrics at `/metrics`
- Health checks at `/health`

---

## Exit Criteria (Crown Jewel)

1. `uvicorn impl.claude.protocols.api.server:app` starts without error
2. `GET /api/v1/world/field/manifest` returns valid JSON
3. `POST /api/v1/concept/justice/refine` executes dialectic
4. WebSocket at `/api/v1/ws/garden` streams live updates
5. SSE at `/api/v1/self/soul/challenge` streams LLM response
6. OpenAPI spec at `/openapi.json` validates clean
7. React example component connects and renders garden
8. marimo notebook uses same bridge as HTTP API
9. All tests pass, mypy clean
10. **Kent says "this is amazing"** (HARD REQUIREMENT)

---

## The Philosophy

> *"Don't build a React app. Build a React-compatible API."*

The AGENTESE Universal Protocol is not about React. It's about making AGENTESE so accessible that **any** frontend can speak it. We maintain:

- Zero JavaScript in our codebase
- Zero React maintenance burden
- One Python server
- Multiple projections (TUI, marimo, React, curl)

The API IS the product. Everything else is a view.

---

*"The functor lifts the string into action. The wire carries the action to the world. The world renders what the observer deserves to see."*

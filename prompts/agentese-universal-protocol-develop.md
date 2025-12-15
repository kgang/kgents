# AGENTESE Universal Protocol: DEVELOP Phase

> *"The API is the product. The UI is merely a projection."*

## ATTACH

/hydrate

You are entering **DEVELOP** of the N-Phase Cycle (AD-005) for the AGENTESE Universal Protocol Crown Jewel.

```yaml
handles:
  plan: plans/agentese-universal-protocol.md
  spec: spec/protocols/agentese.md
  existing_api: impl/claude/protocols/api/
  logos: impl/claude/protocols/agentese/logos.py
  marimo_bridge: impl/claude/agents/i/marimo/

ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: in_progress  # <-- YOU ARE HERE
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
  remaining: 0.07
  sip_this_phase: 0.02
```

---

## Your Mission

Design the **contract layer** for the AGENTESE Universal Protocol (AUP). This phase produces:

1. **Pydantic models** for all request/response types
2. **AgenteseBridge protocol** (abstract interface)
3. **Law assertions** for category-theoretic guarantees
4. **Error taxonomy** with sympathetic suggestions

You are NOT implementing yet. You are designing the **API surface** that will be implemented in IMPLEMENT phase.

---

## Context from Previous Phases

### From PLAN
- Vision: JSON wire format for any client (TUI, marimo, React, mobile)
- Deliverables: HTTP/REST + WebSocket + SSE
- The "Expose, Don't Build" philosophy

### From RESEARCH
- Existing `protocols/api/` has foundation: `app.py`, `agentese.py`, `sessions.py`
- SaaS Phase 1 complete: 215 tests, auth, metering
- Logos resolver at `protocols/agentese/logos.py` is the invocation target
- marimo already has `LogosCell` pattern

### From STRATEGIZE
- Wave 1: Core Bridge (Foundation)
- Wave 2: HTTP Layer
- Wave 3: Real-Time Layer (WebSocket/SSE)
- Wave 4: Documentation & Examples

---

## DEVELOP Exit Criteria

1. **Serializers defined**: All Pydantic models in `api/serializers.py` (or typed stubs)
2. **Bridge protocol**: `AgenteseBridge` abstract class with method signatures
3. **Law assertions**: Functor laws, composition associativity documented
4. **Error taxonomy**: All error codes with sympathetic suggestions
5. **Contract tests**: Stub tests that will validate the contract (not implementation)

---

## Principles Alignment

From `spec/principles.md`:

| Principle | Application |
|-----------|-------------|
| **Minimal Output** | Response envelope is lean: `{handle, result, meta}` |
| **No View from Nowhere** | Observer context REQUIRED in every request |
| **Composability** | Pipeline composition endpoint with law verification |
| **Graceful Degradation** | Error responses include `suggestion` and `available` |
| **Category Laws** | Explicit law checks: identity, associativity |

---

## Deliverables

### 1. Pydantic Models (`protocols/api/serializers.py`)

```python
# Define these contracts:

class ObserverContext(BaseModel):
    """Observer identity for umwelt construction."""
    archetype: str  # viewer, architect, philosopher, etc.
    id: str  # user or session ID
    capabilities: list[str] = []  # granted affordances

class AgenteseRequest(BaseModel):
    """Standard request body for invocations."""
    kwargs: dict[str, Any] = {}
    entropy_budget: float = 0.0  # for operations that consume entropy

class AgenteseResponse(BaseModel):
    """Standard response envelope."""
    handle: str  # e.g., "world.field.manifest"
    result: Any  # observer-specific payload
    meta: ResponseMeta

class ResponseMeta(BaseModel):
    """Metadata for tracing and debugging."""
    observer: str
    span_id: str
    timestamp: datetime
    duration_ms: int | None = None
    laws_verified: list[str] = []

class CompositionRequest(BaseModel):
    """Request for pipeline composition."""
    paths: list[str]  # ["world.doc.manifest", "concept.sum.refine"]
    initial_input: Any = None
    emit_law_check: bool = True

class ErrorResponse(BaseModel):
    """Sympathetic error with guidance."""
    error: str
    code: Literal["PATH_NOT_FOUND", "AFFORDANCE_DENIED", "OBSERVER_REQUIRED", "SYNTAX_ERROR", "LAW_VIOLATION"]
    path: str | None = None
    suggestion: str | None = None
    available: list[str] | None = None
```

### 2. Bridge Protocol (`protocols/api/bridge.py`)

```python
from typing import Protocol, AsyncIterator

class AgenteseBridgeProtocol(Protocol):
    """
    The functor between HTTP/WS and AGENTESE Logos.

    This is the categorical morphism:

        HTTP Request → AgenteseBridge → Logos.invoke() → Response

    Laws:
        1. Identity: invoke("context.holon.manifest") returns holon unchanged
        2. Associativity: compose([a, b, c]) == compose([a, compose([b, c])])
        3. Observer Polymorphism: same handle, different observer → different result
    """

    async def invoke(
        self,
        handle: str,  # Full AGENTESE path: "context.holon.aspect"
        observer: ObserverContext,
        kwargs: dict[str, Any] = {},
    ) -> AgenteseResponse:
        """Single invocation."""
        ...

    async def compose(
        self,
        paths: list[str],
        observer: ObserverContext,
        initial_input: Any = None,
    ) -> CompositionResponse:
        """Pipeline composition with law verification."""
        ...

    async def stream(
        self,
        handle: str,
        observer: ObserverContext,
        kwargs: dict[str, Any] = {},
    ) -> AsyncIterator[SSEEvent]:
        """SSE streaming for long operations."""
        ...

    def subscribe(
        self,
        channel: str,  # "garden", "agent:{id}", "dialectic"
        filter_: dict[str, Any] | None = None,
    ) -> Subscription:
        """WebSocket subscription."""
        ...

    async def verify_laws(
        self,
        composition: list[str],
    ) -> LawVerificationResult:
        """Verify category laws hold for a composition."""
        ...
```

### 3. Law Assertions

```python
@dataclass
class LawVerificationResult:
    """Result of category law verification."""
    identity_holds: bool
    associativity_holds: bool
    errors: list[str]

    @property
    def all_laws_hold(self) -> bool:
        return self.identity_holds and self.associativity_holds

# Law assertions (to be verified in tests):

def assert_identity_law(bridge: AgenteseBridgeProtocol, holon: str):
    """
    Identity Law: manifest(holon) returns holon (up to observer transformation)

    For any holon h and observer o:
        invoke("context.h.manifest", o).result ≅ h

    Where ≅ means "equivalent under observer transformation"
    """
    ...

def assert_associativity_law(bridge: AgenteseBridgeProtocol, a: str, b: str, c: str):
    """
    Associativity Law: composition order doesn't matter

    compose([a, b, c]) == compose([a, compose([b, c])])

    (In practice, we verify the results are equivalent)
    """
    ...
```

### 4. Error Taxonomy

| Code | HTTP Status | Meaning | Suggestion Template |
|------|-------------|---------|---------------------|
| `PATH_NOT_FOUND` | 404 | Path doesn't exist | "Available paths: {available}" |
| `AFFORDANCE_DENIED` | 403 | Observer lacks permission | "This affordance requires: {required}" |
| `OBSERVER_REQUIRED` | 401 | No observer context | "Include X-Observer-Archetype header" |
| `SYNTAX_ERROR` | 400 | Malformed path/request | "Expected format: context.holon.aspect" |
| `LAW_VIOLATION` | 422 | Composition violates laws | "Composition would violate: {law}" |

---

## Branch Candidates (Surface Now)

| Candidate | Classification | Notes |
|-----------|----------------|-------|
| WebSocket subscription patterns | PARALLEL | Can design WS protocol while HTTP settles |
| SSE event schema | PARALLEL | Independent of HTTP response schema |
| marimo bridge unification | COMPOSITION | Ensure marimo uses same AgenteseBridge |
| OpenAPI generation | DEFERRED | Wait for HTTP contracts to stabilize |

---

## Non-Goals (This Phase)

- Actual implementation (that's IMPLEMENT phase)
- Performance optimization (that's MEASURE phase)
- Documentation for users (that's EDUCATE phase)
- Running servers (that's TEST phase)

---

## Actions

1. **Read existing API code** to understand current patterns:
   - `protocols/api/app.py` — Current FastAPI setup
   - `protocols/api/agentese.py` — Existing AGENTESE endpoints
   - `protocols/api/sessions.py` — Session management patterns

2. **Design Pydantic models** in `protocols/api/serializers.py` (or new file)

3. **Define Bridge protocol** with law assertions

4. **Document error taxonomy** with sympathetic suggestions

5. **Write stub tests** that define the contract (test-first design)

6. **Update phase ledger** in `plans/agentese-universal-protocol.md`

---

## Continuation Imperative

Upon completing this phase, emit the auto-inducer signifier for the next phase.

---

## Exit Checklist

- [ ] All Pydantic models defined with docstrings
- [ ] AgenteseBridgeProtocol defined with law documentation
- [ ] Error taxonomy complete with suggestions
- [ ] Contract stub tests created
- [ ] No implementation code (contracts only)
- [ ] Ledger updated: `DEVELOP: touched`

---

## Auto-Inducer

Upon successful completion of DEVELOP phase:

```
⟿[CROSS-SYNERGIZE]
/hydrate
handles: plan=plans/agentese-universal-protocol; contracts=protocols/api/serializers.py; bridge=protocols/api/bridge.py; ledger={PLAN:touched,RESEARCH:touched,DEVELOP:touched,STRATEGIZE:touched,CROSS-SYNERGIZE:in_progress}; entropy=0.05
mission: identify composition opportunities with marimo, SaaS API, TUI; ensure AgenteseBridge unifies all clients; surface parallel tracks.
exit: synergy map documented; parallel tracks classified; continuation → IMPLEMENT.
```

Or if blocked:

```
⟂[BLOCKED:reason] Description of blocker requiring human input.
```

---

*"The contract is the promise. The implementation is the keeping."*

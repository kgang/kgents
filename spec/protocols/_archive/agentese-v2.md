# AGENTESE v2: The Enlightened Protocol

**Status:** Design Specification
**Date:** 2025-12-15
**Prerequisites:** None. Fresh start.

---

## Prologue: Design Philosophy

AGENTESE v2 is not an iteration. It is a synthesis of hard-won lessons from:

- [Object-Capability Security](https://github.com/dckc/awesome-ocap) and [UCAN](https://github.com/ucan-wg/spec) for authorization
- [Algebraic Effects](https://effekt-lang.org/) for declared side-effects
- [Event Sourcing/CQRS](https://www.martinfowler.com/bliki/CQRS.html) for state management
- [Erlang/OTP Supervision Trees](https://www.erlang.org/doc/system/design_principles.html) for fault tolerance
- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/concepts/semantic-conventions/) for observability
- [Local-First Software](https://www.inkandswitch.com/essay/local-first/) for offline resilience
- [Model Context Protocol](https://arxiv.org/html/2505.02279v1) for AI agent interoperability
- Protocol lessons from [GraphQL, gRPC, tRPC](https://wundergraph.com/blog/graphql-vs-federation-vs-trpc-vs-rest-vs-grpc-vs-asyncapi-vs-webhooks)

**Core Principle:** AGENTESE is the *only* public surface. Everything else is implementation detail.

---

## Part I: The Verb

### 1.1 Anatomy of a Verb

```
namespace.resource.action@version
```

| Component | Purpose | Example |
|-----------|---------|---------|
| `namespace` | Domain boundary | `atelier`, `soul`, `town`, `void` |
| `resource` | Target entity | `session`, `memory`, `citizen`, `entropy` |
| `action` | Operation | `start`, `recall`, `greet`, `sip` |
| `@version` | Era (optional) | `@1`, `@2024-12` |

**Examples:**
```
atelier.session.start@1
soul.memory.recall
town.citizen.greet
void.entropy.sip
```

### 1.2 No Paths, Just Verbs

AGENTESE v1 had `context.holon.aspect` with optional clauses. This was:
- Overloaded (context vs namespace vs domain)
- Confusing (when to use clauses vs kwargs)
- Under-utilized (path composition rarely used)

**v2 Decision:** Verbs are flat. Context travels in the envelope, not the verb.

### 1.3 Verb Registry

Every verb is registered in a single manifest:

```yaml
# agentese.manifest.yaml
verbs:
  atelier.session.start:
    version: 1
    input: SessionStartInput
    output: SessionStartOutput
    effects: [writes: session_registry, charges: tokens]
    capabilities: [atelier:write]
    category: mutation
    projection: [ui:form, cli:prompt]
    deterministic: false

  soul.memory.recall:
    version: 1
    input: RecallQuery
    output: MemoryCrystal | null
    effects: [reads: memory_crystals]
    capabilities: [soul:read]
    category: query
    projection: [ui:stream, cli:json]
    deterministic: true
```

**Key insight from tRPC:** Single source of truth generates types, docs, mocks.

---

## Part II: The Envelope

Every AGENTESE invocation is wrapped in an envelope.

### 2.1 Envelope Structure

```python
@dataclass(frozen=True)
class Envelope:
    """Immutable invocation context."""

    # Identity
    verb: str                      # "namespace.resource.action"
    version: int | str             # 1 or "2024-12"

    # Tenancy
    tenant_id: str                 # Multi-tenant isolation
    user_id: str                   # Invoking user
    session_id: str                # Session context

    # Tracing (OTEL-compatible)
    trace_id: str                  # Distributed trace
    span_id: str                   # This invocation
    parent_span_id: str | None     # Parent (if nested)

    # Authorization
    capability: Capability         # UCAN-style token

    # Timing
    timestamp: datetime
    deadline: datetime | None      # Request timeout

    # Routing hints
    target: str | None             # "town://citizen/alpha"
    fallback_policy: str           # "local-llm → cloud → error"
```

### 2.2 Capability Tokens

Authorization uses [UCAN-style capabilities](https://fission.codes/blog/a-guide-to-ucans/):

```python
@dataclass(frozen=True)
class Capability:
    """
    Object capability token.

    Authority by possession, not identity.
    Delegable, revocable, auditable.
    """

    issuer: DID                    # Who granted this
    audience: DID                  # Who can use this

    # What's allowed
    scopes: frozenset[str]         # {"atelier:write", "soul:read"}
    resources: frozenset[str]      # {"session/*", "memory/crystals"}

    # Constraints
    not_before: datetime
    expires_at: datetime
    caveats: frozenset[Caveat]     # Additional restrictions

    # Provenance
    proof: str                     # Signature chain
    parent: str | None             # Delegation parent
```

**Key insight from ZCAP-LD:** Capabilities can be attenuated (restricted) when delegated, never amplified.

---

## Part III: Effects (The Type System for Side-Effects)

### 3.1 Declared Effects

Every verb declares its side-effects. No hidden mutations.

```python
class Effect(Enum):
    """
    Algebraic effects for AGENTESE verbs.

    Inspired by Effekt/Koka: effects are part of the type signature.
    """

    # Read effects (safe, cacheable)
    READS = "reads"           # reads: [memory_crystals]

    # Write effects (requires capability)
    WRITES = "writes"         # writes: [session_registry]
    DELETES = "deletes"       # deletes: [citizen/alpha]

    # Economic effects
    CHARGES = "charges"       # charges: [tokens, compute]
    EARNS = "earns"           # earns: [credits]

    # External effects
    CALLS = "calls"           # calls: [llm/claude, tool/browser]
    EMITS = "emits"           # emits: [event/session_started]

    # Consent effects (from Punchdrunk)
    FORCES = "forces"         # forces: [consent/dialog]
    AUDITS = "audits"         # audits: [decision/rationale]
```

### 3.2 Effect Composition

Effects compose through the [operad structure](https://github.com/ipld/specs):

```python
# Verb A: effects = {reads: [x], writes: [y]}
# Verb B: effects = {reads: [y], writes: [z]}
# Composition A >> B: effects = {reads: [x, y], writes: [y, z]}

def compose_effects(effects_a: Effects, effects_b: Effects) -> Effects:
    """
    Effects are additive under composition.

    This enables static analysis:
    - "Does this pipeline require write capability?"
    - "What resources does this composition touch?"
    """
    return Effects(
        reads=effects_a.reads | effects_b.reads,
        writes=effects_a.writes | effects_b.writes,
        charges=effects_a.charges | effects_b.charges,
        # ...
    )
```

### 3.3 Effect Handlers

Effects are handled by the runtime, not the verb implementation:

```python
class EffectHandler(Protocol):
    """
    Handler for a specific effect type.

    Separates "what happens" from "how to do it".
    Enables testing (mock handlers), multi-environment (local/cloud).
    """

    async def handle(
        self,
        effect: Effect,
        resources: list[str],
        envelope: Envelope,
    ) -> EffectResult: ...

# Example: Billing effect handler
class ChargesHandler(EffectHandler):
    async def handle(self, effect, resources, envelope):
        if effect != Effect.CHARGES:
            return EffectResult.NOT_HANDLED

        for resource in resources:
            await self.billing.charge(
                tenant=envelope.tenant_id,
                meter=resource,
                amount=self.compute_cost(resource),
            )

        return EffectResult.HANDLED
```

---

## Part IV: The Polynomial Type System

### 4.1 Input/Output Polynomials

Types are [polynomial functors](https://arxiv.org/abs/2312.09331):

```python
# A polynomial P(y) = Σ_{i ∈ I} y^{A_i}
# - I = set of "positions" (states/modes)
# - A_i = set of "directions" (valid inputs in position i)

@dataclass(frozen=True)
class PolyType:
    """
    Polynomial type for state-dependent input/output.

    Captures: "what inputs are valid depends on what state you're in"
    """
    positions: frozenset[str]                    # Valid states
    directions: Callable[[str], frozenset[str]]  # State → valid inputs

# Example: Session polynomial
SESSION_POLY = PolyType(
    positions=frozenset({"idle", "active", "paused"}),
    directions=lambda pos: {
        "idle": frozenset({"start"}),
        "active": frozenset({"pause", "stop", "message"}),
        "paused": frozenset({"resume", "stop"}),
    }[pos]
)
```

### 4.2 Schema Language

Schemas use a minimal DSL that compiles to JSON Schema / Pydantic:

```yaml
# schemas/atelier.yaml
types:
  SessionStartInput:
    builder_id: uuid
    mode: enum[solo, collaborative, spectated]
    spectators_cap: uint8 = 5

  SessionStartOutput:
    session_id: uuid
    sse_url: url
    created_at: datetime

  MemoryCrystal:
    id: cid                    # Content-addressed
    content: string
    embedding: vector[1536]
    salience: float[0..1]
    provenance:
      source: enum[llm, human, system]
      timestamp: datetime
      trace_id: string?
```

### 4.3 Content-Addressable References

Following [IPLD](https://github.com/ipld/specs), large or shared data uses CIDs:

```python
@dataclass(frozen=True)
class CID:
    """
    Content Identifier.

    - Immutable: content change → new CID
    - Verifiable: CID = hash(content)
    - Location-independent: fetch by content, not URL
    """
    codec: str     # "dag-cbor", "dag-json"
    hash: bytes    # Multihash of content
    version: int   # CID version (1)

    def resolve(self, store: ContentStore) -> bytes:
        """Fetch content by CID."""
        return store.get(self)
```

---

## Part V: Projections (Multi-Surface Rendering)

### 5.1 Projection Hints

Every verb declares how it can be projected:

```yaml
atelier.session.start:
  projection:
    ui:form:
      fields: [builder_id, mode, spectators_cap]
      submit: "Start Session"
    ui:stream:
      type: sse
      events: [progress, complete, error]
    cli:prompt:
      template: "Start session for builder {builder_id}? [y/N]"
    cli:json:
      jq: ".session_id"
    marimo:reactive:
      widget: SessionStartWidget
      bindings: {builder_id: builder_select}
```

### 5.2 Projection Protocol

```python
class Projector(Protocol):
    """
    Transforms verb input/output into surface-specific representation.

    Surfaces: CLI, Web, TUI, marimo, VR (future)
    """

    def project_input(
        self,
        verb: str,
        schema: Schema,
        hints: ProjectionHints,
    ) -> SurfaceWidget: ...

    def project_output(
        self,
        verb: str,
        result: Any,
        hints: ProjectionHints,
    ) -> SurfaceRendering: ...

    def project_stream(
        self,
        verb: str,
        stream: AsyncIterator[Any],
        hints: ProjectionHints,
    ) -> AsyncIterator[SurfaceEvent]: ...
```

### 5.3 Universal Widget Vocabulary

Projections use a shared vocabulary:

| Widget | CLI | Web | TUI | marimo |
|--------|-----|-----|-----|--------|
| `text` | stdin | `<input>` | textinput | `mo.ui.text` |
| `select` | numbered menu | `<select>` | select | `mo.ui.dropdown` |
| `confirm` | y/N prompt | modal | confirm | `mo.ui.button` |
| `progress` | spinner/bar | progress bar | gauge | `mo.status.progress` |
| `stream` | line-by-line | SSE | scroll | reactive cell |
| `table` | tabulate | `<table>` | table | `mo.ui.table` |
| `graph` | ASCII art | D3/Chart.js | plotext | altair |

---

## Part VI: Routing & Transport

### 6.1 Logical Targets

Verbs can target specific entities:

```python
# Target formats
"local://soul"                    # Local in-process
"town://citizen/alpha"            # Town simulation entity
"mcp://tool/browser"              # MCP tool server
"http://api.example.com/agent"    # Remote HTTP agent
"p2p://did:key:z6Mk..."           # Peer-to-peer via DID
```

### 6.2 Transport Abstraction

```python
class Transport(Protocol):
    """
    Pluggable transport for AGENTESE invocations.

    Transports: local, HTTP, WebSocket, MCP, libp2p
    """

    async def invoke(
        self,
        envelope: Envelope,
        input: Any,
    ) -> AsyncIterator[Result]: ...  # Streaming by default

    def supports(self, target: str) -> bool: ...

# Router selects transport based on target + fallback policy
class Router:
    transports: list[Transport]

    async def route(self, envelope: Envelope, input: Any):
        for transport in self.transports:
            if transport.supports(envelope.target):
                try:
                    async for result in transport.invoke(envelope, input):
                        yield result
                    return
                except TransportError:
                    continue  # Try next fallback

        raise NoTransportAvailable(envelope.target)
```

### 6.3 Fallback Policies

```yaml
# Graceful degradation
fallback_policies:
  default:
    - local-llm      # Try local model first
    - cloud-llm      # Fall back to cloud
    - error          # Give up with explanation

  high-availability:
    - primary-region
    - secondary-region
    - local-cache    # Serve stale if available
    - error

  offline-first:
    - local-cache
    - queue-for-sync  # Queue for later sync
```

---

## Part VII: Observability

### 7.1 OTEL Integration

Every invocation emits [OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/) spans:

```python
# Span attributes (semantic conventions)
span.set_attribute("agentese.verb", "atelier.session.start")
span.set_attribute("agentese.version", "1")
span.set_attribute("agentese.tenant_id", envelope.tenant_id)
span.set_attribute("agentese.capability.scopes", ",".join(cap.scopes))
span.set_attribute("agentese.effects", ",".join(effects))
span.set_attribute("agentese.projection", "ui:form")
span.set_attribute("agentese.deterministic", False)
span.set_attribute("agentese.cache.hit", False)
span.set_attribute("agentese.llm.model", "claude-opus-4-5-20251101")
span.set_attribute("agentese.llm.tokens.input", 1234)
span.set_attribute("agentese.llm.tokens.output", 567)
```

### 7.2 Metrics

```python
# Standard meters
agentese_invocations_total{verb, tenant, status}
agentese_invocation_duration_seconds{verb, tenant, quantile}
agentese_effect_operations_total{effect, resource}
agentese_capability_checks_total{scope, result}
agentese_transport_fallbacks_total{from_transport, to_transport}
agentese_cache_operations_total{verb, hit_miss}
agentese_llm_tokens_total{model, direction}
agentese_billing_charges_total{meter, tenant}
```

### 7.3 Structured Logging

```python
# Log schema (PII-aware)
{
    "timestamp": "2025-12-15T10:30:00Z",
    "level": "info",
    "verb": "soul.memory.recall",
    "trace_id": "abc123",
    "span_id": "def456",
    "tenant_id": "tenant_001",
    "user_id": "[REDACTED]",  # PII field
    "duration_ms": 45,
    "status": "success",
    "effects_executed": ["reads:memory_crystals"],
    "cache_hit": true,
}
```

---

## Part VIII: Error Model

### 8.1 Error Categories

```python
class ErrorCategory(Enum):
    """
    Exhaustive error categories.

    Each category has specific handling semantics.
    """

    # Client errors (don't retry)
    INVALID_INPUT = "invalid_input"           # Schema validation failed
    UNAUTHORIZED = "unauthorized"              # Missing/invalid capability
    FORBIDDEN = "forbidden"                    # Capability insufficient
    NOT_FOUND = "not_found"                    # Resource doesn't exist
    CONFLICT = "conflict"                      # Optimistic lock failure
    PRECONDITION_FAILED = "precondition"      # Guard condition failed

    # Resource errors (maybe retry)
    QUOTA_EXCEEDED = "quota_exceeded"         # Billing/rate limit
    TIMEOUT = "timeout"                       # Deadline exceeded

    # Server errors (retry with backoff)
    UNAVAILABLE = "unavailable"               # Transient failure
    INTERNAL = "internal"                     # Bug in implementation

    # Special
    REFUSED = "refused"                       # Consent/ethical refusal
```

### 8.2 Error Structure

```python
@dataclass(frozen=True)
class AgentError:
    """
    Rich error with recovery hints.

    Sympathetic: explains why, suggests what to do.
    """

    category: ErrorCategory
    code: str                          # "E1001"
    message: str                       # Human-readable

    # Recovery
    retry_after: timedelta | None      # When to retry
    fallback_verb: str | None          # Alternative verb
    suggested_action: str | None       # What user should do

    # Context
    verb: str
    trace_id: str
    details: dict[str, Any]            # Structured details

    # Provenance
    source: str                        # Which component failed
    cause: AgentError | None           # Underlying error

# Example
AgentError(
    category=ErrorCategory.QUOTA_EXCEEDED,
    code="E2001",
    message="Token quota exceeded for this billing period",
    retry_after=timedelta(hours=24),
    fallback_verb="soul.memory.recall_cached",
    suggested_action="Upgrade plan or wait for quota reset",
    verb="soul.memory.recall",
    trace_id="abc123",
    details={"quota_used": 10000, "quota_limit": 10000},
    source="billing.quota_gate",
    cause=None,
)
```

### 8.3 Refusals (Not Errors)

Consent-based refusals are distinct from errors:

```python
@dataclass(frozen=True)
class Refusal:
    """
    Explicit refusal to perform an action.

    Not an error: the system worked correctly by refusing.
    """

    verb: str
    reason: str                        # Why refused
    consent_required: str | None       # What consent would help
    override_cost: float | None        # Cost to force (Punchdrunk)
    appeal_to: str | None              # Where to appeal
```

---

## Part IX: State & Persistence

### 9.1 Event Sourcing

State is derived from events, following [CQRS principles](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs):

```python
@dataclass(frozen=True)
class Event:
    """
    Immutable fact that something happened.

    Events are the source of truth. State is projection.
    """

    id: CID                           # Content-addressed
    verb: str                         # What verb produced this
    timestamp: datetime
    tenant_id: str

    # Payload
    event_type: str                   # "session_started"
    data: dict[str, Any]              # Event-specific data

    # Provenance
    trace_id: str
    caused_by: CID | None             # Parent event

class EventStore(Protocol):
    """Append-only event log."""

    async def append(self, event: Event) -> CID: ...
    async def read(self, after: CID | None, limit: int) -> list[Event]: ...
    async def subscribe(self, filter: EventFilter) -> AsyncIterator[Event]: ...
```

### 9.2 Projections (Read Models)

```python
class Projection(Protocol):
    """
    Read model derived from events.

    Optimized for queries. Eventually consistent with event store.
    """

    async def apply(self, event: Event) -> None: ...
    async def query(self, query: Query) -> QueryResult: ...

# Example: Session count projection
class SessionCountProjection:
    counts: dict[str, int] = {}  # tenant_id → count

    async def apply(self, event: Event):
        if event.event_type == "session_started":
            self.counts[event.tenant_id] = self.counts.get(event.tenant_id, 0) + 1
        elif event.event_type == "session_ended":
            self.counts[event.tenant_id] = max(0, self.counts.get(event.tenant_id, 0) - 1)

    async def query(self, query: Query):
        return self.counts.get(query.tenant_id, 0)
```

### 9.3 Local-First Sync

Following [local-first principles](https://www.inkandswitch.com/essay/local-first/):

```python
class LocalFirstStore:
    """
    Device is primary. Cloud is backup/sync.

    Uses CRDTs for conflict-free merge.
    """

    local: EventStore       # SQLite/IndexedDB
    remote: EventStore      # Cloud
    merge: CRDTMerge        # Conflict resolution

    async def write(self, event: Event):
        # Write locally first (always succeeds)
        await self.local.append(event)

        # Queue for sync (best effort)
        await self.sync_queue.enqueue(event)

    async def sync(self):
        # Merge local and remote using CRDT
        local_events = await self.local.read(after=self.last_sync)
        remote_events = await self.remote.read(after=self.last_sync)

        merged = self.merge(local_events, remote_events)

        # Apply merged events to both stores
        for event in merged:
            await self.local.append(event)
            await self.remote.append(event)
```

---

## Part X: Versioning & Evolution

### 10.1 Era-Based Versioning

Following [API versioning best practices](https://developers.redhat.com/articles/2024/03/25/how-navigate-api-evolution-versioning):

```yaml
# Verb versions are eras, not semver
versions:
  - era: 1
    status: stable
    deprecated: null
    sunset: null

  - era: 2
    status: stable
    deprecated: "2025-06-01"
    sunset: "2025-12-01"
    migration: "See docs/migration/v1-to-v2.md"
```

### 10.2 Schema Evolution

```yaml
# Additive changes (non-breaking)
allowed:
  - Add optional field
  - Add new enum variant (if clients are tolerant)
  - Add new verb
  - Expand union type

# Breaking changes (new era)
breaking:
  - Remove field
  - Change field type
  - Rename field
  - Change verb semantics
  - Remove verb
  - Narrow union type
```

### 10.3 Deprecation Protocol

```python
# Deprecation warning in envelope
{
    "warning": {
        "type": "deprecation",
        "verb": "soul.memory.recall@1",
        "message": "v1 deprecated, migrate to v2",
        "deprecated_at": "2025-06-01",
        "sunset_at": "2025-12-01",
        "migration_guide": "https://docs/migration/v1-to-v2"
    }
}
```

---

## Part XI: Runtime Architecture

### 11.1 The Invoker

```python
class Invoker:
    """
    Central runtime for AGENTESE invocations.

    Responsibilities:
    1. Validate envelope and input
    2. Check capabilities
    3. Execute effects
    4. Route to handler
    5. Project output
    6. Emit telemetry
    """

    # Components
    registry: VerbRegistry
    capability_checker: CapabilityChecker
    effect_handlers: dict[Effect, EffectHandler]
    router: Router
    projector: Projector
    telemetry: TelemetryExporter

    async def invoke(
        self,
        verb: str,
        input: Any,
        envelope: Envelope,
        surface: str = "cli",
    ) -> AsyncIterator[Result]:
        """
        Execute a verb invocation.

        Returns an async iterator for streaming results.
        """

        with self.telemetry.span(verb, envelope) as span:
            try:
                # 1. Validate
                spec = self.registry.get(verb)
                validated_input = spec.validate_input(input)

                # 2. Check capabilities
                await self.capability_checker.check(
                    envelope.capability,
                    spec.capabilities,
                    spec.effects,
                )

                # 3. Pre-execute effects (charges, audit)
                await self._execute_pre_effects(spec.effects, envelope)

                # 4. Route to handler
                async for result in self.router.route(envelope, validated_input):
                    # 5. Project for surface
                    projected = self.projector.project_output(
                        verb, result, spec.projection[surface]
                    )
                    yield projected

                # 6. Post-execute effects (writes, emits)
                await self._execute_post_effects(spec.effects, envelope)

                span.set_status(Status.OK)

            except AgentError as e:
                span.set_status(Status.ERROR, str(e))
                span.record_exception(e)
                yield ErrorResult(e)
```

### 11.2 Handler Protocol

```python
class Handler(Protocol):
    """
    Implementation of a verb.

    Handlers are pure business logic. Effects handled by runtime.
    """

    async def handle(
        self,
        input: Input,
        context: HandlerContext,
    ) -> AsyncIterator[Output]: ...

@dataclass
class HandlerContext:
    """
    Context available to handler.

    No direct access to capabilities/effects—those are runtime concerns.
    """

    tenant_id: str
    user_id: str
    session_id: str
    trace_id: str

    # Read-only state access
    read: Callable[[str, Query], Awaitable[Any]]

    # Event emission (runtime handles persistence)
    emit: Callable[[str, dict], Awaitable[CID]]
```

### 11.3 Supervision (OTP-Inspired)

Following [Erlang supervision patterns](https://www.erlang.org/doc/system/design_principles.html):

```python
class SupervisionStrategy(Enum):
    ONE_FOR_ONE = "one_for_one"      # Restart only failed handler
    ONE_FOR_ALL = "one_for_all"      # Restart all on any failure
    REST_FOR_ONE = "rest_for_one"    # Restart failed + dependents

@dataclass
class SupervisorSpec:
    """
    Supervision tree specification.

    Handlers are supervised. Failures are contained.
    """

    strategy: SupervisionStrategy
    max_restarts: int              # Max restarts in period
    restart_period: timedelta
    children: list[HandlerSpec]

# Example: Town supervisor
TOWN_SUPERVISOR = SupervisorSpec(
    strategy=SupervisionStrategy.ONE_FOR_ONE,
    max_restarts=3,
    restart_period=timedelta(minutes=5),
    children=[
        HandlerSpec("town.citizen.greet", restart=True),
        HandlerSpec("town.citizen.trade", restart=True),
        HandlerSpec("town.simulation.tick", restart=False),  # Let it crash
    ]
)
```

---

## Part XII: Developer Experience

### 12.1 CLI Tools

```bash
# Invoke a verb
agentese call soul.memory.recall --query "last conversation" --json

# Validate a verb manifest
agentese lint agentese.manifest.yaml

# Generate types from manifest
agentese codegen --lang python --out src/agentese/types.py
agentese codegen --lang typescript --out src/agentese/types.ts

# Trace an invocation
agentese trace abc123 --format flamegraph

# Mock server for testing
agentese mock --manifest agentese.manifest.yaml --port 8080
```

### 12.2 IDE Integration

```python
# Type-safe invocation (generated from manifest)
from agentese.generated import verbs, types

result = await verbs.soul.memory.recall(
    input=types.RecallQuery(query="last conversation"),
    envelope=envelope,
)
# result is typed as types.MemoryCrystal | None
```

### 12.3 Testing Utilities

```python
# Mock handler for testing
@agentese.mock("soul.memory.recall")
async def mock_recall(input: RecallQuery, context: HandlerContext):
    return MemoryCrystal(
        id=CID.from_string("bafybeif..."),
        content="Mocked memory",
        embedding=[0.0] * 1536,
        salience=0.9,
    )

# Golden test generation
@agentese.golden("soul.memory.recall")
def test_recall_golden():
    return GoldenTest(
        input=RecallQuery(query="test"),
        expected_output=MemoryCrystal(...),
        expected_effects=[Effect.READS],
    )
```

---

## Part XIII: Security Model

### 13.1 Capability Flow

```
User → creates → Root Capability (full access)
         │
         ├─ delegates → Service Capability (attenuated)
         │                    │
         │                    └─ delegates → Handler Capability (minimal)
         │
         └─ delegates → Session Capability (time-bounded)
```

### 13.2 Sandbox Policies

```yaml
# Per-verb resource limits
sandboxes:
  soul.memory.recall:
    cpu_ms: 100
    memory_mb: 64
    network: false
    filesystem: read_only

  atelier.session.start:
    cpu_ms: 1000
    memory_mb: 256
    network: true
    filesystem: write_temp

  void.pataphysics.solve:
    cpu_ms: 5000
    memory_mb: 1024
    network: true       # LLM calls
    filesystem: none
```

### 13.3 Audit Trail

```python
# Every mutation is audited
@dataclass(frozen=True)
class AuditEntry:
    timestamp: datetime
    verb: str
    tenant_id: str
    user_id: str
    capability_hash: str
    effects: list[Effect]
    input_hash: str        # Hash, not content (privacy)
    output_hash: str
    trace_id: str
    decision: str          # "allowed", "denied", "forced"
    rationale: str | None  # For forced decisions
```

---

## Epilogue: The 50-Line API

If AGENTESE v2 succeeds, the public surface is this:

```python
# Define a verb
@agentese.verb(
    "soul.memory.recall",
    input=RecallQuery,
    output=MemoryCrystal | None,
    effects=[Effect.READS("memory_crystals")],
    capabilities=["soul:read"],
)
async def recall(input: RecallQuery, ctx: HandlerContext):
    crystal = await ctx.read("memory", MemoryQuery(input.query))
    return crystal

# Invoke a verb
result = await agentese.invoke(
    "soul.memory.recall",
    RecallQuery(query="last conversation"),
    envelope=envelope,
)

# Compose verbs
pipeline = agentese.compose(
    "soul.memory.recall",
    "concept.summary.compress",
    "atelier.artifact.save",
)
result = await pipeline.run(input, envelope)

# Query the registry
verbs = agentese.query("soul.*")

# Subscribe to events
async for event in agentese.subscribe("soul.memory.*"):
    print(f"Memory event: {event}")
```

Everything else—routing, effects, projections, telemetry, capabilities—is handled by the runtime.

---

## Sources

This specification synthesizes insights from:

- [Awesome Object Capabilities](https://github.com/dckc/awesome-ocap) - OCap patterns
- [UCAN Specification](https://github.com/ucan-wg/spec) - Decentralized authorization
- [Effekt Language](https://effekt-lang.org/) - Algebraic effects
- [CQRS Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs) - Command/Query separation
- [Erlang OTP Design Principles](https://www.erlang.org/doc/system/design_principles.html) - Supervision trees
- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/concepts/semantic-conventions/) - Observability
- [Local-First Software](https://www.inkandswitch.com/essay/local-first/) - Offline resilience
- [Agent Protocol Survey](https://arxiv.org/html/2505.02279v1) - MCP/ACP interoperability
- [API Protocol Comparison](https://wundergraph.com/blog/graphql-vs-federation-vs-trpc-vs-rest-vs-grpc-vs-asyncapi-vs-webhooks) - Protocol design lessons
- [API Versioning Best Practices](https://developers.redhat.com/articles/2024/03/25/how-navigate-api-evolution-versioning) - Evolution strategies
- [IPLD Specification](https://github.com/ipld/specs) - Content-addressable data

---

*"The best protocol is the one that disappears. You don't think about HTTP when browsing. You shouldn't think about AGENTESE when using agents."*

# AGENTESE: The Verb-First Ontology

**Status:** Canonical Specification
**Date:** 2025-12-15
**Implementation:** `impl/claude/protocols/agentese/` (559 tests)

---

## Epigraph

> *"The noun is a lie. There is only the rate of change."*
>
> *"An affordance is not a property of the object alone, nor of the observer alone—it is their meeting."* — Gibson
>
> *"Simplicity requires conviction."* — Retrospective Insight
>
> *"The best protocol is the one that disappears."* — v2 Insight

---

## Part I: Design Philosophy

AGENTESE v3 synthesizes three years of lessons:

| Source | Key Insight |
|--------|-------------|
| v1 Implementation (559 tests) | Five contexts are complete; observer-dependence works |
| v1 Retrospective | Simplicity > features; WiredLogos was a mistake |
| v2 Draft | Flat verbs + envelope; effects + capabilities |
| v2 Critique | Missing: subscriptions, query bounds, migration plan |
| Evolution Critique | Missing: observer envelope, composition semantics, CLI contract |
| Philosophical Rederivation | Category theory + phenomenology ground the design |

### The Core Tensions (Resolved)

| Tension | v1 | v2 Draft | v3 Resolution |
|---------|----|----|----------------|
| Path vs Verb | `context.holon.aspect` | `namespace.resource.action` | **Hybrid**: Context from v1 + structure from v2 |
| Observer location | In method signature | In envelope | **Both**: Minimal observer in call, full in envelope |
| Composition | Underused `>>` | Compose effects | **First-class**: `>>` on strings + effect composition |
| Query/Subscribe | Missing | Mentioned but unspecified | **Fully specified** with bounds + semantics |

### The 50-Export Target

v1 had 150+ exports. v3 targets <50:

```
Core (10):        Logos, Observer, Umwelt, LogosNode, Aspect, Effect, Envelope, Event, Error, Refusal
Contexts (5):     world, self, concept, void, time
Categories (6):   PERCEPTION, MUTATION, COMPOSITION, INTROSPECTION, GENERATION, ENTROPY
Grammar (4):      query, subscribe, alias, pipe
Runtime (5):      Router, Handler, Projector, Supervisor, Store
```

---

## Part II: The Path Grammar

### 2.1 Canonical Form

```
<context>.<holon>.<aspect>
```

| Component | Purpose | Values |
|-----------|---------|--------|
| `context` | Ontological domain | `world`, `self`, `concept`, `void`, `time` |
| `holon` | Target entity (part-whole) | Any registered entity |
| `aspect` | Mode of engagement (verb) | Registered aspect for that holon |

**Examples:**
```
world.garden.manifest
self.soul.challenge
concept.nphase.compile
void.entropy.sip
time.trace.witness
```

### 2.2 Why Not Flat Verbs?

v2 proposed `namespace.resource.action`. The critique:

1. **Context is ontological, not organizational** — `world` vs `self` matters philosophically
2. **Holon captures part-whole** — Gardens contain plots; this is structure, not namespace
3. **Aspect is not action** — `manifest` is perception, not mutation; category matters

**Decision:** Keep v1's three-part structure. It's earned.

### 2.3 Extended Grammar

```bnf
# Core path (unchanged from v1)
Path := Context "." Holon "." Aspect

# Query (new)
Query := "?" PathPattern
PathPattern := Context "." HolonPattern "." AspectPattern
HolonPattern := Identifier | "*"
AspectPattern := Identifier | "*" | "?"

# Composition (simplified)
ComposedPath := Path (">>" Path)*

# Aspect pipeline (new)
Pipeline := Path ".pipe(" AspectList ")"
AspectList := Aspect ("," Aspect)*
```

### 2.4 What We Removed

From v1:
- **Inline clauses** `[phase=DEVELOP]` → Use kwargs
- **Annotations** `@span=research` → Use envelope
- **Prefix macros** → Use explicit aliases

---

## Part III: The Five Contexts (Unchanged)

The five contexts form a **complete and minimal basis** for semantic reference.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE FIVE CONTEXTS                                    │
├─────────────┬───────────────────────────────────────────────────────────────┤
│ world.*     │ The External: entities, environments, tools                   │
│ self.*      │ The Internal: memory, capability, state, agent boundaries     │
│ concept.*   │ The Abstract: platonics, definitions, logic                   │
│ void.*      │ The Accursed Share: entropy, noise, serendipity, gratitude    │
│ time.*      │ The Temporal: history, forecast, schedule, traces             │
└─────────────┴───────────────────────────────────────────────────────────────┘
```

### 3.1 Completeness Argument

Any semantic claim falls into exactly one context:

1. **Existence claims** ("There is an X") → `world.*`
2. **Self-reference claims** ("I am/have/can X") → `self.*`
3. **Abstract claims** ("X means Y") → `concept.*`
4. **Surplus/entropy claims** ("Give me randomness") → `void.*`
5. **Temporal claims** ("X happened/will happen") → `time.*`

### 3.2 Minimality Argument

Removing any context creates gaps. Adding a sixth creates overlap:
- `space.*` subsumes under `world.*` (locations are world entities)
- `other.*` subsumes under `world.*` (other agents are world entities)
- `relation.*` subsumes under `concept.*` (relations are abstractions)

**Decision:** Five contexts. Final.

---

## Part IV: Observer-Dependent Affordances

### 4.1 The Core Insight

The same path yields different affordances depending on who observes:

```python
# Architect sees blueprints
await logos("world.house.manifest", architect_observer)

# Poet sees metaphor
await logos("world.house.manifest", poet_observer)

# Economist sees appraisal
await logos("world.house.manifest", economist_observer)
```

This is not feature flagging. It's the claim that **what exists depends on who's looking**.

### 4.2 Observer Types (Simplified)

v1 required full `Umwelt` for every call. v3 allows gradations:

```python
# Minimal observer (new)
@dataclass
class Observer:
    """Lightweight observer for simple invocations."""
    archetype: str = "guest"
    capabilities: frozenset[str] = frozenset()

# Full observer (when needed)
@dataclass
class Umwelt(Observer):
    """Embodied observer with full context."""
    tenant_id: str
    user_id: str
    session_id: str
    intent: Intent | None = None
    history: list[Trace] = field(default_factory=list)
```

### 4.3 Anonymous Invocation

For paths that don't require observer context:

```python
# These are equivalent
await logos("world.public.manifest")
await logos("world.public.manifest", Observer.guest())
```

**Key insight from critique:** The "no view from nowhere" principle is about *affordances*, not authentication. A guest is still an observer.

---

## Part V: The Envelope (From v2, Enhanced)

### 5.1 Envelope Structure

Every invocation is wrapped in an envelope:

```python
@dataclass(frozen=True)
class Envelope:
    """Immutable invocation context."""

    # Identity
    verb: str                      # "context.holon.aspect"

    # Tenancy
    tenant_id: str
    user_id: str
    session_id: str

    # Tracing (OTEL-compatible)
    trace_id: str
    span_id: str
    parent_span_id: str | None

    # Authorization
    capability: Capability         # UCAN-style token

    # Timing
    timestamp: datetime
    deadline: datetime | None      # Request timeout

    # Routing
    target: str | None             # "town://citizen/alpha"
    fallback_policy: FallbackPolicy

    # Provenance (from critique)
    provenance: Provenance | None  # NL→AGENTESE translation source
```

### 5.2 Minimal Observer vs Full Envelope

| Context | Use Observer | Use Envelope |
|---------|--------------|--------------|
| Simple CLI call | `Observer(archetype="dev")` | Auto-generated |
| API call | Extracted from token | Required |
| Internal call | Inherited | Inherited |
| Test | `Observer.test()` | `Envelope.test()` |

### 5.3 Capability Tokens (From v2)

Authorization uses object-capability tokens:

```python
@dataclass(frozen=True)
class Capability:
    """
    Authority by possession, not identity.
    Delegable, revocable, auditable.
    """

    issuer: DID
    audience: DID

    # What's allowed
    scopes: frozenset[str]         # {"soul:read", "atelier:write"}
    resources: frozenset[str]      # {"memory/*", "session/123"}

    # Constraints
    not_before: datetime
    expires_at: datetime

    # Provenance
    proof: str                     # Signature chain
```

**From critique:** Capabilities must bind to declared effects. If a verb declares `effects: [writes: session]`, the capability must include `session:write` scope.

---

## Part VI: Declared Effects

### 6.1 Effect Types

Every verb declares its side-effects:

```python
class Effect(Enum):
    # Read effects (safe, cacheable)
    READS = "reads"

    # Write effects (requires capability)
    WRITES = "writes"
    DELETES = "deletes"

    # Economic effects
    CHARGES = "charges"
    EARNS = "earns"

    # External effects
    CALLS = "calls"           # LLM, tools, external APIs
    EMITS = "emits"           # Events

    # Consent effects
    FORCES = "forces"         # Requires user consent
    AUDITS = "audits"         # Logs decision rationale
```

### 6.2 Effect Declaration

```python
@logos.node("self.memory")
class MemoryNode:
    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("memory_crystals")],
    )
    async def recall(self, observer: Observer, query: str) -> Crystal | None:
        ...

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[
            Effect.WRITES("memory_crystals"),
            Effect.CHARGES("tokens"),
        ],
    )
    async def engram(self, observer: Observer, content: str) -> Crystal:
        ...
```

### 6.3 Effect Composition (From Critique)

When composing `a >> b >> c`:

```python
def compose_effects(*paths: str) -> ComposedEffects:
    """
    Effects are additive under composition.

    Returns:
        - reads: union of all reads
        - writes: union of all writes
        - charges: sum of all charges
        - required_capabilities: union of all scopes
    """
```

### 6.4 Effect Semantics (From Critique)

| Issue | Resolution |
|-------|------------|
| Charge-before vs charge-after | **Pre-charge with refund on failure** |
| Idempotency | Mark with `@idempotent` decorator |
| Rollback | Effects declare `rollback: strategy` |
| Sandbox | Per-verb resource limits in manifest |

---

## Part VII: Aspect Categories (Enforced)

### 7.1 The Six Categories

```python
class AspectCategory(Enum):
    PERCEPTION = "perception"      # manifest, witness, sense
    MUTATION = "mutation"          # transform, renovate, evolve
    COMPOSITION = "composition"    # compose, merge, split
    INTROSPECTION = "introspection"  # affordances, constraints
    GENERATION = "generation"      # define, spawn, fork
    ENTROPY = "entropy"            # sip, pour, tithe
```

### 7.2 Runtime Enforcement

Categories aren't documentation—they're **constraints**:

```python
@aspect(category=AspectCategory.PERCEPTION)
async def manifest(self, observer):
    # PERCEPTION aspects cannot mutate state
    # This is enforced at runtime
    ...

@aspect(category=AspectCategory.MUTATION)
async def transform(self, observer, **kwargs):
    # MUTATION aspects require elevated capability
    # This is enforced at invocation
    ...
```

### 7.3 Category Rules

| Category | Can Mutate | Requires Elevation | Auto-Curate |
|----------|------------|-------------------|-------------|
| PERCEPTION | No | No | No |
| MUTATION | Yes | Yes | No |
| COMPOSITION | No | No | No |
| INTROSPECTION | No | No | No |
| GENERATION | Yes | Yes | Optional |
| ENTROPY | No | No | No |

---

## Part VIII: Query Syntax (New)

### 8.1 The Problem

AGENTESE paths are invocations. But sometimes you want to ask "what exists?" without triggering side effects.

### 8.2 Query Grammar

```python
# Query all world.* nodes
paths = logos.query("?world.*")

# Query all manifestable paths
paths = logos.query("?*.*.manifest")

# Query affordances for a specific node
affordances = logos.query("?self.memory.?")
# → ["manifest", "engram", "recall", "forget"]
```

### 8.3 Query Constraints (From Critique)

| Constraint | Default | Purpose |
|------------|---------|---------|
| `limit` | 100 | Prevent unbounded results |
| `offset` | 0 | Pagination |
| `tenant_filter` | Current tenant | Multi-tenant isolation |
| `capability_check` | Enabled | Only return accessible paths |
| `cost_estimate` | Disabled | Dry-run for expensive queries |

### 8.4 Implementation

```python
def query(self, pattern: str, **constraints) -> QueryResult:
    """
    Query the registry without invocation.

    Constraints:
        limit: int = 100
        offset: int = 0
        tenant_id: str | None = current
        dry_run: bool = False
    """
    if not pattern.startswith("?"):
        raise QuerySyntaxError("Queries must start with '?'")

    # Apply bounds
    constraints.setdefault("limit", 100)
    if constraints["limit"] > 1000:
        raise QueryBoundError("Max limit is 1000. Use pagination.")

    matches = self.registry.match(pattern[1:], **constraints)
    return QueryResult(pattern, matches)
```

---

## Part IX: Subscriptions (New)

### 9.1 The Problem

AGENTESE invocations are one-shot. Reactive patterns need continuous observation.

### 9.2 Subscription Grammar

```python
# Subscribe to all memory changes
async for event in logos.subscribe("self.memory.*"):
    print(f"Memory changed: {event.path}")

# Subscribe with aspect filter
async for event in logos.subscribe("world.town.*", aspect="flux"):
    ...

# Context manager for auto-unsubscribe
async with logos.subscription("self.forest.*") as sub:
    async for event in sub:
        if event.data.progress == 100:
            break
```

### 9.3 Event Model

```python
@dataclass
class AgentesEvent:
    path: str               # Which path emitted
    aspect: str             # Which aspect was invoked
    timestamp: datetime
    observer_archetype: str
    data: Any               # The result/payload
    event_type: EventType   # INVOKED, CHANGED, ERROR

class EventType(Enum):
    INVOKED = "invoked"     # Path was invoked
    CHANGED = "changed"     # State changed
    ERROR = "error"         # Error occurred
    REFUSED = "refused"     # Consent refusal
```

### 9.4 Subscription Semantics (From Critique)

| Semantic | Default | Options |
|----------|---------|---------|
| Delivery | At-most-once | At-least-once (with ack) |
| Ordering | Per-path FIFO | Global clock |
| Replay | None | From timestamp, from offset |
| Buffer | 1000 events | Configurable, backpressure on full |
| Heartbeat | 30s | Configurable |

### 9.5 Observability (From Critique)

```python
# Subscription metrics
agentese_subscription_active{pattern, tenant}
agentese_subscription_events_delivered{pattern, event_type}
agentese_subscription_events_dropped{pattern, reason}
agentese_subscription_lag_seconds{pattern}
```

---

## Part X: Path Aliases

### 10.1 Power User Shortcuts

```python
# Define aliases
logos.alias("me", "self.soul")
logos.alias("chaos", "void.entropy")
logos.alias("forest", "self.forest")

# Use aliases
await logos("me.challenge", observer)      # → self.soul.challenge
await logos("chaos.sip", observer)         # → void.entropy.sip
```

### 10.2 Alias Rules

1. **Prefix expansion only** — Alias must be first segment
2. **No recursion** — Aliases don't expand within aliases
3. **User-definable** — Stored in `.kgents/aliases.yaml`
4. **Shadowing forbidden** — Can't alias to context names

### 10.3 Persistence

```yaml
# .kgents/aliases.yaml
aliases:
  me: self.soul
  chaos: void.entropy
  forest: self.forest
  brain: self.memory
```

---

## Part XI: Composition (First-Class)

### 11.1 String-Based Composition

v1's composition was underused because it required `logos.lift()`. v3 makes it work on strings:

```python
# v3: String-based composition
result = await (path("world.doc.manifest") >> "concept.summary.refine" >> "self.memory.engram").run(observer, logos)

# Or with context manager
async with logos.compose(observer) as c:
    result = await c("world.doc.manifest" >> "concept.summary.refine")
```

### 11.2 Composition Semantics (From Critique)

| Semantic | Behavior |
|----------|----------|
| Error propagation | Stop on first error, return error context |
| Refusal propagation | Stop on refusal, return refusal reason |
| Cancellation | Cancel downstream on upstream failure |
| Partial results | Configurable: fail-fast vs collect |
| Billing scope | Sum of all stage charges |
| Trace correlation | Parent span links all stages |

### 11.3 Aspect Pipelines

For multiple aspects on the **same node**:

```python
# Same node, multiple aspects
result = await logos.resolve("world.document").pipe(
    "load",       # First: load from storage
    "parse",      # Second: parse content
    "summarize",  # Third: generate summary
    observer=observer,
)
```

---

## Part XII: CLI Unification

### 12.1 CLI as AGENTESE REPL

```bash
# Direct AGENTESE paths
kg self.forest.manifest
kg world.town.citizens
kg void.entropy.sip

# Shortcuts
kg /forest     # → self.forest.manifest
kg /soul       # → self.soul.dialogue
kg /surprise   # → void.entropy.sip

# Legacy commands (backward compatible)
kg forest status   # → self.forest.manifest
kg soul challenge  # → self.soul.challenge
```

### 12.2 CLI Grammar (From Critique)

```
kg <path|shortcut> [--kwargs]
kg <path> >> <path>           # Piping = composition
kg ?<pattern>                 # Query
kg subscribe <pattern>        # Subscription
kg alias <name> <target>      # Alias management
```

### 12.3 CLI Flags

```bash
kg self.forest.manifest --json        # JSON output
kg self.forest.manifest --trace       # Show trace ID
kg self.forest.manifest --dry-run     # Don't execute, show effects
kg self.forest.manifest --offline     # Local-first mode
```

---

## Part XIII: The Logos API (Unified)

### 13.1 Single Class (From Retrospective)

No `Logos` + `WiredLogos`. Just `Logos`:

```python
@dataclass
class Logos:
    """
    The AGENTESE resolver. One class, optional integrations.
    """

    # Required
    registry: NodeRegistry

    # Optional integrations
    validator: PathValidator | None = None
    tracker: UsageTracker | None = None
    telemetry: TelemetryExporter | None = None
    aliases: AliasRegistry | None = None
    subscriptions: SubscriptionManager | None = None

    # Make Logos callable
    async def __call__(self, path: str, observer: Observer | None = None, **kwargs) -> Any:
        return await self.invoke(path, observer, **kwargs)

    async def invoke(self, path: str, observer: Observer | None = None, **kwargs) -> Any:
        """Invoke a path with the given observer."""
        observer = observer or Observer.guest()
        expanded = self._expand_aliases(path)

        with self._trace(expanded) as span:
            result = await self._resolve_and_invoke(expanded, observer, **kwargs)
            self._track(expanded, success=True)
            return result

    def query(self, pattern: str, **constraints) -> QueryResult:
        """Query the registry without invocation."""
        ...

    def subscribe(self, pattern: str, **options) -> AsyncIterator[AgentesEvent]:
        """Subscribe to path events."""
        ...

    def alias(self, name: str, target: str) -> None:
        """Register a path alias."""
        ...

    def resolve(self, path: str) -> LogosNode:
        """Resolve a path to its node without invoking."""
        ...

    def compose(self, observer: Observer) -> CompositionContext:
        """Create a composition context."""
        ...
```

### 13.2 Node Protocol (Simplified)

One protocol, not four classes:

```python
class LogosNode(Protocol):
    """The only node protocol."""

    handle: str

    def affordances(self, observer: Observer) -> list[str]:
        """What can this observer do with this node?"""
        ...

    async def invoke(self, aspect: str, observer: Observer, **kwargs) -> Any:
        """Invoke an aspect with the given observer."""
        ...
```

### 13.3 Registration API

```python
@logos.node("world.garden")
class GardenNode:
    @aspect(AspectCategory.PERCEPTION)
    async def manifest(self, observer: Observer) -> GardenManifest:
        ...

    @aspect(AspectCategory.MUTATION, effects=[Effect.WRITES("garden")])
    async def plant(self, observer: Observer, seed: str) -> None:
        ...
```

### 13.4 Node Auto-Registration (Discovery)

**Key Insight:** The `@node` decorator runs at **import time**. Nodes must be imported for discovery.

```
                    Import Time                    Runtime
                    ───────────                    ───────
                         │
Module with @node ───────┤
        │                │
        ▼                │
@node decorator ─────────┼───→ NodeRegistry
                         │            │
_import_node_modules() ──┘            │
        │                             ▼
        ▼                      /agentese/discover
gateway.mount_on()                    │
                                      ▼
                              NavigationTree (UI)
```

**The Problem (Disconnected Systems):**
```
crown_jewels.py (PATHS dicts) ────→ Documentation only (NOT discoverable)
@node decorator ──→ NodeRegistry ──→ /discover ──→ NavigationTree
```

**The Solution:**
1. Add `@node("path")` decorator to node classes
2. Import modules in gateway's `_import_node_modules()`
3. Add route mappings to frontend NavigationTree

```python
# gateway.py - Ensures all nodes are imported before discovery
def _import_node_modules() -> None:
    """Import all AGENTESE node modules to trigger @node registration."""
    try:
        from . import contexts
        from .contexts import world_emergence
        from .contexts import world_gestalt_live
        from .contexts import world_park
        logger.debug("AGENTESE node modules imported for registration")
    except ImportError as e:
        logger.warning(f"Could not import some node modules: {e}")

def mount_on(self, app: "FastAPI") -> None:
    # Import node modules to populate registry
    _import_node_modules()
    # ... rest of mount logic
```

**Verification:**
```python
from protocols.agentese.registry import get_registry
registry = get_registry()
print(registry.list_paths())  # Should include your new path
```

**See:** `docs/skills/agentese-node-registration.md` for complete pattern.

---

## Part XIV: Error Model (Enriched)

### 14.1 Error Categories

```python
class ErrorCategory(Enum):
    # Client errors (don't retry)
    INVALID_INPUT = "invalid_input"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    PRECONDITION_FAILED = "precondition"

    # Resource errors (maybe retry)
    QUOTA_EXCEEDED = "quota_exceeded"
    TIMEOUT = "timeout"

    # Server errors (retry with backoff)
    UNAVAILABLE = "unavailable"
    INTERNAL = "internal"
```

### 14.2 Error Structure

```python
@dataclass(frozen=True)
class AgentError:
    """Sympathetic error with recovery hints."""

    category: ErrorCategory
    code: str
    message: str

    # Recovery
    retry_after: timedelta | None
    fallback_verb: str | None
    suggested_action: str | None

    # Context
    path: str
    trace_id: str
    details: dict[str, Any]
```

### 14.3 Refusals (Not Errors)

```python
@dataclass(frozen=True)
class Refusal:
    """Explicit refusal to perform an action."""

    path: str
    reason: str
    consent_required: str | None
    override_cost: float | None
    appeal_to: str | None
```

### 14.4 HTTP Mapping (From Critique)

| Category | HTTP | WebSocket | MCP |
|----------|------|-----------|-----|
| INVALID_INPUT | 400 | error frame | InvalidParams |
| UNAUTHORIZED | 401 | close | - |
| FORBIDDEN | 403 | error | - |
| NOT_FOUND | 404 | error | MethodNotFound |
| QUOTA_EXCEEDED | 429 | error | - |
| TIMEOUT | 504 | timeout | - |
| UNAVAILABLE | 503 | retry | - |
| REFUSED | 451 | refusal | - |

---

## Part XV: Observability

### 15.1 OTEL Spans

```python
span.set_attribute("agentese.path", "self.memory.recall")
span.set_attribute("agentese.context", "self")
span.set_attribute("agentese.aspect", "recall")
span.set_attribute("agentese.aspect_category", "perception")
span.set_attribute("agentese.observer.archetype", "developer")
span.set_attribute("agentese.tenant_id", envelope.tenant_id)
span.set_attribute("agentese.effects", "reads:memory_crystals")
span.set_attribute("agentese.cache.hit", False)
```

### 15.2 Metrics

```python
agentese_invocations_total{path, context, aspect, category, status}
agentese_invocation_duration_seconds{path, quantile}
agentese_effect_operations_total{effect, resource}
agentese_subscription_active{pattern}
agentese_query_fanout{pattern}
```

### 15.3 Cardinality Control (From Critique)

| Field | Strategy |
|-------|----------|
| `tenant_id` | Hash to bounded bucket |
| `user_id` | Never in metrics, only logs (redacted) |
| `path` | Top-N paths, rest as "other" |
| `trace_id` | Logs only, never metrics |

---

## Part XVI: Testing

### 16.1 Conformance Suite (From Critique)

| Test Category | Coverage |
|---------------|----------|
| Path parsing | All grammar forms |
| Category enforcement | All 6 categories |
| Effect composition | Identity, associativity |
| Query bounds | Limit, offset, tenant filter |
| Subscription delivery | Ordering, backpressure |
| Error mapping | All categories → HTTP/WS/MCP |

### 16.2 Property Tests

```python
# Composition is associative
@given(paths=st.lists(st.text(), min_size=2, max_size=5))
def test_composition_associativity(paths):
    left = (paths[0] >> paths[1]) >> paths[2]
    right = paths[0] >> (paths[1] >> paths[2])
    assert left.paths == right.paths

# Effects compose additively
@given(effects_a=effect_set(), effects_b=effect_set())
def test_effect_composition(effects_a, effects_b):
    composed = compose_effects(effects_a, effects_b)
    assert effects_a.reads <= composed.reads
    assert effects_b.reads <= composed.reads
```

### 16.3 Runtime Matrix (From Critique)

| Runtime | Core | Subscriptions | Query | Priority |
|---------|------|---------------|-------|----------|
| CPython 3.11+ | Required | Required | Required | P0 |
| PyPy | Smoke | Optional | Smoke | P2 |
| WASM (Pyodide) | Smoke | N/A | Smoke | P3 |

---

## Part XVII: Migration from v1

### 17.1 Compatibility Layer

```python
# Old API continues to work during migration
from protocols.agentese import logos

# v1 style (deprecated but functional)
result = await logos.invoke("world.house.manifest", umwelt)

# v3 style (preferred)
result = await logos("world.house.manifest", observer)
```

### 17.2 Migration Phases

| Phase | Duration | Action |
|-------|----------|--------|
| 1 | Week 1-2 | Add v3 API alongside v1 |
| 2 | Week 3-4 | Migrate internal code to v3 |
| 3 | Week 5-6 | Add deprecation warnings to v1 |
| 4 | Week 7-8 | Remove v1 code |

### 17.3 Migration Telemetry (From Critique)

```python
# Track migration progress
agentese_api_calls_total{version=["v1", "v3"]}
agentese_v1_deprecated_calls{path}
```

---

## Part XVIII: Federation (Future)

### 18.1 Cross-Instance Routing

```python
# Local path
"self.memory.recall"

# Remote path (future)
"kg://tenant@host/self.memory.recall"
```

### 18.2 Federation Strawman (From Critique)

| Concern | Approach |
|---------|----------|
| Path routing | URI prefix: `kg://host/path` |
| Trust | Signed envelopes (DID) |
| Capability projection | Attenuate on boundary crossing |
| Refusal model | Propagate with source |

**Status:** Exploratory. Not blocking v3.

---

## Part XIX: Success Criteria

### 19.1 Quantitative

| Metric | v1 | v3 Target |
|--------|----|----|
| Public exports | 150+ | <50 |
| Logos classes | 2 | 1 |
| Node types | 4 | 1 |
| Test count | 559 | 600+ |
| Query latency | N/A | <10ms |
| Subscription delivery | N/A | <10ms |

### 19.2 Qualitative

- [ ] `kg self.forest.manifest` works
- [ ] `kg /forest` works (shortcut)
- [ ] `kg forest` works (legacy)
- [ ] Composition with `>>` feels natural
- [ ] New contributor understands API in 10 minutes
- [ ] The Gardener works entirely through AGENTESE

---

## Appendix A: Standard Paths

```
world.*              # External entities
  world.{entity}.manifest       # Perceive entity
  world.{entity}.witness        # View history
  world.{entity}.affordances    # List available aspects
  world.{entity}.define         # Create new entity

self.*               # Agent-internal
  self.memory.manifest          # View current memory
  self.memory.engram            # Store memory
  self.memory.recall            # Retrieve memory
  self.soul.dialogue            # Conversational interface
  self.soul.challenge           # Dialectical challenge
  self.forest.manifest          # Project forest

concept.*            # Abstract space
  concept.{name}.manifest       # Perceive concept
  concept.{name}.refine         # Challenge/evolve
  concept.nphase.compile        # Compile N-Phase project

void.*               # Accursed Share
  void.entropy.sip              # Draw randomness
  void.entropy.pour             # Return randomness
  void.gratitude.tithe          # Pay for order
  void.pataphysics.solve        # Imaginary solutions

time.*               # Temporal operations
  time.trace.witness            # View temporal trace
  time.past.project             # View past state
  time.future.forecast          # Predict future
```

---

## Appendix B: Files to Modify

| File | Action |
|------|--------|
| `logos.py` | Add `__call__`, merge wiring, add query/subscribe/alias |
| `wiring.py` | Delete |
| `node.py` | Consolidate to single protocol |
| `parser.py` | Remove clause/annotation parsing |
| `jit.py` | Archive |
| `affordances.py` | Add runtime enforcement |
| `subscription.py` | Create |
| `query.py` | Create |
| `aliases.py` | Create |
| `__init__.py` | Reduce to <50 exports |

---

## Appendix C: Decision Log

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| Keep 3-part paths | Flat verbs (v2) | Context is ontological, not organizational |
| Observer gradations | Full Umwelt always | Allow lightweight calls |
| Bounded queries | Unbounded wildcards | Prevent footguns |
| At-most-once subscriptions | At-least-once | Simpler default, upgrade optional |
| Pre-charge economics | Post-charge | Safer for failure cases |
| Categories as constraints | Categories as docs | Enforce at runtime |
| Single Logos class | Logos + WiredLogos | No wrapper classes |

---

*"The noun is a lie. There is only the rate of change. But the rate of change toward simplicity is the most profound change of all."*

*Last updated: 2025-12-15*

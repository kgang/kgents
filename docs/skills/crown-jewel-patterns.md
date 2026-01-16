# Skill: Crown Jewel Patterns

> *"Container owns Workflow: Container persists, Workflows come and go."*
> *"Signal Aggregation: multiple signals → confidence + reasons (transparent, composable)."*

**Purpose**: 14 battle-tested patterns for implementing kgents services (Crown Jewels).

**Prerequisites**: [metaphysical-fullstack.md](metaphysical-fullstack.md), [agentese-node-registration.md](agentese-node-registration.md)

---

## When to Use This Skill

- Building a new Crown Jewel service
- Implementing persistence patterns
- Wiring event-driven features
- Debugging service behavior

---

## What is a Crown Jewel?

A **Crown Jewel** is a core kgents service—the "gems" of the system. Each handles a specific domain:

| Crown Jewel | Purpose | Status |
|-------------|---------|--------|
| **Brain** | Spatial cathedral of memory | 100% |
| **Witness** | Marks, crystals, grants, playbooks | 98% |
| **Zero Seed** | Galois loss, layer assignment | 95% |
| **Constitutional** | 7-principle scoring | 95% |
| **Derivation** | Causal lineage tracking | MVP |
| **Town** | Agent simulation | 70% |

Crown Jewels follow consistent patterns for reliability and composability.

---

## The 14 Patterns

### Pattern 1: Container Owns Workflow

**Problem**: Long-running workflows need somewhere to live.

**Solution**: Container persists; workflows come and go.

```python
class BrainContainer:
    """Container persists across sessions."""

    def __init__(self):
        self.crystals: dict[str, Crystal] = {}
        self.active_workflow: Workflow | None = None

    def start_workflow(self, name: str) -> Workflow:
        """Workflow lives within container."""
        workflow = Workflow(name=name, container=self)
        self.active_workflow = workflow
        return workflow

    async def on_workflow_complete(self, workflow: Workflow):
        """Container outlives workflow."""
        self.active_workflow = None
        await self._persist_changes(workflow.changes)
```

**Gotcha**: Workflow should NOT hold references to the container's internals—pass data explicitly.

---

### Pattern 2: Signal Aggregation

**Problem**: Multiple sources produce confidence scores that need combining.

**Solution**: Aggregate with transparency—confidence + reasons.

```python
@dataclass(frozen=True)
class Signal:
    value: float  # [0, 1]
    reason: str
    source: str

def aggregate_signals(signals: list[Signal]) -> AggregatedSignal:
    """Combine signals, preserving reasons."""
    if not signals:
        return AggregatedSignal(confidence=0.5, reasons=[])

    # Weighted average (equal weights here)
    total = sum(s.value for s in signals) / len(signals)

    return AggregatedSignal(
        confidence=total,
        reasons=[f"[{s.source}] {s.reason}" for s in signals],
    )
```

**Key**: Never lose the reasons—they're audit trails.

---

### Pattern 3: Dual-Channel Output

**Problem**: Humans and agents need different output formats.

**Solution**: Emit both human-readable and semantic-parseable output.

```python
def emit(human: str, semantic: dict) -> Output:
    """Dual channel: human prose + machine JSON."""
    return Output(
        human=human,
        semantic=semantic,
        timestamp=datetime.utcnow(),
    )

# Usage
result = emit(
    human="Found 3 crystals matching 'auth': crystal-1, crystal-2, crystal-3",
    semantic={
        "matches": ["crystal-1", "crystal-2", "crystal-3"],
        "query": "auth",
        "count": 3,
    },
)
```

**For CLI**: Show `result.human`
**For agents**: Parse `result.semantic`

---

### Pattern 4: Bounded Trace

**Problem**: Traces grow unboundedly, consuming memory.

**Solution**: Append + trim = trajectory without bloat.

```python
class BoundedTrace:
    """Fixed-size sliding window of events."""

    def __init__(self, max_size: int = 50):
        self.events: list[Event] = []
        self.max_size = max_size

    def append(self, event: Event):
        self.events.append(event)
        if len(self.events) > self.max_size:
            self.events = self.events[-self.max_size:]

    def trajectory(self) -> list[Event]:
        """Return recent trajectory for analysis."""
        return self.events.copy()
```

**Gotcha**: Don't trim below useful analysis threshold (usually 20-50).

---

### Pattern 5: Habitat Guarantee

**Problem**: Users see blank pages or 404s when data is missing.

**Solution**: Every path has habitat—never return nothing.

```python
async def get_crystal(crystal_id: str) -> Crystal | HabitatPlaceholder:
    """Guarantee: ∀ path p: Habitat(p) ≠ ∅"""
    crystal = await universe.get(Crystal, crystal_id)

    if crystal:
        return crystal

    # Never return None—provide habitat
    return HabitatPlaceholder(
        id=crystal_id,
        message="Crystal not found. Would you like to create it?",
        affordances=["create", "search_similar"],
    )
```

**Key**: Placeholder is still a valid response with actionable affordances.

---

### Pattern 6: Cache Key = SHA256(normalized(intent, context))

**Problem**: Caching by intent alone misses context-dependent behavior.

**Solution**: Hash both intent AND context.

```python
import hashlib
import json

def cache_key(intent: str, context: dict) -> str:
    """Deterministic, collision-resistant cache key."""
    normalized = json.dumps({
        "intent": intent.strip().lower(),
        "context": {k: v for k, v in sorted(context.items())},
    }, sort_keys=True)

    return hashlib.sha256(normalized.encode()).hexdigest()[:16]

# Usage
key = cache_key("analyze code", {"file": "main.py", "mode": "strict"})
```

**Gotcha**: Always normalize before hashing (strip, lowercase, sort keys).

---

### Pattern 7: Lazy-Load Dependencies

**Problem**: Importing heavy dependencies slows startup.

**Solution**: Defer import until first use.

```python
_classifier = None

def _get_classifier():
    """Lazy load—defers import until first use."""
    global _classifier
    if _classifier is None:
        from heavy_ml_library import Classifier
        _classifier = Classifier.load("model.pkl")
    return _classifier

async def classify(text: str) -> str:
    """Classification using lazy-loaded model."""
    classifier = _get_classifier()
    return classifier.predict(text)
```

**Key**: Module imports are fast; model loading is deferred.

---

### Pattern 8: Frozen Dataclasses for Contracts

**Problem**: Mutable contracts cause cross-layer bugs.

**Solution**: Freeze boundaries between layers.

```python
from dataclasses import dataclass

@dataclass(frozen=True)  # Immutable!
class CrystalRef:
    """Immutable reference across layer boundaries."""
    id: str
    layer: int
    crystal_type: str
    galois_loss: float

# Attempting mutation raises FrozenInstanceError
ref = CrystalRef(id="abc", layer=3, crystal_type="spec", galois_loss=0.1)
ref.layer = 4  # FrozenInstanceError!
```

**Why**: Frozen = safe to pass across async boundaries, cache, share.

---

### Pattern 9: Explicit Data Requirements

**Problem**: Code assumes data exists; crashes when it doesn't.

**Solution**: `get_or_raise()` makes requirements explicit.

```python
class Universe:
    async def get_or_raise(self, model: type[T], id: str) -> T:
        """Explicit: data MUST exist or we fail loudly."""
        result = await self.get(model, id)
        if result is None:
            raise DataNotFoundError(f"{model.__name__} '{id}' not found")
        return result

# Usage
crystal = await universe.get_or_raise(Crystal, "crystal-123")
# ^ Throws if missing—no silent None
```

**Contrast with Pattern 5**: Habitat is for user-facing; `get_or_raise` is for internal logic that requires data.

---

### Pattern 10: Reactive Invalidation

**Problem**: Cached data becomes stale when source changes.

**Solution**: Events trigger invalidation.

```python
class ProxyReactor:
    """Invalidates caches when upstream changes."""

    def __init__(self, bus: SynergyBus):
        bus.subscribe("spec.updated", self._on_spec_updated)
        bus.subscribe("spec.deleted", self._on_spec_deleted)

    async def _on_spec_updated(self, event: Event):
        """Spec changed → invalidate derived handles."""
        spec_id = event.data["spec_id"]
        await self.cache.invalidate_by_source(spec_id)

    async def _on_spec_deleted(self, event: Event):
        """Spec deleted → remove all derived handles."""
        spec_id = event.data["spec_id"]
        await self.cache.remove_by_source(spec_id)
```

**Wiring**: See [data-bus-integration.md](data-bus-integration.md).

---

### Pattern 11: Explicit Computation with TTL

**Problem**: "When was this computed? Is it fresh?"

**Solution**: `compute()` returns data + provenance + TTL.

```python
@dataclass(frozen=True)
class ComputedHandle:
    value: Any
    computed_at: datetime
    ttl_seconds: int
    source_id: str  # Provenance

    @property
    def is_fresh(self) -> bool:
        age = (datetime.utcnow() - self.computed_at).total_seconds()
        return age < self.ttl_seconds

async def compute(source_id: str, ttl: int = 300) -> ComputedHandle:
    """Explicit computation with TTL."""
    value = await _expensive_computation(source_id)
    return ComputedHandle(
        value=value,
        computed_at=datetime.utcnow(),
        ttl_seconds=ttl,
        source_id=source_id,
    )
```

---

### Pattern 12: Adapters in Service Modules

**Problem**: Where do external integrations live?

**Solution**: Adapters live in the service, not infrastructure.

```
services/brain/
├── __init__.py
├── core.py           # Domain logic
├── contracts.py      # Types and protocols
├── adapters/         # External integrations HERE
│   ├── postgres.py
│   ├── embeddings.py
│   └── llm.py
└── _tests/
```

**Why**: Service owns its boundaries. Infrastructure is shared; adapters are service-specific.

---

### Pattern 13: Constitutional Scoring

**Problem**: Evaluating actions against principles.

**Solution**: Score every action against the 7 principles.

```python
from services.constitutional import constitutional_reward, Principle

score = constitutional_reward(
    action="expand_portal",
    context={"depth": 3, "edge_type": "evidence"},
    domain="portal",
)

print(f"ETHICAL: {score[Principle.ETHICAL]}")
print(f"COMPOSABLE: {score[Principle.COMPOSABLE]}")
print(f"Weighted total: {score.weighted_total()}")
```

**The 7 Principles**:
1. TASTEFUL — Clear purpose
2. CURATED — Intentional
3. ETHICAL — Respects agency (weighted 2x)
4. JOY_INDUCING — Delightful
5. COMPOSABLE — Composes cleanly (weighted 1.5x)
6. HETERARCHICAL — Leads and follows
7. GENERATIVE — Compressive

---

### Pattern 14: Derivation Lineage

**Problem**: "Where did this come from?"

**Solution**: Trace to axioms; measure coherence.

```python
from services.derivation import DerivationService

service = DerivationService(universe, galois)
chain = await service.trace_to_axiom("function-abc123")

print(f"Grounded: {chain.is_grounded}")
print(f"Coherence: {chain.coherence():.1%}")

for ref in chain.chain:
    print(f"  L{ref.layer} {ref.crystal_type}: {ref.id}")
```

**Layer Taxonomy**:
- L1: Axiom (root)
- L2: Value (root)
- L3: Prompt
- L4: Spec
- L5: Code, Test
- L6: Reflection
- L7: Interpretation

**Grounded** = Path reaches L1 or L2.

---

## Pattern Selection Guide

| You Need | Pattern(s) |
|----------|-----------|
| Long-running workflow | #1 Container Owns Workflow |
| Combine multiple scores | #2 Signal Aggregation |
| CLI + agent output | #3 Dual-Channel Output |
| Event history | #4 Bounded Trace |
| Never blank pages | #5 Habitat Guarantee |
| Caching | #6 Cache Key, #11 Explicit TTL, #10 Reactive Invalidation |
| Slow imports | #7 Lazy-Load Dependencies |
| Type safety | #8 Frozen Dataclasses |
| Data requirements | #9 Explicit get_or_raise |
| External APIs | #12 Adapters in Service |
| Evaluate actions | #13 Constitutional Scoring |
| Track provenance | #14 Derivation Lineage |

---

## Crown Jewel Structure

Standard directory layout:

```
services/<jewel>/
├── __init__.py          # Module exports
├── core.py              # Domain logic (or split into multiple)
├── contracts.py         # Types, protocols, frozen dataclasses
├── node.py              # AGENTESE @node registration
├── adapters/            # External integrations
│   └── *.py
└── _tests/
    ├── __init__.py
    └── test_*.py
```

---

## Anti-Patterns

| Don't | Do Instead | Pattern |
|-------|------------|---------|
| Workflow owns container | Container owns workflow | #1 |
| Aggregate without reasons | Preserve all reasons | #2 |
| JSON-only output | Dual channel (human + semantic) | #3 |
| Unbounded event lists | Bounded trace with trim | #4 |
| Return None for missing | Habitat placeholder | #5 |
| Cache by intent alone | Cache by (intent, context) | #6 |
| Import at module level | Lazy load | #7 |
| Mutable contracts | Frozen dataclasses | #8 |
| Silent None returns | get_or_raise | #9 |
| Poll for changes | Reactive invalidation | #10 |
| "Trust the cache" | Explicit TTL + provenance | #11 |
| Adapters in infra/ | Adapters in service | #12 |

---

## For Agents

### JSON Output Mode

When invoked programmatically, Crown Jewels support JSON mode:

```bash
kg brain status --json
# → {"spatial_navigable": true, "crystal_count": 247, ...}

kg derivation trace function-abc --json
# → {"chain": [...], "is_grounded": true, "coherence": 0.766}
```

### Service Invocation

```python
# Via AGENTESE
result = await logos.invoke("self.brain.manifest", observer)

# Via direct import
from services.brain import BrainService
brain = BrainService()
status = await brain.status()
```

---

## Related Skills

- [metaphysical-fullstack.md](metaphysical-fullstack.md) — Architecture context
- [agentese-node-registration.md](agentese-node-registration.md) — Exposing via @node
- [data-bus-integration.md](data-bus-integration.md) — Event wiring
- [test-patterns.md](test-patterns.md) — Testing services
- [validation.md](validation.md) — Measuring service health

---

*"One truth, one store: All Crown Jewels can share ProxyHandleStore for computed data."*

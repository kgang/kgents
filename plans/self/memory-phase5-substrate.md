---
path: self/memory-phase5-substrate
status: proposed
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [agents/k-gent, self/memory]
session_notes: |
  N-Phase Cycle engagement: Full 11-phase for novel architecture.
  Decisions captured: shared substrate, lifecycle-aware ghost, auto-consolidation, categorical routing.
  Accursed Share: 7% exploration budget.
---

# Memory Phase 5: Shared Substrate Architecture

> *"Each agent has a room, but the building is shared."*

**N-Phase Cycle**: Full (PLAN → REFLECT)
**AGENTESE Context**: `self.memory.*`, `concept.allocation.*`
**Principles**: AD-001 (Universal Functor), AD-002 (Polynomial), Composability, Accursed Share

---

## PLAN: Intent & Scope

### Goal
Design and implement the shared memory substrate where agents receive allocated crystals by default, with upgrade paths to dedicated crystals for justified cases.

### Non-Goals
- Full HiveMind consensus (Phase 3 scope)
- Cross-cluster memory federation
- GUI memory browser (I-gent scope)

### Exit Criteria
- [ ] SharedSubstrate with agent allocation
- [ ] CrystalPolicy for upgrade/downgrade decisions
- [ ] Ghost cache with lifecycle metadata
- [ ] Automatic consolidation with configurable triggers
- [ ] Categorical routing via pheromone gradients
- [ ] 60+ tests passing

### Attention Budget
| Chunk | Allocation | Phase Focus |
|-------|------------|-------------|
| Substrate Core | 35% | DEVELOP → IMPLEMENT |
| Ghost Lifecycle | 20% | DEVELOP → QA |
| Auto-Consolidation | 20% | STRATEGIZE → TEST |
| Categorical Routing | 18% | CROSS-SYNERGIZE → IMPLEMENT |
| Accursed Share | 7% | Exploration, serendipity |

### Blockers
- **None** (unblocked by Phase 4 completion)

---

## RESEARCH: Terrain Mapping

### Unknowns to Resolve
1. How do other systems partition shared memory? (Vector DBs, Redis namespacing)
2. What triggers justify crystal promotion? (Access frequency? Size? Agent type?)
3. How does categorical routing differ from naive pheromone following?
4. What lifecycle metadata makes ghost cache human-maintainable?

### Files to Read
```
impl/claude/agents/m/crystal.py          # Current MemoryCrystal API
impl/claude/agents/m/stigmergy.py        # PheromoneField gradients
impl/claude/agents/d/__init__.py         # D-gent storage primitives
impl/claude/infra/ghost/cache.py         # GlassCacheManager
spec/principles.md                       # Composability principles
spec/m-gents/README.md                   # M-gent specification
```

### Research Questions for Next Phase
- What is the natural "room size" for an agent's default allocation?
- Should crystal promotion be agent-requested or system-observed?
- How do we avoid "debris trails" in ghost cache during chaos development?

---

## DEVELOP: Specification Sharpening

### Key Types

```python
@dataclass
class SharedSubstrate:
    """
    The building where all agents have rooms.

    Categorical insight: This is a slice category over Agent.
    Each allocation is a morphism Agent → MemorySpace.
    """
    global_crystal: MemoryCrystal[Any]  # Shared interference pattern
    allocations: dict[AgentId, Allocation]
    promotion_policy: CrystalPolicy

    def allocate(self, agent: AgentId, quota: MemoryQuota) -> Allocation:
        """Give agent a room in the shared building."""
        ...

    def promote(self, agent: AgentId) -> DedicatedCrystal:
        """
        Upgrade agent to own crystal.

        Category law: promote >> demote ≅ id (up to resolution loss)
        """
        ...

@dataclass
class Allocation:
    """An agent's room in the shared substrate."""
    agent_id: AgentId
    namespace: str  # Prefix for concept_ids
    quota: MemoryQuota
    created_at: datetime
    last_accessed: datetime
    access_count: int

    # Lifecycle metadata for ghost cache
    lifecycle: LifecyclePolicy

@dataclass
class LifecyclePolicy:
    """
    Human-readable lifecycle for ghost cache entries.

    Meta principle: "human readable with safeguards by default construction"
    """
    ttl: timedelta
    max_size_bytes: int
    compaction_trigger: CompactionTrigger
    human_label: str  # e.g., "k-gent working memory"

@dataclass
class CrystalPolicy:
    """
    Decides when agents get their own crystal.

    Categorical: This is a predicate in the category of allocations.
    promotion_criteria : Allocation → Bool
    """
    access_frequency_threshold: float  # Accesses per hour
    size_threshold_bytes: int
    explicit_request_allowed: bool

    def should_promote(self, allocation: Allocation) -> bool:
        ...

@dataclass
class CompactionTrigger:
    """When to run automatic consolidation."""
    on_health_degraded: bool = True
    on_schedule: timedelta | None = timedelta(hours=1)
    on_memory_pressure: float = 0.8  # 80% capacity
    custom: Callable[[Allocation], bool] | None = None  # Future: custom compactors
```

### Categorical Routing

```python
class CategoricalRouter:
    """
    Route tasks to agents via pheromone gradients.

    This is a functor: Task → Agent

    The categorical insight: instead of explicit routing tables,
    we follow the gradient in the pheromone field. This is
    adjoint to the deposit operation:

        deposit ⊣ route

    Depositing creates gradients; routing follows them.
    This adjunction ensures routes are "natural" (follow actual usage).
    """

    def __init__(self, field: PheromoneField):
        self.field = field

    async def route(self, task: Task) -> AgentId:
        """
        Follow gradient to find best agent.

        Naturality: route(f(task)) = f(route(task)) for any task morphism f
        """
        gradients = await self.field.sense(task.concept)

        # Categorical choice: take the "terminal" object
        # (strongest gradient = most relevant agent)
        if not gradients:
            return self._default_agent(task)

        return max(gradients, key=lambda g: g.total_intensity).dominant_depositor

```

---

## STRATEGIZE: Sequencing for Leverage

### Critical Path
```
1. SharedSubstrate core (blocks everything)
   ↓
2. Allocation + LifecyclePolicy (blocks ghost integration)
   ↓
3. Ghost cache lifecycle metadata (parallel with 4)
4. CrystalPolicy promotion logic (parallel with 3)
   ↓
5. CompactionTrigger + auto-consolidation
   ↓
6. CategoricalRouter (can start after 1)
```

### Parallelizable Chunks

| Chunk | Dependencies | Can Parallel With |
|-------|--------------|-------------------|
| SharedSubstrate | None | — |
| Allocation | SharedSubstrate | — |
| Ghost Lifecycle | Allocation | CrystalPolicy |
| CrystalPolicy | Allocation | Ghost Lifecycle |
| Auto-Consolidation | Ghost Lifecycle | CategoricalRouter |
| CategoricalRouter | SharedSubstrate | Ghost Lifecycle, CrystalPolicy |

---

## CROSS-SYNERGIZE: Combinatorial Lifts

### Synergies to Explore

1. **D-gent × SharedSubstrate**: UnifiedMemory backend for substrate persistence
2. **Turn-gents × Allocation**: Each turn stores in allocated namespace
3. **K-gent × CrystalPolicy**: Soul gets dedicated crystal by default (justified: identity)
4. **B-gent × MemoryQuota**: Token economics for memory allocation
5. **Operad × CompactionTrigger**: Compose compaction operations (merge crystals, prune namespaces)

### Operad Composition

```python
# CompactionOperad: operations that can be composed
CompactionOperad = Operad[Allocation, Allocation]

# Operations
prune_cold = Operation("prune_cold", arity=1)      # Remove cold patterns
merge_hot = Operation("merge_hot", arity=2)         # Combine hot patterns
compress_all = Operation("compress_all", arity=1)   # Holographic compression

# Composition: prune then compress
prune_then_compress = CompactionOperad.compose(prune_cold, compress_all)
```

---

## IMPLEMENT: Shipping Strategy

### File Plan

```
impl/claude/agents/m/substrate.py       # SharedSubstrate, Allocation
impl/claude/agents/m/policy.py          # CrystalPolicy, LifecyclePolicy
impl/claude/agents/m/compaction.py      # CompactionTrigger, auto-consolidation
impl/claude/agents/m/routing.py         # CategoricalRouter
impl/claude/infra/ghost/lifecycle.py    # Ghost cache lifecycle metadata
impl/claude/agents/m/_tests/test_substrate.py
impl/claude/agents/m/_tests/test_routing.py
```

### Implementation Order
1. `substrate.py` — Core types, SharedSubstrate.allocate()
2. `policy.py` — LifecyclePolicy, CrystalPolicy.should_promote()
3. `infra/ghost/lifecycle.py` — Lifecycle metadata in ghost cache
4. `compaction.py` — CompactionTrigger, integrate with InferenceGuidedCrystal
5. `routing.py` — CategoricalRouter with adjoint relationship

---

## QA: Quality Gates

### Checklist
- [ ] All types have docstrings with categorical insights
- [ ] LifecyclePolicy.human_label is always set
- [ ] Ghost cache entries have TTL and max_size
- [ ] No orphaned allocations (cleanup on agent removal)
- [ ] CrystalPolicy logs promotion decisions (auditability)

### Hygiene
- [ ] Mypy strict: 0 errors
- [ ] Ruff: 0 warnings
- [ ] No hardcoded magic numbers (use constants or config)

---

## TEST: Verification Strategy

### Test Categories

| Category | Count | Focus |
|----------|-------|-------|
| Unit: Substrate | 15 | allocate, promote, demote |
| Unit: Policy | 10 | should_promote, lifecycle bounds |
| Unit: Compaction | 10 | triggers, auto-consolidation |
| Unit: Routing | 10 | gradient following, adjoint property |
| Integration | 15 | Full flow: allocate → use → compact → route |

### Property Tests
```python
# Categorical laws
def test_promote_demote_roundtrip():
    """promote >> demote ≅ id (up to resolution loss)"""
    ...

def test_routing_naturality():
    """route(f(task)) = f(route(task))"""
    ...

def test_deposit_route_adjunction():
    """deposit ⊣ route: following gradients is adjoint to creating them"""
    ...
```

---

## EDUCATE: Teaching Plan

### Documentation
- `docs/memory-substrate.md` — Architecture overview
- `plans/skills/memory-allocation.md` — Skill for allocating agent memory
- Update `plans/devex/memory-dashboard.md` with Phase 5

### Examples
```python
# Quick start
substrate = SharedSubstrate()
allocation = substrate.allocate("k-gent", MemoryQuota(max_patterns=1000))

# Use the allocation
await allocation.store("python_patterns", content, embedding)

# Automatic compaction happens when triggers fire
# Or manual:
await substrate.compact(allocation)

# Routing via gradients
router = CategoricalRouter(pheromone_field)
best_agent = await router.route(task)
```

---

## MEASURE: Instrumentation

### Metrics to Track
| Metric | Type | Purpose |
|--------|------|---------|
| `memory.allocations.count` | Gauge | Total allocations |
| `memory.promotions.total` | Counter | Crystal promotions |
| `memory.compactions.duration_ms` | Histogram | Compaction performance |
| `memory.routing.gradient_strength` | Histogram | Route confidence |
| `memory.ghost.entries.age_hours` | Histogram | Cache freshness |

### OTEL Integration
```python
# Trace compaction operations
with tracer.start_as_current_span("memory.compact") as span:
    span.set_attribute("allocation.agent_id", allocation.agent_id)
    span.set_attribute("trigger", trigger.name)
    result = await compactor.run(allocation)
    span.set_attribute("patterns_removed", result.removed)
```

---

## REFLECT: Learning Seeds

### Questions for Post-Implementation
1. Did the categorical routing feel "natural" or forced?
2. Was the promotion threshold right? Too eager? Too conservative?
3. Did lifecycle metadata actually prevent ghost debris?
4. What compaction triggers fired most? Were any never used?

### Meta-Learning
- How well did the N-Phase Cycle structure this work?
- Which phases felt most valuable? Least?
- What would we do differently in the next cycle?

### Accursed Share Seeds
Exploration directions for the 7%:
- Memory "seasons" (different policies for different times of day)
- Crystal "genealogy" (track lineage through promotions)
- "Desire line" discovery from routing patterns
- Entropy-based crystal naming (poetic identifiers)

---

## Hand-off to RESEARCH

### Next Steps
1. Read files listed in RESEARCH section
2. Answer the three research questions
3. Prototype SharedSubstrate.allocate() to validate types
4. Return to this plan with findings

---

*"The substrate is the commons; the crystal is the garden."*

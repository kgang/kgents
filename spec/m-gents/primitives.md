# M-gent Primitives

**Status:** Standard
**Implementation:** `impl/claude/agents/m/` (consolidated with D-gent substrate)

## Purpose

M-gents provide the **cognitive layer** for memory operations: generative recall, consolidation during idle cycles, prospective memory (remembering the future), ethical navigation through experience, and stigmergic coordination through environmental traces. Unlike database lookups, M-gent operations are reconstructive, context-sensitive, and always return gracefully degraded results rather than failures.

## Core Insight

Memory is not storage retrieval—it is reconstruction from holographic patterns, where every query produces a composite view influenced by all stored memories.

## Type Signatures

### Core Memory Agents

```python
@dataclass
class RecollectionAgent(Agent[Concept, Recollection]):
    """
    Generative memory retrieval: reconstruction, not lookup.
    - Partial matches always return something (graceful degradation)
    - Results are composite views of resonant patterns
    - Resolution proportional to pattern match strength
    """
    memory: HolographicMemory
    reconstructor: Agent[Pattern, Recollection]


@dataclass
class ConsolidationAgent(Agent[HolographicMemory, HolographicMemory]):
    """
    Background memory processing during idle cycles (hypnagogic worker).

    Operations:
    - COMPRESS: Reduce resolution of cold memories
    - STRENGTHEN: Increase resolution of hot memories
    - INTEGRATE: Merge similar memories (chunking)
    - FORGET: Reduce interference from irrelevant patterns
    """
    temperature_threshold: float
    forget_threshold: timedelta


@dataclass
class ProspectiveAgent(Agent[Situation, list[PredictedAction]]):
    """
    Memory as prediction: find similar past situations, project likely actions.
    "Remembering the future" via pattern matching.
    """
    memory: HolographicMemory
    action_log: ActionHistory


@dataclass
class EthicalGeometryAgent(Agent[ActionProposal, EthicalPath]):
    """
    Ethics as learned geometry in action space.
    - Harmful actions expand forbidden regions
    - Beneficial actions strengthen virtuous regions
    - Boundaries are probabilistic, not binary
    """
    geometry: EthicalGeometry

    @property
    def energy_cost(self, action_vector: Vector) -> float:
        """Distance from hazards minus alignment with values."""
        ...


@dataclass
class EthicalGeometry:
    """Learned constraint manifold for ethical navigation."""
    forbidden_regions: list[Region]
    virtuous_regions: list[Region]
    values_vector: Vector
```

### Stigmergic Primitives

```python
@dataclass
class PheromoneAgent(Agent[tuple[Concept, Action], TraceDeposit]):
    """
    Environmental memory via pheromone-like traces.
    Deposit intensity proportional to outcome quality.
    Integration: trace deposit IS void.tithe (paying forward).
    """
    field: PheromoneField
    decay_rate: float = 0.1

    async def follow_gradient(self, position: Concept) -> Concept:
        """Move toward strongest trace (ant algorithm)."""
        ...


@dataclass
class HiveMindAgent(Agent[Query, CollectiveRecollection]):
    """
    Collective memory emerging from distributed traces.
    No central store—consensus from accumulated pheromones.
    """
    field: PheromoneField
    participants: list[StigmergicAgent]
```

### Wittgensteinian Primitives

```python
@dataclass
class LanguageGameAgent(Agent[tuple[Concept, Context], list[Move]]):
    """
    Memory as knowing-how-to-play a language game.
    Meaning is use: a concept's memory is valid moves in context.

    Polynomial structure: P(y) = Σₛ y^{D(s)}
    - S: positions (states)
    - D(s): directions (valid moves from state s)
    """
    games: dict[str, LanguageGame]


@dataclass
class GrammarEvolver(Agent[Interaction, GameUpdate]):
    """
    Language games evolve through use.
    - Successful novel moves → expand grammar
    - Failed grammatical moves → add context constraints
    """
    games: dict[str, LanguageGame]
```

### Active Inference Primitives

```python
@dataclass
class FreeEnergyAgent(Agent[Observation, Action]):
    """
    Memory in service of self-evidencing (Free Energy Principle).
    Minimize prediction error via:
    1. Better predictions (reduce surprise)
    2. Policy selection (reduce expected future surprise)
    3. Model update (learning)

    Expected Free Energy: G = pragmatic_value - epistemic_value
    """
    generative_model: GenerativeModel
    preferences: Distribution


@dataclass
class SurpriseMinimizer(Agent[set[Memory], HolographicMemory]):
    """
    Consolidation as free energy minimization.
    - Keep memories that reduce prediction error
    - Compress memories with marginal improvement
    - Forget memories that increase free energy
    """
    world_model: GenerativeModel
```

### Cartographic Primitives

```python
@dataclass
class CartographerAgent(Agent[tuple[ContextVector, Resolution], HoloMap]):
    """
    Project high-dimensional memory space into navigable topology.
    Integrations: L-gent (terrain), N-gent (desire lines), B-gent (budget)
    """
    memory_space: HolographicMemory
    resolution_strategy: ResolutionStrategy


@dataclass
class PathfinderAgent(Agent[Goal, NavigationPlan]):
    """
    Navigate via desire lines (historical paths) or bushwhack (explore).

    Modes:
    - Desire Line Navigation: Follow history (safe, high confidence)
    - Bushwhacking: No history, must explore (risky, low confidence)
    """
    cartographer: CartographerAgent
    trace_history: TraceMonoid


@dataclass
class ContextInjector(Agent[tuple[AgentState, Task], OptimalContext]):
    """
    The answer to: "What is the most perfect context injection for any given turn?"
    Budget-constrained, foveated context with resolution varying by relevance.
    """
    cartographer: CartographerAgent
    budget: TokenBudget
```

### Temporal Primitives

```python
@dataclass
class TemporalLens:
    """Time travel through memory: reconstruct state at any point."""
    unified: UnifiedMemory

    async def at_time(self, t: datetime) -> MemorySnapshot: ...
    async def evolution(self, concept: Concept) -> list[MemoryState]: ...


@dataclass
class ForgettingCurveAgent(Agent[Memory, RetentionPlan]):
    """
    Ebbinghaus forgetting curve: R = e^(-t/S)
    Spaced repetition via SM-2 algorithm.
    """
    retention_threshold: float = 0.3

    def optimal_interval(self, strength: float) -> timedelta: ...


@dataclass
class ContextualRecallAgent(Agent[ContextualQuery, list[Memory]]):
    """
    Memory retrieval influenced by current context.
    Encoding specificity principle: same cue, different contexts → different recalls.
    """
    context_weights: dict[str, float]
```

### Bi-Temporal Primitives

```python
@dataclass
class BiTemporalFact:
    """Every fact has two times: when it happened, when we learned it."""
    content: Any
    t_event: datetime      # When did this happen?
    t_known: datetime      # When did we learn this?
    superseded_by: Optional[str] = None


@dataclass
class BiTemporalStore(Agent[BiTemporalQuery, list[BiTemporalFact]]):
    """
    Two-dimensional temporal memory.
    Enables:
    - Point-in-time queries: "What did I know at time T?"
    - Retroactive correction: "I now know X was wrong"
    - Belief archaeology: "How has my understanding evolved?"
    """
    facts: list[BiTemporalFact]

    async def correct(self, fact_id: str, new_content: Any, reason: str): ...


@dataclass
class BeliefArchaeologist(Agent[Concept, BeliefTimeline]):
    """
    Trace belief evolution over time.
    Excavate layers: what was believed, when did it change, why?
    """
    store: BiTemporalStore
```

### Trace Monoid Primitives

```python
@dataclass
class CausalCone:
    """Causal structure of a memory event."""
    event: MemoryEvent
    past_cone: list[MemoryEvent]      # What caused this
    future_cone: list[MemoryEvent]    # What this caused
    concurrent: list[MemoryEvent]     # Independent events


@dataclass
class CausalConeAgent(Agent[MemoryEvent, CausalCone]):
    """
    Navigate causal structure: given event, find past/future/concurrent.
    Memory respects causality (trace monoid structure).
    """
    weave: TraceMonoid


@dataclass
class KnotAgent(Agent[list[MemoryBranch], MergedMemory]):
    """
    Synchronization barrier for merging concurrent memory branches.
    Like git merge for memories: identify conflicts, apply strategy, unify.
    """
    merge_strategy: MergeStrategy
```

### Advanced Primitives

```python
@dataclass
class AssociativeWeb:
    """
    Memory linked by explicit associations.
    Relations: reminds_of, contradicts, supports, caused_by
    """
    unified: UnifiedMemory

    async def spread_activation(
        self,
        start: Memory,
        depth: int = 3
    ) -> list[tuple[Memory, float]]:
        """Spreading activation with distance decay."""
        ...
```

## Laws/Invariants

### Holographic Law
```
∀ cue ∈ Concept: RecollectionAgent(cue) → Recollection
(Always returns something, never fails)
```

### Graceful Degradation
```
compression_ratio(memory, 0.5) → resolution_loss(0.5)
(50% compression = 50% fidelity loss, NOT 50% data loss)
```

### Temperature Conservation
```
∑ heat(memory) = constant
(Total system temperature conserved across hot/cold promotion/demotion)
```

### Consolidation Idempotence
```
ConsolidationAgent(ConsolidationAgent(M)) ≈ ConsolidationAgent(M)
(Repeated consolidation converges to stable state)
```

### Ethical Monotonicity
```
harmful_outcome(action) → expand(forbidden_region(action))
beneficial_outcome(action) → strengthen(virtuous_region(action))
(Ethics learned from experience, not hardcoded)
```

### Stigmergic Emergence
```
consensus(HiveMind) = aggregate(individual_traces)
(Collective memory emerges without central coordination)
```

### Bi-Temporal Consistency
```
∀ t: query(as_of_known=t) returns beliefs_at(t)
(Time travel queries are consistent with historical state)
```

### Causal Ordering
```
event_a → event_b ⟹ event_a ∈ past_cone(event_b)
(Memory respects causal structure)
```

## Integration

### AGENTESE Paths

```python
# M-gent via AGENTESE
await logos.invoke("self.memory.recall", concept)          # RecollectionAgent
await logos.invoke("self.memory.consolidate")              # ConsolidationAgent (idle)
await logos.invoke("self.memory.prospect", situation)      # ProspectiveAgent
await logos.invoke("self.ethics.navigate", action)         # EthicalGeometryAgent
await logos.invoke("self.memory.at_time", timestamp)       # TemporalLens
await logos.invoke("self.memory.belief_history", concept)  # BeliefArchaeologist

# Stigmergic coordination
await logos.invoke("world.pheromone.deposit", (concept, outcome))
await logos.invoke("world.pheromone.follow")

# Cartography
await logos.invoke("self.memory.map", resolution)          # CartographerAgent
await logos.invoke("self.memory.path", goal)               # PathfinderAgent
await logos.invoke("self.memory.inject_context", task)     # ContextInjector
```

### Relation to Other Gents

```
┌─────────────────────────────────────────────────────────┐
│                   M-gent (Cognitive)                     │
│   Recollection, Consolidation, Prospective, Ethics      │
│   Cartography, Context Injection                         │
├─────────────────────────────────────────────────────────┤
│          ↕ terrain           ↕ traces                    │
│   ┌──────────────┐      ┌──────────────┐                │
│   │    L-gent    │      │    N-gent    │                │
│   │ (embeddings) │      │  (history)   │                │
│   └──────────────┘      └──────────────┘                │
├─────────────────────────────────────────────────────────┤
│                   D-gent (Storage)                       │
│   Volatile, Persistent, Unified, Vector                  │
└─────────────────────────────────────────────────────────┘
```

**M-gent + D-gent**: M-gents are the cognitive operations; D-gents are the storage substrate.

**M-gent + L-gent**: L-gent provides the vector embedding space (terrain for cartography).

**M-gent + N-gent**: N-gents record narrative traces; M-gents remember them as stories.

**M-gent + B-gent**: Memory has costs (storage, retrieval, consolidation). B-gent economics constrain operations.

**M-gent + K-gent**: K-gent (soul) uses M-gent for persona memory and hypnagogic consolidation.

## Anti-Patterns

- **Database Fallacy**: Treating memory as exact retrieval. Memory is reconstruction—embrace fuzziness.
- **Binary Ethics**: Hardcoding allowed/forbidden actions. Ethics is learned geometry, probabilistic.
- **Synchronous Consolidation**: Running consolidation on critical path. It's a hypnagogic worker (idle-time only).
- **Centralized Stigmergy**: Storing all traces in one place. Stigmergy is distributed by design.
- **Forgetting as Deletion**: Treating forgetting as data loss. It's resolution reduction (compression).
- **Context-Free Recall**: Ignoring current context when retrieving. Recall is always contextual.
- **Single Timeline**: Conflating event-time and knowledge-time. Use bi-temporal for belief tracking.

## Implementation Reference

```
impl/claude/agents/m/
├── protocol.py              # Core protocols (HolographicMemory, etc.)
├── memory.py                # RecollectionAgent, basic operations
├── consolidation_engine.py  # ConsolidationAgent (hypnagogic worker)
├── stigmergy.py             # PheromoneAgent, HiveMindAgent
├── associative.py           # AssociativeWeb, spreading activation
├── substrate.py             # Integration with D-gent storage
├── lifecycle.py             # Memory lifecycle (hot/cold promotion)
└── soul_memory.py           # K-gent integration (persona memory)

impl/claude/agents/d/        # Storage substrate (D-gent)
└── (volatile, persistent, unified, vector agents)

impl/claude/agents/l/        # Vector embeddings (L-gent terrain)
└── vector_db.py

impl/claude/agents/n/        # Narrative traces (N-gent history)
└── (trace recording)
```

**Tests**: Consolidated with D-gent storage layer tests.

## Success Criteria

### Functional
- Holographic retrieval: partial match always returns results
- Graceful degradation: compression reduces resolution, not data
- Tiered memory: automatic hot/cold promotion/demotion
- Consolidation: background processing during idle cycles

### Performance
- Recall latency: <100ms working memory, <500ms long-term
- Compression ratio: 10:1 for cold memories
- Budget compliance: respect token limits for context injection

## See Also

- [holographic.md](holographic.md) - Holographic memory architecture
- [README.md](README.md) - M-gent philosophy and four pillars
- [../d-gents/README.md](../d-gents/README.md) - Storage substrate (D-gent)
- [../anatomy.md](../anatomy.md) - Hypnagogic patterns

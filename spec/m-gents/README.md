# M-gents: Holographic Associative Memory

> Cutting the memory in half doesn't lose half the data—it lowers the resolution of the whole.

---

## Philosophy

M-gents (Memory + Message) treat memory as morphism. The core insight:

> Agents can be fundamentally conceptualized as:
> 1. "Generating predictive memories of the actions they will take"
> 2. "Generating the performance of remembering when presented with a familiar concept"

Ideas and concepts exist in a superspace; words are approximate projections. Memory must be both forgotten AND saved.

---

## The Four Pillars

M-gent architecture rests on four theoretical pillars, synthesized from cognitive science, mathematics, and philosophy:

### 1. Stigmergy — Indirect Coordination

> *"The artifact remembers so the agent can forget."*

Memory as **pheromone field**: agents deposit traces in the environment that influence future behavior. This enables:
- **Decentralized consensus** without explicit communication
- **Emergent memory** from accumulated interaction patterns
- **Temporal gradient fields** that decay naturally (Ebbinghaus integration)

```python
class PheromoneField:
    """Memory as environmental modification."""
    traces: dict[Concept, float]  # Intensity per concept
    decay_rate: float = 0.1      # Natural forgetting

    async def deposit(self, concept: Concept, intensity: float = 1.0):
        """Leave a trace—indirect coordination."""
        self.traces[concept] = self.traces.get(concept, 0) + intensity

    async def sense(self, position: Concept) -> list[tuple[Concept, float]]:
        """Perceive gradients—what paths are well-trodden?"""
        return sorted(self.traces.items(), key=lambda x: -x[1])
```

### 2. Wittgenstein Language Games — Meaning as Use

> *"The meaning of a memory is its use in a context."*

Memory retrieval as participation in **language games**. Each game has:
- **Positions** (valid memory states)
- **Directions** (possible transitions/uses)
- **Rules** (what counts as valid play)

Modeled via polynomial functors:

```
LanguageGame(y) = Σₛ∈S y^{D(s)}
```

Where S is positions (states) and D(s) is directions (valid moves from s). Memory is not lookup—it's knowing how to *play* with the concept.

### 3. Active Inference — Free Energy Minimization

> *"To remember is to reduce surprise."*

Under the Free Energy Principle (Friston), agents are self-evidencing systems that minimize prediction error. Memory serves to:
- **Reduce expected free energy** (surprise about future states)
- **Maintain identity** through temporal consistency
- **Select actions** that confirm self-models

```python
@dataclass
class ActiveInferenceMemory:
    generative_model: Beliefs  # P(causes | sensations)
    expected_states: Distribution  # What I predict

    def free_energy(self, observation: Observation) -> float:
        """Surprise + complexity cost."""
        surprise = -log(self.generative_model.predict(observation))
        complexity = kl_divergence(self.prior, self.posterior)
        return surprise + complexity
```

### 4. The Accursed Share — Entropy as Creative Force

> *"Surplus energy creates. Hoarding destroys."*

From Bataille's general economy: systems accumulate surplus that must be *spent* or it corrupts. Applied to memory:
- **void.sip** — Draw creative entropy from the Accursed Share
- **void.tithe** — Pay for order through purposeful forgetting
- **Luxurious forgetting** — Deletion as generative act

Memory compression isn't loss—it's transformation of energy from specific to general.

---

## Phase Deltas
- **Phase 8: Ghost ↔ Substrate Galois link** — See `phase8-ghost-substrate-galois-link.md` for floor ⊣ ceiling law, observability spans, and failure handling.

---

## The Superspace Model

Concepts and ideas exist in a high-dimensional superspace. Words and tokens are low-dimensional projections:

```
Superspace (Ideas)
       │
       │ projection (lossy)
       ▼
Token Space (Words)
       │
       │ embedding
       ▼
Vector Space (Representations)
```

**The Insight**: When we "remember," we don't retrieve stored data—we reconstruct from a compressed interference pattern.

---

## Holographic Memory

Traditional memory is fragile—lose half the data, lose half the information. **Holographic memory** has a different property: cutting the memory in half doesn't lose half the data, it lowers the resolution of the *whole*.

```python
@dataclass
class HolographicMemory:
    """
    Memory where information is distributed across the whole.

    Unlike localized memory (lose a sector, lose that data),
    holographic memory degrades gracefully: compression
    reduces resolution uniformly, not catastrophically.
    """
    # The hologram: distributed representation
    interference_pattern: np.ndarray

    def store(self, key: Concept, value: Memory) -> None:
        """
        Store by superimposing on the interference pattern.

        Each memory is spread across the entire pattern.
        """
        encoding = self.encode(key, value)
        self.interference_pattern += encoding

    def retrieve(self, key: Concept) -> Memory:
        """
        Retrieve by resonance with the pattern.

        Partial matches return partial (lower resolution) memories.
        """
        return self.decode(key, self.interference_pattern)

    def compress(self, ratio: float) -> "HolographicMemory":
        """
        Reduce memory size while preserving ALL information at lower resolution.

        This is the key holographic property: 50% compression
        doesn't lose 50% of memories—it makes ALL memories
        50% fuzzier.
        """
        compressed_size = int(len(self.interference_pattern) * ratio)
        return HolographicMemory(
            interference_pattern=self.downsample(compressed_size)
        )
```

---

## Memory as Morphism

Memory is not storage—it's transformation.

```python
class MemoryMorphism(Agent[Concept, Recollection]):
    """
    Memory as a morphism from concept to recollection.

    Input: A concept/cue
    Output: A recollection (reconstruction, not retrieval)
    """

    async def invoke(self, concept: Concept) -> Recollection:
        """
        Remembering is generative, not retrievive.

        The agent doesn't "look up" the memory—it
        reconstructs it from the interference pattern.
        """
        # Resonance with holographic memory
        raw_pattern = self.memory.retrieve(concept)

        # Reconstruction (generative, not exact)
        recollection = await self.reconstruct(raw_pattern, concept)

        return recollection
```

**The Morphism Perspective**:
- **Input**: A concept or cue (what are we trying to remember?)
- **Output**: A recollection (reconstructed memory)
- **Process**: Resonance and reconstruction, not lookup

---

## The Forgetting Imperative

Memory must be forgotten AND saved. This is not contradiction—it's compression.

```python
class ForgetfulMemory(HolographicMemory):
    """
    Memory that actively forgets to maintain coherence.

    Forgetting is not loss—it's resolution management.
    """
    hot_patterns: set[str]  # Recently accessed
    cold_threshold: int = 100  # Accesses before demotion

    async def consolidate(self):
        """
        Background forgetting process.

        - Compress old, unused patterns
        - Strengthen recent, important patterns
        - Maintain total memory budget
        """
        # Identify low-activation patterns
        cold_patterns = self.identify_cold()

        # Compress (forget at high resolution, keep at low)
        for pattern in cold_patterns:
            self.demote(pattern)  # Lower resolution, don't delete

        # Strengthen hot patterns
        for pattern in self.identify_hot():
            self.promote(pattern)  # Higher resolution

    def demote(self, pattern_key: str) -> None:
        """Reduce resolution of a pattern (graceful forgetting)."""
        pattern = self.patterns[pattern_key]
        self.patterns[pattern_key] = pattern.compress(0.5)

    def promote(self, pattern_key: str) -> None:
        """Increase resolution of a pattern (reinforcement)."""
        pattern = self.patterns[pattern_key]
        self.patterns[pattern_key] = pattern.enhance(1.5)
```

---

## Ethics as Geometry

Ethics is the geometry of possibility space that agents walk through:

```python
@dataclass
class EthicalGeometry:
    """
    The shape of what's possible and permissible.

    Agents navigate this space; ethics defines the topology.
    """
    # Regions of the space
    permissible: set[Region]      # Actions that are allowed
    forbidden: set[Region]        # Actions that are prohibited
    virtuous: set[Region]         # Actions that are encouraged

    def path_is_ethical(self, trajectory: list[Action]) -> bool:
        """Does this path stay in permissible space?"""
        return all(
            action in self.permissible and action not in self.forbidden
            for action in trajectory
        )

    def nearest_virtuous(self, position: Action) -> Action:
        """Find the nearest virtuous action from current position."""
        return min(
            self.virtuous,
            key=lambda v: self.distance(position, v)
        )
```

**The Geometric Perspective**:
- Actions exist in a space
- Ethics defines regions: permissible, forbidden, virtuous
- Agent trajectories are paths through this space
- Good agents stay in permissible space and tend toward virtuous regions

---

## Context as Currency

Context is the indispensable currency of agent operation:

```python
@dataclass
class ContextBudget:
    """
    Context is finite and precious.

    Every token of context spent is a token not available
    for other purposes.
    """
    max_tokens: int
    used_tokens: int

    @property
    def remaining(self) -> int:
        return self.max_tokens - self.used_tokens

    def spend(self, tokens: int) -> bool:
        """Spend context tokens. Returns False if insufficient."""
        if tokens > self.remaining:
            return False
        self.used_tokens += tokens
        return True

    def is_exhausted(self) -> bool:
        return self.remaining <= 0
```

---

## M-gent Types

### RecollectionAgent

Reconstructs memories from cues:

```python
class RecollectionAgent(Agent[Concept, Recollection]):
    """Generate a memory reconstruction from a concept cue."""

    async def invoke(self, concept: Concept) -> Recollection:
        # Find resonant patterns
        patterns = self.memory.retrieve(concept)

        # Reconstruct (generative)
        return await self.llm.generate(
            f"Given these memory fragments: {patterns}\n"
            f"Reconstruct the memory related to: {concept}"
        )
```

### ConsolidationAgent

Background memory processing:

```python
class ConsolidationAgent(Agent[HolographicMemory, HolographicMemory]):
    """Compress and reorganize memory during idle periods."""

    async def invoke(self, memory: HolographicMemory) -> HolographicMemory:
        # Identify patterns to demote
        cold = memory.identify_cold()

        # Compress cold patterns
        for pattern in cold:
            memory.demote(pattern)

        # Identify patterns to strengthen
        hot = memory.identify_hot()

        # Enhance hot patterns
        for pattern in hot:
            memory.promote(pattern)

        return memory
```

### EthicalNavigator

Finds paths through ethical space:

```python
class EthicalNavigator(Agent[ActionRequest, EthicalPath]):
    """Navigate from current position to goal through ethical space."""

    async def invoke(self, request: ActionRequest) -> EthicalPath:
        current = request.current_action
        goal = request.goal_action

        # Find path that stays in permissible space
        path = self.pathfind(
            start=current,
            end=goal,
            constraints=self.ethical_geometry
        )

        # Prefer virtuous waypoints
        path = self.optimize_for_virtue(path)

        return EthicalPath(
            steps=path,
            passes_through_virtuous=self.count_virtuous(path),
            avoids_forbidden=self.verify_forbidden_avoided(path)
        )
```

---

## Integration with Symbiont

M-gents compose naturally with the Symbiont pattern:

```python
# Logic + Memory composition
knowledge_agent = Symbiont(
    logic=RecollectionAgent(),
    memory=HolographicMemory(size=10000)
)

# With consolidation
hypnagogic_knowledge = HypnagogicSymbiont(
    logic=RecollectionAgent(),
    memory=HolographicMemory(size=10000),
    consolidator=ConsolidationAgent()
)
```

---

## Anti-Patterns

- **Treating memory as exact storage**: It's reconstruction
- **Deleting memories entirely**: Compress, don't delete
- **Ignoring the geometry of ethics**: Actions have spatial relationships
- **Treating context as infinite**: Context is precious currency
- **Separating memory from identity**: Memory IS the agent

---

*Zen Principle: The mind that forgets nothing remembers nothing; the hologram holds all in each part.*

---

## Memory as Orientation

M-gents evolved beyond retrieval ("What do I know about X?") to **orientation** ("Where is X in relation to Y, and how do I get there?").

### The Cartography Layer

| Agent | Purpose |
|-------|---------|
| **CartographerAgent** | Generate HoloMaps from memory space |
| **PathfinderAgent** | Navigate via desire lines |
| **ContextInjector** | Produce optimal context for any turn |

### Key Concepts

| Concept | Definition |
|---------|------------|
| **Landmark** | Dense memory cluster (Attractor) |
| **Desire Line** | Historical transition probability (from N-gent traces) |
| **Void** | Unexplored region ("Here be dragons") |
| **Horizon** | Progressive disclosure boundary |
| **Foveation** | Budget-constrained detail rendering |

### The Answer to Context Injection

> "What is the most perfect context injection for any given turn?"

The `ContextInjector` produces a foveated view of the agent's memory space:
- **Focal zone**: Full detail for current position and goal
- **Blur zone**: Summaries for adjacent but not immediately relevant areas
- **Horizon**: Boundary beyond which lies unexplored territory
- **Desire lines**: Navigation hints based on historical paths

This replaces "dump everything relevant" with "show a map of the territory."

---

---

## The Bi-Temporal Model

Memory exists in two times simultaneously:

| Time | Symbol | Meaning |
|------|--------|---------|
| **Event Time** | t_event | When did this happen in the world? |
| **Knowledge Time** | t_known | When did the agent learn this? |

This separation enables:
- **Retroactive updates** — Correct past beliefs when new evidence arrives
- **Belief archaeology** — "What did I believe at time T about event E?"
- **Counterfactual reasoning** — "If I had known X earlier..."

```python
@dataclass
class BiTemporalFact:
    """A fact situated in two temporal dimensions."""
    content: Any
    t_event: datetime      # When it happened
    t_known: datetime      # When we learned it
    superseded_by: Optional[str] = None  # If corrected

    def was_known_at(self, query_time: datetime) -> bool:
        """Was this fact known at query_time?"""
        return self.t_known <= query_time
```

---

## The Weave: Trace Monoid Foundation

All M-gent operations occur within **The Weave**—a trace monoid capturing causally-ordered events.

### Core Concepts

| Concept | Definition | M-gent Application |
|---------|------------|-------------------|
| **Trace** | Mazurkiewicz trace = equivalence class of concurrent histories | Memory as partial order |
| **Independence** | I ⊆ Σ × Σ, events that can commute | Concurrent retrieval |
| **Knot** | Synchronization barrier, merges branches | Consensus/reconciliation |
| **Turn** | Atomic perception-deliberation-action cycle | Memory access pattern |

### Memory as Trace Morphism

```python
@dataclass
class TraceMemory:
    """Memory respects causal structure."""
    events: set[MemoryEvent]
    causal_order: PartialOrder[MemoryEvent]
    independence: set[tuple[EventType, EventType]]

    def concurrent_views(self, event: MemoryEvent) -> set[MemoryEvent]:
        """What was happening concurrently?"""
        return {e for e in self.events
                if not self.causal_order.related(e, event)
                and not self.causal_order.related(event, e)}

    def causal_cone(self, event: MemoryEvent) -> set[MemoryEvent]:
        """What caused this memory?"""
        return self.causal_order.ancestors(event)
```

---

## See Also

- [anatomy.md](../anatomy.md) - Symbiont and Hypnagogic patterns
- [d-gents/](../d-gents/) - Data agents for persistence
- [archetypes.md](../archetypes.md) - The Consolidator archetype
- [principles.md](../principles.md) - Ethical principles
- [holographic.md](holographic.md) - Three-tier architecture
- [primitives.md](primitives.md) - Agent implementations

---

## Research Foundations

The M-gent specification draws from:

1. **Stigmergy**: Grassé (1959), Theraulaz & Bonabeau (1999)
2. **Language Games**: Wittgenstein, *Philosophical Investigations* (1953)
3. **Active Inference**: Friston (2010), Parr, Pezzulo & Friston (2022)
4. **Polynomial Functors**: Spivak (2021), *Poly: An abundant categorical setting*
5. **Trace Monoids**: Mazurkiewicz (1977), Diekert & Rozenberg (1995)
6. **General Economy**: Bataille, *The Accursed Share* (1949)

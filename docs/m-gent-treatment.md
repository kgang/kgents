# M-gents: Holographic Associative Memory - Expanded Treatment

> **Status**: Design Document v1.0
> **Date**: 2025-12-09
> **Purpose**: Comprehensive M-gent architecture bridging spec and impl

---

## Executive Summary

M-gents represent memory as **generative reconstruction, not retrieval**. This document expands the philosophical spec into implementable architecture, introduces novel memory primitives, and defines integration paths with existing D-gent, L-gent, and N-gent infrastructure.

**Key Insight**: Memory is a morphism from cue to reconstruction. The hologram metaphor isn't decorative—it's architecturally load-bearing.

---

## Part 1: The Holographic Principle (Architectural Implications)

### 1.1 Why Holographic?

Traditional memory:
```
Store(key, value) → Index[key] = value
Retrieve(key) → Index[key]  # Exact or fail
```

Holographic memory:
```
Store(concept, memory) → Pattern += encode(concept, memory)
Recall(concept) → decode(concept, Pattern)  # Always returns something
```

**The Key Properties**:

| Property | Traditional | Holographic |
|----------|-------------|-------------|
| **Graceful degradation** | Lose sector → lose data | Lose 50% → 50% fuzzier |
| **Content-addressable** | Key lookup | Similarity resonance |
| **Associative** | Explicit links | Implicit interference |
| **Generative** | Exact retrieval | Reconstruction |

### 1.2 The Interference Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    HolographicMemory                         │
│                                                              │
│   Memory₁ ───┐                                               │
│              ├──► Interference Pattern ───► Reconstruction   │
│   Memory₂ ───┤         (superposition)         (from cue)    │
│              │                                               │
│   Memory₃ ───┘    All memories exist in                     │
│                   the same distributed space                 │
└─────────────────────────────────────────────────────────────┘
```

**Implementation Insight**: This maps naturally to **vector embeddings**. The L-gent vector DB (`vector_db.py`) already provides the substrate. M-gents add the **generative reconstruction** layer on top.

---

## Part 2: Memory Modes (The M-gent Taxonomy)

### 2.1 RecollectionAgent (Basic Holographic Recall)

```python
RecollectionAgent: Cue → Recollection

class RecollectionAgent(Agent[Concept, Recollection]):
    """
    The fundamental M-gent: generative memory retrieval.

    Unlike a database lookup, recollection is RECONSTRUCTION:
    - Partial matches always return something
    - Results are influenced by all stored memories
    - The "resolution" depends on the depth of the cue
    """
    memory: HolographicMemory
    reconstructor: Agent[Pattern, Recollection]  # LLM or decoder

    async def invoke(self, concept: Concept) -> Recollection:
        # Find resonant patterns (vector similarity)
        patterns = await self.memory.retrieve(concept)

        # Reconstruct (generative, not lookup)
        return await self.reconstructor.invoke(
            ReconstructionRequest(
                cue=concept,
                resonant_patterns=patterns,
                resolution=self.compute_resolution(patterns)
            )
        )
```

### 2.2 ConsolidationAgent (Sleep/Wake Memory Processing)

**THE HYPNAGOGIC PATTERN REALIZED**

The Symbiont spec introduces the Hypnagogic pattern (spec/d-gents/symbiont.md:179). M-gents make this concrete:

```python
ConsolidationAgent: HolographicMemory → HolographicMemory

class ConsolidationAgent(Agent[HolographicMemory, HolographicMemory]):
    """
    Background memory processing during "sleep" cycles.

    Operations:
    1. COMPRESS: Reduce resolution of cold memories
    2. STRENGTHEN: Increase resolution of hot memories
    3. INTEGRATE: Merge similar memories (chunking)
    4. FORGET: Reduce interference from irrelevant patterns
    """

    async def invoke(self, memory: HolographicMemory) -> HolographicMemory:
        # Identify activation levels
        hot = memory.identify_hot()   # Recently/frequently accessed
        cold = memory.identify_cold() # Dormant patterns

        # Temperature-based processing
        for pattern in cold:
            if pattern.age > self.forget_threshold:
                memory.demote(pattern, factor=0.5)  # Lower resolution
            else:
                memory.compress(pattern)  # Save space, keep pattern

        for pattern in hot:
            memory.promote(pattern, factor=1.2)  # Higher resolution

        # Integration pass: merge near-duplicates
        clusters = memory.cluster_similar(threshold=0.9)
        for cluster in clusters:
            memory.integrate(cluster)  # Create unified pattern

        return memory
```

### 2.3 ProspectiveAgent (Predictive Memory)

**NOVEL**: Memory as future-prediction, not just past-retrieval.

From the M-gent philosophy: *"Generating predictive memories of the actions they will take"*

```python
ProspectiveAgent: Situation → PredictedActions

class ProspectiveAgent(Agent[Situation, list[PredictedAction]]):
    """
    Memory as prediction: what will the agent do next?

    Uses holographic memory to find similar past situations,
    then projects the actions that followed.
    """
    memory: HolographicMemory
    action_log: ActionHistory  # D-gent for action sequences

    async def invoke(self, situation: Situation) -> list[PredictedAction]:
        # Find similar past situations
        similar_situations = await self.memory.retrieve(situation)

        # What actions followed those situations?
        predictions = []
        for past_situation, similarity in similar_situations:
            actions = await self.action_log.get_subsequent(past_situation)
            for action in actions:
                predictions.append(PredictedAction(
                    action=action,
                    confidence=similarity * action.success_rate,
                    source_situation=past_situation
                ))

        return sorted(predictions, key=lambda p: -p.confidence)
```

### 2.4 EthicalGeometryAgent (Memory of Constraints)

**NOVEL**: The ethical geometry spec (m-gents/README.md:173) as a living agent.

```python
EthicalGeometryAgent: Action → EthicalPath

class EthicalGeometryAgent(Agent[ActionProposal, EthicalPath]):
    """
    Navigate action space using remembered ethical constraints.

    The geometry is LEARNED from experience:
    - Actions that led to harm → forbidden regions expand
    - Actions that led to good → virtuous regions strengthen
    - Boundaries are probabilistic, not binary
    """
    geometry: EthicalGeometry  # Learned constraint manifold

    async def invoke(self, proposal: ActionProposal) -> EthicalPath:
        # Where is this action in the geometry?
        position = self.geometry.locate(proposal.action)

        # Is it in forbidden territory?
        if position in self.geometry.forbidden:
            # Find alternative path
            alternatives = self.geometry.nearest_permissible(position)
            return EthicalPath(
                blocked=True,
                reason=self.geometry.why_forbidden(position),
                alternatives=alternatives
            )

        # Is there a more virtuous path?
        virtuous_option = self.geometry.nearest_virtuous(position)

        return EthicalPath(
            blocked=False,
            current_path=position,
            virtuous_alternative=virtuous_option,
            distance_to_virtue=self.geometry.distance(position, virtuous_option)
        )
```

---

## Part 3: The Memory Hierarchy (Novel Architecture)

### 3.1 Three-Tier Holographic Memory

Inspired by human memory (sensory → working → long-term):

```
┌─────────────────────────────────────────────────────────────────┐
│                   THREE-TIER HOLOGRAPHIC MEMORY                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TIER 1: SENSORY BUFFER (Immediate)                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  • Last 10 seconds of raw input                          │    │
│  │  • High resolution, no compression                       │    │
│  │  • Volatile (D-gent: VolatileAgent)                      │    │
│  │  • Purpose: "What just happened?"                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          ↓ attention filter                      │
│                                                                  │
│  TIER 2: WORKING MEMORY (Active)                                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  • Current task context                                  │    │
│  │  • Medium resolution, some compression                   │    │
│  │  • Cached (D-gent: CachedAgent)                          │    │
│  │  • Purpose: "What am I doing?"                           │    │
│  │  • Capacity: ~7±2 chunks (Miller's Law)                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          ↓ consolidation                         │
│                                                                  │
│  TIER 3: HOLOGRAPHIC LONG-TERM (Persistent)                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  • All experiences, compressed holographically           │    │
│  │  • Variable resolution (hot=high, cold=low)              │    │
│  │  • Persistent (D-gent: PersistentAgent + VectorAgent)    │    │
│  │  • Purpose: "What do I know?"                            │    │
│  │  • Capacity: Theoretically unlimited (graceful degrade)  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Memory Tier Implementation

```python
@dataclass
class TieredMemory:
    """
    Three-tier holographic memory with automatic promotion/demotion.

    Composed from existing D-gent primitives:
    - Tier 1: VolatileAgent (impl/claude/agents/d/volatile.py)
    - Tier 2: CachedAgent (impl/claude/agents/d/cached.py)
    - Tier 3: UnifiedMemory (impl/claude/agents/d/unified.py) + VectorBackend
    """

    sensory: VolatileAgent[SensoryBuffer]      # Tier 1
    working: CachedAgent[WorkingMemory]        # Tier 2
    longterm: UnifiedMemory[HolographicState]  # Tier 3

    # Flow control
    attention: AttentionFilter  # Sensory → Working
    consolidator: ConsolidationAgent  # Working → Long-term

    async def perceive(self, input: RawInput) -> None:
        """Add to sensory buffer."""
        await self.sensory.save(input)

    async def attend(self, focus: Focus) -> None:
        """
        Move attended items from sensory to working memory.

        This is the ATTENTION mechanism:
        - Filter sensory buffer by relevance to focus
        - Chunk into working memory
        """
        sensory_state = await self.sensory.load()
        attended = self.attention.filter(sensory_state, focus)

        # Chunk and save to working memory
        chunks = self.chunk(attended)  # Miller's Law
        await self.working.save(chunks)

    async def consolidate(self) -> None:
        """
        Move working memory to long-term (the "sleep" phase).

        This is where holographic encoding happens.
        """
        working_state = await self.working.load()

        # Encode into holographic pattern
        pattern = self.encode_holographic(working_state)

        # Superimpose on long-term memory
        await self.longterm.save(pattern)

        # Run consolidation agent
        await self.consolidator.invoke(self.longterm)
```

---

## Part 4: Integration with Existing Infrastructure

### 4.1 M-gent + D-gent (The Symbiont Bridge)

M-gents are the **cognitive layer** on top of D-gent **storage**:

```
┌─────────────────────────────────────────────────────────────┐
│                      M-gent (Cognitive)                      │
│    RecollectionAgent, ConsolidationAgent, ProspectiveAgent   │
├─────────────────────────────────────────────────────────────┤
│                      D-gent (Storage)                        │
│    VolatileAgent, PersistentAgent, UnifiedMemory, VectorAgent│
└─────────────────────────────────────────────────────────────┘
```

**The Key Interface**: `HolographicMemory` wraps `UnifiedMemory`:

```python
class HolographicMemory:
    """
    Holographic layer on top of D-gent UnifiedMemory.

    Uses D-gent's three layers:
    - Semantic: associate/recall → holographic pattern matching
    - Temporal: witness/replay → memory timeline
    - Relational: relate/trace → associative links
    """

    def __init__(self, storage: UnifiedMemory):
        self.storage = storage
        assert MemoryLayer.SEMANTIC in storage.available_layers
        assert MemoryLayer.TEMPORAL in storage.available_layers

    async def store(self, concept: Concept, memory: Memory) -> None:
        """Superimpose memory on the interference pattern."""
        # Use D-gent semantic layer
        await self.storage.associate(memory, concept.key)
        # Record temporal event
        await self.storage.witness(f"store:{concept.key}", memory)

    async def retrieve(self, concept: Concept) -> list[tuple[Memory, float]]:
        """Recall by resonance (similarity search)."""
        # Use D-gent semantic recall
        results = await self.storage.recall(concept.key, limit=10)
        return [(await self.load_memory(id), score) for id, score in results]
```

### 4.2 M-gent + L-gent (Semantic Substrate)

L-gent's vector infrastructure provides the **embedding space**:

```python
class VectorHolographicMemory(HolographicMemory):
    """
    Holographic memory backed by L-gent vector search.

    Uses:
    - DgentVectorBackend (impl/claude/agents/l/vector_db.py)
    - SemanticRegistry (impl/claude/agents/l/semantic_registry.py)
    """

    def __init__(
        self,
        vector_backend: DgentVectorBackend,
        embedder: Embedder
    ):
        self.vectors = vector_backend
        self.embedder = embedder

    async def store(self, concept: Concept, memory: Memory) -> None:
        """Embed and store in vector space."""
        embedding = await self.embedder.embed(memory.content)
        await self.vectors.store(
            id=concept.key,
            vector=embedding,
            metadata=memory.metadata
        )

    async def retrieve(self, concept: Concept) -> list[tuple[Memory, float]]:
        """Vector similarity search = holographic resonance."""
        query_embedding = await self.embedder.embed(concept.cue)
        results = await self.vectors.search(query_embedding, k=10)
        return [(Memory.from_result(r), r.similarity) for r in results]

    async def compress(self, ratio: float) -> None:
        """
        Holographic compression: reduce dimension, keep all memories.

        Uses L-gent's curvature analysis to identify compressible regions.
        """
        # Find low-curvature regions (flat = compressible)
        low_curvature = await self.vectors.find_void(threshold=0.1)

        # Project to lower dimension in those regions
        for region in low_curvature:
            await self.vectors.project_to_lower_dim(region, ratio)
```

### 4.3 M-gent + N-gent (Memory as Narrative)

N-gents tell stories; M-gents remember them:

```python
class NarrativeMemory:
    """
    Memory organized as stories (N-gent integration).

    Uses Chronicle structure from N-gents to store memories
    as interconnected narratives, not isolated facts.
    """

    def __init__(self, memory: HolographicMemory, narrator: NarratorAgent):
        self.memory = memory
        self.narrator = narrator

    async def store_experience(self, execution: AgentExecution) -> None:
        """Store an agent execution as a narrative memory."""
        # N-gent produces the story
        result, narrative = await self.narrator.invoke(execution)

        # Store story as holographic memory
        await self.memory.store(
            concept=self.extract_concept(narrative),
            memory=Memory(
                content=narrative.to_narrative(),
                traces=narrative.traces,
                type="narrative"
            )
        )

    async def recall_similar_story(self, situation: Situation) -> NarrativeLog:
        """Find a past story similar to current situation."""
        results = await self.memory.retrieve(Concept(cue=situation.summary))

        if results:
            best_match, similarity = results[0]
            return NarrativeLog(traces=best_match.traces)

        return None
```

---

## Part 5: Novel Memory Primitives

### 5.1 TemporalLens (Memory as Time Travel)

```python
class TemporalLens:
    """
    View memory at different points in time.

    Composes with D-gent temporal layer to enable:
    - "What did I know at time T?"
    - "How has my understanding evolved?"
    """

    async def at_time(self, t: datetime) -> MemorySnapshot:
        """Reconstruct memory state at time t."""
        return await self.unified.replay(t)

    async def evolution(self, concept: Concept) -> list[MemoryState]:
        """How has understanding of concept changed over time?"""
        timeline = await self.unified.timeline()
        return [
            state for state in timeline
            if self.is_about(state, concept)
        ]
```

### 5.2 AssociativeWeb (Memory as Graph)

```python
class AssociativeWeb:
    """
    Memories linked by association, not just similarity.

    Uses D-gent relational layer to build explicit links:
    - "reminds_of"
    - "contradicts"
    - "supports"
    - "caused_by"
    """

    async def link(
        self,
        source: Memory,
        relation: str,
        target: Memory
    ) -> None:
        """Create associative link between memories."""
        await self.unified.relate(source.id, relation, target.id)

    async def spread_activation(
        self,
        start: Memory,
        depth: int = 3
    ) -> list[tuple[Memory, float]]:
        """
        Spreading activation from a memory.

        Like neural activation: nearby memories activate,
        activation decays with distance.
        """
        graph = await self.unified.trace(start.id, max_depth=depth)

        activations = []
        for node in graph["nodes"]:
            distance = self.shortest_path(start.id, node)
            activation = 1.0 / (1.0 + distance)  # Decay
            activations.append((await self.load(node), activation))

        return sorted(activations, key=lambda x: -x[1])
```

### 5.3 ForgettingCurve (Active Memory Management)

**NOVEL**: Ebbinghaus forgetting curve as an agent:

```python
class ForgettingCurveAgent(Agent[Memory, RetentionPlan]):
    """
    Model of forgetting to guide consolidation.

    The Ebbinghaus forgetting curve: R = e^(-t/S)
    Where:
    - R = retention (0 to 1)
    - t = time since last recall
    - S = strength (increases with repetition)
    """

    async def invoke(self, memory: Memory) -> RetentionPlan:
        # Calculate current retention
        t = now() - memory.last_accessed
        S = memory.strength
        R = math.exp(-t / S)

        if R < 0.3:
            # About to forget - needs review
            return RetentionPlan(
                action="review",
                urgency="high",
                suggested_interval=self.optimal_interval(S)
            )
        elif R > 0.9:
            # Well retained - can compress
            return RetentionPlan(
                action="compress",
                urgency="low",
                current_retention=R
            )
        else:
            # Normal retention
            return RetentionPlan(
                action="maintain",
                current_retention=R
            )

    def optimal_interval(self, strength: float) -> timedelta:
        """
        Spaced repetition: optimal interval for next review.

        Based on SuperMemo SM-2 algorithm.
        """
        return timedelta(days=2.5 * strength)
```

### 5.4 ContextualRecall (Memory + Situation)

**NOVEL**: Memory retrieval influenced by current context:

```python
class ContextualRecallAgent(Agent[ContextualQuery, list[Memory]]):
    """
    Recall memories with context weighting.

    The same cue retrieves different memories depending on:
    - Current task (what am I doing?)
    - Emotional state (how am I feeling?)
    - Environment (where am I?)
    """

    async def invoke(self, query: ContextualQuery) -> list[Memory]:
        # Base retrieval
        base_results = await self.memory.retrieve(query.cue)

        # Context weighting
        weighted = []
        for memory, base_score in base_results:
            context_boost = self.compute_context_relevance(
                memory=memory,
                current_task=query.task,
                current_mood=query.mood,
                current_location=query.location
            )

            weighted.append((memory, base_score * context_boost))

        return sorted(weighted, key=lambda x: -x[1])

    def compute_context_relevance(
        self,
        memory: Memory,
        current_task: str,
        current_mood: str,
        current_location: str
    ) -> float:
        """
        Context-dependent memory enhancement.

        Based on encoding specificity principle:
        memories are easier to recall in similar contexts.
        """
        task_match = self.similarity(memory.context.task, current_task)
        mood_match = self.similarity(memory.context.mood, current_mood)
        location_match = self.similarity(memory.context.location, current_location)

        return 0.5 + 0.5 * (0.4 * task_match + 0.3 * mood_match + 0.3 * location_match)
```

---

## Part 6: The Memory Budget (B-gent Integration)

### 6.1 MemoryEconomics

Integrate with B-gent's token economics:

```python
class MemoryBudget:
    """
    Memory has costs: storage, retrieval, consolidation.

    Integrates with B-gent CentralBank for token accounting.
    """

    async def store_with_budget(
        self,
        memory: Memory,
        bank: CentralBank
    ) -> Receipt:
        """Store memory if budget allows."""
        # Calculate cost
        storage_cost = self.estimate_storage_cost(memory)

        # Request tokens
        receipt = await bank.authorize(
            operation="memory_store",
            tokens_requested=storage_cost
        )

        if receipt.status == "approved":
            await self.memory.store(memory)
            await bank.settle(receipt)
        else:
            # Budget exceeded - compress or reject
            compressed = await self.compress_to_budget(memory, receipt.available)
            await self.memory.store(compressed)

        return receipt
```

### 6.2 ResolutionBudget

Trade resolution for capacity:

```python
class ResolutionBudget:
    """
    Manage memory resolution as economic resource.

    High-resolution memories cost more tokens.
    Hot memories get more budget.
    Cold memories are compressed.
    """

    async def allocate_resolution(
        self,
        memory_id: str,
        budget: TokenBudget
    ) -> float:
        """Determine resolution level given budget."""
        # Priority factors
        access_frequency = await self.get_access_count(memory_id)
        recency = await self.get_recency_score(memory_id)
        importance = await self.get_importance(memory_id)

        # Priority score
        priority = 0.4 * access_frequency + 0.3 * recency + 0.3 * importance

        # Allocate resolution proportionally
        total_priority = await self.sum_all_priorities()
        budget_share = priority / total_priority

        resolution = budget_share * budget.total_tokens
        return min(1.0, resolution / self.max_resolution_cost)
```

---

## Part 7: Implementation Roadmap

### Phase 1: Foundation (Build on Existing)

| Task | Depends On | Status |
|------|------------|--------|
| `HolographicMemory` class | D-gent UnifiedMemory | TODO |
| `RecollectionAgent` | HolographicMemory | TODO |
| Integration tests | Both above | TODO |

### Phase 2: Cognitive Layer

| Task | Depends On | Status |
|------|------------|--------|
| `ConsolidationAgent` | HolographicMemory | TODO |
| `TieredMemory` | D-gent Volatile/Cached/Unified | TODO |
| `ForgettingCurveAgent` | ConsolidationAgent | TODO |

### Phase 3: Advanced Primitives

| Task | Depends On | Status |
|------|------------|--------|
| `ProspectiveAgent` | RecollectionAgent | TODO |
| `EthicalGeometryAgent` | HolographicMemory | TODO |
| `AssociativeWeb` | D-gent Relational Layer | TODO |

### Phase 4: Integration

| Task | Depends On | Status |
|------|------------|--------|
| L-gent VectorHolographicMemory | L-gent vector_db.py | TODO |
| N-gent NarrativeMemory | N-gent narrator | TODO |
| B-gent MemoryBudget | B-gent CentralBank | TODO |

---

## Part 8: Success Criteria

### Functional Requirements

- [ ] Holographic retrieval: partial match always returns results
- [ ] Graceful degradation: 50% compression = 50% resolution loss (not 50% data loss)
- [ ] Tiered memory: automatic promotion/demotion between tiers
- [ ] Consolidation: background memory processing during idle

### Performance Requirements

- [ ] Recall latency: <100ms for working memory, <500ms for long-term
- [ ] Compression ratio: 10:1 for cold memories
- [ ] Budget compliance: memory operations respect token budget

### Integration Requirements

- [ ] D-gent: Seamless use of UnifiedMemory, VectorAgent
- [ ] L-gent: Vector search as holographic substrate
- [ ] N-gent: Narrative storage and recall
- [ ] B-gent: Memory economics

---

## Appendix A: The Mathematics of Holographic Memory

### Encoding

Given concept $c$ and memory $m$, the encoding is:

$$e(c, m) = c \otimes m$$

Where $\otimes$ is the tensor product (or convolution in Fourier space).

### Storage

The interference pattern $P$ accumulates encodings:

$$P = \sum_{i} e(c_i, m_i)$$

### Retrieval

Given cue $c$, retrieval is:

$$\hat{m} = P \otimes c^* = \sum_{i} (c_i \otimes m_i) \otimes c^*$$

If $c \approx c_j$, then $\hat{m} \approx m_j$ (by orthogonality of other terms).

### Compression

Dimensionality reduction preserves structure:

$$P' = \text{SVD}_k(P)$$

Where $k < \dim(P)$. All memories are preserved at lower resolution.

---

## Appendix B: Philosophical Grounding

### Memory as Morphism

From spec/m-gents/README.md:

> "Memory is not storage—it's transformation."

The M-gent philosophy:
1. **Generative**: Memory reconstructs, not retrieves
2. **Distributed**: Every memory is everywhere
3. **Contextual**: Recall depends on current state
4. **Active**: Forgetting is a feature, not a bug
5. **Compositional**: Memory composes with logic (Symbiont)

### The Ethics of Memory

From spec/m-gents/README.md (EthicalGeometry):

Memory shapes behavior. What we remember constrains what we can do. The ethical geometry is **learned** from experience:

- Actions that caused harm → expand forbidden regions
- Actions that produced good → reinforce virtuous regions
- The geometry evolves as the agent learns

This is **memory as conscience**.

---

*Zen Principle: The mind that forgets nothing remembers nothing; the hologram holds all in each part.*

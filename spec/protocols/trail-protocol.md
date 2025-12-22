# The Trail Protocol

> *"The web gave us hyperlinks but lost the trails. We're recovering them."*
>
> — Vannevar Bush's unfulfilled vision, realized (2025)

**Status:** Specification (Partially Implemented)
**Date:** 2025-12-22
**Heritage:** Memex (Bush, 1945), Typed-Hypergraph, Agent-as-Witness
**Implementation:** `impl/claude/protocols/trail/`

---

## Implementation Status (2025-12-22)

| Layer | Status | Tests | Notes |
|-------|--------|-------|-------|
| Postgres Persistence | ✅ Complete | 20 | `storage.py`, migrations 006+007 |
| File Persistence | ✅ Complete | 26 | `file_persistence.py` (~/.kgents/trails/) |
| SQLAlchemy Models | ✅ Complete | — | `models/trail.py` with `Vector(1536)` |
| Trail → Witness Bridge | ✅ Complete | 28 | `services/witness/trail_bridge.py` |
| pgvector Semantic Search | ✅ Complete | 18 | Native `<=>` operator, IVFFlat index |
| Fork/Merge | ✅ Complete | 3 | `fork_trail()` implemented |
| Concurrent Co-Exploration | ⏳ Planned | — | WebSocket sync not started |
| Visual Trail Graph | ⏳ Planned | — | React components not started |

**Total Trail Tests:** 46 (trail) + 18 (pgvector) = 64

**Next Priority:** Visual Trail Graph (joy feature), then Concurrent Co-Exploration

---

## Epigraph

> *"A new profession of trailblazers would appear for those who took pleasure in finding useful trails through the enormous mass of the common record."*
> — Vannevar Bush, "As We May Think" (1945)

> *"The proof IS the decision. The mark IS the witness."*
> — kgents Constitution

---

## 1. Overview

The Trail Protocol defines **trails as first-class, durable, composable knowledge artifacts**. A trail is not navigation history—it is **evidence of understanding being built**.

### 1.1 Core Value Proposition

**Structural guarantees are the axiological foundation.** Data for the sake of it comes first. The Trail Protocol provides:

| Guarantee | Mechanism |
|-----------|-----------|
| **Durability** | Postgres persistence via D-gent (not ephemeral) |
| **Provenance** | Every claim traceable to exploration evidence |
| **Composability** | Trails fork, merge, compose like git branches |
| **Observability** | Concurrent explorers see the same live state |

### 1.2 What a Trail IS

```
Trail ≠ Browser history (log of URLs visited)
Trail ≠ Breadcrumb (linear back-stack)
Trail ≠ Session recording (replay only)

Trail = Shareable, forkable, mergeable artifact of understanding
Trail = Evidence that grounds claims in observable exploration
Trail = Living document that multiple explorers navigate simultaneously
```

### 1.3 The Paradigm Recovery

| What We Lost | What We're Recovering |
|--------------|----------------------|
| Bush's associative trails | Trails as first-class artifacts |
| Nelson's bidirectional links | Hyperedge-based navigation |
| Shared knowledge building | Concurrent co-exploration |
| Evidence-grounded claims | ASHC commitment protocol |

---

## 2. The Axiological Foundation

**Why trails matter axiologically:**

1. **Agency requires evidence.** An agent that claims without evidence is performing, not reasoning.
2. **Collaboration requires shared ground.** Co-explorers need a common artifact to build upon.
3. **Safety requires bounds.** Unbounded exploration is unbounded risk.
4. **Trust requires transparency.** If you can't show your trail, you can't be trusted.

The Trail Protocol operationalizes Article V of the kgents Constitution: *"Trust is earned through demonstrated alignment."* Trails ARE the demonstration.

---

## 3. Data Structures

### 3.1 Trail (The Core Artifact)

```python
@dataclass
class Trail:
    """
    First-class knowledge artifact.

    Not ephemeral—persisted to Postgres via D-gent.
    Not solo—supports concurrent co-exploration.
    Not linear—supports fork/merge semantics.
    """

    id: UUID
    name: str
    created_by: Observer
    created_at: datetime

    # The exploration record
    steps: list[TrailStep]
    annotations: dict[int, Annotation]  # step_index → annotation

    # Concurrent exploration support
    explorers: set[Observer]            # Currently active explorers
    version: int                        # Optimistic locking

    # Fork/merge lineage
    forked_from: UUID | None
    merged_into: UUID | None

    # Evidence integration
    evidence: list[Evidence]
    commitments: list[Commitment]       # Claims made on this trail

    # Semantic handles
    topics: frozenset[str]              # Auto-extracted themes
    content_hash: str                   # For integrity verification
```

### 3.2 TrailStep (Atomic Navigation)

```python
@dataclass(frozen=True)
class TrailStep:
    """
    Single navigation action in a trail.

    Immutable once recorded. Forms the audit trail.
    """

    index: int
    timestamp: datetime
    explorer: Observer                  # Who took this step

    # Navigation
    source: ContextNode
    edge: str                           # Hyperedge followed
    destinations: frozenset[ContextNode]

    # Semantic enrichment
    reasoning: str | None               # Why this edge was followed
    embedding: list[float] | None       # For semantic search

    # Budget accounting
    budget_consumed: BudgetDelta
    loop_status: LoopStatus
```

### 3.3 TrailFork (Branching)

```python
@dataclass
class TrailFork:
    """
    Fork point in a trail, enabling divergent exploration.

    Like git branches—multiple explorers can diverge
    and later merge their findings.
    """

    id: UUID
    parent_trail: UUID
    fork_point: int                     # Step index where fork occurred
    child_trail: UUID
    forked_by: Observer
    forked_at: datetime

    # Merge state
    merged: bool = False
    merge_strategy: MergeStrategy | None = None
    merge_conflicts: list[MergeConflict] | None = None
```

### 3.4 TrailMerge (Synthesis)

```python
@dataclass
class TrailMerge:
    """
    Merge operation combining multiple trails.

    Strategies:
    - UNION: All steps from both trails
    - INTERSECTION: Only shared steps
    - REBASE: Replay one trail on top of another
    - SYNTHESIS: LLM-assisted semantic merge
    """

    id: UUID
    source_trails: list[UUID]
    target_trail: UUID
    strategy: MergeStrategy
    merged_by: Observer
    merged_at: datetime

    # Conflict resolution
    conflicts: list[MergeConflict]
    resolutions: dict[UUID, Resolution]
```

---

## 4. Semantic Navigation

### 4.1 Dual-Mode Semantic Matching

The Trail Protocol supports **two modes of semantic navigation**:

| Mode | Mechanism | Use Case |
|------|-----------|----------|
| **Vector** | Embedding similarity (cosine) | Fast, batch-friendly |
| **LLM** | Haiku/Sonnet reasoning | Nuanced, context-aware |

```python
class SemanticResolver:
    """
    Navigate by meaning, not just structure.

    Two complementary approaches:
    1. Vector embeddings for fast similarity
    2. LLM reasoning for nuanced semantic matching
    """

    async def resolve_vector(
        self,
        node: ContextNode,
        query: str,
        threshold: float = 0.8,
    ) -> list[ContextNode]:
        """
        Find semantically similar nodes via embedding.

        Fast, deterministic, good for "find similar" queries.
        """
        query_embedding = await self.embed(query)
        candidates = await self.index.search(query_embedding, k=20)
        return [c for c in candidates if c.similarity > threshold]

    async def resolve_llm(
        self,
        node: ContextNode,
        query: str,
        model: str = "haiku",  # or "sonnet" for complex queries
    ) -> list[ContextNode]:
        """
        Find semantically related nodes via LLM reasoning.

        Slower, but handles nuance:
        - "What implements this concept?"
        - "What contradicts this claim?"
        - "What's the architectural parent?"
        """
        context = await self._build_context(node)
        response = await self.llm.complete(
            model=model,
            prompt=f"""
            Given this context:
            {context}

            Find nodes that match: {query}

            Return AGENTESE paths.
            """,
        )
        return self._parse_paths(response)
```

### 4.2 Hybrid Resolution

```python
class HybridResolver:
    """
    Best of both worlds: vector speed + LLM nuance.

    Strategy:
    1. Vector search for candidates (fast)
    2. LLM reranking for relevance (accurate)
    """

    async def resolve(
        self,
        node: ContextNode,
        query: str,
        budget: NavigationBudget,
    ) -> list[ContextNode]:
        # Fast vector search
        candidates = await self.vector.resolve(node, query, threshold=0.6)

        if len(candidates) <= 3:
            return candidates

        # LLM reranking for precision
        if budget.allows_llm_call():
            return await self.llm.rerank(candidates, query, top_k=5)

        return candidates[:5]
```

---

## 5. Concurrent Co-Exploration

### 5.1 The Shared Workspace Model

Multiple explorers can navigate the same trail simultaneously:

```
┌─────────────────────────────────────────────────────────────┐
│                     SHARED TRAIL                            │
│                                                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                 │
│  │ Step 1  │───▶│ Step 2  │───▶│ Step 3  │                 │
│  │ (Kent)  │    │ (Agent) │    │ (Kent)  │                 │
│  └─────────┘    └─────────┘    └─────────┘                 │
│                      │              │                       │
│                      │              │                       │
│              ┌───────┴────┐   ┌────┴─────┐                 │
│              │  Fork A    │   │  Fork B   │                │
│              │  (Agent)   │   │  (Kent)   │                │
│              └────────────┘   └───────────┘                │
│                                                             │
│  [Kent: Viewing]  [Agent: Navigating Fork A]               │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Concurrency Semantics

```python
class ConcurrentTrail:
    """
    Trail with concurrent explorer support.

    Guarantees:
    - All explorers see consistent state (eventual consistency)
    - No lost updates (optimistic locking)
    - Fork/merge for divergent exploration
    """

    async def navigate(
        self,
        explorer: Observer,
        edge: str,
    ) -> NavigationResult:
        async with self.lock:
            # Check version hasn't changed
            current = await self.storage.get(self.id)
            if current.version != self.version:
                return NavigationResult.CONFLICT

            # Perform navigation
            step = await self._navigate(edge, explorer)

            # Persist with version bump
            self.steps.append(step)
            self.version += 1
            await self.storage.save(self)

            # Broadcast to other explorers
            await self.broadcast(TrailStepAdded(step))

            return NavigationResult.OK(step)

    async def fork(self, explorer: Observer, name: str) -> "Trail":
        """
        Create a branch for divergent exploration.

        The forked trail is independent—changes don't affect parent.
        Can be merged back later.
        """
        forked = Trail(
            id=uuid4(),
            name=name,
            created_by=explorer,
            forked_from=self.id,
            steps=list(self.steps),  # Copy current state
            explorers={explorer},
        )
        await self.storage.save(forked)
        return forked
```

### 5.3 Real-Time Sync

```python
class TrailSyncProtocol:
    """
    WebSocket-based real-time synchronization.

    Events:
    - STEP_ADDED: New navigation step
    - ANNOTATION_ADDED: Comment on step
    - EXPLORER_JOINED: New concurrent explorer
    - EXPLORER_LEFT: Explorer disconnected
    - FORK_CREATED: Branch created
    - MERGE_REQUESTED: Merge proposal
    """

    async def connect(self, trail_id: UUID, explorer: Observer):
        """Join a trail as concurrent explorer."""
        ws = await self.websocket_pool.connect(trail_id)

        # Announce presence
        await ws.send(ExplorerJoined(explorer))

        # Subscribe to updates
        async for event in ws:
            match event:
                case TrailStepAdded(step):
                    await self.on_step(step)
                case ForkCreated(fork):
                    await self.on_fork(fork)
                case MergeRequested(merge):
                    await self.on_merge_request(merge)
```

---

## 6. Persistence Layer

### 6.1 Postgres Schema (D-gent Integration)

```sql
-- Core trail table
CREATE TABLE trails (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    created_by UUID REFERENCES observers(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version INTEGER NOT NULL DEFAULT 1,
    forked_from UUID REFERENCES trails(id),
    merged_into UUID REFERENCES trails(id),
    content_hash TEXT NOT NULL,
    topics TEXT[] NOT NULL DEFAULT '{}',

    -- Optimistic locking
    CONSTRAINT version_positive CHECK (version > 0)
);

-- Trail steps (immutable once written)
CREATE TABLE trail_steps (
    id UUID PRIMARY KEY,
    trail_id UUID NOT NULL REFERENCES trails(id) ON DELETE CASCADE,
    index INTEGER NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    explorer_id UUID REFERENCES observers(id),

    -- Navigation data
    source_path TEXT NOT NULL,
    edge TEXT NOT NULL,
    destination_paths TEXT[] NOT NULL,

    -- Semantic data
    reasoning TEXT,
    embedding VECTOR(1536),  -- pgvector for semantic search

    -- Budget tracking
    budget_consumed JSONB NOT NULL,
    loop_status TEXT NOT NULL,

    UNIQUE (trail_id, index)
);

-- Annotations (comments on steps)
CREATE TABLE trail_annotations (
    id UUID PRIMARY KEY,
    trail_id UUID NOT NULL REFERENCES trails(id) ON DELETE CASCADE,
    step_index INTEGER NOT NULL,
    author_id UUID REFERENCES observers(id),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Fork relationships
CREATE TABLE trail_forks (
    id UUID PRIMARY KEY,
    parent_trail_id UUID NOT NULL REFERENCES trails(id),
    child_trail_id UUID NOT NULL REFERENCES trails(id),
    fork_point INTEGER NOT NULL,
    forked_by UUID REFERENCES observers(id),
    forked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    merged BOOLEAN NOT NULL DEFAULT FALSE,
    merge_strategy TEXT
);

-- Evidence linked to trails
CREATE TABLE trail_evidence (
    id UUID PRIMARY KEY,
    trail_id UUID NOT NULL REFERENCES trails(id) ON DELETE CASCADE,
    claim TEXT NOT NULL,
    strength TEXT NOT NULL,
    content JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Commitments (claims made on trails)
CREATE TABLE trail_commitments (
    id UUID PRIMARY KEY,
    trail_id UUID NOT NULL REFERENCES trails(id) ON DELETE CASCADE,
    claim TEXT NOT NULL,
    level TEXT NOT NULL,  -- tentative, moderate, strong, definitive
    evidence_ids UUID[] NOT NULL,
    committed_by UUID REFERENCES observers(id),
    committed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_trail_steps_trail_id ON trail_steps(trail_id);
CREATE INDEX idx_trail_steps_embedding ON trail_steps USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_trails_topics ON trails USING GIN (topics);
CREATE INDEX idx_trails_forked_from ON trails(forked_from);
```

### 6.2 D-gent Adapter

```python
class TrailStorageAdapter:
    """
    D-gent adapter for trail persistence.

    Durability > Performance:
    - All writes are transactional
    - Reads use connection pooling
    - Semantic search via pgvector
    """

    def __init__(self, storage_provider: StorageProvider):
        self.storage = storage_provider

    async def save_trail(self, trail: Trail) -> None:
        """Persist trail with all related data."""
        async with self.storage.transaction() as tx:
            await tx.execute("""
                INSERT INTO trails (id, name, created_by, version, content_hash, topics)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (id) DO UPDATE SET
                    version = EXCLUDED.version,
                    content_hash = EXCLUDED.content_hash,
                    topics = EXCLUDED.topics
            """, trail.id, trail.name, trail.created_by.id,
                trail.version, trail.content_hash, list(trail.topics))

            # Save new steps
            for step in trail.steps:
                await self._save_step(tx, trail.id, step)

    async def search_semantic(
        self,
        query_embedding: list[float],
        limit: int = 10,
    ) -> list[Trail]:
        """Find trails with semantically similar steps."""
        results = await self.storage.execute("""
            SELECT DISTINCT t.*
            FROM trails t
            JOIN trail_steps s ON t.id = s.trail_id
            ORDER BY s.embedding <=> $1
            LIMIT $2
        """, query_embedding, limit)
        return [Trail.from_row(r) for r in results]
```

---

## 7. AGENTESE Integration

### 7.1 Paths

```
self.trail.manifest           # Current trail state
self.trail.navigate           # Follow hyperedge
self.trail.fork               # Create branch
self.trail.merge              # Merge branches
self.trail.commit             # Commit a claim
self.trail.share              # Export for sharing
self.trail.replay             # Replay a saved trail
self.trail.search             # Semantic trail search
self.trail.explorers          # Who's currently exploring
```

### 7.2 Node Registration

```python
@node(
    path="self.trail",
    description="First-class knowledge artifacts with concurrent co-exploration",
    contracts={
        "manifest": Response(TrailManifestResponse),
        "navigate": Contract(NavigateRequest, NavigationResult),
        "fork": Contract(ForkRequest, Trail),
        "merge": Contract(MergeRequest, MergeResult),
        "commit": Contract(CommitRequest, CommitmentResult),
        "share": Response(SharedTrail),
        "replay": Contract(ReplayRequest, Trail),
        "search": Contract(SearchRequest, list[Trail]),
        "explorers": Response(list[Observer]),
    },
    effects=[
        "reads:trails",
        "writes:trails",
        "reads:embeddings",
        "invokes:llm",  # For semantic resolution
    ],
    affordances={
        "guest": ["manifest", "search"],
        "observer": ["manifest", "search", "replay"],
        "participant": ["*"],
        "architect": ["*"],
    },
    dependencies=("storage_provider", "embedding_service", "llm_service"),
)
class TrailNode:
    """AGENTESE interface to the Trail Protocol."""
```

---

## 8. Visual Projection

### 8.1 Trail Graph (The Joy Feature)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  TRAIL: "Auth Investigation"                     [Fork] [Merge] [Share] │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                    ┌──────────────────────────────────────────┐         │
│                    │  LIVE GRAPH                              │         │
│                    │                                          │         │
│                    │       ┌────┐                             │         │
│                    │       │root│                             │         │
│                    │       └──┬─┘                             │         │
│                    │          │ [contains]                    │         │
│                    │       ┌──┴──┐                            │         │
│                    │       │brain│                            │         │
│                    │       └──┬──┘                            │         │
│                    │     ┌────┴────┐                          │         │
│                    │     │ [tests] │ [imports]                │         │
│                    │     ▼         ▼                          │         │
│                    │  ┌─────┐  ┌──────┐                       │         │
│                    │  │tests│  │ poly │ ← Kent exploring      │         │
│                    │  └─────┘  └──────┘                       │         │
│                    │              │                           │         │
│                    │         [semantic: "state machine"]      │         │
│                    │              ▼                           │         │
│                    │          ┌──────┐                        │         │
│                    │          │ flux │ ← Agent exploring      │         │
│                    │          └──────┘                        │         │
│                    │                                          │         │
│                    └──────────────────────────────────────────┘         │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  REASONING TRACE                                                        │
│  ────────────────────────────────────────────────────────────────────── │
│  Step 3: Kent followed [imports] because "need to understand deps"      │
│  Step 4: Agent followed [semantic: state machine] via Haiku reasoning   │
│          → "flux implements continuous-time polynomial agents"          │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  EXPLORERS: 👤 Kent (viewing) • 🤖 Agent (navigating)                   │
│  EVIDENCE: 4 items (2 strong) • BUDGET: 67% remaining                   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Rich Data Integration

The visual projection integrates:

| Data Type | Source | Visualization |
|-----------|--------|---------------|
| **Trail steps** | Trail.steps | Node/edge graph |
| **Reasoning traces** | TrailStep.reasoning | Annotation panel |
| **Evidence** | Trail.evidence | Strength badges |
| **Explorer presence** | Trail.explorers | Avatar indicators |
| **Semantic links** | LLM resolution | Dashed edges with labels |
| **Budget** | NavigationBudget | Progress ring |
| **Loop warnings** | LoopDetector | Warning icons |

---

## 9. Laws

### 9.1 Trail Immutability

```
∀ step ∈ trail.steps:
    once_persisted(step) → immutable(step)
```

Steps cannot be modified after persistence. Annotations can be added, but steps are append-only.

### 9.2 Fork Independence

```
fork(trail, point) → new_trail where:
    new_trail.steps[0:point] = trail.steps[0:point]
    ∀ changes to new_trail: trail.unaffected
    ∀ changes to trail after point: new_trail.unaffected
```

Forks are independent—changes don't propagate until explicit merge.

### 9.3 Merge Associativity

```
merge(merge(A, B), C) ≡ merge(A, merge(B, C))
```

Merge order doesn't affect final result (for compatible merges).

### 9.4 Evidence Monotonicity

```
evidence(trail ++ step) ⊇ evidence(trail)
```

Evidence can only grow during exploration.

### 9.5 Commitment Irreversibility

```
commit(claim, STRONG) → ¬commit(claim, WEAK) later
```

Cannot downgrade commitment level.

### 9.6 Explorer Visibility

```
∀ explorer ∈ trail.explorers:
    explorer.sees(trail.steps) = trail.steps  # All see same state
```

Concurrent explorers see consistent state.

---

## 10. Constitutional Alignment

| Constitution Article | Trail Protocol Implementation |
|----------------------|-------------------------------|
| **I. Symmetric Agency** | Same protocol for Kent and agents |
| **II. Adversarial Cooperation** | Fork/merge enables divergent exploration |
| **III. Supersession Rights** | Higher commitment supersedes lower |
| **IV. Disgust Veto** | Human can halt any exploration |
| **V. Trust Accumulation** | Trails ARE the evidence of alignment |
| **VI. Fusion as Goal** | Merged trails produce shared understanding |
| **VII. Amendment** | Trail protocol itself can evolve |

---

## 11. Related Specs

- `spec/protocols/exploration-harness.md` — Safety layer (budget, loops, evidence)
- `spec/protocols/typed-hypergraph.md` — Navigation substrate
- `spec/services/witness.md` — Sibling artifact (experience crystals)
- `spec/agents/d-gent.md` — Persistence provider

---

## 12. Sources & Heritage

- [Vannevar Bush, "As We May Think" (1945)](https://en.wikipedia.org/wiki/As_We_May_Think) — Original Memex vision
- [DARPA Memex Program](https://www.darpa.mil/research/programs/memex) — Modern search capabilities
- [Blockchain Decision Provenance](https://www.mdpi.com/2624-831X/6/3/37) — Immutable audit trails
- [CMU COHUMAIN Framework](https://www.cmu.edu/news/stories/archives/2025/october/researchers-explore-how-ai-can-strengthen-not-replace-human-collaboration) — Human-AI collaboration
- [CHI 2025 CoExploreDS](https://dl.acm.org/doi/10.1145/3706598.3713869) — Collaborative design exploration
- [International AI Safety Report 2025](https://internationalaisafetyreport.org/publication/international-ai-safety-report-2025) — Bounded agent safety

---

*"The web gave us hyperlinks but lost the trails. The Trail Protocol recovers them—not as history, but as living, shareable, collaborative knowledge artifacts."*

---

**Filed:** 2025-12-22
**Voice anchor:** *"Daring, bold, creative, opinionated but not gaudy"*

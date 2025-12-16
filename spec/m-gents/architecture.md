# M-gent Architecture: Intelligent Memory Management

> *"M-gent is gardening. It cultivates, prunes, and composts data into memory."*

**Status**: REWRITE — This spec supersedes all prior M-gent documentation.

---

## Purpose

M-gent provides **intelligent memory management** layered on top of D-gent. While D-gent handles raw persistence (plumbing), M-gent handles what to remember, what to forget, how to organize, and when to consolidate.

The key insight: **memory is not storage**. Storage is bytes with IDs. Memory is meaning with lifecycle.

---

## The Core Abstraction

```python
@dataclass
class Memory:
    """
    A memory is a datum enriched with semantic meaning and lifecycle.

    Built on top of D-gent Datum but adds:
    - Semantic embedding for associative recall
    - Resolution (fidelity that can degrade gracefully)
    - Lifecycle state (active → dormant → composting)
    - Relevance score (decays over time unless reinforced)
    """
    datum_id: str              # Reference to underlying D-gent Datum
    embedding: list[float]     # Semantic vector (for associative recall)
    resolution: float          # 0.0 to 1.0 (graceful degradation)
    lifecycle: Lifecycle       # ACTIVE | DORMANT | DREAMING | COMPOSTING
    relevance: float           # 0.0 to 1.0 (decays without reinforcement)
    last_accessed: float       # Unix timestamp
    access_count: int          # Reinforcement counter

class Lifecycle(Enum):
    ACTIVE = "active"          # Currently in working memory
    DORMANT = "dormant"        # Saved, not actively used
    DREAMING = "dreaming"      # Being reorganized/consolidated
    COMPOSTING = "composting"  # Gracefully degrading (but recoverable)
```

---

## The Memory Lifecycle

```
                    ┌─────────┐
              ┌────▶│ ACTIVE  │◀────┐
              │     └────┬────┘     │
              │          │          │
          recall      timeout    reinforce
              │          │          │
              │     ┌────▼────┐     │
              └─────│ DORMANT │─────┘
                    └────┬────┘
                         │
                    consolidate
                         │
                    ┌────▼────┐
                    │DREAMING │ (background reorganization)
                    └────┬────┘
                         │
                      forget
                         │
                    ┌────▼─────┐
                    │COMPOSTING│ (graceful degradation)
                    └──────────┘
```

**Active**: In working memory, high resolution, frequently accessed.
**Dormant**: Saved to D-gent, normal resolution, occasionally accessed.
**Dreaming**: Being reorganized during "sleep" cycles. Not accessible.
**Composting**: Resolution degrading. Still retrievable but lossy.

---

## The Protocol

```python
class MgentProtocol(Protocol):
    """
    The interface for intelligent memory management.

    Built on top of DgentProtocol.
    """

    # --- Core Operations ---

    async def remember(
        self,
        content: bytes,
        embedding: list[float] | None = None,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """
        Store content as a memory.

        If embedding not provided, will be computed via L-gent.
        Returns memory ID (same as underlying datum ID).
        """
        ...

    async def recall(
        self,
        cue: str | list[float],
        limit: int = 5,
        threshold: float = 0.5,
    ) -> list[Memory]:
        """
        Associative recall by semantic similarity.

        cue: Text query or embedding vector
        Returns memories sorted by relevance.
        """
        ...

    async def forget(self, memory_id: str) -> bool:
        """
        Begin graceful forgetting (transition to COMPOSTING).

        Memory is not deleted, just degraded over time.
        """
        ...

    async def cherish(self, memory_id: str) -> bool:
        """
        Pin memory from forgetting (high relevance, won't compost).
        """
        ...

    # --- Lifecycle Operations ---

    async def consolidate(self) -> ConsolidationReport:
        """
        Run consolidation cycle ("sleep").

        - Moves DORMANT → DREAMING
        - Reorganizes associations
        - Demotes low-relevance memories
        - Returns report of changes
        """
        ...

    async def wake(self) -> None:
        """
        End consolidation, return DREAMING → DORMANT.
        """
        ...

    # --- Introspection ---

    async def status(self) -> MemoryStatus:
        """Get current memory state."""
        ...

    async def by_lifecycle(self, lifecycle: Lifecycle) -> list[Memory]:
        """Get memories in a specific lifecycle state."""
        ...
```

---

## Associative Recall

M-gent uses semantic embeddings for associative (not exact-match) recall:

```python
class AssociativeMemory:
    """
    Memory with semantic similarity search.

    Uses L-gent for embeddings if available, otherwise falls back
    to simple hash-based pseudo-embeddings (deterministic but not semantic).
    """

    def __init__(self, dgent: DgentProtocol, embedder: Embedder | None = None):
        self.dgent = dgent
        self.embedder = embedder or HashEmbedder()
        self._index: dict[str, list[float]] = {}  # memory_id → embedding

    async def remember(self, content: bytes, **kwargs) -> str:
        # Store raw data via D-gent
        datum = Datum(
            id=uuid4().hex,
            content=content,
            created_at=time.time(),
            causal_parent=kwargs.get("causal_parent"),
            metadata=kwargs.get("metadata", {}),
        )
        datum_id = await self.dgent.put(datum)

        # Compute embedding
        embedding = kwargs.get("embedding")
        if embedding is None:
            embedding = await self.embedder.embed(content.decode("utf-8", errors="ignore"))

        # Index for recall
        self._index[datum_id] = embedding

        return datum_id

    async def recall(self, cue: str | list[float], limit: int = 5, threshold: float = 0.5) -> list[Memory]:
        # Get cue embedding
        if isinstance(cue, str):
            cue_embedding = await self.embedder.embed(cue)
        else:
            cue_embedding = cue

        # Find similar memories
        scored = []
        for memory_id, embedding in self._index.items():
            similarity = cosine_similarity(cue_embedding, embedding)
            if similarity >= threshold:
                scored.append((memory_id, similarity))

        # Sort by similarity, take top N
        scored.sort(key=lambda x: x[1], reverse=True)
        top_ids = [mid for mid, _ in scored[:limit]]

        # Fetch full memories
        return [await self._load_memory(mid) for mid in top_ids]
```

---

## Graceful Degradation (Resolution)

Memories degrade gracefully, not catastrophically:

```python
class GracefulMemory:
    """
    Memory with resolution-based graceful degradation.

    Resolution 1.0: Full fidelity (all details preserved)
    Resolution 0.5: Summary only (gist preserved, details lost)
    Resolution 0.1: Title only (existence known, content forgotten)
    Resolution 0.0: Fully composted (only causal trace remains)
    """

    async def degrade(self, memory_id: str, factor: float = 0.5) -> Memory:
        """
        Reduce resolution by factor.

        Content is summarized/compressed, not deleted.
        """
        memory = await self._load_memory(memory_id)

        new_resolution = memory.resolution * factor
        if new_resolution < 0.1:
            # Minimal resolution: just keep title/summary
            new_content = self._extract_title(memory)
        elif new_resolution < 0.5:
            # Low resolution: summarize
            new_content = await self._summarize(memory)
        else:
            # Medium resolution: compress
            new_content = self._compress(memory)

        # Update datum with degraded content
        await self.dgent.put(Datum(
            id=memory_id,
            content=new_content,
            created_at=memory.datum.created_at,
            causal_parent=memory.datum.causal_parent,
            metadata={**memory.datum.metadata, "resolution": str(new_resolution)},
        ))

        return memory.with_resolution(new_resolution)
```

---

## Consolidation ("Sleep")

M-gent periodically enters a consolidation phase:

```python
class ConsolidationEngine:
    """
    The "sleep" cycle for memory reorganization.

    During consolidation:
    1. Low-relevance memories are demoted (DORMANT → COMPOSTING)
    2. Associations are strengthened between related memories
    3. Duplicate/similar memories are merged
    4. Embeddings are recomputed with updated context
    """

    async def consolidate(self) -> ConsolidationReport:
        # Mark all DORMANT as DREAMING (not accessible during consolidation)
        dreaming = await self._transition_dormant_to_dreaming()

        # Compute relevance decay
        demoted = await self._apply_relevance_decay(dreaming)

        # Find and merge duplicates
        merged = await self._merge_similar(dreaming, threshold=0.95)

        # Strengthen cross-references
        strengthened = await self._strengthen_associations(dreaming)

        # Return DREAMING → DORMANT
        await self._transition_dreaming_to_dormant()

        return ConsolidationReport(
            dreaming_count=len(dreaming),
            demoted_count=len(demoted),
            merged_count=len(merged),
            strengthened_count=len(strengthened),
        )
```

---

## AGENTESE Paths

M-gent exposes these paths under `self.memory.*`:

| Path | Description |
|------|-------------|
| `self.memory.remember[content]` | Store with semantic indexing |
| `self.memory.recall[cue]` | Associative retrieval |
| `self.memory.forget[id]` | Begin graceful forgetting |
| `self.memory.cherish[id]` | Pin from forgetting |
| `self.memory.consolidate` | Trigger sleep cycle |
| `self.memory.status` | Get memory state |
| `self.memory.lifecycle[state]` | List memories by lifecycle |

---

## Relationship to D-gent

```
┌─────────────────────────────────────────────────────────┐
│                      M-gent                              │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Semantic Index    │  Lifecycle Manager         │    │
│  │  (embeddings)      │  (consolidation, decay)    │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
│                          ▼                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │                    D-gent                        │    │
│  │  (raw storage: put, get, delete, list, chain)   │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

**Key principle**: M-gent NEVER bypasses D-gent. All data flows through D-gent's projection lattice.

---

## Relationship to K-gent (Soul)

K-gent uses M-gent for identity continuity:

```python
class SoulMemory:
    """
    K-gent's use of M-gent for identity.

    The soul needs:
    - Persistent beliefs (high relevance, cherished)
    - Session context (normal relevance, may compost)
    - Creative seeds (low relevance, experiments)
    """

    def __init__(self, mgent: MgentProtocol):
        self.mgent = mgent

    async def remember_belief(self, belief: str) -> str:
        """Store a core belief (cherished, won't forget)."""
        memory_id = await self.mgent.remember(
            belief.encode(),
            metadata={"type": "belief"},
        )
        await self.mgent.cherish(memory_id)
        return memory_id

    async def recall_context(self, topic: str) -> list[Memory]:
        """Recall memories relevant to current topic."""
        return await self.mgent.recall(topic, limit=10)
```

---

## Relationship to Tracing

M-gent integrates with TraceMonoid for causal memory:

```python
class TracedMemory:
    """
    Memory with full causal tracing.

    Every memory operation generates a trace event.
    Traces can be used for:
    - Debugging ("why did I remember this?")
    - Accountability ("what influenced this decision?")
    - Recollection ("what happened before X?")
    """

    def __init__(self, mgent: MgentProtocol, trace: TraceMonoid):
        self.mgent = mgent
        self.trace = trace

    async def remember(self, content: bytes, **kwargs) -> str:
        memory_id = await self.mgent.remember(content, **kwargs)

        # Record trace event
        self.trace.append_mut(
            Event(
                id=uuid4().hex,
                source="mgent",
                timestamp=time.time(),
                payload={"action": "remember", "memory_id": memory_id},
            ),
            depends_on=kwargs.get("trace_depends_on"),
        )

        return memory_id
```

---

## What M-gent Is NOT

- **Not raw storage** — That's D-gent's job
- **Not a vector database** — Embeddings are for recall, not the storage format
- **Not schema enforcement** — Schema is D-gent's lens concern
- **Not real-time** — Consolidation happens in background
- **Not deterministic** — Relevance decay introduces intentional entropy

---

## See Also

- `spec/d-gents/architecture.md` — Raw data persistence (M-gent depends on this)
- `spec/protocols/data-bus.md` — Reactive data flow
- `spec/k-gents/soul.md` — Identity continuity via M-gent

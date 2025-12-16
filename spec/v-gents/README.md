# V-gents: Vector Agents

**Genus**: V (Vector)
**Theme**: Semantic geometry, similarity search, embedding infrastructure
**Motto**: *"Distance is meaning."*

> **Note**: This specification supersedes the previous V-gent (Validator) spec.
> Validator functionality has been absorbed by T-gents (Testing) and K-gent (Soul/Gatekeeper).

---

## Overview

V-gents are the **geometric infrastructure** of the kgents ecosystem. They provide vector storage and similarity search as a dedicated service, enabling semantic operations across all other agents.

The metaphor: If D-gent is the **filing cabinet** (raw storage), V-gent is the **spatial arrangement** of files—organizing by meaning rather than label, so that similar things are near each other.

---

## Philosophy

> "Meaning lives in geometry. Vectors are coordinates in semantic space."

V-gents synthesize a single theoretical foundation:

### Metric Space (Geometric Structure)

**Core Morphism**: `(Vector, Vector) → Distance`

All semantic operations reduce to distance calculations. "Is this document relevant?" becomes "How far is this vector from the query?" V-gent makes this explicit and reusable.

---

## The Joy Factor: Discovery

V-gent enables **serendipitous discovery**:

```
User: "I want to understand category theory."
V-gent: Returns vectors near the query, including:
  - Category theory papers (obvious)
  - Functional programming guides (connected)
  - Type theory lectures (related)
  - Algebraic topology notes (surprising but relevant)
```

The similarity search doesn't just find exact matches—it surfaces **conceptually adjacent** content the user didn't know to ask for.

---

## Core Concepts

### The Separation of Concerns

Before V-gent, vector operations were embedded in L-gent and M-gent:

| Agent | Before | After |
|-------|--------|-------|
| L-gent | Catalog + Vectors | Catalog (uses V-gent) |
| M-gent | Memory + Vectors | Memory (uses V-gent) |
| V-gent | (didn't exist) | Pure vector operations |

**Key insight**: Vectors are infrastructure. Every agent that needs similarity search should use V-gent, not reinvent it.

### The VgentProtocol

Seven methods. That's the entire interface:

```python
class VgentProtocol(Protocol):
    # Write
    async def add(id, embedding, metadata) -> str
    async def add_batch(entries) -> list[str]
    async def remove(id) -> bool
    async def clear() -> int

    # Read
    async def get(id) -> VectorEntry | None
    async def search(query, limit, filters, threshold) -> list[SearchResult]
    async def count() -> int
```

### The Projection Lattice

Like D-gent, V-gent has a projection lattice of backends:

```
    Qdrant (10M+ vectors, distributed)
       ↑
    pgvector (100K-1M, SQL filtering)
       ↑
    D-gent (10K-100K, local persistence)
       ↑
    Memory (< 10K, ephemeral)
```

Graceful degradation: if Qdrant is unavailable, fall back to pgvector → D-gent → Memory.

---

## Relationship to Other Agents

### L-gent (Library)

**V-gent is L-gent's search engine**:
- L-gent manages catalog metadata, lineage, lattice relationships
- V-gent handles the vector index for semantic search
- L-gent asks V-gent: "Find catalog entries similar to this query"

```python
# L-gent uses V-gent
class SemanticCatalog:
    def __init__(self, vgent: VgentProtocol):
        self.vgent = vgent

    async def search(self, intent: str) -> list[CatalogEntry]:
        embedding = await self.embedder.embed(intent)
        results = await self.vgent.search(embedding, limit=10)
        return [self.registry[r.id] for r in results]
```

### M-gent (Memory)

**V-gent is M-gent's recall mechanism**:
- M-gent manages memory lifecycle (active, dormant, composting)
- V-gent provides the similarity index for associative recall
- M-gent asks V-gent: "Find memories similar to this cue"

```python
# M-gent uses V-gent
class AssociativeMemory:
    def __init__(self, vgent: VgentProtocol, dgent: DgentProtocol):
        self.vgent = vgent
        self.dgent = dgent

    async def recall(self, cue: str) -> list[Memory]:
        embedding = await self.embedder.embed(cue)
        results = await self.vgent.search(embedding)
        return [await self._load_memory(r.id) for r in results]
```

### D-gent (Data)

**V-gent can use D-gent as a backend**:
- D-gent provides projection-agnostic persistence
- V-gent's DgentVectorBackend stores vectors as Datum
- This gives V-gent automatic graceful degradation

```python
# V-gent uses D-gent
class DgentVectorBackend(VgentProtocol):
    def __init__(self, dgent: DgentProtocol):
        self.dgent = dgent
        self._index: dict[str, tuple] = {}  # In-memory for search
```

### K-gent (Soul)

**V-gent enables K-gent's belief retrieval**:
- K-gent stores beliefs and preferences
- V-gent indexes them for topic-based recall
- K-gent asks: "What do I believe about X?"

---

## Success Criteria

A V-gent is well-designed if:

- ✓ **Fast**: Search latency < 100ms for interactive use
- ✓ **Accurate**: High recall and precision for similarity queries
- ✓ **Scalable**: Handles dataset growth without degradation
- ✓ **Backend-agnostic**: Same API regardless of storage
- ✓ **Filterable**: Supports metadata-based filtering
- ✓ **Composable**: Works with any embedder

---

## Anti-Patterns

V-gents must **never**:

1. ❌ Generate embeddings (that's the embedder's job)
2. ❌ Manage meaning (that's L-gent's or M-gent's job)
3. ❌ Store raw content (that's D-gent's job)
4. ❌ Own lifecycle state (that's M-gent's job)
5. ❌ Enforce schema (vectors are schema-free)

---

## Specifications

| Document | Description |
|----------|-------------|
| [core.md](core.md) | VgentProtocol, Embedding, SearchResult |
| [backends.md](backends.md) | Memory, D-gent, pgvector, Qdrant backends |
| [integrations.md](integrations.md) | L-gent, M-gent, D-gent integration |

---

## Design Principles Alignment

### Tasteful
V-gent does one thing well: vector operations. No scope creep.

### Curated
Limited API surface (7 methods). Clear boundaries with other agents.

### Ethical
Transparent distance calculations. No hidden magic.

### Joy-Inducing
Enables serendipitous discovery through similarity search.

### Composable
Pure infrastructure—any agent can use V-gent.

### Heterarchical
V-gent serves multiple masters (L-gent, M-gent, K-gent) equally.

### Generative
The projection lattice generates appropriate backends from environment.

---

## Example: Semantic Search Pipeline

```python
# Setup
embedder = OpenAIEmbedder(model="text-embedding-3-small")
vgent = VgentRouter(dimension=1536)

# Index documents
for doc in documents:
    embedding = await embedder.embed(doc.content)
    await vgent.add(doc.id, embedding, {"type": doc.type, "author": doc.author})

# Search
query_embedding = await embedder.embed("machine learning optimization")
results = await vgent.search(
    query=query_embedding,
    limit=10,
    filters={"type": "paper"},
    threshold=0.7,
)

# Results include semantically similar papers, even if they
# don't contain the exact phrase "machine learning optimization"
```

---

## Vision

V-gent transforms semantic operations from **scattered implementations** into **shared infrastructure**:

- **For L-gent**: A dedicated search backend, not an embedded concern
- **For M-gent**: A similarity engine for associative recall
- **For K-gent**: A belief index for topic-based retrieval
- **For the Ecosystem**: The geometric foundation that enables meaning-based discovery

The ultimate test: Can any agent that needs similarity search just use V-gent? Is the API clear enough that no one needs to understand the backend?

V-gent makes the answer "yes" to both.

---

*"In semantic space, meaning is proximity."*

---

## See Also

- [core.md](core.md) — Core protocol and types
- [backends.md](backends.md) — Backend implementations
- [integrations.md](integrations.md) — Cross-agent integration
- [../l-gents/](../l-gents/) — Library (primary consumer)
- [../m-gents/](../m-gents/) — Memory (primary consumer)
- [../d-gents/](../d-gents/) — Data persistence (backend option)

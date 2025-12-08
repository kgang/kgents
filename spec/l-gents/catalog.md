# L-gent Catalog: Registry & Indexing

**Purpose**: Define the three-layer catalog architecture and indexing strategy for ecosystem artifacts.

---

## Overview

The catalog is L-gent's **persistent knowledge state**—a structured representation of everything the ecosystem knows about its artifacts. It's organized in three layers that answer three fundamental questions:

| Layer | Question | Structure |
|-------|----------|-----------|
| **Registry** | What exists? | Flat index of artifacts |
| **Lineage** | Where did it come from? | Directed acyclic graph of ancestry |
| **Lattice** | How does it fit? | Partial order of type compatibility |

## Layer 1: Registry (What Exists?)

The registry is an **indexed collection** of catalog entries. Each entry describes one artifact.

### Entry Schema

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

class EntityType(Enum):
    """Types of artifacts L-gent tracks."""
    AGENT = "agent"           # Executable agents (A → B morphisms)
    CONTRACT = "contract"     # Interface definitions (type + invariants)
    MEMORY = "memory"         # Session/context records
    SPEC = "spec"             # Specification documents
    TEST = "test"             # Test artifacts
    TEMPLATE = "template"     # F-gent forge templates
    PATTERN = "pattern"       # Reusable design patterns

class Status(Enum):
    """Lifecycle status of an artifact."""
    ACTIVE = "active"         # Available for use
    DEPRECATED = "deprecated" # Still works, not recommended
    RETIRED = "retired"       # No longer functional
    DRAFT = "draft"           # Work in progress

@dataclass
class CatalogEntry:
    """A single entry in the L-gent registry."""

    # Identity
    id: str                           # Unique, immutable identifier
    entity_type: EntityType           # What kind of artifact
    name: str                         # Human-readable name
    version: str                      # Semantic version (e.g., "1.2.3")

    # Description (for semantic search)
    description: str                  # Natural language purpose
    keywords: list[str]               # Manual tags for discovery
    embedding: list[float] | None     # Auto-generated semantic vector

    # Provenance
    author: str                       # Creator identifier
    created_at: datetime
    updated_at: datetime
    forged_by: str | None             # F-gent instance that created it
    forged_from: str | None           # Intent/prompt that spawned it

    # Type information (for lattice)
    input_type: str | None            # For agents: input type signature
    output_type: str | None           # For agents: output type signature
    contracts_implemented: list[str]  # Contracts this satisfies
    contracts_required: list[str]     # Contracts this needs

    # Graph relationships (for lineage)
    relationships: dict[str, list[str]] = field(default_factory=dict)
    # Relationship types:
    # - "successor_to": Previous versions
    # - "forked_from": Parent artifact (branching)
    # - "depends_on": Runtime dependencies
    # - "tested_by": Associated test artifacts
    # - "documented_by": Associated spec documents
    # - "composes_with": Known good composition partners

    # Health metrics
    status: Status = Status.ACTIVE
    usage_count: int = 0
    success_rate: float = 1.0         # 0.0 to 1.0
    last_used: datetime | None = None
    last_error: str | None = None

    # Deprecation info
    deprecation_reason: str | None = None
    deprecated_in_favor_of: str | None = None
```

### Registry Operations

```python
class Registry:
    """Layer 1: What exists in the ecosystem."""

    async def register(self, entry: CatalogEntry) -> str:
        """
        Add or update an artifact in the registry.

        Steps:
        1. Validate entry (required fields, type consistency)
        2. Generate embedding if description changed
        3. Update indices (keyword, type, author)
        4. Trigger relationship updates in lineage layer
        5. Return entry ID

        Idempotent: Re-registering same ID updates existing entry.
        """
        ...

    async def get(self, id: str) -> CatalogEntry | None:
        """Retrieve entry by ID. O(1) lookup."""
        ...

    async def exists(self, id: str) -> bool:
        """Check existence without retrieving."""
        ...

    async def list(
        self,
        entity_type: EntityType | None = None,
        status: Status | None = None,
        author: str | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[CatalogEntry]:
        """List entries with filters. For bulk operations."""
        ...

    async def deprecate(
        self,
        id: str,
        reason: str,
        replacement: str | None = None
    ) -> None:
        """
        Mark artifact as deprecated.

        Does NOT delete—artifacts are immutable for lineage integrity.
        """
        ...

    async def update_metrics(
        self,
        id: str,
        success: bool,
        error: str | None = None
    ) -> None:
        """
        Record usage outcome. Called after each invocation.

        Updates: usage_count, success_rate, last_used, last_error
        """
        ...
```

### Indexing Strategy

The registry maintains multiple indices for fast retrieval:

```
┌─────────────────────────────────────────────────────────────┐
│                    Registry Indices                          │
├─────────────────┬───────────────────────────────────────────┤
│ Primary Index   │ id → CatalogEntry                         │
│ (Hash Map)      │ O(1) lookup by ID                         │
├─────────────────┼───────────────────────────────────────────┤
│ Type Index      │ entity_type → [id, id, ...]              │
│ (Inverted)      │ "Find all agents"                         │
├─────────────────┼───────────────────────────────────────────┤
│ Author Index    │ author → [id, id, ...]                   │
│ (Inverted)      │ "Find Kent's artifacts"                   │
├─────────────────┼───────────────────────────────────────────┤
│ Keyword Index   │ keyword → [id, id, ...]                  │
│ (Inverted)      │ "Find tagged 'summarization'"             │
├─────────────────┼───────────────────────────────────────────┤
│ Contract Index  │ contract_id → {implements: [], requires:[]}│
│ (Bipartite)     │ "Who implements/requires TextOutput?"     │
├─────────────────┼───────────────────────────────────────────┤
│ Version Index   │ base_name → [(version, id), ...]         │
│ (Sorted)        │ "Get latest NewsParser"                   │
└─────────────────┴───────────────────────────────────────────┘
```

## Layer 2: Lineage (Where Did It Come From?)

See [lineage.md](lineage.md) for full specification.

**Summary**: A directed acyclic graph where:
- **Nodes** = Artifact IDs
- **Edges** = Relationships (successor_to, forked_from, depends_on)
- **Properties** = Timestamp, author, context

Enables queries like:
- "Show me the evolution history of Summarizer"
- "What depends on BaseNetworkAgent?"
- "Find all artifacts forged from 'summarization' intent"

## Layer 3: Lattice (How Does It Fit?)

See [lattice.md](lattice.md) for full specification.

**Summary**: A partial order over types where:
- **Elements** = Types (input/output signatures, contracts)
- **Ordering** = Subtyping / compatibility
- **Operations** = Meet (greatest lower bound), Join (least upper bound)

Enables queries like:
- "Can AgentA's output connect to AgentB's input?"
- "Find all agents that satisfy Contract C or something more specific"
- "What's the most general type that subsumes both A and B?"

## Persistence Architecture

L-gent's catalog is backed by D-gents:

```python
class Catalog:
    """Complete L-gent knowledge state."""

    def __init__(self, storage_path: Path):
        # Layer 1: Registry
        self.registry = PersistentAgent[RegistryState](
            path=storage_path / "registry.json",
            schema=RegistryState
        )

        # Layer 2: Lineage (graph storage)
        self.lineage = GraphAgent[str, Relationship](
            path=storage_path / "lineage.jsonl"
        )

        # Layer 3: Lattice (type relationships)
        self.lattice = PersistentAgent[LatticeState](
            path=storage_path / "lattice.json",
            schema=LatticeState
        )

        # Semantic index (for query layer)
        self.vectors = VectorAgent[CatalogEmbedding](
            path=storage_path / "embeddings.db",
            dimension=768
        )

@dataclass
class RegistryState:
    """Serializable registry state."""
    entries: dict[str, CatalogEntry]
    indices: RegistryIndices
    version: str
    last_updated: datetime

@dataclass
class LatticeState:
    """Serializable lattice state."""
    types: dict[str, TypeNode]
    subtype_edges: list[tuple[str, str]]  # (subtype, supertype)
    version: str
```

### Consistency Guarantees

**Atomicity**: Updates to all three layers happen in transaction:

```python
async def register_with_lineage(
    self,
    entry: CatalogEntry,
    parent_id: str | None = None
) -> str:
    """Atomic registration with lineage update."""

    async with self.transaction():
        # 1. Add to registry
        await self.registry.save(
            self._add_entry(entry)
        )

        # 2. Update lineage if parent exists
        if parent_id:
            await self.lineage.add_edge(
                parent_id, entry.id,
                relationship="successor_to"
            )

        # 3. Update lattice with type info
        if entry.input_type and entry.output_type:
            await self.lattice.register_morphism(
                entry.id,
                entry.input_type,
                entry.output_type
            )

        # 4. Index embedding
        if entry.embedding:
            await self.vectors.store(
                id=entry.id,
                vector=entry.embedding,
                metadata={"name": entry.name, "type": entry.entity_type}
            )

    return entry.id
```

**Eventual Consistency**: Embeddings may lag behind text changes:

```python
async def reindex_embeddings(self) -> int:
    """Background job to sync embeddings with descriptions."""
    outdated = []
    for entry in await self.registry.list():
        if entry.embedding is None or self._embedding_stale(entry):
            outdated.append(entry)

    for entry in outdated:
        entry.embedding = await self._generate_embedding(entry.description)
        await self.registry.update(entry)
        await self.vectors.store(entry.id, entry.embedding)

    return len(outdated)
```

## Catalog Events

L-gent emits events for ecosystem coordination:

```python
@dataclass
class CatalogEvent:
    """Base class for catalog events."""
    timestamp: datetime
    catalog_version: str

@dataclass
class ArtifactRegistered(CatalogEvent):
    """New artifact added to catalog."""
    artifact_id: str
    entity_type: EntityType
    author: str

@dataclass
class ArtifactDeprecated(CatalogEvent):
    """Artifact marked as deprecated."""
    artifact_id: str
    reason: str
    replacement_id: str | None

@dataclass
class LineageUpdated(CatalogEvent):
    """New relationship added to lineage graph."""
    source_id: str
    target_id: str
    relationship: str

@dataclass
class CompatibilityChanged(CatalogEvent):
    """Lattice structure modified."""
    affected_types: list[str]
    change_type: str  # "subtype_added", "type_registered", etc.
```

Subscribers can react to changes:

```python
# F-gent subscribes to deprecations
@l_gent.on(ArtifactDeprecated)
async def notify_dependents(event: ArtifactDeprecated):
    dependents = await l_gent.lineage.get_dependents(event.artifact_id)
    for dep in dependents:
        await notify(f"Dependency {event.artifact_id} deprecated: {event.reason}")
```

## Catalog Maintenance

### Garbage Collection

Artifacts are never deleted (lineage integrity), but can be cleaned:

```python
async def cleanup_catalog(self) -> CleanupReport:
    """Identify artifacts that may need attention."""

    report = CleanupReport()

    # Find unused artifacts
    for entry in await self.registry.list():
        if entry.usage_count == 0 and entry.age > timedelta(days=90):
            report.unused.append(entry.id)

    # Find failing artifacts
    for entry in await self.registry.list():
        if entry.success_rate < 0.5 and entry.usage_count > 10:
            report.failing.append(entry.id)

    # Find orphaned artifacts (no lineage connections)
    all_ids = {e.id for e in await self.registry.list()}
    connected_ids = set(await self.lineage.all_nodes())
    report.orphaned = list(all_ids - connected_ids)

    return report
```

### Integrity Checks

Validate catalog consistency:

```python
async def verify_integrity(self) -> list[IntegrityIssue]:
    """Check catalog for inconsistencies."""
    issues = []

    # 1. Registry-Lineage consistency
    for entry in await self.registry.list():
        for rel_type, targets in entry.relationships.items():
            for target in targets:
                if not await self.lineage.has_edge(entry.id, target, rel_type):
                    issues.append(IntegrityIssue(
                        type="missing_lineage_edge",
                        source=entry.id,
                        target=target,
                        relationship=rel_type
                    ))

    # 2. Lattice-Registry consistency
    for entry in await self.registry.list():
        if entry.entity_type == EntityType.AGENT:
            if entry.input_type and not await self.lattice.type_exists(entry.input_type):
                issues.append(IntegrityIssue(
                    type="unknown_input_type",
                    source=entry.id,
                    details=entry.input_type
                ))

    # 3. Vector index completeness
    indexed_ids = set(await self.vectors.all_ids())
    for entry in await self.registry.list():
        if entry.description and entry.id not in indexed_ids:
            issues.append(IntegrityIssue(
                type="missing_embedding",
                source=entry.id
            ))

    return issues
```

## Performance Characteristics

| Operation | Complexity | Notes |
|-----------|------------|-------|
| `get(id)` | O(1) | Hash map lookup |
| `register()` | O(log n) | Index updates |
| `list(type=X)` | O(k) | k = matching entries |
| `find_by_keyword()` | O(k) | Inverted index |
| `semantic_search()` | O(log n) | Vector ANN search |
| `lineage_ancestors()` | O(d) | d = depth to root |
| `lattice_compatible()` | O(1) | Cached subtype check |

**Scaling strategy**:
- Registry: Partition by entity_type for large ecosystems
- Lineage: Prune old history, keep recent + milestones
- Vectors: Use approximate nearest neighbor (HNSW) for >100k entries

## See Also

- [query.md](query.md) - Search operations over the catalog
- [lineage.md](lineage.md) - Ancestry and provenance tracking
- [lattice.md](lattice.md) - Type compatibility and composition
- [../d-gents/](../d-gents/) - Persistence infrastructure
- [../f-gents/artifacts.md](../f-gents/artifacts.md) - What gets registered

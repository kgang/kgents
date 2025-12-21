# L-gent Lineage: Provenance & Ancestry

**Purpose**: Track the genetic history of artifacts—where they came from, how they evolved, and what depends on them.

---

## Overview

Lineage is the ecosystem's **memory of transformation**. Every artifact has a story: who created it, what it was forked from, how it evolved, what depends on it. L-gent's lineage layer captures this history as a **directed acyclic graph (DAG)** of relationships.

> "Know where you came from to know where you can go."

Lineage enables:
- **Blame attribution**: Which change caused this regression?
- **Impact analysis**: What breaks if I deprecate this?
- **Evolution tracking**: How did this artifact improve over time?
- **Audit trails**: Who created what, when, and why?

## The Lineage Graph

```
                    ┌─────────────┐
                    │ BaseScraper │
                    │    v1.0     │
                    └──────┬──────┘
                           │ successor_to
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       ┌───────────┐ ┌───────────┐ ┌───────────┐
       │NewsScraper│ │APIScraper │ │HTMLScraper│
       │   v1.0    │ │   v1.0    │ │   v1.0    │
       └─────┬─────┘ └───────────┘ └─────┬─────┘
             │ forked_from                │ successor_to
             ▼                            ▼
       ┌───────────┐               ┌───────────┐
       │NewsScraper│               │HTMLScraper│
       │   v2.0    │               │   v2.0    │
       └───────────┘               └───────────┘
```

**Nodes** = Artifact IDs (immutable, versioned)
**Edges** = Relationships (typed, timestamped, attributed)

## Relationship Types

### Core Relationships

| Relationship | Meaning | Example |
|--------------|---------|---------|
| `successor_to` | Evolution (same lineage) | v2.0 → v1.0 |
| `forked_from` | Branching (new lineage) | NewsScraper → BaseScraper |
| `depends_on` | Runtime dependency | StockTicker → NetworkClient |
| `tested_by` | Test coverage | Parser → ParserTest |
| `documented_by` | Documentation link | Agent → Spec |
| `implements` | Contract satisfaction | Agent → Contract |
| `composed_with` | Known composition | ParserA >> ParserB |

### Relationship Schema

```python
@dataclass
class Relationship:
    """A directed edge in the lineage graph."""
    source_id: str           # Origin artifact
    target_id: str           # Destination artifact
    relationship_type: str   # One of the core types
    created_at: datetime
    created_by: str          # Who/what created this relationship

    # Context
    context: dict[str, Any] = field(default_factory=dict)
    # Examples:
    # - For successor_to: {"change_summary": "Performance optimization"}
    # - For forked_from: {"reason": "Specialized for news domain"}
    # - For depends_on: {"version_constraint": ">=2.0"}

    # Validity
    deprecated: bool = False
    deprecated_at: datetime | None = None
    deprecation_reason: str | None = None
```

## Lineage Operations

```python
class LineageGraph:
    """Layer 2: Provenance and ancestry tracking."""

    def __init__(self, storage: GraphAgent):
        self.storage = storage

    # ─────────────────────────────────────────────────────────────
    # Write Operations
    # ─────────────────────────────────────────────────────────────

    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        created_by: str,
        context: dict[str, Any] | None = None
    ) -> Relationship:
        """
        Add a new relationship to the lineage graph.

        Validates:
        - Source and target exist in registry
        - No cycles created (DAG property preserved)
        - Relationship type is valid for entity types
        """
        # Validate entities exist
        if not await self.registry.exists(source_id):
            raise LineageError(f"Source not found: {source_id}")
        if not await self.registry.exists(target_id):
            raise LineageError(f"Target not found: {target_id}")

        # Check for cycles (would violate DAG)
        if await self._would_create_cycle(source_id, target_id):
            raise LineageError(f"Relationship would create cycle: {source_id} -> {target_id}")

        rel = Relationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            created_at=datetime.utcnow(),
            created_by=created_by,
            context=context or {}
        )

        await self.storage.add_edge(rel)
        await self._emit_event(LineageUpdated(rel))

        return rel

    async def record_evolution(
        self,
        parent_id: str,
        child_id: str,
        evolution_type: str,
        created_by: str,
        success: bool,
        metrics: dict[str, float] | None = None
    ) -> Relationship:
        """
        Record an evolution relationship (E-gent integration).

        Special handling:
        - Records success/failure in context
        - Tracks improvement metrics
        - Enables "what worked?" queries
        """
        context = {
            "evolution_type": evolution_type,  # "complexity_reduction", "performance", etc.
            "success": success,
            "metrics": metrics or {}
        }

        return await self.add_relationship(
            source_id=child_id,
            target_id=parent_id,
            relationship_type="successor_to",
            created_by=created_by,
            context=context
        )

    async def record_forge(
        self,
        artifact_id: str,
        intent: str,
        forger: str,
        template_id: str | None = None
    ) -> None:
        """
        Record that F-gent forged an artifact.

        Creates special "forged_from" relationships if template used.
        Stores intent in catalog entry (for re-forging).
        """
        entry = await self.registry.get(artifact_id)
        entry.forged_by = forger
        entry.forged_from = intent

        if template_id:
            await self.add_relationship(
                source_id=artifact_id,
                target_id=template_id,
                relationship_type="forged_from",
                created_by=forger,
                context={"intent": intent}
            )

        await self.registry.update(entry)

    # ─────────────────────────────────────────────────────────────
    # Read Operations
    # ─────────────────────────────────────────────────────────────

    async def get_ancestors(
        self,
        artifact_id: str,
        relationship_types: list[str] | None = None,
        max_depth: int = -1  # -1 = unlimited
    ) -> list[AncestryNode]:
        """
        Get the ancestry tree of an artifact.

        Returns nodes ordered by depth (closest first).
        """
        types = relationship_types or ["successor_to", "forked_from"]

        visited = set()
        result = []
        queue = [(artifact_id, 0)]

        while queue:
            current_id, depth = queue.pop(0)

            if current_id in visited:
                continue
            visited.add(current_id)

            if depth > 0:  # Don't include self
                entry = await self.registry.get(current_id)
                result.append(AncestryNode(
                    id=current_id,
                    depth=depth,
                    entry=entry
                ))

            if max_depth != -1 and depth >= max_depth:
                continue

            # Find parents
            edges = await self.storage.get_outbound_edges(
                current_id, relationship_types=types
            )
            for edge in edges:
                queue.append((edge.target_id, depth + 1))

        return sorted(result, key=lambda n: n.depth)

    async def get_descendants(
        self,
        artifact_id: str,
        relationship_types: list[str] | None = None,
        max_depth: int = -1
    ) -> list[AncestryNode]:
        """
        Get all artifacts that descend from this one.

        Useful for impact analysis: "What breaks if I change this?"
        """
        types = relationship_types or ["successor_to", "forked_from"]

        visited = set()
        result = []
        queue = [(artifact_id, 0)]

        while queue:
            current_id, depth = queue.pop(0)

            if current_id in visited:
                continue
            visited.add(current_id)

            if depth > 0:
                entry = await self.registry.get(current_id)
                result.append(AncestryNode(
                    id=current_id,
                    depth=depth,
                    entry=entry
                ))

            if max_depth != -1 and depth >= max_depth:
                continue

            # Find children (inbound edges to this node)
            edges = await self.storage.get_inbound_edges(
                current_id, relationship_types=types
            )
            for edge in edges:
                queue.append((edge.source_id, depth + 1))

        return sorted(result, key=lambda n: n.depth)

    async def get_dependents(
        self,
        artifact_id: str,
        depth: int = 1
    ) -> list[AncestryNode]:
        """
        Get artifacts that depend on this one.

        Critical for deprecation: "Who do I need to notify?"
        """
        return await self.get_descendants(
            artifact_id,
            relationship_types=["depends_on"],
            max_depth=depth
        )

    async def get_evolution_history(
        self,
        artifact_id: str
    ) -> list[EvolutionStep]:
        """
        Get the evolution history of an artifact.

        Returns chronological list of evolution attempts.
        """
        ancestors = await self.get_ancestors(
            artifact_id,
            relationship_types=["successor_to"],
            max_depth=-1
        )

        # Build evolution steps with metrics
        steps = []
        current_id = artifact_id

        for ancestor in ancestors:
            edge = await self.storage.get_edge(current_id, ancestor.id, "successor_to")
            if edge:
                steps.append(EvolutionStep(
                    from_id=ancestor.id,
                    to_id=current_id,
                    evolution_type=edge.context.get("evolution_type", "unknown"),
                    success=edge.context.get("success", True),
                    metrics=edge.context.get("metrics", {}),
                    timestamp=edge.created_at
                ))
            current_id = ancestor.id

        return list(reversed(steps))  # Chronological order

    async def find_common_ancestor(
        self,
        artifact_a: str,
        artifact_b: str
    ) -> str | None:
        """
        Find the most recent common ancestor of two artifacts.

        Useful for: "Where did these two diverge?"
        """
        ancestors_a = {n.id for n in await self.get_ancestors(artifact_a)}
        ancestors_b = await self.get_ancestors(artifact_b)

        for ancestor in ancestors_b:
            if ancestor.id in ancestors_a:
                return ancestor.id

        return None

@dataclass
class AncestryNode:
    """A node in an ancestry traversal."""
    id: str
    depth: int                    # Distance from query origin
    entry: CatalogEntry | None
    relationship: str | None = None  # How connected to parent

@dataclass
class EvolutionStep:
    """One step in an artifact's evolution history."""
    from_id: str
    to_id: str
    evolution_type: str           # "complexity_reduction", "performance", etc.
    success: bool
    metrics: dict[str, float]     # Before/after measurements
    timestamp: datetime
```

## F-gent Integration: Forge Provenance

Track the complete creation story of F-gent artifacts:

```python
class ForgeProvenance:
    """Track F-gent forging history."""

    async def record_forge_attempt(
        self,
        intent: str,
        phases: list[ForgePhase],
        result: CatalogEntry | None,
        success: bool
    ) -> ForgeRecord:
        """
        Record a complete F-gent forge attempt.

        Enables:
        - "What intents have we seen before?"
        - "How many attempts did this take?"
        - "What phase failed?"
        """
        record = ForgeRecord(
            id=generate_id(),
            intent=intent,
            phases=phases,
            result_id=result.id if result else None,
            success=success,
            timestamp=datetime.utcnow()
        )

        await self.storage.store_forge_record(record)

        if result:
            # Link artifact to forge record
            await self.lineage.add_relationship(
                source_id=result.id,
                target_id=record.id,
                relationship_type="forged_from",
                created_by="F-gent",
                context={"intent": intent}
            )

        return record

    async def find_similar_forges(
        self,
        intent: str,
        threshold: float = 0.8
    ) -> list[ForgeRecord]:
        """
        Find past forge attempts with similar intent.

        Prevents duplicate forging: "We already built something like this."
        """
        intent_embedding = await self.embedder.embed(intent)
        similar = await self.vectors.search(
            vector=intent_embedding,
            filter={"type": "forge_record"},
            threshold=threshold
        )
        return [await self.get_forge_record(r.id) for r in similar]

@dataclass
class ForgePhase:
    """One phase of the forge loop."""
    phase_name: str               # understand, contract, prototype, validate, crystallize
    input_summary: str
    output_summary: str
    success: bool
    errors: list[str]
    duration_ms: int

@dataclass
class ForgeRecord:
    """Complete record of a forge attempt."""
    id: str
    intent: str
    phases: list[ForgePhase]
    result_id: str | None         # Artifact ID if successful
    success: bool
    timestamp: datetime
```

## Impact Analysis

Before deprecating or modifying an artifact, analyze impact:

```python
class ImpactAnalyzer:
    """Analyze the impact of artifact changes."""

    async def analyze_deprecation(
        self,
        artifact_id: str
    ) -> ImpactReport:
        """
        Analyze what would break if this artifact is deprecated.
        """
        # Direct dependents
        dependents = await self.lineage.get_dependents(artifact_id, depth=1)

        # Transitive dependents
        all_dependents = await self.lineage.get_dependents(artifact_id, depth=-1)

        # Active usage
        entry = await self.registry.get(artifact_id)
        active_users = entry.usage_count > 0 and entry.last_used > datetime.utcnow() - timedelta(days=30)

        return ImpactReport(
            artifact_id=artifact_id,
            direct_dependents=len(dependents),
            transitive_dependents=len(all_dependents),
            dependent_ids=[d.id for d in all_dependents],
            active_usage=active_users,
            severity=self._calculate_severity(dependents, active_users),
            recommended_actions=self._recommend_actions(dependents)
        )

    async def find_replacement_candidates(
        self,
        artifact_id: str
    ) -> list[CatalogEntry]:
        """
        Find potential replacements for a deprecated artifact.

        Uses type compatibility + semantic similarity.
        """
        entry = await self.registry.get(artifact_id)

        # Find type-compatible artifacts
        candidates = await self.lattice.find_satisfying(
            input_type=entry.input_type,
            output_type=entry.output_type
        )

        # Filter out self and deprecated
        candidates = [
            c for c in candidates
            if c.id != artifact_id and c.status == Status.ACTIVE
        ]

        # Rank by semantic similarity
        return await self.semantic.rank_by_similarity(
            reference=entry,
            candidates=candidates
        )

@dataclass
class ImpactReport:
    """Report on the impact of a change."""
    artifact_id: str
    direct_dependents: int
    transitive_dependents: int
    dependent_ids: list[str]
    active_usage: bool
    severity: str                 # "low", "medium", "high", "critical"
    recommended_actions: list[str]
```

## Lineage Visualization

Generate visual representations of lineage:

```python
async def generate_lineage_diagram(
    self,
    artifact_id: str,
    depth: int = 3,
    format: str = "mermaid"
) -> str:
    """Generate a visual diagram of artifact lineage."""

    ancestors = await self.get_ancestors(artifact_id, max_depth=depth)
    descendants = await self.get_descendants(artifact_id, max_depth=depth)

    if format == "mermaid":
        return self._to_mermaid(artifact_id, ancestors, descendants)
    elif format == "dot":
        return self._to_dot(artifact_id, ancestors, descendants)

def _to_mermaid(self, root_id, ancestors, descendants) -> str:
    """Generate Mermaid diagram syntax."""
    lines = ["graph TD"]

    # Add root
    lines.append(f"    {root_id}[{root_id}]:::root")

    # Add ancestors
    for node in ancestors:
        lines.append(f"    {node.id}[{node.id}]")
        lines.append(f"    {root_id} -->|{node.relationship}| {node.id}")

    # Add descendants
    for node in descendants:
        lines.append(f"    {node.id}[{node.id}]")
        lines.append(f"    {node.id} -->|{node.relationship}| {root_id}")

    lines.append("    classDef root fill:#f96,stroke:#333")

    return "\n".join(lines)
```

## Storage: The Lineage Log

Lineage is stored as an **append-only log** (event sourcing):

```python
@dataclass
class LineageEvent:
    """An event in the lineage log."""
    event_type: str               # "relationship_added", "relationship_deprecated"
    timestamp: datetime
    actor: str                    # Who/what caused this event
    payload: dict[str, Any]       # Event-specific data

class LineageLog:
    """Append-only lineage event log."""

    async def append(self, event: LineageEvent) -> None:
        """Append event to log."""
        await self.storage.append_jsonl(
            path=self.log_path,
            data=asdict(event)
        )

    async def replay(self, until: datetime | None = None) -> LineageGraph:
        """Rebuild graph state by replaying events."""
        graph = LineageGraph()

        async for event in self.storage.read_jsonl(self.log_path):
            if until and event["timestamp"] > until:
                break
            await self._apply_event(graph, event)

        return graph

    async def snapshot(self) -> None:
        """Create snapshot for faster rebuilds."""
        graph = await self.replay()
        await self.storage.write_json(
            path=self.snapshot_path,
            data=graph.to_dict()
        )
```

## See Also

- [catalog.md](catalog.md) - What gets tracked
- [query.md](query.md) - How to search lineage
- [../f-gents/artifacts.md](../f-gents/artifacts.md) - Forging that initiates lineage
- [../d-gents/streams.md](../d-gents/streams.md) - Event sourcing for storage

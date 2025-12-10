"""
UnifiedMemory: Composing all memory modes into a single interface.

The enlightened D-gent that unifies:
- Immediate (volatile/cached)
- Durable (persistent)
- Semantic (vector)
- Temporal (stream)
- Relational (graph)

All through compositional lenses.
"""

from typing import (
    TypeVar,
    Generic,
    List,
    Optional,
    Any,
    Dict,
    Callable,
    Awaitable,
    Union,
    Tuple,
)
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
import asyncio

from .protocol import DataAgent
from .errors import StateError, NoosphereError
from .lens import Lens


class UnifiedMemoryError(NoosphereError):
    """UnifiedMemory operation failed."""


class LayerNotAvailableError(UnifiedMemoryError):
    """Requested memory layer is not configured."""


S = TypeVar("S")
A = TypeVar("A")


class MemoryLayer(Enum):
    """Available memory layers."""

    IMMEDIATE = auto()  # Volatile/cached
    DURABLE = auto()  # Persistent
    SEMANTIC = auto()  # Vector embeddings
    TEMPORAL = auto()  # Event stream
    RELATIONAL = auto()  # Graph


@dataclass
class MemoryConfig:
    """Configuration for UnifiedMemory."""

    # Layer availability
    enable_semantic: bool = False
    enable_temporal: bool = False
    enable_relational: bool = False

    # Semantic config
    embedding_dimension: int = 384
    similarity_threshold: float = 0.7

    # Temporal config
    max_events: int = 10000
    event_retention: timedelta = timedelta(days=30)

    # Relational config
    max_relationships: int = 1000

    # General
    auto_associate: bool = False  # Auto-create semantic associations
    track_lineage: bool = True  # Track state provenance


@dataclass
class MemoryEntry(Generic[S]):
    """An entry in unified memory with all metadata."""

    id: str
    state: S
    timestamp: datetime

    # Semantic metadata
    concepts: List[str] = field(default_factory=list)
    embedding: Optional[Any] = None

    # Relational metadata
    related_to: List[str] = field(default_factory=list)
    derived_from: Optional[str] = None

    # Temporal metadata
    event_label: Optional[str] = None
    lineage_depth: int = 0


class UnifiedMemory(Generic[S]):
    """
    The enlightened D-gent: all memory modes unified.

    Provides:
    - Immediate: load()/save() (volatile)
    - Durable: persist()/recover() (file/db)
    - Semantic: associate()/recall() (vectors)
    - Temporal: witness()/replay() (events)
    - Relational: relate()/trace() (graphs)

    All through compositional lenses.

    Example:
        >>> config = MemoryConfig(enable_semantic=True, enable_temporal=True)
        >>> memory = UnifiedMemory(volatile_agent, config)
        >>>
        >>> # Basic operations
        >>> await memory.save({"user": "alice"})
        >>> state = await memory.load()
        >>>
        >>> # Semantic operations
        >>> await memory.associate(state, "user-profile")
        >>> related = await memory.recall("profile", limit=5)
        >>>
        >>> # Temporal operations
        >>> await memory.witness("login", state)
        >>> past = await memory.replay(one_hour_ago)
        >>>
        >>> # Relational operations
        >>> await memory.relate("session-123", "belongs_to", "user-alice")
        >>> chain = await memory.ancestors("session-123")
    """

    def __init__(
        self,
        underlying: DataAgent[S],
        config: Optional[MemoryConfig] = None,
    ):
        """
        Create unified memory wrapping a base D-gent.

        Args:
            underlying: Base D-gent for storage
            config: Memory configuration
        """
        self._underlying = underlying
        self._config = config or MemoryConfig()

        # State tracking
        self._current_entry: Optional[MemoryEntry[S]] = None
        self._entry_counter = 0

        # Semantic layer (in-memory for now)
        self._concepts: Dict[str, List[str]] = {}  # concept -> entry_ids
        self._entry_concepts: Dict[str, List[str]] = {}  # entry_id -> concepts

        # Temporal layer
        self._events: List[Tuple[datetime, str, S]] = []  # (timestamp, label, state)

        # Relational layer
        self._relationships: Dict[
            str, List[Tuple[str, str]]
        ] = {}  # source -> [(rel, target)]
        self._reverse_relationships: Dict[
            str, List[Tuple[str, str]]
        ] = {}  # target -> [(rel, source)]
        self._lineage: Dict[str, str] = {}  # entry_id -> parent_id

    # === Core DataAgent Interface ===

    async def load(self) -> S:
        """Load current state."""
        return await self._underlying.load()

    async def save(self, state: S) -> str:
        """
        Save state and return entry ID.

        Creates a new memory entry with tracking metadata.
        """
        self._entry_counter += 1
        entry_id = f"entry-{self._entry_counter}"

        entry = MemoryEntry(
            id=entry_id,
            state=state,
            timestamp=datetime.now(),
            derived_from=self._current_entry.id if self._current_entry else None,
            lineage_depth=(self._current_entry.lineage_depth + 1)
            if self._current_entry
            else 0,
        )

        await self._underlying.save(state)
        self._current_entry = entry

        # Track lineage
        if self._config.track_lineage and entry.derived_from:
            self._lineage[entry_id] = entry.derived_from

        return entry_id

    async def history(self, limit: int | None = None) -> List[S]:
        """Get state history from underlying D-gent."""
        return await self._underlying.history(limit)

    # === Semantic Layer ===

    async def associate(self, state: S, concept: str) -> None:
        """
        Tag state with a semantic concept.

        Creates an association between current state and the concept
        for later semantic recall.
        """
        if not self._config.enable_semantic:
            raise LayerNotAvailableError("Semantic layer not enabled")

        if not self._current_entry:
            # Create entry if needed
            await self.save(state)

        entry_id = self._current_entry.id

        # Add to concept index
        if concept not in self._concepts:
            self._concepts[concept] = []
        if entry_id not in self._concepts[concept]:
            self._concepts[concept].append(entry_id)

        # Add to entry's concepts
        if entry_id not in self._entry_concepts:
            self._entry_concepts[entry_id] = []
        if concept not in self._entry_concepts[entry_id]:
            self._entry_concepts[entry_id].append(concept)
            self._current_entry.concepts.append(concept)

    async def recall(
        self,
        concept: str,
        limit: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Find states associated with concept.

        Returns list of (entry_id, relevance_score) tuples.
        """
        if not self._config.enable_semantic:
            raise LayerNotAvailableError("Semantic layer not enabled")

        results = []

        # Exact match
        if concept in self._concepts:
            for entry_id in self._concepts[concept][:limit]:
                results.append((entry_id, 1.0))

        # Partial match (simple substring for now)
        if len(results) < limit:
            for stored_concept, entry_ids in self._concepts.items():
                if (
                    concept.lower() in stored_concept.lower()
                    or stored_concept.lower() in concept.lower()
                ):
                    for entry_id in entry_ids:
                        if entry_id not in [r[0] for r in results]:
                            results.append((entry_id, 0.7))
                            if len(results) >= limit:
                                break

        return results[:limit]

    async def semantic_neighbors(
        self,
        entry_id: str,
        limit: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Find entries semantically similar to given entry.

        Uses shared concepts as similarity measure.
        """
        if not self._config.enable_semantic:
            raise LayerNotAvailableError("Semantic layer not enabled")

        if entry_id not in self._entry_concepts:
            return []

        my_concepts = set(self._entry_concepts[entry_id])
        if not my_concepts:
            return []

        # Find entries with overlapping concepts
        candidates: Dict[str, float] = {}
        for concept in my_concepts:
            for other_id in self._concepts.get(concept, []):
                if other_id != entry_id:
                    other_concepts = set(self._entry_concepts.get(other_id, []))
                    # Jaccard similarity
                    intersection = len(my_concepts & other_concepts)
                    union = len(my_concepts | other_concepts)
                    similarity = intersection / union if union > 0 else 0
                    candidates[other_id] = max(candidates.get(other_id, 0), similarity)

        # Sort by similarity
        sorted_candidates = sorted(candidates.items(), key=lambda x: -x[1])
        return sorted_candidates[:limit]

    async def concepts_for(self, entry_id: str) -> List[str]:
        """Get concepts associated with an entry."""
        return self._entry_concepts.get(entry_id, [])

    # === Temporal Layer ===

    async def witness(
        self,
        event_label: str,
        state: S,
    ) -> None:
        """
        Record state transition with event label.

        Creates a temporal record for later replay.
        """
        if not self._config.enable_temporal:
            raise LayerNotAvailableError("Temporal layer not enabled")

        self._events.append((datetime.now(), event_label, state))

        # Enforce retention limit
        if len(self._events) > self._config.max_events:
            self._events = self._events[-self._config.max_events :]

    async def replay(self, timestamp: datetime) -> Optional[S]:
        """
        Reconstruct state at specific time.

        Finds the most recent state before the given timestamp.
        """
        if not self._config.enable_temporal:
            raise LayerNotAvailableError("Temporal layer not enabled")

        latest = None
        for ts, _, state in self._events:
            if ts <= timestamp:
                latest = state
            else:
                break

        return latest

    async def timeline(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[Tuple[datetime, str, S]]:
        """
        Get state evolution within time window.

        Returns list of (timestamp, event_label, state) tuples.
        """
        if not self._config.enable_temporal:
            raise LayerNotAvailableError("Temporal layer not enabled")

        results = []
        for ts, label, state in self._events:
            if start and ts < start:
                continue
            if end and ts > end:
                continue
            results.append((ts, label, state))

        if limit:
            results = results[-limit:]

        return results

    async def events_by_label(
        self,
        label: str,
        limit: Optional[int] = None,
    ) -> List[Tuple[datetime, S]]:
        """Get all events with a specific label."""
        if not self._config.enable_temporal:
            raise LayerNotAvailableError("Temporal layer not enabled")

        results = [(ts, state) for ts, l, state in self._events if l == label]
        if limit:
            results = results[-limit:]
        return results

    # === Relational Layer ===

    async def relate(
        self,
        source: str,
        relation: str,
        target: str,
    ) -> None:
        """
        Establish relationship between entities.

        Args:
            source: Source entity ID
            relation: Relationship type
            target: Target entity ID
        """
        if not self._config.enable_relational:
            raise LayerNotAvailableError("Relational layer not enabled")

        # Forward relationship
        if source not in self._relationships:
            self._relationships[source] = []
        if (relation, target) not in self._relationships[source]:
            self._relationships[source].append((relation, target))

        # Reverse relationship (for ancestry queries)
        if target not in self._reverse_relationships:
            self._reverse_relationships[target] = []
        if (relation, source) not in self._reverse_relationships[target]:
            self._reverse_relationships[target].append((relation, source))

    async def related_to(
        self,
        entity_id: str,
        relation: Optional[str] = None,
    ) -> List[Tuple[str, str]]:
        """
        Get entities related to this one.

        Returns list of (relation, target_id) tuples.
        """
        if not self._config.enable_relational:
            raise LayerNotAvailableError("Relational layer not enabled")

        rels = self._relationships.get(entity_id, [])
        if relation:
            rels = [(r, t) for r, t in rels if r == relation]
        return rels

    async def related_from(
        self,
        entity_id: str,
        relation: Optional[str] = None,
    ) -> List[Tuple[str, str]]:
        """
        Get entities that relate to this one (reverse).

        Returns list of (relation, source_id) tuples.
        """
        if not self._config.enable_relational:
            raise LayerNotAvailableError("Relational layer not enabled")

        rels = self._reverse_relationships.get(entity_id, [])
        if relation:
            rels = [(r, s) for r, s in rels if r == relation]
        return rels

    async def trace(
        self,
        start: str,
        max_depth: int = 3,
    ) -> Dict[str, Any]:
        """
        Graph traversal from starting entity.

        Returns subgraph of reachable entities.
        """
        if not self._config.enable_relational:
            raise LayerNotAvailableError("Relational layer not enabled")

        visited = set()
        edges = []

        def dfs(node: str, depth: int):
            if depth > max_depth or node in visited:
                return
            visited.add(node)

            for rel, target in self._relationships.get(node, []):
                edges.append({"source": node, "relation": rel, "target": target})
                dfs(target, depth + 1)

        dfs(start, 0)

        return {
            "nodes": list(visited),
            "edges": edges,
            "depth": max_depth,
        }

    async def ancestors(
        self,
        entity_id: str,
        max_depth: int = 10,
    ) -> List[str]:
        """
        Lineage chain to root.

        Uses the lineage tracking from save operations.
        """
        chain = []
        current = entity_id
        depth = 0

        while current in self._lineage and depth < max_depth:
            parent = self._lineage[current]
            chain.append(parent)
            current = parent
            depth += 1

        return chain

    async def descendants(
        self,
        entity_id: str,
        max_depth: int = 10,
    ) -> List[str]:
        """Find all entities derived from this one."""
        # Build reverse lineage
        reverse_lineage: Dict[str, List[str]] = {}
        for child, parent in self._lineage.items():
            if parent not in reverse_lineage:
                reverse_lineage[parent] = []
            reverse_lineage[parent].append(child)

        # BFS traversal
        result = []
        queue = [entity_id]
        depth = 0

        while queue and depth < max_depth:
            next_queue = []
            for node in queue:
                children = reverse_lineage.get(node, [])
                result.extend(children)
                next_queue.extend(children)
            queue = next_queue
            depth += 1

        return result

    # === Lens Composition ===

    def __rshift__(self, lens: Lens[S, A]) -> "LensedUnifiedMemory[A]":
        """
        Compose with lens for focused access.

        Usage:
            focused = memory >> user_lens
            user = await focused.load()
        """
        return LensedUnifiedMemory(self, lens)

    # === Convenience Methods ===

    @property
    def available_layers(self) -> List[MemoryLayer]:
        """Get list of enabled memory layers."""
        layers = [MemoryLayer.IMMEDIATE, MemoryLayer.DURABLE]
        if self._config.enable_semantic:
            layers.append(MemoryLayer.SEMANTIC)
        if self._config.enable_temporal:
            layers.append(MemoryLayer.TEMPORAL)
        if self._config.enable_relational:
            layers.append(MemoryLayer.RELATIONAL)
        return layers

    def stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "entry_count": self._entry_counter,
            "concept_count": len(self._concepts),
            "event_count": len(self._events),
            "relationship_count": sum(len(r) for r in self._relationships.values()),
            "lineage_depth": self._current_entry.lineage_depth
            if self._current_entry
            else 0,
            "layers": [l.name for l in self.available_layers],
        }


class LensedUnifiedMemory(Generic[A]):
    """UnifiedMemory focused through a lens."""

    def __init__(self, parent: UnifiedMemory, lens: Lens):
        self._parent = parent
        self._lens = lens

    async def load(self) -> A:
        """Load focused state."""
        full_state = await self._parent.load()
        return self._lens.get(full_state)

    async def save(self, value: A) -> str:
        """Save focused state."""
        full_state = await self._parent.load()
        new_state = self._lens.set(full_state, value)
        return await self._parent.save(new_state)


# === Factory Functions ===


def create_unified_memory(
    underlying: DataAgent[S],
    enable_all: bool = False,
    **kwargs,
) -> UnifiedMemory[S]:
    """
    Create UnifiedMemory with convenient defaults.

    Args:
        underlying: Base D-gent
        enable_all: Enable all layers
        **kwargs: MemoryConfig overrides

    Returns:
        Configured UnifiedMemory
    """
    if enable_all:
        kwargs.setdefault("enable_semantic", True)
        kwargs.setdefault("enable_temporal", True)
        kwargs.setdefault("enable_relational", True)

    config = MemoryConfig(**kwargs)
    return UnifiedMemory(underlying, config)

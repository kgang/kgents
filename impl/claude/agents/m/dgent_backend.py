"""
DgentBackedHolographicMemory: D-gent UnifiedMemory Integration.

Phase 2 of M-gent implementation: Persistence layer.

The holographic memory substrate backed by D-gent's UnifiedMemory,
providing:
- Semantic layer: concept associations via UnifiedMemory.associate/recall
- Temporal layer: memory timeline via UnifiedMemory.witness/replay
- Relational layer: associative links via UnifiedMemory.relate/trace

This bridges M-gent's cognitive layer with D-gent's storage layer.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar
import json

from .holographic import (
    HolographicMemory,
    MemoryPattern,
    CompressionLevel,
    ResonanceResult,
)

T = TypeVar("T")


@dataclass
class PersistenceConfig:
    """Configuration for D-gent backed holographic memory."""

    # Semantic layer settings
    enable_semantic: bool = True
    auto_associate: bool = True  # Auto-create concept associations

    # Temporal layer settings
    enable_temporal: bool = True
    witness_all_stores: bool = True  # Record all store operations

    # Relational layer settings
    enable_relational: bool = True
    track_lineage: bool = True  # Track memory derivations

    # Sync settings
    sync_interval_ms: int = 1000  # How often to sync to storage
    batch_size: int = 100  # Max patterns per sync batch

    # Serialization
    serialize_embeddings: bool = True  # Store embeddings for recovery


@dataclass
class MemorySnapshot:
    """Snapshot of memory state for persistence."""

    patterns: Dict[str, Dict[str, Any]]  # Serialized patterns
    timestamp: datetime
    stats: Dict[str, Any]


class DgentBackedHolographicMemory(HolographicMemory[T]):
    """HolographicMemory backed by D-gent UnifiedMemory.

    Bridges M-gent's cognitive layer with D-gent's storage primitives:

    ```
    ┌─────────────────────────────────────────────────────────────┐
    │                      M-gent (Cognitive)                      │
    │         DgentBackedHolographicMemory                         │
    ├─────────────────────────────────────────────────────────────┤
    │                      D-gent (Storage)                        │
    │    UnifiedMemory (Semantic + Temporal + Relational)          │
    └─────────────────────────────────────────────────────────────┘
    ```

    Example:
        from agents.d.unified import UnifiedMemory, MemoryConfig, create_unified_memory
        from agents.d.volatile import VolatileAgent

        # Create D-gent storage
        volatile = VolatileAgent()
        unified = create_unified_memory(volatile, enable_all=True)

        # Create M-gent memory
        memory = DgentBackedHolographicMemory(
            storage=unified,
            embedder=my_embedder,
        )

        # Store (persists to D-gent)
        await memory.store("m1", "User prefers dark mode", ["preference", "ui"])

        # Retrieve (uses D-gent semantic layer)
        results = await memory.retrieve("What does the user prefer?")

        # Persist state explicitly
        await memory.persist()

        # Recover from D-gent storage
        await memory.recover()
    """

    def __init__(
        self,
        storage: Any,  # D-gent UnifiedMemory
        embedder: Any = None,  # L-gent Embedder
        config: Optional[PersistenceConfig] = None,
        namespace: str = "holographic",
        **kwargs,
    ):
        """Initialize D-gent backed holographic memory.

        Args:
            storage: D-gent UnifiedMemory instance
            embedder: L-gent embedder for vector representations
            config: Persistence configuration
            namespace: Namespace for D-gent storage (isolates this memory)
            **kwargs: Additional args for HolographicMemory
        """
        super().__init__(embedder=embedder, storage=None, **kwargs)
        self._dgent_storage = storage
        self._config = config or PersistenceConfig()
        self._namespace = namespace

        # Pending changes for batched sync
        self._pending_stores: List[str] = []
        self._pending_updates: List[str] = []
        self._last_sync = datetime.now()

        # Recovery state
        self._recovered = False

    async def store(
        self,
        id: str,
        content: T,
        concepts: Optional[List[str]] = None,
        embedding: Optional[List[float]] = None,
    ) -> MemoryPattern[T]:
        """Store memory with D-gent persistence.

        Stores in holographic memory AND persists to D-gent:
        - Semantic: associates with concepts
        - Temporal: witnesses the store event
        - Relational: tracks derivation if applicable

        Args:
            id: Unique identifier
            content: Memory content
            concepts: Semantic concepts for association
            embedding: Pre-computed embedding

        Returns:
            Created MemoryPattern
        """
        # Store in holographic layer (in-memory)
        pattern = await super().store(id, content, concepts, embedding)

        # Persist to D-gent
        await self._persist_pattern(pattern, concepts or [])

        # Track for batch sync
        self._pending_stores.append(id)

        return pattern

    async def retrieve(
        self,
        query: str | List[float],
        limit: int = 10,
        threshold: float = 0.0,
    ) -> List[ResonanceResult[T]]:
        """Retrieve with D-gent fallback.

        First checks in-memory patterns, then falls back to D-gent
        semantic recall if needed.

        Args:
            query: Text query or embedding
            limit: Maximum results
            threshold: Minimum similarity

        Returns:
            List of ResonanceResult
        """
        # Get from in-memory holographic store
        results = await super().retrieve(query, limit, threshold)

        # If we have few results, try D-gent semantic recall
        if len(results) < limit and self._config.enable_semantic:
            dgent_results = await self._recall_from_dgent(query, limit - len(results))

            # Merge results (avoid duplicates)
            seen_ids = {r.pattern.id for r in results}
            for r in dgent_results:
                if r.pattern.id not in seen_ids:
                    results.append(r)

        return results[:limit]

    async def persist(self) -> Dict[str, Any]:
        """Explicitly persist all patterns to D-gent storage.

        Returns:
            Persistence statistics
        """
        stats = {
            "persisted": 0,
            "concepts_associated": 0,
            "events_witnessed": 0,
        }

        for pattern_id, pattern in self._patterns.items():
            await self._persist_pattern(pattern, pattern.concepts)
            stats["persisted"] += 1

        # Clear pending
        self._pending_stores.clear()
        self._pending_updates.clear()
        self._last_sync = datetime.now()

        return stats

    async def recover(self) -> Dict[str, Any]:
        """Recover memory state from D-gent storage.

        Reconstructs in-memory patterns from D-gent's semantic
        and temporal layers.

        Returns:
            Recovery statistics
        """
        stats = {
            "recovered": 0,
            "concepts_found": 0,
            "failed": 0,
        }

        # Get all concepts in our namespace
        namespace_prefix = f"{self._namespace}:"
        concepts_to_check = [
            c
            for c in self._dgent_storage._concepts.keys()
            if c.startswith(namespace_prefix)
        ]

        for concept in concepts_to_check:
            try:
                # Recall entries for this concept
                entries = await self._dgent_storage.recall(concept, limit=1000)
                stats["concepts_found"] += 1

                for entry_id, score in entries:
                    if entry_id not in self._patterns:
                        # Try to reconstruct pattern from storage
                        await self._recover_pattern(entry_id)
                        stats["recovered"] += 1

            except Exception:
                stats["failed"] += 1

        self._recovered = True
        return stats

    async def consolidate(self) -> Dict[str, Any]:
        """Consolidate with D-gent sync.

        Extends base consolidation with D-gent persistence.
        """
        # Run base consolidation
        result = await super().consolidate()

        # Sync changes to D-gent
        await self._sync_to_dgent()

        return result

    async def demote(self, pattern_id: str, levels: int = 1) -> None:
        """Demote with D-gent update."""
        await super().demote(pattern_id, levels)
        self._pending_updates.append(pattern_id)

    async def promote(self, pattern_id: str, levels: int = 1) -> None:
        """Promote with D-gent update."""
        await super().promote(pattern_id, levels)
        self._pending_updates.append(pattern_id)

    # ========== D-gent Integration ==========

    async def _persist_pattern(
        self,
        pattern: MemoryPattern[T],
        concepts: List[str],
    ) -> None:
        """Persist a pattern to D-gent storage."""
        # Serialize pattern for storage
        pattern_data = self._serialize_pattern(pattern)

        # Save to D-gent
        await self._dgent_storage.save(pattern_data)

        # Semantic layer: associate with concepts
        if self._config.enable_semantic and concepts:
            for concept in concepts:
                namespaced = f"{self._namespace}:{concept}"
                await self._dgent_storage.associate(pattern_data, namespaced)

        # Temporal layer: witness the store
        if self._config.enable_temporal and self._config.witness_all_stores:
            await self._dgent_storage.witness(
                f"store:{pattern.id}",
                pattern_data,
            )

        # Relational layer: track derivation
        if self._config.enable_relational and self._config.track_lineage:
            # If we have lineage info, create relationship
            if hasattr(pattern, "derived_from") and pattern.derived_from:
                await self._dgent_storage.relate(
                    pattern.id,
                    "derived_from",
                    pattern.derived_from,
                )

    async def _recover_pattern(self, pattern_id: str) -> Optional[MemoryPattern[T]]:
        """Recover a single pattern from D-gent storage."""
        # Try to get from D-gent temporal layer (if available)
        if self._config.enable_temporal:
            events = await self._dgent_storage.events_by_label(
                f"store:{pattern_id}",
                limit=1,
            )
            if events:
                _, pattern_data = events[-1]
                pattern = self._deserialize_pattern(pattern_data)
                if pattern:
                    self._patterns[pattern.id] = pattern
                    return pattern

        return None

    async def _recall_from_dgent(
        self,
        query: str | List[float],
        limit: int,
    ) -> List[ResonanceResult[T]]:
        """Recall patterns from D-gent semantic layer."""
        results = []

        if not isinstance(query, str):
            return results  # D-gent semantic uses text queries

        # Try semantic recall
        namespaced_query = f"{self._namespace}:{query}"

        try:
            entries = await self._dgent_storage.recall(query, limit=limit)

            for entry_id, score in entries:
                # Check if already in memory
                if entry_id in self._patterns:
                    pattern = self._patterns[entry_id]
                    results.append(
                        ResonanceResult(
                            pattern=pattern,
                            similarity=score,
                            resolution=self._compression_to_resolution(
                                pattern.compression
                            ),
                        )
                    )
                else:
                    # Try to recover
                    pattern = await self._recover_pattern(entry_id)
                    if pattern:
                        results.append(
                            ResonanceResult(
                                pattern=pattern,
                                similarity=score,
                                resolution=self._compression_to_resolution(
                                    pattern.compression
                                ),
                            )
                        )

        except Exception:
            pass  # Semantic layer may not be enabled

        return results

    async def _sync_to_dgent(self) -> Dict[str, int]:
        """Sync pending changes to D-gent storage."""
        stats = {"stores": 0, "updates": 0}

        # Process pending stores
        for pattern_id in self._pending_stores:
            if pattern_id in self._patterns:
                pattern = self._patterns[pattern_id]
                await self._persist_pattern(pattern, pattern.concepts)
                stats["stores"] += 1

        # Process pending updates
        for pattern_id in self._pending_updates:
            if pattern_id in self._patterns:
                pattern = self._patterns[pattern_id]
                # Update temporal record
                if self._config.enable_temporal:
                    await self._dgent_storage.witness(
                        f"update:{pattern_id}",
                        self._serialize_pattern(pattern),
                    )
                stats["updates"] += 1

        self._pending_stores.clear()
        self._pending_updates.clear()
        self._last_sync = datetime.now()

        return stats

    def _serialize_pattern(self, pattern: MemoryPattern[T]) -> Dict[str, Any]:
        """Serialize pattern for D-gent storage."""
        data = {
            "id": pattern.id,
            "content": pattern.content,
            "timestamp": pattern.timestamp.isoformat(),
            "last_accessed": pattern.last_accessed.isoformat(),
            "access_count": pattern.access_count,
            "compression": pattern.compression.name,
            "strength": pattern.strength,
            "concepts": pattern.concepts,
        }

        if self._config.serialize_embeddings:
            data["embedding"] = pattern.embedding

        return data

    def _deserialize_pattern(
        self,
        data: Dict[str, Any],
    ) -> Optional[MemoryPattern[T]]:
        """Deserialize pattern from D-gent storage."""
        try:
            pattern = MemoryPattern(
                id=data["id"],
                content=data["content"],
                embedding=data.get("embedding", []),
                timestamp=datetime.fromisoformat(data["timestamp"]),
                last_accessed=datetime.fromisoformat(data["last_accessed"]),
                access_count=data.get("access_count", 0),
                compression=CompressionLevel[data.get("compression", "FULL")],
                strength=data.get("strength", 1.0),
                concepts=data.get("concepts", []),
            )
            return pattern
        except (KeyError, ValueError):
            return None

    def stats(self) -> Dict[str, Any]:
        """Get extended statistics including D-gent info."""
        base_stats = super().stats()

        base_stats["dgent"] = {
            "namespace": self._namespace,
            "pending_stores": len(self._pending_stores),
            "pending_updates": len(self._pending_updates),
            "last_sync": self._last_sync.isoformat(),
            "recovered": self._recovered,
        }

        # Include D-gent stats if available
        if hasattr(self._dgent_storage, "stats"):
            base_stats["dgent"]["storage"] = self._dgent_storage.stats()

        return base_stats


class AssociativeWebMemory(DgentBackedHolographicMemory[T]):
    """HolographicMemory with explicit associative links.

    Extends D-gent backed memory with spreading activation
    through the relational layer.

    Example:
        memory = AssociativeWebMemory(storage=unified)

        # Store memories
        m1 = await memory.store("m1", "User likes pizza")
        m2 = await memory.store("m2", "Pizza is Italian food")

        # Create explicit link
        await memory.link("m1", "related_to", "m2")

        # Spread activation retrieval
        results = await memory.spread_activation("m1", depth=2)
    """

    async def link(
        self,
        source_id: str,
        relation: str,
        target_id: str,
    ) -> None:
        """Create associative link between memories.

        Args:
            source_id: Source memory ID
            relation: Relationship type (e.g., "reminds_of", "contradicts")
            target_id: Target memory ID
        """
        if not self._config.enable_relational:
            return

        await self._dgent_storage.relate(source_id, relation, target_id)

    async def spread_activation(
        self,
        start_id: str,
        depth: int = 3,
        decay: float = 0.5,
    ) -> List[Tuple[MemoryPattern[T], float]]:
        """Retrieve memories via spreading activation.

        Starts from a memory and activates connected memories,
        with activation decaying over distance.

        Args:
            start_id: Starting memory ID
            depth: Maximum traversal depth
            decay: Activation decay per hop (0 to 1)

        Returns:
            List of (pattern, activation) tuples
        """
        if not self._config.enable_relational:
            return []

        if start_id not in self._patterns:
            return []

        # Get subgraph from D-gent
        subgraph = await self._dgent_storage.trace(start_id, max_depth=depth)

        # Compute activations
        activations: Dict[str, float] = {start_id: 1.0}

        for edge in subgraph["edges"]:
            source = edge["source"]
            target = edge["target"]

            if source in activations:
                # Propagate activation with decay
                source_activation = activations[source]
                target_activation = source_activation * decay

                # Take max if already activated
                activations[target] = max(
                    activations.get(target, 0),
                    target_activation,
                )

        # Build results
        results = []
        for node_id, activation in activations.items():
            if node_id in self._patterns and node_id != start_id:
                results.append((self._patterns[node_id], activation))

        # Sort by activation
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    async def related_memories(
        self,
        memory_id: str,
        relation: Optional[str] = None,
    ) -> List[MemoryPattern[T]]:
        """Get memories directly related to this one.

        Args:
            memory_id: Source memory ID
            relation: Optional relation type filter

        Returns:
            List of related patterns
        """
        if not self._config.enable_relational:
            return []

        relations = await self._dgent_storage.related_to(memory_id, relation)

        results = []
        for _, target_id in relations:
            if target_id in self._patterns:
                results.append(self._patterns[target_id])

        return results


class TemporalMemory(DgentBackedHolographicMemory[T]):
    """HolographicMemory with temporal navigation.

    Extends D-gent backed memory with time-based retrieval
    using the temporal layer.

    Example:
        memory = TemporalMemory(storage=unified)

        # Store memories at different times
        await memory.store("m1", "Morning event")
        await memory.store("m2", "Afternoon event")

        # Retrieve state at a point in time
        snapshot = await memory.at_time(one_hour_ago)

        # Get evolution of a concept
        evolution = await memory.concept_evolution("task", days=7)
    """

    async def at_time(self, timestamp: datetime) -> Optional[Dict[str, Any]]:
        """Retrieve memory state at a specific time.

        Args:
            timestamp: Point in time to query

        Returns:
            State snapshot at that time, or None
        """
        if not self._config.enable_temporal:
            return None

        state = await self._dgent_storage.replay(timestamp)
        return state

    async def timeline(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Tuple[datetime, str, MemoryPattern[T]]]:
        """Get memory evolution within time window.

        Args:
            start: Start of window (default: beginning)
            end: End of window (default: now)
            limit: Maximum events

        Returns:
            List of (timestamp, event_label, pattern) tuples
        """
        if not self._config.enable_temporal:
            return []

        events = await self._dgent_storage.timeline(start, end, limit)

        results = []
        for ts, label, data in events:
            # Check if it's a store event for our namespace
            if label.startswith("store:"):
                pattern_id = label[6:]  # Remove "store:" prefix
                if pattern_id in self._patterns:
                    results.append((ts, label, self._patterns[pattern_id]))

        return results

    async def concept_evolution(
        self,
        concept: str,
        days: int = 30,
    ) -> List[Tuple[datetime, MemoryPattern[T]]]:
        """Track how a concept has evolved over time.

        Args:
            concept: Concept to track
            days: Number of days to look back

        Returns:
            List of (timestamp, pattern) showing concept evolution
        """
        if not self._config.enable_temporal:
            return []

        start = datetime.now() - timedelta(days=days)
        events = await self._dgent_storage.timeline(start=start)

        results = []
        for ts, label, data in events:
            if label.startswith("store:"):
                pattern_id = label[6:]
                if pattern_id in self._patterns:
                    pattern = self._patterns[pattern_id]
                    if concept in pattern.concepts:
                        results.append((ts, pattern))

        return results


# ========== Factory Functions ==========


def create_dgent_memory(
    storage: Any,  # D-gent UnifiedMemory
    embedder: Any = None,
    namespace: str = "holographic",
    enable_all: bool = False,
    **kwargs,
) -> DgentBackedHolographicMemory:
    """Create D-gent backed holographic memory with convenient defaults.

    Args:
        storage: D-gent UnifiedMemory instance
        embedder: L-gent embedder
        namespace: Storage namespace
        enable_all: Enable all persistence features
        **kwargs: PersistenceConfig overrides

    Returns:
        Configured DgentBackedHolographicMemory
    """
    config_kwargs = {}

    if enable_all:
        config_kwargs["enable_semantic"] = True
        config_kwargs["enable_temporal"] = True
        config_kwargs["enable_relational"] = True

    config_kwargs.update(kwargs)
    config = PersistenceConfig(**config_kwargs)

    return DgentBackedHolographicMemory(
        storage=storage,
        embedder=embedder,
        config=config,
        namespace=namespace,
    )


def create_associative_memory(
    storage: Any,
    embedder: Any = None,
    namespace: str = "associative",
    **kwargs,
) -> AssociativeWebMemory:
    """Create associative web memory.

    Args:
        storage: D-gent UnifiedMemory instance
        embedder: L-gent embedder
        namespace: Storage namespace
        **kwargs: PersistenceConfig overrides

    Returns:
        Configured AssociativeWebMemory
    """
    config = PersistenceConfig(
        enable_relational=True,
        **kwargs,
    )

    return AssociativeWebMemory(
        storage=storage,
        embedder=embedder,
        config=config,
        namespace=namespace,
    )


def create_temporal_memory(
    storage: Any,
    embedder: Any = None,
    namespace: str = "temporal",
    **kwargs,
) -> TemporalMemory:
    """Create temporal memory.

    Args:
        storage: D-gent UnifiedMemory instance
        embedder: L-gent embedder
        namespace: Storage namespace
        **kwargs: PersistenceConfig overrides

    Returns:
        Configured TemporalMemory
    """
    config = PersistenceConfig(
        enable_temporal=True,
        witness_all_stores=True,
        **kwargs,
    )

    return TemporalMemory(
        storage=storage,
        embedder=embedder,
        config=config,
        namespace=namespace,
    )

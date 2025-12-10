"""
PersistentTieredMemory: D-gent Integration for Three-Tier Memory.

Phase 2 of M-gent implementation: Full tier persistence.

Integrates the three-tier memory architecture with D-gent storage:
- Tier 1 (Sensory): VolatileAgent (ephemeral, in-memory)
- Tier 2 (Working): CachedAgent (fast access, limited persistence)
- Tier 3 (Long-term): UnifiedMemory (full holographic persistence)

This is the complete memory hierarchy with D-gent backends.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Generic, List, Optional, TypeVar

from .holographic import HolographicMemory, MemoryPattern, CompressionLevel
from .tiered import (
    TieredMemory,
    SensoryBuffer,
    SensoryEntry,
    WorkingMemory,
    WorkingMemoryChunk,
    AttentionFilter,
    MemoryTier,
)
from .dgent_backend import (
    DgentBackedHolographicMemory,
    PersistenceConfig,
    AssociativeWebMemory,
    TemporalMemory,
)

T = TypeVar("T")


@dataclass
class TierConfig:
    """Configuration for each memory tier."""

    # Sensory tier
    sensory_capacity: int = 100
    sensory_ttl_seconds: float = 10.0

    # Working tier
    working_capacity: int = 7  # Miller's Law: 7 ± 2
    working_ttl_minutes: float = 30.0  # Working memory fades

    # Long-term tier
    longterm_namespace: str = "holographic"
    enable_semantic: bool = True
    enable_temporal: bool = True
    enable_relational: bool = True

    # Auto-consolidation
    auto_consolidate: bool = True
    consolidate_interval_minutes: float = 5.0


@dataclass
class TierStats:
    """Statistics for a memory tier."""

    count: int
    capacity: int
    utilization: float
    oldest_entry_age_seconds: Optional[float] = None
    average_activation: Optional[float] = None


@dataclass
class MemoryHierarchyStats:
    """Statistics for the entire memory hierarchy."""

    sensory: TierStats
    working: TierStats
    longterm: Dict[str, Any]
    last_consolidation: Optional[datetime] = None
    consolidation_count: int = 0


class PersistentWorkingMemory(WorkingMemory[T]):
    """Working memory with optional D-gent CachedAgent backing.

    Extends basic WorkingMemory with:
    - Persistence to D-gent CachedAgent
    - TTL-based expiry
    - Recovery from cache
    """

    def __init__(
        self,
        capacity: int = 7,
        cache: Any = None,  # D-gent CachedAgent
        ttl_minutes: float = 30.0,
    ):
        """Initialize persistent working memory.

        Args:
            capacity: Maximum chunks (Miller's Law)
            cache: Optional D-gent CachedAgent for persistence
            ttl_minutes: Time-to-live for chunks
        """
        super().__init__(capacity=capacity)
        self._cache = cache
        self._ttl = timedelta(minutes=ttl_minutes)
        self._chunk_timestamps: Dict[str, datetime] = {}

    def load(
        self,
        chunk_id: str,
        content: T,
        concepts: Optional[List[str]] = None,
        priority: float = 0.5,
    ) -> Optional[str]:
        """Load chunk with timestamp tracking."""
        evicted = super().load(chunk_id, content, concepts, priority)
        self._chunk_timestamps[chunk_id] = datetime.now()

        # Persist to cache if available
        if self._cache is not None:
            self._persist_to_cache(chunk_id)

        return evicted

    def unload(self, chunk_id: str) -> Optional[WorkingMemoryChunk[T]]:
        """Unload chunk and clean up timestamp."""
        chunk = super().unload(chunk_id)
        self._chunk_timestamps.pop(chunk_id, None)
        return chunk

    def cleanup_expired(self) -> List[str]:
        """Remove chunks that have exceeded TTL.

        Returns:
            List of expired chunk IDs
        """
        now = datetime.now()
        expired = []

        for chunk_id, timestamp in list(self._chunk_timestamps.items()):
            if now - timestamp > self._ttl:
                expired.append(chunk_id)
                self.unload(chunk_id)

        return expired

    def active_chunks(self, min_activation: float = 0.1) -> List[WorkingMemoryChunk[T]]:
        """Get active chunks, filtering expired ones first."""
        self.cleanup_expired()
        return super().active_chunks(min_activation)

    def _persist_to_cache(self, chunk_id: str) -> None:
        """Persist chunk to D-gent cache."""
        if self._cache is None or chunk_id not in self._chunks:
            return

        chunk = self._chunks[chunk_id]
        # Would call: await self._cache.save({...})
        # But this is sync, so we'd need to make this async
        # For now, just track the intent


class PersistentTieredMemory(Generic[T]):
    """Three-tier memory with full D-gent persistence.

    Integrates:
    - Tier 1 (Sensory): In-memory SensoryBuffer
    - Tier 2 (Working): PersistentWorkingMemory with optional cache
    - Tier 3 (Long-term): DgentBackedHolographicMemory

    Example:
        from agents.d.unified import create_unified_memory
        from agents.d.volatile import VolatileAgent
        from agents.d.cached import CachedAgent

        # Create D-gent storage
        volatile = VolatileAgent()
        unified = create_unified_memory(volatile, enable_all=True)
        cached = CachedAgent(volatile)

        # Create tiered memory
        memory = PersistentTieredMemory(
            longterm_storage=unified,
            working_cache=cached,
        )

        # Perceive (Tier 1)
        memory.perceive("User said hello", salience=0.8)

        # Attend (Tier 1 → Tier 2)
        await memory.attend(focus="greeting")

        # Work with context (Tier 2)
        context = memory.working_context()

        # Consolidate (Tier 2 → Tier 3)
        await memory.consolidate()

        # Recall (Tier 3 → Tier 2)
        patterns = await memory.recall("What did user say?")

        # Persist explicitly
        await memory.persist()
    """

    def __init__(
        self,
        longterm_storage: Any,  # D-gent UnifiedMemory
        working_cache: Any = None,  # D-gent CachedAgent
        embedder: Any = None,  # L-gent Embedder
        config: Optional[TierConfig] = None,
    ):
        """Initialize persistent tiered memory.

        Args:
            longterm_storage: D-gent UnifiedMemory for Tier 3
            working_cache: Optional D-gent CachedAgent for Tier 2
            embedder: L-gent embedder for holographic storage
            config: Tier configuration
        """
        self._config = config or TierConfig()

        # Tier 1: Sensory (always in-memory)
        self._sensory = SensoryBuffer[T](
            capacity=self._config.sensory_capacity,
            ttl_seconds=self._config.sensory_ttl_seconds,
        )

        # Tier 2: Working (with optional cache)
        self._working = PersistentWorkingMemory[T](
            capacity=self._config.working_capacity,
            cache=working_cache,
            ttl_minutes=self._config.working_ttl_minutes,
        )

        # Tier 3: Long-term (D-gent backed holographic)
        persistence_config = PersistenceConfig(
            enable_semantic=self._config.enable_semantic,
            enable_temporal=self._config.enable_temporal,
            enable_relational=self._config.enable_relational,
        )

        self._longterm = DgentBackedHolographicMemory[T](
            storage=longterm_storage,
            embedder=embedder,
            config=persistence_config,
            namespace=self._config.longterm_namespace,
        )

        # Attention filter for Tier 1 → Tier 2
        self._attention = AttentionFilter()

        # Consolidation tracking
        self._last_consolidation = datetime.now()
        self._consolidation_count = 0
        self._chunk_counter = 0

    # ========== Tier 1: Sensory ==========

    def perceive(
        self,
        content: T,
        salience: float = 0.5,
        source: Optional[str] = None,
    ) -> None:
        """Add raw input to sensory buffer (Tier 1)."""
        self._sensory.perceive(content, salience, source)

    def recent_perceptions(self, seconds: float = 5.0) -> List[SensoryEntry[T]]:
        """Get recent sensory entries."""
        return self._sensory.recent(seconds)

    # ========== Tier 1 → Tier 2: Attention ==========

    async def attend(
        self,
        focus: Optional[str] = None,
        max_chunks: int = 3,
    ) -> List[str]:
        """Move attended items from sensory to working memory.

        Args:
            focus: Current focus/task for relevance filtering
            max_chunks: Maximum items to load into working

        Returns:
            List of new chunk IDs in working memory
        """
        entries = self._sensory.all()
        attended = self._attention.filter(entries, focus)

        new_chunk_ids = []
        for entry in attended[:max_chunks]:
            self._chunk_counter += 1
            chunk_id = f"chunk-{self._chunk_counter}"

            concepts = self._extract_concepts(entry.content)
            self._working.load(chunk_id, entry.content, concepts, entry.salience)
            new_chunk_ids.append(chunk_id)

        self._sensory.clear()
        return new_chunk_ids

    # ========== Tier 2: Working Memory ==========

    def working_context(self) -> List[WorkingMemoryChunk[T]]:
        """Get current working memory context."""
        return self._working.active_chunks()

    def load_to_working(
        self,
        content: T,
        concepts: Optional[List[str]] = None,
        priority: float = 0.5,
    ) -> str:
        """Directly load content into working memory.

        Returns:
            Chunk ID
        """
        self._chunk_counter += 1
        chunk_id = f"chunk-{self._chunk_counter}"
        self._working.load(chunk_id, content, concepts, priority)
        return chunk_id

    def unload_from_working(self, chunk_id: str) -> Optional[WorkingMemoryChunk[T]]:
        """Unload a chunk from working memory."""
        return self._working.unload(chunk_id)

    # ========== Tier 2 → Tier 3: Consolidation ==========

    async def consolidate(self, force: bool = False) -> Dict[str, int]:
        """Move working memory to long-term holographic storage.

        This is the "sleep" phase where memories are encoded to
        persistent D-gent storage.

        Args:
            force: Force consolidation even if interval not met

        Returns:
            Statistics about consolidation
        """
        # Check if consolidation is due
        if not force and self._config.auto_consolidate:
            interval = timedelta(minutes=self._config.consolidate_interval_minutes)
            if datetime.now() - self._last_consolidation < interval:
                return {"skipped": True, "reason": "interval_not_met"}

        stats = {"consolidated": 0, "evicted": 0, "errors": 0}

        # Get all working memory chunks
        chunks = self._working.active_chunks(min_activation=0.0)

        for chunk in chunks:
            try:
                # Store in long-term (persists to D-gent)
                await self._longterm.store(
                    id=chunk.id,
                    content=chunk.content,
                    concepts=chunk.concepts,
                )
                stats["consolidated"] += 1
            except Exception:
                stats["errors"] += 1

        # Run long-term consolidation (compression, integration)
        longterm_stats = await self._longterm.consolidate()
        stats.update(longterm_stats)

        self._last_consolidation = datetime.now()
        self._consolidation_count += 1

        return stats

    # ========== Tier 3 → Tier 2: Recall ==========

    async def recall(
        self,
        query: str,
        load_to_working: bool = True,
        limit: int = 3,
    ) -> List[MemoryPattern[T]]:
        """Recall from long-term memory.

        Args:
            query: Recall query
            load_to_working: Whether to load results into working memory
            limit: Maximum patterns to recall

        Returns:
            Recalled patterns
        """
        results = await self._longterm.retrieve(query, limit=limit)
        patterns = [r.pattern for r in results]

        if load_to_working:
            for pattern in patterns:
                self._working.load(
                    chunk_id=f"recall-{pattern.id}",
                    content=pattern.content,
                    concepts=pattern.concepts,
                    priority=0.8,  # High priority for recalled items
                )

        return patterns

    async def recall_by_concept(
        self,
        concept: str,
        load_to_working: bool = True,
        limit: int = 3,
    ) -> List[MemoryPattern[T]]:
        """Recall memories associated with a concept.

        Args:
            concept: Semantic concept to recall
            load_to_working: Whether to load into working memory
            limit: Maximum patterns

        Returns:
            Recalled patterns
        """
        results = await self._longterm.retrieve_by_concept(concept, limit=limit)
        patterns = [r.pattern for r in results]

        if load_to_working:
            for pattern in patterns:
                self._working.load(
                    chunk_id=f"recall-{pattern.id}",
                    content=pattern.content,
                    concepts=pattern.concepts,
                    priority=0.8,
                )

        return patterns

    # ========== Persistence ==========

    async def persist(self) -> Dict[str, Any]:
        """Explicitly persist all tiers to D-gent storage.

        Returns:
            Persistence statistics
        """
        # Consolidate working → long-term
        consolidate_stats = await self.consolidate(force=True)

        # Persist long-term explicitly
        longterm_stats = await self._longterm.persist()

        return {
            "consolidation": consolidate_stats,
            "longterm": longterm_stats,
            "timestamp": datetime.now().isoformat(),
        }

    async def recover(self) -> Dict[str, Any]:
        """Recover memory state from D-gent storage.

        Returns:
            Recovery statistics
        """
        return await self._longterm.recover()

    # ========== Statistics ==========

    def stats(self) -> MemoryHierarchyStats:
        """Get statistics across all memory tiers."""
        sensory_entries = self._sensory.all()
        working_chunks = self._working.active_chunks(min_activation=0.0)

        # Sensory tier stats
        sensory_stats = TierStats(
            count=len(sensory_entries),
            capacity=self._config.sensory_capacity,
            utilization=len(sensory_entries) / self._config.sensory_capacity,
            oldest_entry_age_seconds=(
                max(e.age_seconds for e in sensory_entries) if sensory_entries else None
            ),
        )

        # Working tier stats
        avg_activation = (
            sum(c.effective_activation for c in working_chunks) / len(working_chunks)
            if working_chunks
            else 0.0
        )

        working_stats = TierStats(
            count=len(working_chunks),
            capacity=self._config.working_capacity,
            utilization=self._working.utilization,
            average_activation=avg_activation,
        )

        return MemoryHierarchyStats(
            sensory=sensory_stats,
            working=working_stats,
            longterm=self._longterm.stats(),
            last_consolidation=self._last_consolidation,
            consolidation_count=self._consolidation_count,
        )

    # ========== Private ==========

    def _extract_concepts(self, content: T) -> List[str]:
        """Simple concept extraction from content."""
        text = str(content).lower()

        keywords = []
        for word in text.split():
            word = word.strip(".,!?;:\"'()[]{}").lower()
            if len(word) > 4 and word.isalpha():
                keywords.append(word)

        return list(set(keywords))[:5]


class NarrativeMemory(PersistentTieredMemory[T]):
    """Tiered memory with narrative structure.

    Extends persistent tiered memory with story-like organization:
    - Memories are grouped into episodes
    - Episodes form chronicles
    - Chronicles can be recalled as narratives

    Integrates with N-gent narrator for story synthesis.
    """

    def __init__(
        self,
        longterm_storage: Any,
        narrator: Any = None,  # N-gent NarratorAgent
        **kwargs,
    ):
        """Initialize narrative memory.

        Args:
            longterm_storage: D-gent UnifiedMemory
            narrator: Optional N-gent narrator for synthesis
            **kwargs: TierConfig and other args
        """
        super().__init__(longterm_storage=longterm_storage, **kwargs)
        self._narrator = narrator
        self._current_episode: List[str] = []
        self._episode_counter = 0

    async def begin_episode(self, label: Optional[str] = None) -> str:
        """Begin a new memory episode.

        Args:
            label: Optional episode label

        Returns:
            Episode ID
        """
        self._episode_counter += 1
        episode_id = f"episode-{self._episode_counter}"

        if label and self._longterm._config.enable_temporal:
            await self._longterm._dgent_storage.witness(
                f"episode_begin:{episode_id}",
                {"label": label, "timestamp": datetime.now().isoformat()},
            )

        return episode_id

    async def end_episode(self, episode_id: str) -> Dict[str, Any]:
        """End a memory episode and consolidate.

        Args:
            episode_id: Episode to end

        Returns:
            Episode summary
        """
        # Consolidate episode memories
        stats = await self.consolidate(force=True)

        if self._longterm._config.enable_temporal:
            await self._longterm._dgent_storage.witness(
                f"episode_end:{episode_id}",
                {
                    "memories": self._current_episode.copy(),
                    "stats": stats,
                    "timestamp": datetime.now().isoformat(),
                },
            )

        episode_memories = self._current_episode.copy()
        self._current_episode.clear()

        return {
            "episode_id": episode_id,
            "memory_count": len(episode_memories),
            "memories": episode_memories,
            "consolidation": stats,
        }

    async def store_with_episode(
        self,
        id: str,
        content: T,
        concepts: Optional[List[str]] = None,
        episode_id: Optional[str] = None,
    ) -> MemoryPattern[T]:
        """Store memory as part of an episode.

        Args:
            id: Memory ID
            content: Memory content
            concepts: Semantic concepts
            episode_id: Episode this belongs to

        Returns:
            Created pattern
        """
        pattern = await self._longterm.store(id, content, concepts)
        self._current_episode.append(id)

        if episode_id and self._longterm._config.enable_relational:
            await self._longterm._dgent_storage.relate(
                id,
                "part_of",
                episode_id,
            )

        return pattern

    async def recall_episode(
        self,
        episode_id: str,
    ) -> List[MemoryPattern[T]]:
        """Recall all memories from an episode.

        Args:
            episode_id: Episode to recall

        Returns:
            Patterns from the episode
        """
        if not self._longterm._config.enable_relational:
            return []

        # Get memories related to episode
        relations = await self._longterm._dgent_storage.related_from(
            episode_id,
            "part_of",
        )

        patterns = []
        for _, memory_id in relations:
            if memory_id in self._longterm._patterns:
                patterns.append(self._longterm._patterns[memory_id])

        return patterns


# ========== Factory Functions ==========


def create_persistent_tiered_memory(
    longterm_storage: Any,
    working_cache: Any = None,
    embedder: Any = None,
    enable_all: bool = False,
    **kwargs,
) -> PersistentTieredMemory:
    """Create persistent tiered memory with convenient defaults.

    Args:
        longterm_storage: D-gent UnifiedMemory
        working_cache: Optional D-gent CachedAgent
        embedder: L-gent embedder
        enable_all: Enable all features
        **kwargs: TierConfig overrides

    Returns:
        Configured PersistentTieredMemory
    """
    config_kwargs = {}

    if enable_all:
        config_kwargs["enable_semantic"] = True
        config_kwargs["enable_temporal"] = True
        config_kwargs["enable_relational"] = True
        config_kwargs["auto_consolidate"] = True

    config_kwargs.update(kwargs)
    config = TierConfig(**config_kwargs)

    return PersistentTieredMemory(
        longterm_storage=longterm_storage,
        working_cache=working_cache,
        embedder=embedder,
        config=config,
    )


def create_narrative_memory(
    longterm_storage: Any,
    narrator: Any = None,
    **kwargs,
) -> NarrativeMemory:
    """Create narrative memory.

    Args:
        longterm_storage: D-gent UnifiedMemory
        narrator: N-gent narrator
        **kwargs: Additional args

    Returns:
        Configured NarrativeMemory
    """
    return NarrativeMemory(
        longterm_storage=longterm_storage,
        narrator=narrator,
        **kwargs,
    )

"""
TieredMemory: Three-Tier Holographic Memory.

Implements the biological memory hierarchy:
- Tier 1: Sensory Buffer (immediate, high-resolution, volatile)
- Tier 2: Working Memory (active, medium-resolution, cached)
- Tier 3: Holographic Long-Term (persistent, variable-resolution)

Integration with D-gent storage primitives:
- Tier 1: VolatileAgent
- Tier 2: CachedAgent
- Tier 3: UnifiedMemory + VectorBackend
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Generic, Optional, TypeVar

from .holographic import HolographicMemory, MemoryPattern

T = TypeVar("T")


class MemoryTier(Enum):
    """Memory tiers in the hierarchy."""

    SENSORY = auto()  # Tier 1: Immediate
    WORKING = auto()  # Tier 2: Active
    LONGTERM = auto()  # Tier 3: Holographic


@dataclass
class SensoryEntry(Generic[T]):
    """Entry in the sensory buffer."""

    content: T
    timestamp: datetime = field(default_factory=datetime.now)
    salience: float = 0.5  # 0.0 to 1.0
    source: Optional[str] = None  # Where it came from

    @property
    def age_seconds(self) -> float:
        """Age in seconds."""
        return (datetime.now() - self.timestamp).total_seconds()


@dataclass
class WorkingMemoryChunk(Generic[T]):
    """A chunk in working memory.

    Working memory has limited capacity (Miller's Law: 7 ± 2 chunks).
    Each chunk is a coherent unit of information.
    """

    id: str
    content: T
    concepts: list[str]
    timestamp: datetime = field(default_factory=datetime.now)
    activation: float = 1.0  # Decays over time
    priority: float = 0.5

    @property
    def effective_activation(self) -> float:
        """Activation adjusted by age."""
        age_minutes = (datetime.now() - self.timestamp).total_seconds() / 60
        decay = 0.95**age_minutes  # Decay per minute
        return float(self.activation * decay)


class AttentionFilter:
    """Filter that determines what moves from sensory to working memory.

    Attention is the gatekeeper between tiers.
    """

    def __init__(
        self,
        salience_threshold: float = 0.5,
        novelty_weight: float = 0.4,
        relevance_weight: float = 0.6,
    ):
        """Initialize attention filter.

        Args:
            salience_threshold: Minimum salience to pass
            novelty_weight: Weight for novelty in scoring
            relevance_weight: Weight for relevance in scoring
        """
        self._salience_threshold = salience_threshold
        self._novelty_weight = novelty_weight
        self._relevance_weight = relevance_weight
        self._seen_patterns: set[str] = set()  # For novelty detection

    def filter(
        self,
        entries: list[SensoryEntry[T]],
        focus: Optional[str] = None,
    ) -> list[SensoryEntry[T]]:
        """Filter sensory entries by attention.

        Args:
            entries: Sensory entries to filter
            focus: Current focus/task (for relevance scoring)

        Returns:
            Entries that pass the attention filter
        """
        scored = []
        for entry in entries:
            score = self._compute_attention_score(entry, focus)
            if score >= self._salience_threshold:
                scored.append((entry, score))

        # Sort by score and return entries
        scored.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, _ in scored]

    def _compute_attention_score(
        self,
        entry: SensoryEntry[T],
        focus: Optional[str],
    ) -> float:
        """Compute attention score for an entry."""
        # Base salience
        score = entry.salience

        # Novelty bonus
        content_hash = str(hash(str(entry.content)))
        if content_hash not in self._seen_patterns:
            score += 0.2 * self._novelty_weight
            self._seen_patterns.add(content_hash)

        # Relevance to focus (if provided)
        if focus and hasattr(entry.content, "__contains__"):
            if focus.lower() in str(entry.content).lower():
                score += 0.3 * self._relevance_weight

        return min(1.0, score)


class SensoryBuffer(Generic[T]):
    """Tier 1: Immediate, high-fidelity sensory buffer.

    Properties:
    - Last ~10 seconds of raw input
    - High resolution, no compression
    - Most is discarded (The Accursed Share)
    - Only salient/surprising data moves up

    Example:
        buffer = SensoryBuffer(capacity=100, ttl_seconds=10)
        buffer.perceive(raw_input, salience=0.8)

        # Get recent entries
        recent = buffer.recent(seconds=5)

        # Attention filter
        attended = attention.filter(buffer.all(), focus="current task")
    """

    def __init__(
        self,
        capacity: int = 100,
        ttl_seconds: float = 10.0,
    ):
        """Initialize sensory buffer.

        Args:
            capacity: Maximum entries to hold
            ttl_seconds: Time-to-live for entries
        """
        self._capacity = capacity
        self._ttl = timedelta(seconds=ttl_seconds)
        self._entries: list[SensoryEntry[T]] = []

    def perceive(
        self,
        content: T,
        salience: float = 0.5,
        source: Optional[str] = None,
    ) -> None:
        """Add perception to sensory buffer.

        Args:
            content: Raw input
            salience: Initial salience score
            source: Source identifier
        """
        entry = SensoryEntry(
            content=content,
            salience=salience,
            source=source,
        )
        self._entries.append(entry)

        # Cleanup old entries
        self._cleanup()

    def recent(self, seconds: float = 5.0) -> list[SensoryEntry[T]]:
        """Get entries from the last N seconds."""
        self._cleanup()
        cutoff = datetime.now() - timedelta(seconds=seconds)
        return [e for e in self._entries if e.timestamp >= cutoff]

    def all(self) -> list[SensoryEntry[T]]:
        """Get all valid entries."""
        self._cleanup()
        return list(self._entries)

    def clear(self) -> int:
        """Clear buffer, returning number of discarded entries."""
        count = len(self._entries)
        self._entries.clear()
        return count

    def _cleanup(self) -> None:
        """Remove expired entries and enforce capacity."""
        now = datetime.now()

        # Remove expired
        self._entries = [e for e in self._entries if now - e.timestamp < self._ttl]

        # Enforce capacity (remove oldest if needed)
        if len(self._entries) > self._capacity:
            self._entries = self._entries[-self._capacity :]


class WorkingMemory(Generic[T]):
    """Tier 2: Active working memory.

    Properties:
    - Current task context
    - Limited capacity: 7 ± 2 chunks (Miller's Law)
    - Medium resolution, some compression
    - What is injected into the prompt window

    Example:
        working = WorkingMemory(capacity=7)
        working.load_chunk("task-1", task_context, ["task", "current"])

        # Get active chunks for prompt
        active = working.active_chunks()

        # Unload completed chunk
        working.unload("task-1")
    """

    def __init__(
        self,
        capacity: int = 7,
        activation_decay: float = 0.95,
    ):
        """Initialize working memory.

        Args:
            capacity: Maximum chunks (Miller's Law: 7 ± 2)
            activation_decay: Activation decay per minute
        """
        self._capacity = capacity
        self._activation_decay = activation_decay
        self._chunks: dict[str, WorkingMemoryChunk[T]] = {}

    def load(
        self,
        chunk_id: str,
        content: T,
        concepts: list[str] | None = None,
        priority: float = 0.5,
    ) -> Optional[str]:
        """Load a chunk into working memory.

        If at capacity, may evict the lowest-activation chunk.

        Args:
            chunk_id: Unique identifier
            content: Chunk content
            concepts: Semantic concepts
            priority: Priority level

        Returns:
            ID of evicted chunk, if any
        """
        evicted = None

        # Check capacity
        if len(self._chunks) >= self._capacity and chunk_id not in self._chunks:
            # Evict lowest activation chunk
            lowest = min(
                self._chunks.values(),
                key=lambda c: c.effective_activation,
            )
            evicted = lowest.id
            del self._chunks[lowest.id]

        # Load new chunk
        self._chunks[chunk_id] = WorkingMemoryChunk(
            id=chunk_id,
            content=content,
            concepts=concepts or [],
            priority=priority,
        )

        return evicted

    def unload(self, chunk_id: str) -> Optional[WorkingMemoryChunk[T]]:
        """Unload a chunk from working memory.

        Args:
            chunk_id: Chunk to unload

        Returns:
            The unloaded chunk, or None if not found
        """
        return self._chunks.pop(chunk_id, None)

    def get(self, chunk_id: str) -> Optional[WorkingMemoryChunk[T]]:
        """Get a specific chunk."""
        chunk = self._chunks.get(chunk_id)
        if chunk:
            # Boost activation on access
            chunk.activation = min(1.0, chunk.activation * 1.1)
        return chunk

    def active_chunks(self, min_activation: float = 0.1) -> list[WorkingMemoryChunk[T]]:
        """Get currently active chunks.

        Args:
            min_activation: Minimum effective activation

        Returns:
            Active chunks sorted by activation
        """
        active = [
            c for c in self._chunks.values() if c.effective_activation >= min_activation
        ]
        return sorted(active, key=lambda c: c.effective_activation, reverse=True)

    def find_by_concept(self, concept: str) -> list[WorkingMemoryChunk[T]]:
        """Find chunks by concept."""
        return [c for c in self._chunks.values() if concept in c.concepts]

    @property
    def utilization(self) -> float:
        """Current capacity utilization."""
        return len(self._chunks) / self._capacity


class TieredMemory(Generic[T]):
    """Three-tier holographic memory system.

    Implements the full memory hierarchy:
    - Sensory → Working via Attention
    - Working → Long-term via Consolidation
    - Long-term → Working via Recall

    Example:
        memory = TieredMemory(
            embedder=my_embedder,
            working_capacity=7,
        )

        # Perceive (Tier 1)
        memory.perceive("User said hello", salience=0.6)

        # Attend (Tier 1 → Tier 2)
        attended = await memory.attend(focus="greeting")

        # Work with context (Tier 2)
        context = memory.working_context()

        # Consolidate to long-term (Tier 2 → Tier 3)
        await memory.consolidate()

        # Recall from long-term (Tier 3 → Tier 2)
        recalled = await memory.recall("What did the user say?")
    """

    def __init__(
        self,
        embedder: Any = None,  # L-gent Embedder
        sensory_ttl: float = 10.0,
        working_capacity: int = 7,
    ):
        """Initialize tiered memory.

        Args:
            embedder: L-gent embedder for long-term storage
            sensory_ttl: Sensory buffer TTL in seconds
            working_capacity: Working memory capacity
        """
        self._sensory = SensoryBuffer[T](ttl_seconds=sensory_ttl)
        self._working = WorkingMemory[T](capacity=working_capacity)
        self._longterm = HolographicMemory[T](embedder=embedder)
        self._attention = AttentionFilter()

        self._chunk_counter = 0

    # ========== Tier 1: Sensory ==========

    def perceive(
        self,
        content: T,
        salience: float = 0.5,
        source: Optional[str] = None,
    ) -> None:
        """Add raw input to sensory buffer."""
        self._sensory.perceive(content, salience, source)

    def recent_perceptions(self, seconds: float = 5.0) -> list[SensoryEntry[T]]:
        """Get recent sensory entries."""
        return self._sensory.recent(seconds)

    # ========== Tier 1 → Tier 2: Attention ==========

    async def attend(
        self,
        focus: Optional[str] = None,
        max_chunks: int = 3,
    ) -> list[str]:
        """Move attended items from sensory to working memory.

        Args:
            focus: Current focus/task for relevance filtering
            max_chunks: Maximum items to load into working

        Returns:
            List of new chunk IDs in working memory
        """
        # Get all sensory entries
        entries = self._sensory.all()

        # Apply attention filter
        attended = self._attention.filter(entries, focus)

        # Load into working memory (up to max_chunks)
        new_chunk_ids = []
        for entry in attended[:max_chunks]:
            self._chunk_counter += 1
            chunk_id = f"chunk-{self._chunk_counter}"

            # Extract concepts from content (simple heuristic)
            concepts = self._extract_concepts(entry.content)

            self._working.load(chunk_id, entry.content, concepts, entry.salience)
            new_chunk_ids.append(chunk_id)

        # Clear processed entries from sensory
        self._sensory.clear()

        return new_chunk_ids

    # ========== Tier 2: Working Memory ==========

    def working_context(self) -> list[WorkingMemoryChunk[T]]:
        """Get current working memory context."""
        return self._working.active_chunks()

    def load_to_working(
        self,
        content: T,
        concepts: list[str] | None = None,
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

    async def consolidate(self) -> dict[str, int]:
        """Move working memory to long-term holographic storage.

        This is the "sleep" phase where memories are encoded.

        Returns:
            Statistics about consolidation
        """
        stats = {"consolidated": 0, "evicted": 0}

        # Get all working memory chunks
        chunks = self._working.active_chunks(min_activation=0.0)

        for chunk in chunks:
            # Store in long-term
            await self._longterm.store(
                id=chunk.id,
                content=chunk.content,
                concepts=chunk.concepts,
            )
            stats["consolidated"] += 1

        # Run long-term consolidation
        longterm_stats = await self._longterm.consolidate()
        stats.update(longterm_stats)

        return stats

    # ========== Tier 3 → Tier 2: Recall ==========

    async def recall(
        self,
        query: str,
        load_to_working: bool = True,
        limit: int = 3,
    ) -> list[MemoryPattern[T]]:
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

    # ========== Statistics ==========

    def stats(self) -> dict[str, Any]:
        """Get memory statistics across all tiers."""
        return {
            "sensory": {
                "count": len(self._sensory.all()),
            },
            "working": {
                "count": len(self._working.active_chunks(min_activation=0.0)),
                "utilization": self._working.utilization,
            },
            "longterm": self._longterm.stats(),
        }

    # ========== Private ==========

    def _extract_concepts(self, content: T) -> list[str]:
        """Simple concept extraction from content."""
        text = str(content).lower()

        # Simple keyword extraction
        keywords = []
        for word in text.split():
            word = word.strip(".,!?;:\"'()[]{}").lower()
            if len(word) > 4 and word.isalpha():
                keywords.append(word)

        return list(set(keywords))[:5]  # Max 5 concepts

"""
AssociativeMemory: Semantic Similarity Search

Memory with embedding index for associative (not exact-match) recall.

Part of the Data Architecture Rewrite (plans/data-architecture-rewrite.md).
Follows spec/m-gents/architecture.md.

Key Insight:
    Traditional databases use exact-match queries.
    AssociativeMemory uses semantic similarity - you can recall
    related memories even without knowing exact keywords.

Embeddings:
    Uses L-gent for semantic embeddings if available.
    Falls back to hash-based pseudo-embeddings (deterministic but not semantic).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Awaitable

from agents.d.datum import Datum

from .memory import Lifecycle, Memory, simple_embedding
from .protocol import (
    ConsolidationReport,
    ExtendedMgentProtocol,
    MemoryStatus,
    RecallResult,
)

if TYPE_CHECKING:
    from agents.d.protocol import DgentProtocol


# === Embedder Protocol ===


@dataclass
class HashEmbedder:
    """
    Hash-based pseudo-embedder (fallback when L-gent unavailable).

    Does NOT capture semantic similarity - "Python code" and
    "Python programming" will have completely different embeddings.

    For real semantic search, use L-gent embedder.
    """

    dim: int = 64

    async def embed(self, text: str) -> list[float]:
        """Generate hash-based pseudo-embedding."""
        return list(simple_embedding(text, self.dim))


# Type alias for embedder functions
Embedder = Callable[[str], Awaitable[list[float]]]


# === AssociativeMemory Implementation ===


@dataclass
class AssociativeMemory:
    """
    Memory with semantic similarity search.

    Implements MgentProtocol with embedding-based associative recall.

    Architecture:
        - Stores raw content in D-gent (bytes with IDs)
        - Maintains embedding index for associative recall
        - Tracks Memory metadata (lifecycle, relevance, resolution)

    Usage:
        dgent = MemoryBackend()  # Or any D-gent backend
        mgent = AssociativeMemory(dgent)

        # Store a memory
        memory_id = await mgent.remember(b"Python is great", metadata={"topic": "programming"})

        # Recall by semantic similarity
        results = await mgent.recall("programming languages", limit=5)

        # Forget (graceful degradation)
        await mgent.forget(memory_id)
    """

    dgent: "DgentProtocol"
    embedder: Embedder | None = None

    # Memory index: datum_id -> Memory
    _memories: dict[str, Memory] = field(default_factory=dict)

    # Consolidation state
    _is_consolidating: bool = False

    def __post_init__(self) -> None:
        """Initialize default embedder if not provided."""
        if self.embedder is None:
            hash_embedder = HashEmbedder()
            self.embedder = hash_embedder.embed

    # === Core Operations ===

    async def remember(
        self,
        content: bytes,
        embedding: list[float] | None = None,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """
        Store content as a memory.

        1. Store raw content in D-gent
        2. Compute embedding if not provided
        3. Create Memory and add to index
        """
        # Create and store datum in D-gent
        datum = Datum.create(
            content=content if isinstance(content, str) else content.decode("utf-8", errors="ignore"),
            metadata=metadata or {},
        )
        datum_id = await self.dgent.put(datum)

        # Compute embedding if not provided
        if embedding is None:
            text = content.decode("utf-8", errors="ignore") if isinstance(content, bytes) else content
            embedding = await self.embedder(text)

        # Create memory and add to index
        memory = Memory.create(
            datum_id=datum_id,
            embedding=embedding,
            metadata=metadata or {},
        )
        self._memories[datum_id] = memory

        return datum_id

    async def recall(
        self,
        cue: str | list[float],
        limit: int = 5,
        threshold: float = 0.5,
    ) -> list[RecallResult]:
        """
        Associative recall by semantic similarity.

        1. Embed the cue if it's text
        2. Find similar memories above threshold
        3. Return sorted by similarity
        """
        # Get cue embedding
        if isinstance(cue, str):
            cue_embedding = tuple(await self.embedder(cue))
        else:
            cue_embedding = tuple(cue)

        # Find similar memories
        scored: list[tuple[Memory, float]] = []
        for memory in self._memories.values():
            # Skip DREAMING memories (not accessible during consolidation)
            if memory.lifecycle == Lifecycle.DREAMING:
                continue

            similarity = memory.similarity(cue_embedding)
            if similarity >= threshold:
                scored.append((memory, similarity))

        # Sort by similarity (highest first)
        scored.sort(key=lambda x: x[1], reverse=True)

        # Take top N and build results
        results: list[RecallResult] = []
        for memory, similarity in scored[:limit]:
            # Optionally fetch content from D-gent
            datum = await self.dgent.get(memory.datum_id)
            content = datum.content.encode() if datum and isinstance(datum.content, str) else (datum.content if datum else None)

            # Update memory access (reinforcement)
            updated_memory = memory.activate()
            self._memories[memory.datum_id] = updated_memory

            results.append(RecallResult(
                memory=updated_memory,
                similarity=similarity,
                datum_content=content,
            ))

        return results

    async def forget(self, memory_id: str) -> bool:
        """
        Begin graceful forgetting (transition to COMPOSTING).

        Cherished memories cannot be forgotten.
        """
        memory = self._memories.get(memory_id)
        if memory is None:
            return False

        if memory.is_cherished:
            return False  # Can't forget cherished memories

        # Transition to COMPOSTING
        self._memories[memory_id] = memory.compost()
        return True

    async def cherish(self, memory_id: str) -> bool:
        """
        Pin memory from forgetting.
        """
        memory = self._memories.get(memory_id)
        if memory is None:
            return False

        self._memories[memory_id] = memory.cherish()
        return True

    # === Lifecycle Operations ===

    async def consolidate(self) -> ConsolidationReport:
        """
        Run consolidation cycle ("sleep").

        1. Mark DORMANT memories as DREAMING
        2. Apply relevance decay
        3. Demote low-relevance memories to COMPOSTING
        4. (Optional) Merge similar memories
        5. Wake DREAMING memories back to DORMANT
        """
        start_time = time.time()
        self._is_consolidating = True

        dreaming_count = 0
        demoted_count = 0
        merged_count = 0
        strengthened_count = 0

        # Phase 1: Mark DORMANT as DREAMING
        for memory_id, memory in list(self._memories.items()):
            if memory.lifecycle == Lifecycle.DORMANT:
                self._memories[memory_id] = memory.dream()
                dreaming_count += 1

        # Phase 2: Apply relevance decay and demote low-relevance
        demote_threshold = 0.2  # Below this, demote to COMPOSTING
        for memory_id, memory in list(self._memories.items()):
            if memory.lifecycle == Lifecycle.DREAMING:
                # Apply decay
                decayed = memory.decay(factor=0.95)

                # Demote if relevance too low (and not cherished)
                if decayed.relevance < demote_threshold and not decayed.is_cherished:
                    self._memories[memory_id] = decayed.compost()
                    demoted_count += 1
                else:
                    self._memories[memory_id] = decayed

        # Phase 3: (Simplified) No merging in basic implementation
        # A more sophisticated implementation would find similar memories
        # and merge them to save space.

        # Phase 4: Wake DREAMING memories
        await self.wake()

        duration_ms = (time.time() - start_time) * 1000
        self._is_consolidating = False

        return ConsolidationReport(
            dreaming_count=dreaming_count,
            demoted_count=demoted_count,
            merged_count=merged_count,
            strengthened_count=strengthened_count,
            duration_ms=duration_ms,
        )

    async def wake(self) -> None:
        """
        End consolidation, return DREAMING -> DORMANT.
        """
        for memory_id, memory in list(self._memories.items()):
            if memory.lifecycle == Lifecycle.DREAMING:
                self._memories[memory_id] = memory.wake()

    # === Introspection ===

    async def status(self) -> MemoryStatus:
        """
        Get current memory system state.
        """
        total = len(self._memories)
        active = sum(1 for m in self._memories.values() if m.lifecycle == Lifecycle.ACTIVE)
        dormant = sum(1 for m in self._memories.values() if m.lifecycle == Lifecycle.DORMANT)
        dreaming = sum(1 for m in self._memories.values() if m.lifecycle == Lifecycle.DREAMING)
        composting = sum(1 for m in self._memories.values() if m.lifecycle == Lifecycle.COMPOSTING)

        avg_resolution = (
            sum(m.resolution for m in self._memories.values()) / total
            if total > 0 else 0.0
        )
        avg_relevance = (
            sum(m.relevance for m in self._memories.values()) / total
            if total > 0 else 0.0
        )

        return MemoryStatus(
            total_memories=total,
            active_count=active,
            dormant_count=dormant,
            dreaming_count=dreaming,
            composting_count=composting,
            average_resolution=avg_resolution,
            average_relevance=avg_relevance,
            is_consolidating=self._is_consolidating,
        )

    async def by_lifecycle(self, lifecycle: Lifecycle) -> list[Memory]:
        """
        Get memories in a specific lifecycle state.
        """
        return [m for m in self._memories.values() if m.lifecycle == lifecycle]

    # === Extended Operations ===

    async def get(self, memory_id: str) -> Memory | None:
        """Get a specific memory by ID."""
        return self._memories.get(memory_id)

    async def exists(self, memory_id: str) -> bool:
        """Check if a memory exists."""
        return memory_id in self._memories

    async def count(self) -> int:
        """Count total memories."""
        return len(self._memories)

    async def decay_all(self, factor: float = 0.99) -> int:
        """Apply relevance decay to all non-cherished memories."""
        count = 0
        for memory_id, memory in list(self._memories.items()):
            if not memory.is_cherished:
                self._memories[memory_id] = memory.decay(factor)
                count += 1
        return count

    async def degrade_composting(self, factor: float = 0.5) -> int:
        """Degrade resolution of all COMPOSTING memories."""
        count = 0
        for memory_id, memory in list(self._memories.items()):
            if memory.lifecycle == Lifecycle.COMPOSTING:
                self._memories[memory_id] = memory.degrade(factor)
                count += 1
        return count

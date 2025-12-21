"""
MgentProtocol: The M-gent Interface

Seven core methods for intelligent memory management.

Part of the Data Architecture Rewrite (plans/data-architecture-rewrite.md).
Follows spec/m-gents/architecture.md.

The Protocol:
    remember(content, embedding?, metadata?) -> str   # Store content as memory
    recall(cue, limit?, threshold?) -> list[Memory]  # Associative retrieval
    forget(memory_id) -> bool                        # Begin graceful forgetting
    cherish(memory_id) -> bool                       # Pin from forgetting
    consolidate() -> ConsolidationReport             # Sleep cycle
    wake() -> None                                   # End consolidation
    status() -> MemoryStatus                         # Introspection

Relationship to D-gent:
    M-gent builds ON D-gent. Every Memory references an underlying Datum.
    M-gent NEVER bypasses D-gent - all data flows through D-gent's projection lattice.

Teaching:
    gotcha: forget() returns False for cherished memories - they're protected
            Call cherish() to pin important memories from the forgetting cycle.
            This is intentional: cherished memories have relevance=1.0 and can't compost.
            (Evidence: test_associative.py::TestForget::test_forget_cherished_returns_false)

    gotcha: recall() reinforces accessed memories (increases access_count)
            Every recall is a touch - relevance increases through repeated access.
            This is the stigmergy pattern: use strengthens memory.
            (Evidence: test_associative.py::TestRecall::test_recall_reinforces_memory)

    gotcha: ACTIVE -> COMPOSTING is INVALID transition (must go through DORMANT)
            Lifecycle transitions have strict rules. Memory must be DORMANT
            before it can be demoted to COMPOSTING during consolidation.
            (Evidence: test_lifecycle.py::TestValidTransitions::test_active_to_composting_invalid)

    gotcha: Consolidation applies relevance decay to non-cherished memories only
            Cherished memories keep relevance=1.0 through sleep cycles.
            Use cherish() sparingly - it's a commitment to preserve.
            (Evidence: test_consolidation_engine.py::TestConsolidationBasic::test_consolidate_protects_cherished)

    gotcha: similarity() returns 0.0 for mismatched embedding dimensions
            If you mix embeddings of different sizes, comparisons silently fail.
            Ensure all embeddings use consistent dimension (e.g., 64 for HashEmbedder).
            (Evidence: test_memory.py::TestSimilarity::test_similarity_mismatched_dimensions)

    gotcha: Memory.embedding is a tuple, not list (converted on creation)
            Pass list to create(), get tuple back. This ensures hashability.
            (Evidence: test_memory.py::TestMemoryCreation::test_embedding_list_to_tuple)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from .memory import Lifecycle, Memory

if TYPE_CHECKING:
    from agents.d.protocol import DgentProtocol


# === Result Types ===


@dataclass(frozen=True, slots=True)
class ConsolidationReport:
    """
    Report from a consolidation ("sleep") cycle.

    Consolidation reorganizes memories:
    - Demotes low-relevance memories (DORMANT -> COMPOSTING)
    - Merges similar memories
    - Strengthens associations between related memories
    - Recomputes embeddings with updated context
    """

    dreaming_count: int  # Memories that entered DREAMING
    demoted_count: int  # Memories demoted to COMPOSTING
    merged_count: int  # Memories merged with similar ones
    strengthened_count: int  # Cross-references strengthened
    duration_ms: float = 0.0  # Time taken for consolidation

    @property
    def summary(self) -> str:
        """Human-readable summary."""
        return (
            f"Consolidated {self.dreaming_count} memories: "
            f"{self.demoted_count} demoted, {self.merged_count} merged, "
            f"{self.strengthened_count} strengthened ({self.duration_ms:.1f}ms)"
        )


@dataclass(frozen=True, slots=True)
class MemoryStatus:
    """
    Current state of the memory system.
    """

    total_memories: int
    active_count: int
    dormant_count: int
    dreaming_count: int
    composting_count: int
    average_resolution: float
    average_relevance: float
    is_consolidating: bool = False

    @property
    def summary(self) -> str:
        """Human-readable summary."""
        return (
            f"Memories: {self.total_memories} "
            f"(A:{self.active_count} D:{self.dormant_count} "
            f"Dr:{self.dreaming_count} C:{self.composting_count})"
        )


@dataclass
class RecallResult:
    """
    Result from a recall operation.

    Includes the memory and its similarity score to the query cue.
    """

    memory: Memory
    similarity: float
    datum_content: bytes | None = None  # Optionally includes D-gent content

    @property
    def is_strong_match(self) -> bool:
        """Is this a strong match (>= 0.8 similarity)?"""
        return self.similarity >= 0.8


# === The Protocol ===


@runtime_checkable
class MgentProtocol(Protocol):
    """
    The interface for intelligent memory management.

    Built on top of DgentProtocol.
    Seven core methods, plus introspection.

    Implementation Notes:
        - remember() stores content in D-gent AND indexes embedding
        - recall() uses semantic similarity, not exact match
        - forget() transitions to COMPOSTING, doesn't delete
        - cherish() pins relevance to 1.0
        - consolidate() runs during "sleep", reorganizes memories
        - wake() ends consolidation, returns DREAMING -> DORMANT
        - status() returns current memory state
    """

    # === Core Operations ===

    async def remember(
        self,
        content: bytes,
        embedding: list[float] | None = None,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """
        Store content as a memory.

        If embedding not provided, will be computed via L-gent (if available)
        or fallback to hash-based pseudo-embedding.

        Args:
            content: Raw content to store
            embedding: Optional semantic embedding vector
            metadata: Optional metadata dict

        Returns:
            Memory ID (same as underlying Datum ID)
        """
        ...

    async def recall(
        self,
        cue: str | list[float],
        limit: int = 5,
        threshold: float = 0.5,
    ) -> list[RecallResult]:
        """
        Associative recall by semantic similarity.

        Args:
            cue: Text query (will be embedded) or embedding vector
            limit: Maximum memories to return
            threshold: Minimum similarity threshold [0, 1]

        Returns:
            Memories sorted by similarity (highest first)
        """
        ...

    async def forget(self, memory_id: str) -> bool:
        """
        Begin graceful forgetting (transition to COMPOSTING).

        Memory is not deleted - it degrades gracefully over time.
        Cherished memories cannot be forgotten.

        Args:
            memory_id: ID of memory to forget

        Returns:
            True if memory transitioned to COMPOSTING
        """
        ...

    async def cherish(self, memory_id: str) -> bool:
        """
        Pin memory from forgetting (high relevance, won't compost).

        Cherished memories have relevance = 1.0 and are protected
        from the forgetting cycle.

        Args:
            memory_id: ID of memory to cherish

        Returns:
            True if memory was cherished
        """
        ...

    # === Lifecycle Operations ===

    async def consolidate(self) -> ConsolidationReport:
        """
        Run consolidation cycle ("sleep").

        During consolidation:
        1. DORMANT memories transition to DREAMING (not accessible)
        2. Low-relevance memories are demoted (DREAMING -> COMPOSTING)
        3. Similar memories are merged
        4. Cross-references between related memories are strengthened
        5. Embeddings may be recomputed with updated context
        6. DREAMING memories return to DORMANT

        Returns:
            Report of consolidation actions
        """
        ...

    async def wake(self) -> None:
        """
        End consolidation, return DREAMING -> DORMANT.

        Called automatically at end of consolidate(), but can be
        called explicitly to interrupt consolidation.
        """
        ...

    # === Introspection ===

    async def status(self) -> MemoryStatus:
        """
        Get current memory system state.

        Returns:
            MemoryStatus with counts and averages
        """
        ...

    async def by_lifecycle(self, lifecycle: Lifecycle) -> list[Memory]:
        """
        Get memories in a specific lifecycle state.

        Args:
            lifecycle: The lifecycle state to filter by

        Returns:
            List of memories in that state
        """
        ...


# === Additional Optional Methods ===


class ExtendedMgentProtocol(MgentProtocol, Protocol):
    """
    Extended protocol with additional convenience methods.

    These are optional - implementations may provide them
    but the core 7 methods are sufficient.
    """

    async def get(self, memory_id: str) -> Memory | None:
        """Get a specific memory by ID."""
        ...

    async def exists(self, memory_id: str) -> bool:
        """Check if a memory exists."""
        ...

    async def count(self) -> int:
        """Count total memories."""
        ...

    async def decay_all(self, factor: float = 0.99) -> int:
        """Apply relevance decay to all non-cherished memories."""
        ...

    async def degrade_composting(self, factor: float = 0.5) -> int:
        """Degrade resolution of all COMPOSTING memories."""
        ...

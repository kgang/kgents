"""
SoulMemory: K-gent Identity Continuity via M-gent

K-gent uses M-gent for identity persistence across sessions.
This module provides the wiring between K-gent's soul and M-gent's memory.

Part of the Data Architecture Rewrite (plans/data-architecture-rewrite.md).
Follows spec/m-gents/architecture.md.

Key Insight:
    The soul needs different memory categories:
    - Beliefs: Core values, permanently cherished
    - Session Context: Conversation history, may compost
    - Creative Seeds: Experiments, low relevance, ephemeral
    - Patterns: Behavioral patterns Kent exhibits

Memory Tiers for K-gent:
    BELIEF (cherished=True): Never forgets, always high relevance
    PATTERN (cherished=False): Decays but can be reinforced
    CONTEXT (cherished=False): Session-specific, may compost
    SEED (cherished=False): Creative experiments, most ephemeral
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from .memory import Lifecycle, Memory
from .protocol import RecallResult

if TYPE_CHECKING:
    from .associative import AssociativeMemory


class MemoryCategory(Enum):
    """Categories of K-gent memories."""

    BELIEF = "belief"  # Core values, principles
    PATTERN = "pattern"  # Behavioral patterns
    CONTEXT = "context"  # Session context
    SEED = "seed"  # Creative experiments


@dataclass
class BeliefMemory:
    """
    A cherished belief in K-gent's soul.
    """

    memory_id: str
    content: str
    category: MemoryCategory = MemoryCategory.BELIEF
    tags: list[str] = field(default_factory=list)

    @property
    def is_principle(self) -> bool:
        """Is this a core principle?"""
        return "principle" in self.tags

    @property
    def is_preference(self) -> bool:
        """Is this a preference?"""
        return "preference" in self.tags


@dataclass
class ContextMemory:
    """
    Session context in K-gent's soul.
    """

    memory_id: str
    content: str
    session_id: str
    category: MemoryCategory = MemoryCategory.CONTEXT


@dataclass
class PatternMemory:
    """
    A behavioral pattern K-gent has observed.
    """

    memory_id: str
    pattern: str
    frequency: int = 1
    category: MemoryCategory = MemoryCategory.PATTERN


# === Soul Memory Interface ===


class SoulMemory:
    """
    K-gent's use of M-gent for identity continuity.

    Provides higher-level abstractions for soul-specific memory needs:
    - Beliefs that are always cherished
    - Session context that may fade
    - Patterns that strengthen with use
    - Creative seeds for experimentation

    Usage:
        mgent = AssociativeMemory(dgent)
        soul_memory = SoulMemory(mgent)

        # Store a core belief (always cherished)
        belief_id = await soul_memory.remember_belief(
            "Simplicity is the ultimate sophistication",
            tags=["principle", "aesthetic"]
        )

        # Store session context (may fade)
        await soul_memory.remember_context(
            "User is working on the data architecture rewrite",
            session_id="session-123"
        )

        # Recall relevant context
        results = await soul_memory.recall_for_topic("data persistence")
    """

    def __init__(self, mgent: "AssociativeMemory") -> None:
        self.mgent = mgent

    # === Beliefs (Cherished) ===

    async def remember_belief(
        self,
        belief: str,
        tags: list[str] | None = None,
    ) -> BeliefMemory:
        """
        Store a core belief (automatically cherished).

        Beliefs never compost - they are the soul's foundation.

        Args:
            belief: The belief content
            tags: Optional tags for categorization

        Returns:
            BeliefMemory with the stored belief
        """
        tags = tags or []

        memory_id = await self.mgent.remember(
            belief.encode("utf-8"),
            metadata={
                "category": MemoryCategory.BELIEF.value,
                "tags": ",".join(tags),
            },
        )

        # Cherish immediately - beliefs never fade
        await self.mgent.cherish(memory_id)

        return BeliefMemory(
            memory_id=memory_id,
            content=belief,
            tags=tags,
        )

    async def get_beliefs(self) -> list[BeliefMemory]:
        """
        Get all cherished beliefs.

        Returns all memories marked as beliefs.
        """
        beliefs: list[BeliefMemory] = []

        for memory_id, memory in self.mgent._memories.items():
            if memory.is_cherished:
                category = memory.metadata.get("category", "")
                if category == MemoryCategory.BELIEF.value:
                    # Fetch content from D-gent
                    datum = await self.mgent.dgent.get(memory_id)
                    content = datum.content if datum else ""
                    tags_str = memory.metadata.get("tags", "")
                    tags = tags_str.split(",") if tags_str else []

                    beliefs.append(BeliefMemory(
                        memory_id=memory_id,
                        content=content,
                        tags=tags,
                    ))

        return beliefs

    async def reinforce_belief(self, memory_id: str) -> bool:
        """
        Reinforce a belief (increase its relevance).

        While beliefs are already cherished, reinforcement
        tracks how often they're invoked.
        """
        memory = await self.mgent.get(memory_id)
        if memory is None:
            return False

        # Apply reinforcement
        reinforced = memory.reinforce(boost=0.1)
        self.mgent._memories[memory_id] = reinforced
        return True

    # === Patterns (Decaying) ===

    async def remember_pattern(
        self,
        pattern: str,
        initial_relevance: float = 0.7,
    ) -> PatternMemory:
        """
        Store a behavioral pattern.

        Patterns decay over time unless reinforced.

        Args:
            pattern: Description of the pattern
            initial_relevance: Starting relevance (default 0.7)

        Returns:
            PatternMemory with the stored pattern
        """
        memory_id = await self.mgent.remember(
            pattern.encode("utf-8"),
            metadata={
                "category": MemoryCategory.PATTERN.value,
                "frequency": "1",
            },
        )

        # Set initial relevance (not cherished, will decay)
        memory = self.mgent._memories[memory_id]
        adjusted = Memory(
            datum_id=memory.datum_id,
            embedding=memory.embedding,
            resolution=memory.resolution,
            lifecycle=memory.lifecycle,
            relevance=initial_relevance,
            last_accessed=memory.last_accessed,
            access_count=memory.access_count,
            metadata=memory.metadata,
        )
        self.mgent._memories[memory_id] = adjusted

        return PatternMemory(
            memory_id=memory_id,
            pattern=pattern,
        )

    async def reinforce_pattern(self, memory_id: str) -> bool:
        """
        Reinforce a pattern (increase frequency + relevance).

        Patterns that are reinforced often become stronger.
        """
        memory = await self.mgent.get(memory_id)
        if memory is None:
            return False

        # Update frequency in metadata
        freq = int(memory.metadata.get("frequency", "1"))
        new_metadata = {**memory.metadata, "frequency": str(freq + 1)}

        # Apply reinforcement with larger boost for patterns
        reinforced = memory.reinforce(boost=0.15)
        updated = Memory(
            datum_id=reinforced.datum_id,
            embedding=reinforced.embedding,
            resolution=reinforced.resolution,
            lifecycle=reinforced.lifecycle,
            relevance=reinforced.relevance,
            last_accessed=reinforced.last_accessed,
            access_count=reinforced.access_count,
            metadata=new_metadata,
        )
        self.mgent._memories[memory_id] = updated
        return True

    async def get_active_patterns(self, limit: int = 10) -> list[PatternMemory]:
        """
        Get the most active patterns (highest relevance).
        """
        patterns: list[tuple[PatternMemory, float]] = []

        for memory_id, memory in self.mgent._memories.items():
            category = memory.metadata.get("category", "")
            if category == MemoryCategory.PATTERN.value:
                if memory.lifecycle in (Lifecycle.ACTIVE, Lifecycle.DORMANT):
                    datum = await self.mgent.dgent.get(memory_id)
                    content = datum.content if datum else ""
                    freq = int(memory.metadata.get("frequency", "1"))

                    pm = PatternMemory(
                        memory_id=memory_id,
                        pattern=content,
                        frequency=freq,
                    )
                    patterns.append((pm, memory.relevance))

        # Sort by relevance and take top N
        patterns.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in patterns[:limit]]

    # === Context (Session-Specific) ===

    async def remember_context(
        self,
        context: str,
        session_id: str,
        initial_relevance: float = 0.8,
    ) -> ContextMemory:
        """
        Store session context.

        Context is tied to a session and decays faster than patterns.

        Args:
            context: The context content
            session_id: ID of the current session
            initial_relevance: Starting relevance (default 0.8)

        Returns:
            ContextMemory with the stored context
        """
        memory_id = await self.mgent.remember(
            context.encode("utf-8"),
            metadata={
                "category": MemoryCategory.CONTEXT.value,
                "session_id": session_id,
            },
        )

        # Set initial relevance
        memory = self.mgent._memories[memory_id]
        adjusted = Memory(
            datum_id=memory.datum_id,
            embedding=memory.embedding,
            resolution=memory.resolution,
            lifecycle=memory.lifecycle,
            relevance=initial_relevance,
            last_accessed=memory.last_accessed,
            access_count=memory.access_count,
            metadata=memory.metadata,
        )
        self.mgent._memories[memory_id] = adjusted

        return ContextMemory(
            memory_id=memory_id,
            content=context,
            session_id=session_id,
        )

    async def get_session_context(
        self,
        session_id: str,
        limit: int = 20,
    ) -> list[ContextMemory]:
        """
        Get context memories for a specific session.
        """
        context_mems: list[tuple[ContextMemory, float]] = []

        for memory_id, memory in self.mgent._memories.items():
            category = memory.metadata.get("category", "")
            sid = memory.metadata.get("session_id", "")

            if category == MemoryCategory.CONTEXT.value and sid == session_id:
                if memory.lifecycle != Lifecycle.COMPOSTING:
                    datum = await self.mgent.dgent.get(memory_id)
                    content = datum.content if datum else ""

                    cm = ContextMemory(
                        memory_id=memory_id,
                        content=content,
                        session_id=session_id,
                    )
                    context_mems.append((cm, memory.last_accessed))

        # Sort by recency
        context_mems.sort(key=lambda x: x[1], reverse=True)
        return [c for c, _ in context_mems[:limit]]

    # === Seeds (Creative Experiments) ===

    async def plant_seed(
        self,
        idea: str,
        initial_relevance: float = 0.4,
    ) -> str:
        """
        Plant a creative seed (experimental idea).

        Seeds have low initial relevance and will fade quickly
        unless explicitly reinforced.

        Returns memory_id for the seed.
        """
        memory_id = await self.mgent.remember(
            idea.encode("utf-8"),
            metadata={
                "category": MemoryCategory.SEED.value,
            },
        )

        # Set low initial relevance
        memory = self.mgent._memories[memory_id]
        adjusted = Memory(
            datum_id=memory.datum_id,
            embedding=memory.embedding,
            resolution=memory.resolution,
            lifecycle=memory.lifecycle,
            relevance=initial_relevance,
            last_accessed=memory.last_accessed,
            access_count=memory.access_count,
            metadata=memory.metadata,
        )
        self.mgent._memories[memory_id] = adjusted

        return memory_id

    async def grow_seed(self, memory_id: str) -> bool:
        """
        Grow a seed (convert to pattern if reinforced enough).

        If seed relevance reaches 0.7, it becomes a pattern.
        """
        memory = await self.mgent.get(memory_id)
        if memory is None:
            return False

        category = memory.metadata.get("category", "")
        if category != MemoryCategory.SEED.value:
            return False

        # Reinforce the seed
        reinforced = memory.reinforce(boost=0.2)

        # Check if seed should graduate to pattern
        if reinforced.relevance >= 0.7:
            new_metadata = {
                **reinforced.metadata,
                "category": MemoryCategory.PATTERN.value,
                "frequency": "1",
            }
            graduated = Memory(
                datum_id=reinforced.datum_id,
                embedding=reinforced.embedding,
                resolution=reinforced.resolution,
                lifecycle=reinforced.lifecycle,
                relevance=reinforced.relevance,
                last_accessed=reinforced.last_accessed,
                access_count=reinforced.access_count,
                metadata=new_metadata,
            )
            self.mgent._memories[memory_id] = graduated
        else:
            self.mgent._memories[memory_id] = reinforced

        return True

    # === Associative Recall ===

    async def recall_for_topic(
        self,
        topic: str | list[float],
        limit: int = 10,
        include_seeds: bool = False,
    ) -> list[RecallResult]:
        """
        Recall memories relevant to a topic.

        Args:
            topic: Text query (will be embedded) or embedding vector
            limit: Maximum memories to return
            include_seeds: Whether to include seed memories

        By default excludes seeds (ephemeral experiments).
        """
        results = await self.mgent.recall(topic, limit=limit * 2, threshold=0.5)

        if not include_seeds:
            results = [
                r for r in results
                if r.memory.metadata.get("category") != MemoryCategory.SEED.value
            ]

        return results[:limit]

    async def recall_beliefs_for_decision(
        self,
        decision: str,
        limit: int = 5,
    ) -> list[BeliefMemory]:
        """
        Recall beliefs relevant to a decision.

        Used for ethical reasoning and principle-based decision making.
        """
        # First, get general recall
        results = await self.mgent.recall(decision, limit=20)

        # Filter to beliefs only
        beliefs: list[BeliefMemory] = []
        for result in results:
            if result.memory.is_cherished:
                category = result.memory.metadata.get("category", "")
                if category == MemoryCategory.BELIEF.value:
                    content = result.datum_content.decode("utf-8") if result.datum_content else ""
                    tags_str = result.memory.metadata.get("tags", "")
                    tags = tags_str.split(",") if tags_str else []

                    beliefs.append(BeliefMemory(
                        memory_id=result.memory.datum_id,
                        content=content,
                        tags=tags,
                    ))

        return beliefs[:limit]

    # === Identity Status ===

    async def identity_status(self) -> dict[str, Any]:
        """
        Get status of K-gent's identity memory.

        Returns counts by category and lifecycle.
        """
        status = await self.mgent.status()

        # Count by category
        categories: dict[str, int] = {c.value: 0 for c in MemoryCategory}
        for memory in self.mgent._memories.values():
            category = memory.metadata.get("category", "unknown")
            if category in categories:
                categories[category] += 1

        return {
            "total": status.total_memories,
            "active": status.active_count,
            "dormant": status.dormant_count,
            "composting": status.composting_count,
            "by_category": categories,
            "cherished": sum(
                1 for m in self.mgent._memories.values() if m.is_cherished
            ),
            "avg_relevance": status.average_relevance,
        }


# === Factory ===


def create_soul_memory(mgent: "AssociativeMemory") -> SoulMemory:
    """Create a SoulMemory instance."""
    return SoulMemory(mgent)

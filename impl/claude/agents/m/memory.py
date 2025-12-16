"""
Memory: The Core M-gent Dataclass

A Memory is a Datum enriched with semantic meaning and lifecycle.

Part of the Data Architecture Rewrite (plans/data-architecture-rewrite.md).
Follows spec/m-gents/architecture.md.

Key Distinction:
    Datum (D-gent): bytes + id + timestamp + metadata (raw storage)
    Memory (M-gent): datum_id + embedding + resolution + lifecycle + relevance (meaning)

M-gent builds ON D-gent. Every Memory references an underlying Datum.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Lifecycle(Enum):
    """
    Memory lifecycle states.

    The lifecycle represents the "health" of a memory:
    - ACTIVE: In working memory, high resolution, frequently accessed
    - DORMANT: Saved to storage, normal resolution, occasionally accessed
    - DREAMING: Being reorganized during "sleep" cycles, not accessible
    - COMPOSTING: Resolution degrading, still retrievable but lossy
    """

    ACTIVE = "active"
    DORMANT = "dormant"
    DREAMING = "dreaming"
    COMPOSTING = "composting"


@dataclass(frozen=True, slots=True)
class Memory:
    """
    A Memory is a Datum enriched with semantic meaning and lifecycle.

    Attributes:
        datum_id: Reference to the underlying D-gent Datum
        embedding: Semantic vector for associative recall
        resolution: Fidelity level [0.0, 1.0] - graceful degradation
        lifecycle: Current lifecycle state
        relevance: Importance score [0.0, 1.0] - decays without reinforcement
        last_accessed: Unix timestamp of last access
        access_count: Number of times this memory has been accessed (reinforcement)
        metadata: Optional metadata dict

    Invariants:
        - 0.0 <= resolution <= 1.0
        - 0.0 <= relevance <= 1.0
        - embedding is immutable tuple, not list
    """

    datum_id: str
    embedding: tuple[float, ...]  # Immutable for hashability
    resolution: float = 1.0
    lifecycle: Lifecycle = Lifecycle.ACTIVE
    relevance: float = 1.0
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate memory fields."""
        # Validate resolution
        if not 0.0 <= self.resolution <= 1.0:
            object.__setattr__(
                self, "resolution", max(0.0, min(1.0, self.resolution))
            )

        # Validate relevance
        if not 0.0 <= self.relevance <= 1.0:
            object.__setattr__(
                self, "relevance", max(0.0, min(1.0, self.relevance))
            )

        # Convert embedding list to tuple if needed
        if isinstance(self.embedding, list):
            object.__setattr__(self, "embedding", tuple(self.embedding))

        # Ensure metadata is a dict (not mutable default issue with frozen)
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})

    @classmethod
    def create(
        cls,
        datum_id: str,
        embedding: list[float] | tuple[float, ...],
        resolution: float = 1.0,
        lifecycle: Lifecycle = Lifecycle.ACTIVE,
        relevance: float = 1.0,
        metadata: dict[str, str] | None = None,
    ) -> Memory:
        """
        Factory method to create a Memory.

        Handles list → tuple conversion for embedding.
        """
        return cls(
            datum_id=datum_id,
            embedding=tuple(embedding) if isinstance(embedding, list) else embedding,
            resolution=resolution,
            lifecycle=lifecycle,
            relevance=relevance,
            last_accessed=time.time(),
            access_count=0,
            metadata=metadata or {},
        )

    # === Lifecycle Transitions ===

    def activate(self) -> Memory:
        """Transition to ACTIVE state (recall)."""
        return Memory(
            datum_id=self.datum_id,
            embedding=self.embedding,
            resolution=self.resolution,
            lifecycle=Lifecycle.ACTIVE,
            relevance=self.relevance,
            last_accessed=time.time(),
            access_count=self.access_count + 1,
            metadata=self.metadata,
        )

    def deactivate(self) -> Memory:
        """Transition to DORMANT state (timeout)."""
        return Memory(
            datum_id=self.datum_id,
            embedding=self.embedding,
            resolution=self.resolution,
            lifecycle=Lifecycle.DORMANT,
            relevance=self.relevance,
            last_accessed=self.last_accessed,
            access_count=self.access_count,
            metadata=self.metadata,
        )

    def dream(self) -> Memory:
        """Transition to DREAMING state (consolidation)."""
        return Memory(
            datum_id=self.datum_id,
            embedding=self.embedding,
            resolution=self.resolution,
            lifecycle=Lifecycle.DREAMING,
            relevance=self.relevance,
            last_accessed=self.last_accessed,
            access_count=self.access_count,
            metadata=self.metadata,
        )

    def wake(self) -> Memory:
        """Transition from DREAMING to DORMANT."""
        if self.lifecycle != Lifecycle.DREAMING:
            return self
        return Memory(
            datum_id=self.datum_id,
            embedding=self.embedding,
            resolution=self.resolution,
            lifecycle=Lifecycle.DORMANT,
            relevance=self.relevance,
            last_accessed=self.last_accessed,
            access_count=self.access_count,
            metadata=self.metadata,
        )

    def compost(self) -> Memory:
        """Transition to COMPOSTING state (forgetting)."""
        return Memory(
            datum_id=self.datum_id,
            embedding=self.embedding,
            resolution=self.resolution,
            lifecycle=Lifecycle.COMPOSTING,
            relevance=self.relevance,
            last_accessed=self.last_accessed,
            access_count=self.access_count,
            metadata=self.metadata,
        )

    # === Resolution & Relevance ===

    def degrade(self, factor: float = 0.5) -> Memory:
        """
        Reduce resolution by factor (graceful degradation).

        Memory degrades gracefully, not catastrophically:
        - resolution 1.0: Full fidelity
        - resolution 0.5: Summary only
        - resolution 0.1: Title only
        - resolution 0.0: Only causal trace remains
        """
        new_resolution = max(0.0, self.resolution * factor)
        return Memory(
            datum_id=self.datum_id,
            embedding=self.embedding,
            resolution=new_resolution,
            lifecycle=self.lifecycle,
            relevance=self.relevance,
            last_accessed=self.last_accessed,
            access_count=self.access_count,
            metadata=self.metadata,
        )

    def reinforce(self, boost: float = 0.1) -> Memory:
        """
        Increase relevance (reinforcement learning).

        Called when memory is accessed or explicitly reinforced.
        """
        new_relevance = min(1.0, self.relevance + boost)
        return Memory(
            datum_id=self.datum_id,
            embedding=self.embedding,
            resolution=self.resolution,
            lifecycle=self.lifecycle,
            relevance=new_relevance,
            last_accessed=time.time(),
            access_count=self.access_count + 1,
            metadata=self.metadata,
        )

    def decay(self, factor: float = 0.99) -> Memory:
        """
        Decay relevance over time.

        Relevance naturally decays without reinforcement.
        """
        new_relevance = max(0.0, self.relevance * factor)
        return Memory(
            datum_id=self.datum_id,
            embedding=self.embedding,
            resolution=self.resolution,
            lifecycle=self.lifecycle,
            relevance=new_relevance,
            last_accessed=self.last_accessed,
            access_count=self.access_count,
            metadata=self.metadata,
        )

    def cherish(self) -> Memory:
        """
        Pin memory from forgetting (max relevance).

        Cherished memories won't compost.
        """
        return Memory(
            datum_id=self.datum_id,
            embedding=self.embedding,
            resolution=self.resolution,
            lifecycle=self.lifecycle,
            relevance=1.0,
            last_accessed=time.time(),
            access_count=self.access_count,
            metadata={**self.metadata, "cherished": "true"},
        )

    @property
    def is_cherished(self) -> bool:
        """Check if memory is cherished (pinned from forgetting)."""
        return self.metadata.get("cherished") == "true"

    # === Semantic Operations ===

    def similarity(self, other_embedding: tuple[float, ...] | list[float]) -> float:
        """
        Compute cosine similarity with another embedding.

        Returns value in [-1, 1], where 1 = identical, 0 = orthogonal.
        """
        if isinstance(other_embedding, list):
            other_embedding = tuple(other_embedding)

        if len(self.embedding) != len(other_embedding):
            return 0.0

        dot_product = sum(a * b for a, b in zip(self.embedding, other_embedding))
        norm_a = sum(a * a for a in self.embedding) ** 0.5
        norm_b = sum(b * b for b in other_embedding) ** 0.5

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    # === Serialization ===

    def to_dict(self) -> dict[str, Any]:
        """Serialize memory to dict for JSON storage."""
        return {
            "datum_id": self.datum_id,
            "embedding": list(self.embedding),
            "resolution": self.resolution,
            "lifecycle": self.lifecycle.value,
            "relevance": self.relevance,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Memory:
        """Deserialize memory from dict."""
        return cls(
            datum_id=data["datum_id"],
            embedding=tuple(data["embedding"]),
            resolution=data.get("resolution", 1.0),
            lifecycle=Lifecycle(data.get("lifecycle", "dormant")),
            relevance=data.get("relevance", 1.0),
            last_accessed=data.get("last_accessed", time.time()),
            access_count=data.get("access_count", 0),
            metadata=data.get("metadata", {}),
        )


# === Helper: Simple Hash Embedder ===


def simple_embedding(text: str, dim: int = 64) -> tuple[float, ...]:
    """
    Generate simple hash-based embedding (NO semantic similarity).

    This is a fallback when L-gent embedder is not available.
    Hash-based embeddings are deterministic but DO NOT capture
    semantic similarity.

    For real semantic search, use L-gent embedder.
    """
    h = hashlib.sha256(text.encode()).digest()
    # Convert bytes to floats in [-1, 1] range
    values = [(b - 128) / 128.0 for b in h[:dim]]
    # Pad if needed
    while len(values) < dim:
        values.extend(values)
    return tuple(values[:dim])

"""
V-gent: Vector Agents for Semantic Search.

> *"V-gent is geometry. It maps meaning to distance."*

V-gent provides semantic vector operations as a dedicated agent genus:
- Vector storage and retrieval
- Similarity search
- Metadata filtering
- Backend abstraction (memory, D-gent, pgvector, Qdrant)

V-gent is embedding-agnostic—it stores and searches vectors, not creates them.

Key Types:
    - Embedding: A semantic vector with dimension and metadata
    - VectorEntry: A vector stored in an index with its identifier
    - SearchResult: Result from a vector search

Protocol:
    - VgentProtocol: The minimal interface every V-gent backend implements
    - BaseVgent: Base class with default implementations

Backends:
    - MemoryVectorBackend: In-memory (Tier 0)
    - DgentVectorBackend: D-gent persisted (Tier 1) [Phase 2]
    - PostgresVectorBackend: pgvector (Tier 2) [Phase 6]
    - QdrantBackend: Qdrant (Tier 3) [Phase 6]

Usage:
    from agents.v import VgentProtocol, MemoryVectorBackend, Embedding, DistanceMetric

    # Create a memory backend
    backend = MemoryVectorBackend(dimension=768)

    # Add vectors
    await backend.add("doc1", [0.1, 0.2, ...])

    # Search
    results = await backend.search([0.1, 0.2, ...], limit=10)

See Also:
    - spec/v-gents/core.md — Core protocol and types
    - spec/v-gents/backends.md — Backend implementations
    - spec/v-gents/integrations.md — L-gent, M-gent integration
"""

from __future__ import annotations

from .protocol import BaseVgent, VgentProtocol
from .types import DistanceMetric, Embedding, SearchResult, VectorEntry

# Backends
from .backends.memory import MemoryVectorBackend

__all__ = [
    # Types
    "Embedding",
    "VectorEntry",
    "SearchResult",
    "DistanceMetric",
    # Protocol
    "VgentProtocol",
    "BaseVgent",
    # Backends
    "MemoryVectorBackend",
]

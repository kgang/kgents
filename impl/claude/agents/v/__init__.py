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
    - DgentVectorBackend: D-gent persisted (Tier 1)
    - PostgresVectorBackend: pgvector (Tier 2) [Phase 6]
    - QdrantBackend: Qdrant (Tier 3) [Phase 6]

Router:
    - VgentRouter: Auto-selects best backend with graceful degradation
    - create_vgent: Factory function for creating routers

Usage:
    # Simple: Use the router (auto-selects best backend)
    from agents.v import create_vgent

    vgent = create_vgent(dimension=768)
    await vgent.add("doc1", [0.1, 0.2, ...])
    results = await vgent.search([0.1, 0.2, ...], limit=10)

    # Direct backend: Memory (ephemeral)
    from agents.v import MemoryVectorBackend

    backend = MemoryVectorBackend(dimension=768)
    await backend.add("doc1", [0.1, 0.2, ...])

    # Direct backend: D-gent persistence (Tier 1)
    from agents.d import DgentRouter
    from agents.v import DgentVectorBackend

    dgent = DgentRouter()
    backend = DgentVectorBackend(dgent, dimension=768)
    await backend.load_index()  # Load persisted vectors

See Also:
    - spec/v-gents/core.md — Core protocol and types
    - spec/v-gents/backends.md — Backend implementations
    - spec/v-gents/integrations.md — L-gent, M-gent integration
"""

from __future__ import annotations

# Backends
from .backends.dgent import DgentVectorBackend
from .backends.memory import MemoryVectorBackend
from .protocol import BaseVgent, VgentProtocol

# Router
from .router import BackendStatus, VectorBackend, VgentRouter, create_vgent
from .types import DistanceMetric, Embedding, SearchResult, VectorEntry

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
    "DgentVectorBackend",
    # Router
    "VgentRouter",
    "VectorBackend",
    "BackendStatus",
    "create_vgent",
]

"""
V-gent Backends: The Projection Lattice for Vectors.

> *"Same search, different plumbing."*

Backend Tiers:
    - Tier 0: MemoryVectorBackend (ephemeral, fast)
    - Tier 1: DgentVectorBackend (D-gent persisted)
    - Tier 2: PostgresVectorBackend (pgvector, required)
    - Tier 3: QdrantBackend (dedicated vector DB) [Phase 6]

Note: pgvector is required for PostgresVectorBackend.
"""

from __future__ import annotations

from .dgent import DgentVectorBackend
from .memory import MemoryVectorBackend
from .postgres import PostgresVectorBackend

__all__ = [
    "MemoryVectorBackend",
    "DgentVectorBackend",
    "PostgresVectorBackend",
]

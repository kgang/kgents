"""
V-gent Backends: The Projection Lattice for Vectors.

> *"Same search, different plumbing."*

Backend Tiers:
    - Tier 0: MemoryVectorBackend (ephemeral, fast)
    - Tier 1: DgentVectorBackend (D-gent persisted)
    - Tier 2: PostgresVectorBackend (pgvector) [Phase 6]
    - Tier 3: QdrantBackend (dedicated vector DB) [Phase 6]

Graceful Degradation:
    If preferred backend unavailable, descend the lattice.
    Memory is always the last resort.
"""

from __future__ import annotations

from .dgent import DgentVectorBackend
from .memory import MemoryVectorBackend

__all__ = [
    "MemoryVectorBackend",
    "DgentVectorBackend",
]

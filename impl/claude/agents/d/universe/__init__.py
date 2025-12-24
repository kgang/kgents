"""
Universe: D-gent's unified data management domain.

The Universe provides a higher-level interface over DgentProtocol for services
that work with typed objects (Crystal, Mark, etc.) while maintaining schema-free
storage underneath.

Quick Start:
    >>> from agents.d.universe import get_universe, init_universe
    >>>
    >>> # Singleton pattern (lazy init)
    >>> universe = get_universe()
    >>> await universe.store(crystal)
    >>>
    >>> # Explicit initialization
    >>> universe = await init_universe(backend="postgres")
    >>> await universe.store(crystal)

Schema Registration:
    >>> from services.witness.crystal import Crystal
    >>> universe = get_universe()
    >>> universe.register_type("crystal", Crystal)
    >>> crystal_id = await universe.store(crystal)
    >>> retrieved = await universe.get(crystal_id)  # Returns Crystal

See: agents/d/universe/universe.py
"""

from .universe import (
    Backend,
    DataclassSchema,
    Query,
    Schema,
    Universe,
    UniverseStats,
    get_universe,
    init_universe,
)

__all__ = [
    # Core
    "Universe",
    "get_universe",
    "init_universe",
    # Schema
    "Schema",
    "DataclassSchema",
    # Query
    "Query",
    # Backend
    "Backend",
    # Stats
    "UniverseStats",
]

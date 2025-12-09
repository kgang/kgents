"""
L-gents: Synaptic Librarian

The ecosystem's knowledge graph and artifact registry.
Three layers: Registry (what exists) → Lineage (where from) → Lattice (how fits).

Core components:
- CatalogEntry: Artifact metadata
- Registry: Indexed collection of entries
- Search: Three-brain semantic + keyword + graph search
- Lineage: Provenance and evolution tracking
- Lattice: Type compatibility and composition planning
"""

from .catalog import CatalogEntry, EntityType, Status, Registry
from .search import Search, SearchResult, SearchStrategy

# Hypothesis Indexing (Cross-pollination T2.10)
from .hypothesis_indexing import (
    HypothesisIndex,
    HypothesisRecord,
    HypothesisOutcome,
    HypothesisSearchQuery,
    HypothesisSearchResult,
    HypothesisPatternAnalysis,
    bgent_hypothesis_to_record,
)

__all__ = [
    "CatalogEntry",
    "EntityType",
    "Status",
    "Registry",
    "Search",
    "SearchResult",
    "SearchStrategy",
    # Hypothesis Indexing (Cross-pollination T2.10)
    "HypothesisIndex",
    "HypothesisRecord",
    "HypothesisOutcome",
    "HypothesisSearchQuery",
    "HypothesisSearchResult",
    "HypothesisPatternAnalysis",
    "bgent_hypothesis_to_record",
]

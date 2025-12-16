"""
Gallery: Persistence layer for Tiny Atelier.

Stores pieces with full provenance for later retrieval and lineage tracking.
"""

from agents.atelier.gallery.lineage import LineageGraph
from agents.atelier.gallery.store import Gallery

__all__ = ["Gallery", "LineageGraph"]

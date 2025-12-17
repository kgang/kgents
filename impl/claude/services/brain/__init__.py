"""
Brain Crown Jewel: Spatial Cathedral of Memory.

The Brain is a holographic memory system that stores crystallized knowledge
with both queryable metadata (Alembic tables) and semantic content (D-gent).

AGENTESE Paths (via @node("self.memory")):
- self.memory.manifest  - Brain health status
- self.memory.capture   - Store content with semantic embedding
- self.memory.search    - Semantic search for similar memories
- self.memory.surface   - Serendipity from the void
- self.memory.get       - Get specific crystal by ID
- self.memory.recent    - List recent crystals
- self.memory.bytag     - List crystals by tag
- self.memory.delete    - Delete a crystal
- self.memory.heal      - Heal ghost memories

Dual-Track Storage:
- SQLAlchemy tables (models/brain.py) - Fast queries by tag, recency, access
- D-gent datums - Semantic search, associative connections

The Metaphysical Fullstack Pattern (AD-009):
- BrainNode wraps BrainPersistence as AGENTESE node
- Universal gateway auto-exposes all aspects
- No explicit routes needed

See: docs/skills/metaphysical-fullstack.md
"""

from .node import (
    BrainManifestRendering,
    BrainNode,
    CaptureRendering,
    SearchRendering,
)
from .persistence import (
    BrainPersistence,
    BrainStatus,
    CaptureResult,
    SearchResult,
)

__all__ = [
    # Node (AGENTESE interface)
    "BrainNode",
    "BrainManifestRendering",
    "CaptureRendering",
    "SearchRendering",
    # Persistence (domain logic)
    "BrainPersistence",
    "BrainStatus",
    "CaptureResult",
    "SearchResult",
]

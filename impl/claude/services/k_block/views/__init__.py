"""K-Block Views: Hyperdimensional rendering of canonical content.

Views are projections of the same underlying content into different
modalities. The Prose view is canonical; others derive from it.

Phase 3: Bidirectional editing via semantic transforms.

Architecture (Bidirectional model):

    PROSE (Canonical) ◄──► GRAPH (bidirectional)
                      ◄──► CODE (bidirectional)
                      ◄──► OUTLINE (bidirectional)
                      ───► DIFF (read-only, from base_content)

Edit in any view; semantic deltas propagate to all others.
"""

from .base import View, ViewDelta, ViewType, create_view
from .references import (
    Reference,
    ReferenceKind,
    ReferencesView,
    discover_references,
)
from .sync import (
    BidirectionalSync,
    CodeTransform,
    GraphTransform,
    OutlineTransform,
    SemanticDelta,
    TransformRegistry,
    ViewTransform,
)
from .tokens import SemanticToken, TokenKind

__all__ = [
    # Core types
    "View",
    "ViewType",
    "ViewDelta",
    "create_view",
    # Token types
    "SemanticToken",
    "TokenKind",
    # Phase 3: Bidirectional sync
    "SemanticDelta",
    "ViewTransform",
    "GraphTransform",
    "CodeTransform",
    "OutlineTransform",
    "TransformRegistry",
    "BidirectionalSync",
    # Phase 3: Loose references
    "Reference",
    "ReferenceKind",
    "ReferencesView",
    "discover_references",
]

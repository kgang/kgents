"""K-Block Views: Hyperdimensional rendering of canonical content.

Views are projections of the same underlying content into different
modalities. The Prose view is canonical; others derive from it.

Architecture (Prose-canonical model):

    PROSE (Canonical) ──┬──► GRAPH (derived)
                        ├──► CODE (derived)
                        ├──► OUTLINE (derived)
                        └──► DIFF (read-only, from base_content)
"""

from .base import View, ViewDelta, ViewType, create_view
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
]

"""
Gallery Agent: Living Autopoietic Showcase.

The Gallery demonstrates the kgents categorical ground by being a vertical slice itself.
See: spec/gallery/gallery-v2.md

Provides:
- GalleryPolynomial: State machine for gallery navigation
- GALLERY_OPERAD: Composition grammar for gallery operations
"""

from .operad import (
    GALLERY_OPERAD,
)
from .polynomial import (
    GALLERY_POLYNOMIAL,
    GalleryPhase,
    gallery_visualization,
)

__all__ = [
    # Polynomial
    "GalleryPhase",
    "GALLERY_POLYNOMIAL",
    "gallery_visualization",
    # Operad
    "GALLERY_OPERAD",
]

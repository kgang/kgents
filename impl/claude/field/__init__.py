"""
The Holographic Field - Hyperdimensional Computing Memory.

This module implements HDC-based distributed memory that enables
"Morphic Resonance" - cross-agent learning without explicit message passing.

Key Components:
- HolographicField: The main HDC memory class
- hdc_ops: Primitive HDC operations (bind, bundle, permute)

AGENTESE Integration:
- field.resonate: Query similarity to global field
- field.imprint: Add pattern to superposition
- field.bind: Role-filler binding
- field.bundle: Compose multiple patterns
"""

from .hdc_ops import (
    hdc_bind,
    hdc_bundle,
    hdc_permute,
    hdc_similarity,
    random_hd_vector,
)
from .holographic import (
    DIMENSIONS,
    GLOBAL_HOLOGRAM,
    HolographicField,
    Vector,
)

__all__ = [
    "HolographicField",
    "DIMENSIONS",
    "Vector",
    "GLOBAL_HOLOGRAM",
    "hdc_bind",
    "hdc_bundle",
    "hdc_permute",
    "hdc_similarity",
    "random_hd_vector",
]

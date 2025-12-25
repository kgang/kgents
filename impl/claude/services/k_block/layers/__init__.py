"""
K-Block Layer Factories: Zero Seed L1-L7 K-Block Creation.

Provides factory functions for creating K-Blocks at each Zero Seed layer,
with proper lineage tracking and layer-specific defaults.

Philosophy:
    "Each layer has its own confidence, its own lineage, its own truth."

Layers:
- L1: Axioms (no lineage, confidence=1.0)
- L2: Values (derives from axioms, confidence=0.95)
- L3: Goals (derives from values, confidence=0.90)
- L4: Specs (derives from goals, confidence=0.85)
- L5: Actions (derives from specs, confidence=0.80)
- L6: Reflections (derives from actions, confidence=0.75)
- L7: Representations (derives from any layer, confidence varies)

See: spec/protocols/zero-seed1/layers.md
"""

from .classifier import (
    LAYER_CONFIDENCE,
    LAYER_NAMES,
    LAYER_THRESHOLDS,
    classify_crystal,
    classify_layer,
    get_layer_confidence,
    get_layer_name,
)
from .factories import (
    ActionKBlockFactory,
    AxiomKBlockFactory,
    GoalKBlockFactory,
    ReflectionKBlockFactory,
    RepresentationKBlockFactory,
    SpecKBlockFactory,
    ValueKBlockFactory,
    ZeroSeedKBlockFactory,
)

__all__ = [
    # Factories
    "ZeroSeedKBlockFactory",
    "AxiomKBlockFactory",
    "ValueKBlockFactory",
    "GoalKBlockFactory",
    "SpecKBlockFactory",
    "ActionKBlockFactory",
    "ReflectionKBlockFactory",
    "RepresentationKBlockFactory",
    # Classifier
    "classify_layer",
    "classify_crystal",
    "get_layer_name",
    "get_layer_confidence",
    "LAYER_THRESHOLDS",
    "LAYER_NAMES",
    "LAYER_CONFIDENCE",
]

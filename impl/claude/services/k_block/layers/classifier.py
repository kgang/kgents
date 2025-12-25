"""
Layer Classifier - Assigns Zero Seed layers based on Galois loss convergence.

Layers are DERIVED from restructuring depth, not stipulated:
- L1-L2: Axiomatic (loss < 0.15 after 0-1 restructurings)
- L3-L4: Specifications (loss < 0.45 after 2-3 restructurings)
- L5-L6: Actions/Reflections (loss < 0.75 after 4-5 restructurings)
- L7: Representations (doesn't converge quickly)

Philosophy:
    "The axiom knows itself. The representation needs interpretation."

Integration with Galois Loss:
    Lower loss = more axiomatic = lower layer
    Higher loss = more representational = higher layer

Example:
    >>> from agents.d.galois import GaloisLossComputer
    >>> galois = GaloisLossComputer(metric="token")
    >>> layer = await classify_layer("Earth is round", galois)
    >>> print(layer)  # Low loss -> L1 or L2 (axiomatic)
    1
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agents.d.galois import GaloisLossComputer
    from agents.d.crystal import Crystal


# Loss thresholds per layer (from spec/protocols/zero-seed.md)
LAYER_THRESHOLDS = [
    (0.05, 1),  # L1: Axioms (loss < 0.05) - nearly perfect coherence
    (0.15, 2),  # L2: Values (loss < 0.15) - high coherence
    (0.30, 3),  # L3: Goals (loss < 0.30) - moderate coherence
    (0.45, 4),  # L4: Specs (loss < 0.45) - acceptable coherence
    (0.60, 5),  # L5: Actions (loss < 0.60) - lower coherence
    (0.75, 6),  # L6: Reflections (loss < 0.75) - minimal coherence
    (1.00, 7),  # L7: Representations (loss >= 0.75) - doesn't converge
]


async def classify_layer(
    content: str,
    galois: "GaloisLossComputer | None" = None,
) -> int:
    """
    Classify content into Zero Seed layer based on Galois loss.

    Uses Galois loss to determine epistemic layer:
    - Lower loss = more axiomatic = lower layer (L1-L2)
    - Higher loss = more representational = higher layer (L6-L7)

    Args:
        content: String content to classify
        galois: GaloisLossComputer instance (if None, assumes L4)

    Returns:
        Layer number (1-7)

    Example:
        >>> from agents.d.galois import GaloisLossComputer
        >>> galois = GaloisLossComputer(metric="token")
        >>> layer = await classify_layer("All humans are mortal", galois)
        >>> print(layer)  # Likely L1 or L2 (axiomatic)
        1
    """
    if galois is None:
        # Fallback: assume L4 (spec-level) without Galois
        # This is a conservative default for unclassified content
        return 4

    # Compute Galois loss
    loss = await galois.compute(content)

    # Find layer by threshold
    for threshold, layer in LAYER_THRESHOLDS:
        if loss < threshold:
            return layer

    # Default to highest layer (shouldn't reach here)
    return 7


async def classify_crystal(
    crystal: "Crystal[Any]",
    galois: "GaloisLossComputer | None" = None,
) -> int:
    """
    Classify a Crystal into Zero Seed layer.

    Extracts content from crystal value, then classifies.

    Args:
        crystal: Crystal to classify
        galois: GaloisLossComputer instance (if None, assumes L4)

    Returns:
        Layer number (1-7)

    Example:
        >>> from agents.d.schemas.witness import WITNESS_MARK_SCHEMA, WitnessMark
        >>> from agents.d.crystal import Crystal
        >>> from agents.d.galois import GaloisLossComputer
        >>>
        >>> mark = WitnessMark(action="test", reasoning="example")
        >>> crystal = Crystal.create(mark, WITNESS_MARK_SCHEMA)
        >>> galois = GaloisLossComputer()
        >>> layer = await classify_crystal(crystal, galois)
    """
    # Extract content from crystal value
    value = crystal.value

    # Try different content extraction strategies
    if hasattr(value, "action") and hasattr(value, "reasoning"):
        # WitnessMark-like structure
        content = f"{value.action}. {value.reasoning}"
    elif hasattr(value, "content"):
        # Content-like structure
        content = value.content
    elif hasattr(value, "title") and hasattr(value, "body"):
        # Document-like structure
        content = f"{value.title}. {value.body}"
    else:
        # Generic: use string representation
        content = str(value)

    # Classify using extracted content
    return await classify_layer(content, galois)


# Layer names for display (from spec/protocols/zero-seed.md)
LAYER_NAMES = {
    1: "Axiom",
    2: "Value",
    3: "Goal",
    4: "Specification",
    5: "Action",
    6: "Reflection",
    7: "Representation",
}


def get_layer_name(layer: int) -> str:
    """
    Get human-readable layer name.

    Args:
        layer: Layer number (1-7)

    Returns:
        Layer name string

    Example:
        >>> get_layer_name(1)
        'Axiom'
        >>> get_layer_name(7)
        'Representation'
    """
    return LAYER_NAMES.get(layer, "Unknown")


# Layer confidence defaults (from K-Block factories)
LAYER_CONFIDENCE = {
    1: 1.00,  # Axioms: perfect confidence
    2: 0.95,  # Values: near-perfect confidence
    3: 0.90,  # Goals: high confidence
    4: 0.85,  # Specs: good confidence
    5: 0.80,  # Actions: moderate confidence
    6: 0.75,  # Reflections: lower confidence
    7: 0.70,  # Representations: variable confidence
}


def get_layer_confidence(layer: int) -> float:
    """
    Get default confidence for a layer.

    Args:
        layer: Layer number (1-7)

    Returns:
        Default confidence score (0.0-1.0)

    Example:
        >>> get_layer_confidence(1)
        1.0
        >>> get_layer_confidence(7)
        0.7
    """
    return LAYER_CONFIDENCE.get(layer, 0.50)


__all__ = [
    "classify_layer",
    "classify_crystal",
    "get_layer_name",
    "get_layer_confidence",
    "LAYER_THRESHOLDS",
    "LAYER_NAMES",
    "LAYER_CONFIDENCE",
]

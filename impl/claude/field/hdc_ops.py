"""
Hyperdimensional Computing (HDC) Primitive Operations.

These are the core operations for Vector Symbolic Architectures (VSA):
- bind: Circular convolution (role-filler association)
- bundle: Normalized sum (superposition)
- permute: Rotation (sequence encoding)
- similarity: Cosine similarity

Mathematical Foundation:
- In high dimensions (D=10,000+), random vectors are nearly orthogonal
- bind(a, b) produces a vector orthogonal to both a and b
- bundle([a, b, c]) produces a vector similar to all inputs
- permute encodes position in sequences

References:
- Kanerva (2009): Hyperdimensional Computing
- Kleyko et al (2021): Vector Symbolic Architectures
"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

# Standard HDC dimensionality - high enough for near-orthogonality
DIMENSIONS = 10_000

# Type alias for HD vectors
Vector = NDArray[np.floating[Any]]


def random_hd_vector(dimensions: int = DIMENSIONS, seed: int | None = None) -> Vector:
    """
    Generate a random HD vector (normalized).

    Random HD vectors are nearly orthogonal with high probability.
    Expected cosine similarity between random vectors ≈ 0 with std ≈ 1/sqrt(D).

    Args:
        dimensions: Vector dimensionality (default: 10,000)
        seed: Optional random seed for reproducibility

    Returns:
        Normalized random vector of shape (dimensions,)
    """
    if seed is not None:
        rng = np.random.default_rng(seed)
    else:
        rng = np.random.default_rng()

    vec = rng.standard_normal(dimensions)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec


def hdc_bind(a: Vector, b: Vector) -> Vector:
    """
    Bind two vectors using circular convolution.

    This creates a role-filler association. The result is:
    - Nearly orthogonal to both a and b (new concept in high-D)
    - Commutative: bind(a, b) = bind(b, a)
    - Associative: bind(a, bind(b, c)) = bind(bind(a, b), c)

    Note: Circular convolution is NOT self-inverse. Use hdc_unbind
    for recovering fillers from bound vectors.

    Implementation uses FFT for O(n log n) convolution.

    Args:
        a: First HD vector
        b: Second HD vector

    Returns:
        Bound vector (same dimensionality)

    Example:
        >>> house = random_hd_vector()
        >>> architect = random_hd_vector()
        >>> house_architect = hdc_bind(house, architect)
        >>> # house_architect is nearly orthogonal to both in high-D
    """
    # Circular convolution via FFT
    result = np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)).real
    return result.astype(np.float64)


def hdc_bundle(vectors: list[Vector], normalize: bool = True) -> Vector:
    """
    Bundle multiple vectors into a superposition.

    The result is similar to all input vectors - it represents
    "something like all of these". This is the HDC equivalent of
    set union or disjunction.

    Properties:
    - Similar to all inputs (above-chance cosine similarity)
    - Graceful degradation (can bundle thousands of vectors)
    - Order-independent (commutative)

    Args:
        vectors: List of HD vectors to bundle
        normalize: Whether to normalize the result (default: True)

    Returns:
        Bundled vector (superposition)

    Example:
        >>> cat = random_hd_vector(seed=1)
        >>> dog = random_hd_vector(seed=2)
        >>> animal = hdc_bundle([cat, dog])
        >>> # animal is similar to both cat and dog
        >>> hdc_similarity(animal, cat) > 0.3
        True
    """
    if not vectors:
        raise ValueError("Cannot bundle empty list of vectors")

    result: Vector = np.sum(vectors, axis=0)

    if normalize:
        norm = np.linalg.norm(result)
        if norm > 0:
            result = result / norm

    return result


def hdc_permute(v: Vector, n: int = 1) -> Vector:
    """
    Permute vector for sequence position encoding.

    Permutation encodes order in sequences. P(v, 0) = v,
    P(v, 1) = first position, P(v, 2) = second position, etc.

    The permutation is a fixed random rotation that:
    - Produces orthogonal results: similarity(P(v, i), P(v, j)) ≈ 0 for i ≠ j
    - Is invertible: P(P(v, n), -n) = v

    Args:
        v: HD vector to permute
        n: Number of positions to shift (can be negative for inverse)

    Returns:
        Permuted vector

    Example:
        >>> word = random_hd_vector(seed=1)
        >>> word_pos0 = hdc_permute(word, 0)  # First position
        >>> word_pos1 = hdc_permute(word, 1)  # Second position
        >>> # Different positions are orthogonal
        >>> abs(hdc_similarity(word_pos0, word_pos1)) < 0.1
        True
    """
    if n == 0:
        return v.copy()

    # Use cyclic shift (rotation) as permutation
    # This is deterministic and invertible
    return np.roll(v, n)


def hdc_similarity(a: Vector, b: Vector) -> float:
    """
    Compute cosine similarity between two HD vectors.

    Returns value in [-1, 1] where:
    - 1.0 = identical
    - 0.0 = orthogonal (unrelated)
    - -1.0 = opposite

    For random HD vectors, expected similarity ≈ 0 with std ≈ 1/sqrt(D).

    Args:
        a: First HD vector
        b: Second HD vector

    Returns:
        Cosine similarity in [-1, 1]
    """
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))


def hdc_unbind(bound: Vector, role: Vector) -> Vector:
    """
    Unbind a role from a bound vector to recover the filler.

    For circular convolution binding, unbinding uses circular correlation
    (convolution with the time-reversed signal).

    bind(a, b) = ifft(fft(a) * fft(b))
    unbind(c, a) = ifft(fft(c) * conj(fft(a))) = correlation

    Args:
        bound: The bound vector (role ⊛ filler where ⊛ is convolution)
        role: The role to unbind

    Returns:
        Approximate filler vector
    """
    # Circular correlation: unbind using conjugate of role's FFT
    # This is the inverse operation for circular convolution
    result = np.fft.ifft(np.fft.fft(bound) * np.conj(np.fft.fft(role))).real
    return result.astype(np.float64)


def hdc_encode_sequence(vectors: list[Vector]) -> Vector:
    """
    Encode a sequence of vectors preserving order.

    Uses permutation to encode position and bundling to combine.
    The result contains information about both content and order.

    Args:
        vectors: Ordered list of HD vectors

    Returns:
        Sequence-encoded vector

    Example:
        >>> a = random_hd_vector(seed=1)
        >>> b = random_hd_vector(seed=2)
        >>> seq_ab = hdc_encode_sequence([a, b])
        >>> seq_ba = hdc_encode_sequence([b, a])
        >>> # Different orders produce different encodings
        >>> hdc_similarity(seq_ab, seq_ba) < 0.8
        True
    """
    if not vectors:
        raise ValueError("Cannot encode empty sequence")

    positioned = [hdc_permute(v, i) for i, v in enumerate(vectors)]
    return hdc_bundle(positioned)


def hdc_encode_set(vectors: list[Vector]) -> Vector:
    """
    Encode a set of vectors (order-independent).

    Unlike sequence encoding, this produces the same result
    regardless of input order.

    Args:
        vectors: List of HD vectors (order doesn't matter)

    Returns:
        Set-encoded vector
    """
    if not vectors:
        raise ValueError("Cannot encode empty set")

    return hdc_bundle(vectors)


def hdc_resonance_score(query: Vector, memory: Vector) -> float:
    """
    Compute "resonance" between a query and a memory field.

    This is the core operation for Morphic Resonance - measuring
    how familiar a pattern is to the collective memory.

    Higher values indicate stronger resonance (more familiar).

    Args:
        query: Pattern to test
        memory: Global memory superposition

    Returns:
        Resonance score (cosine similarity)
    """
    return hdc_similarity(query, memory)

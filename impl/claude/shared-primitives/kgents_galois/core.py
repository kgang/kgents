"""
kgents-galois.core: Core Distance Computation Utilities

This module provides foundational utilities for text distance computation,
including tokenization, normalization, and set-theoretic operations.

Design Philosophy:
    - Pure functions (no side effects)
    - Composable primitives
    - Type-safe interfaces

Example:
    >>> from kgents_galois.core import tokenize, normalize
    >>> tokens = tokenize("Hello, World!")
    >>> print(tokens)  # {'hello', 'world'}
"""

from __future__ import annotations

import math
import re
from collections.abc import Callable, Sequence
from typing import TypeVar

# -----------------------------------------------------------------------------
# Type Variables
# -----------------------------------------------------------------------------

T = TypeVar("T")


# -----------------------------------------------------------------------------
# Text Normalization
# -----------------------------------------------------------------------------


def normalize(text: str) -> str:
    """
    Normalize text for comparison.

    Applies:
    - Lowercase conversion
    - Whitespace normalization
    - Punctuation removal (optional by design choice)

    Args:
        text: Raw input text

    Returns:
        Normalized text suitable for comparison

    Example:
        >>> normalize("  Hello,   World!  ")
        'hello world'
    """
    # Lowercase
    text = text.lower()
    # Remove punctuation (keep alphanumeric and spaces)
    text = re.sub(r"[^\w\s]", "", text)
    # Normalize whitespace
    text = " ".join(text.split())
    return text


def tokenize(text: str) -> set[str]:
    """
    Tokenize text into a set of normalized tokens.

    Uses simple whitespace tokenization after normalization.
    For more sophisticated tokenization, use dedicated NLP libraries.

    Args:
        text: Input text

    Returns:
        Set of unique, normalized tokens

    Example:
        >>> tokenize("The quick brown fox")
        {'the', 'quick', 'brown', 'fox'}
        >>> tokenize("Hello hello HELLO")
        {'hello'}
    """
    normalized = normalize(text)
    if not normalized:
        return set()
    return set(normalized.split())


def character_ngrams(text: str, n: int = 3) -> set[str]:
    """
    Extract character n-grams from text.

    N-grams capture local character patterns, useful for
    fuzzy matching and typo tolerance.

    Args:
        text: Input text
        n: N-gram size (default: 3 for trigrams)

    Returns:
        Set of unique n-grams

    Example:
        >>> sorted(character_ngrams("hello", 2))
        ['el', 'he', 'll', 'lo']
        >>> character_ngrams("hi", 3)
        {'hi'}  # Falls back to shorter if text too short
    """
    text = text.lower()
    if len(text) < n:
        return {text} if text else set()
    return {text[i : i + n] for i in range(len(text) - n + 1)}


def word_ngrams(text: str, n: int = 2) -> set[tuple[str, ...]]:
    """
    Extract word-level n-grams from text.

    Captures local word sequences, useful for phrase matching.

    Args:
        text: Input text
        n: N-gram size (default: 2 for bigrams)

    Returns:
        Set of unique word n-gram tuples

    Example:
        >>> word_ngrams("the quick brown fox", 2)
        {('the', 'quick'), ('quick', 'brown'), ('brown', 'fox')}
    """
    tokens = list(tokenize(text))
    if len(tokens) < n:
        return {tuple(tokens)} if tokens else set()
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


# -----------------------------------------------------------------------------
# Set-Theoretic Operations
# -----------------------------------------------------------------------------


def set_intersection_size(a: set[T], b: set[T]) -> int:
    """
    Compute |A intersection B|.

    Args:
        a: First set
        b: Second set

    Returns:
        Size of intersection

    Example:
        >>> set_intersection_size({1, 2, 3}, {2, 3, 4})
        2
    """
    return len(a & b)


def set_union_size(a: set[T], b: set[T]) -> int:
    """
    Compute |A union B|.

    Args:
        a: First set
        b: Second set

    Returns:
        Size of union

    Example:
        >>> set_union_size({1, 2, 3}, {2, 3, 4})
        4
    """
    return len(a | b)


def set_symmetric_difference_size(a: set[T], b: set[T]) -> int:
    """
    Compute |A symmetric_difference B|.

    The symmetric difference is elements in either but not both.

    Args:
        a: First set
        b: Second set

    Returns:
        Size of symmetric difference

    Example:
        >>> set_symmetric_difference_size({1, 2, 3}, {2, 3, 4})
        2  # {1, 4}
    """
    return len(a ^ b)


# -----------------------------------------------------------------------------
# Mathematical Utilities
# -----------------------------------------------------------------------------


def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """
    Clamp value to [min_val, max_val] range.

    Args:
        value: Value to clamp
        min_val: Minimum bound (default: 0.0)
        max_val: Maximum bound (default: 1.0)

    Returns:
        Clamped value

    Example:
        >>> clamp(1.5)
        1.0
        >>> clamp(-0.1)
        0.0
        >>> clamp(0.5)
        0.5
    """
    return max(min_val, min(max_val, value))


def cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cos(theta) = (A . B) / (||A|| * ||B||)

    Args:
        vec_a: First vector
        vec_b: Second vector

    Returns:
        Cosine similarity in [-1, 1]

    Raises:
        ValueError: If vectors have different lengths

    Example:
        >>> cosine_similarity([1, 0], [0, 1])
        0.0
        >>> cosine_similarity([1, 0], [1, 0])
        1.0
    """
    if len(vec_a) != len(vec_b):
        raise ValueError(f"Vector length mismatch: {len(vec_a)} vs {len(vec_b)}")

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b, strict=False))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def cosine_distance(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    """
    Compute cosine distance between two vectors.

    distance = 1 - similarity

    Args:
        vec_a: First vector
        vec_b: Second vector

    Returns:
        Cosine distance in [0, 2]

    Example:
        >>> cosine_distance([1, 0], [1, 0])
        0.0
        >>> cosine_distance([1, 0], [-1, 0])
        2.0
    """
    return 1.0 - cosine_similarity(vec_a, vec_b)


def geometric_mean(values: Sequence[float]) -> float:
    """
    Compute geometric mean of values.

    GM = (x1 * x2 * ... * xn) ^ (1/n)

    The geometric mean is appropriate when values represent rates
    or ratios, and when you want the mean to be sensitive to
    any individual value being zero.

    Args:
        values: Sequence of non-negative values

    Returns:
        Geometric mean, or 0.0 if any value is 0

    Example:
        >>> geometric_mean([2, 8])
        4.0
        >>> geometric_mean([0, 100])
        0.0
    """
    if not values:
        return 0.0

    product = 1.0
    for v in values:
        if v <= 0:
            return 0.0
        product *= v

    return float(product ** (1.0 / len(values)))


def harmonic_mean(values: Sequence[float]) -> float:
    """
    Compute harmonic mean of values.

    HM = n / (1/x1 + 1/x2 + ... + 1/xn)

    The harmonic mean is appropriate for averaging rates.
    It is more sensitive to small values than arithmetic mean.

    Args:
        values: Sequence of positive values

    Returns:
        Harmonic mean, or 0.0 if any value is 0

    Example:
        >>> harmonic_mean([1, 2])
        1.333...
        >>> harmonic_mean([40, 60])
        48.0
    """
    if not values:
        return 0.0

    reciprocal_sum = 0.0
    for v in values:
        if v <= 0:
            return 0.0
        reciprocal_sum += 1.0 / v

    return len(values) / reciprocal_sum


# -----------------------------------------------------------------------------
# Distance Conversion Utilities
# -----------------------------------------------------------------------------


def similarity_to_distance(similarity: float) -> float:
    """
    Convert similarity score to distance.

    distance = 1 - similarity

    Args:
        similarity: Similarity score in [0, 1]

    Returns:
        Distance in [0, 1]

    Example:
        >>> similarity_to_distance(0.8)
        0.2
    """
    return clamp(1.0 - similarity)


def distance_to_similarity(distance: float) -> float:
    """
    Convert distance score to similarity.

    similarity = 1 - distance

    Args:
        distance: Distance score in [0, 1]

    Returns:
        Similarity in [0, 1]

    Example:
        >>> distance_to_similarity(0.3)
        0.7
    """
    return clamp(1.0 - distance)


# -----------------------------------------------------------------------------
# Higher-Order Distance Functions
# -----------------------------------------------------------------------------


def compose_distances(
    *distance_fns: Callable[[str, str], float],
    weights: Sequence[float] | None = None,
) -> Callable[[str, str], float]:
    """
    Compose multiple distance functions into a weighted average.

    Args:
        *distance_fns: Distance functions to compose
        weights: Optional weights (defaults to uniform)

    Returns:
        Composed distance function

    Example:
        >>> from kgents_galois.jaccard import jaccard_distance
        >>> from kgents_galois.levenshtein import normalized_levenshtein
        >>> combined = compose_distances(jaccard_distance, normalized_levenshtein)
        >>> combined("hello", "hallo")  # Average of both distances
    """
    if not distance_fns:
        return lambda a, b: 0.0

    if weights is None:
        weights = [1.0] * len(distance_fns)

    total_weight = sum(weights)
    if total_weight == 0:
        return lambda a, b: 0.0

    def composed(a: str, b: str) -> float:
        weighted_sum = sum(
            fn(a, b) * w for fn, w in zip(distance_fns, weights, strict=False)
        )
        return clamp(weighted_sum / total_weight)

    return composed


def threshold_distance(
    distance_fn: Callable[[str, str], float],
    threshold: float,
) -> Callable[[str, str], bool]:
    """
    Create a boolean predicate from a distance function.

    Args:
        distance_fn: Distance function to threshold
        threshold: Maximum distance to consider "similar"

    Returns:
        Predicate returning True if distance <= threshold

    Example:
        >>> from kgents_galois.jaccard import jaccard_distance
        >>> is_similar = threshold_distance(jaccard_distance, 0.3)
        >>> is_similar("hello world", "hello there")
        False
    """

    def predicate(a: str, b: str) -> bool:
        return distance_fn(a, b) <= threshold

    return predicate


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    # Normalization
    "normalize",
    "tokenize",
    "character_ngrams",
    "word_ngrams",
    # Set operations
    "set_intersection_size",
    "set_union_size",
    "set_symmetric_difference_size",
    # Math utilities
    "clamp",
    "cosine_similarity",
    "cosine_distance",
    "geometric_mean",
    "harmonic_mean",
    # Conversion
    "similarity_to_distance",
    "distance_to_similarity",
    # Composition
    "compose_distances",
    "threshold_distance",
]

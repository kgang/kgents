"""
kgents-galois.jaccard: Jaccard Similarity and Distance

The Jaccard index measures similarity between finite sample sets as the
size of the intersection divided by the size of the union.

    J(A, B) = |A intersection B| / |A union B|

This module provides token-based Jaccard operations for text comparison.

Mathematical Properties:
    - Jaccard similarity: J(A, B) in [0, 1]
    - Jaccard distance: d_J(A, B) = 1 - J(A, B) in [0, 1]
    - Metric space: d_J satisfies identity, symmetry, triangle inequality
    - Empty set handling: J(empty, empty) = 1, J(empty, non-empty) = 0

Use Cases:
    - Quick text similarity check
    - Duplicate detection
    - Fuzzy matching
    - Document clustering

Example:
    >>> from kgents_galois.jaccard import jaccard_distance, jaccard_similarity
    >>> jaccard_similarity("the cat sat", "the dog sat")
    0.5  # intersection: {the, sat}, union: {the, cat, sat, dog}
    >>> jaccard_distance("the cat sat", "the dog sat")
    0.5
"""

from __future__ import annotations

from .core import character_ngrams, set_intersection_size, set_union_size, tokenize

# -----------------------------------------------------------------------------
# Token-Based Jaccard
# -----------------------------------------------------------------------------


def jaccard_similarity(a: str, b: str) -> float:
    """
    Compute Jaccard similarity between two strings (token-based).

    J(A, B) = |A intersection B| / |A union B|

    Tokenizes both strings on whitespace after lowercasing,
    then computes the Jaccard index of the resulting sets.

    Args:
        a: First string
        b: Second string

    Returns:
        Jaccard similarity in [0, 1]
        - 1.0 = identical token sets
        - 0.0 = no tokens in common

    Example:
        >>> jaccard_similarity("hello world", "hello there")
        0.333...  # {"hello"} / {"hello", "world", "there"}

        >>> jaccard_similarity("the cat sat on the mat", "the cat sat")
        0.75  # {the, cat, sat} / {the, cat, sat, on, mat}

        >>> jaccard_similarity("", "")
        1.0  # Both empty = identical

        >>> jaccard_similarity("abc", "xyz")
        0.0  # No overlap
    """
    tokens_a = tokenize(a)
    tokens_b = tokenize(b)

    # Both empty = identical
    if not tokens_a and not tokens_b:
        return 1.0

    # One empty, one not = maximally different
    if not tokens_a or not tokens_b:
        return 0.0

    intersection = set_intersection_size(tokens_a, tokens_b)
    union = set_union_size(tokens_a, tokens_b)

    return intersection / union if union > 0 else 0.0


def jaccard_distance(a: str, b: str) -> float:
    """
    Compute Jaccard distance between two strings.

    d_J(A, B) = 1 - J(A, B)

    This is the complement of Jaccard similarity and forms a proper
    metric on the space of finite sets.

    Args:
        a: First string
        b: Second string

    Returns:
        Jaccard distance in [0, 1]
        - 0.0 = identical token sets
        - 1.0 = no tokens in common

    Example:
        >>> jaccard_distance("hello world", "hello there")
        0.666...

        >>> jaccard_distance("identical text", "identical text")
        0.0

        >>> jaccard_distance("completely", "different")
        1.0
    """
    return 1.0 - jaccard_similarity(a, b)


# -----------------------------------------------------------------------------
# Weighted Jaccard
# -----------------------------------------------------------------------------


def weighted_jaccard_similarity(
    a: str,
    b: str,
    weights: dict[str, float] | None = None,
) -> float:
    """
    Compute weighted Jaccard similarity.

    Allows assigning different importance to different tokens.
    Useful when certain words are more semantically significant.

    J_w(A, B) = sum(min(w_a, w_b)) / sum(max(w_a, w_b))

    Where w_a, w_b are the weights for each token in A, B respectively.

    Args:
        a: First string
        b: Second string
        weights: Optional dict mapping tokens to weights (default: 1.0 each)

    Returns:
        Weighted Jaccard similarity in [0, 1]

    Example:
        >>> weights = {"important": 10.0, "the": 0.1}
        >>> weighted_jaccard_similarity(
        ...     "the important thing",
        ...     "the trivial thing",
        ...     weights
        ... )
        # Lower than unweighted due to "important" being emphasized
    """
    tokens_a = tokenize(a)
    tokens_b = tokenize(b)

    if not tokens_a and not tokens_b:
        return 1.0

    if not tokens_a or not tokens_b:
        return 0.0

    all_tokens = tokens_a | tokens_b

    if weights is None:
        weights = {}

    def get_weight(token: str) -> float:
        return weights.get(token, 1.0)

    numerator = 0.0
    denominator = 0.0

    for token in all_tokens:
        w_a = get_weight(token) if token in tokens_a else 0.0
        w_b = get_weight(token) if token in tokens_b else 0.0

        numerator += min(w_a, w_b)
        denominator += max(w_a, w_b)

    return numerator / denominator if denominator > 0 else 0.0


def weighted_jaccard_distance(
    a: str,
    b: str,
    weights: dict[str, float] | None = None,
) -> float:
    """
    Compute weighted Jaccard distance.

    Args:
        a: First string
        b: Second string
        weights: Optional dict mapping tokens to weights

    Returns:
        Weighted Jaccard distance in [0, 1]

    Example:
        >>> weighted_jaccard_distance("hello world", "hello there")
        0.666...
    """
    return 1.0 - weighted_jaccard_similarity(a, b, weights)


# -----------------------------------------------------------------------------
# N-Gram Jaccard (Character-Based)
# -----------------------------------------------------------------------------


def ngram_jaccard_similarity(a: str, b: str, n: int = 3) -> float:
    """
    Compute Jaccard similarity using character n-grams.

    Instead of tokenizing on whitespace, extracts overlapping
    character sequences of length n. More robust to typos and
    morphological variations.

    Args:
        a: First string
        b: Second string
        n: N-gram length (default: 3 for trigrams)

    Returns:
        N-gram Jaccard similarity in [0, 1]

    Example:
        >>> ngram_jaccard_similarity("hello", "hallo", n=2)
        0.5  # Shares "al", "ll", "lo" patterns

        >>> ngram_jaccard_similarity("running", "runner", n=3)
        0.5  # Shares "run", "unn", "nni"/"nne" overlaps
    """
    ngrams_a = character_ngrams(a, n)
    ngrams_b = character_ngrams(b, n)

    if not ngrams_a and not ngrams_b:
        return 1.0

    if not ngrams_a or not ngrams_b:
        return 0.0

    intersection = set_intersection_size(ngrams_a, ngrams_b)
    union = set_union_size(ngrams_a, ngrams_b)

    return intersection / union if union > 0 else 0.0


def ngram_jaccard_distance(a: str, b: str, n: int = 3) -> float:
    """
    Compute Jaccard distance using character n-grams.

    Args:
        a: First string
        b: Second string
        n: N-gram length (default: 3)

    Returns:
        N-gram Jaccard distance in [0, 1]

    Example:
        >>> ngram_jaccard_distance("hello", "hallo", n=2)
        0.5
    """
    return 1.0 - ngram_jaccard_similarity(a, b, n)


# -----------------------------------------------------------------------------
# Generalized Jaccard
# -----------------------------------------------------------------------------


def generalized_jaccard_similarity(
    multiset_a: dict[str, int],
    multiset_b: dict[str, int],
) -> float:
    """
    Compute generalized Jaccard similarity for multisets.

    Unlike standard Jaccard which uses sets (element present/absent),
    generalized Jaccard considers element counts (multiplicity).

    J_g(A, B) = sum(min(a_i, b_i)) / sum(max(a_i, b_i))

    Args:
        multiset_a: First multiset as {element: count}
        multiset_b: Second multiset as {element: count}

    Returns:
        Generalized Jaccard similarity in [0, 1]

    Example:
        >>> generalized_jaccard_similarity(
        ...     {"the": 3, "cat": 1},
        ...     {"the": 2, "dog": 1}
        ... )
        0.4  # min(3,2) / (max(3,2) + 1 + 1) = 2/5
    """
    all_elements = set(multiset_a.keys()) | set(multiset_b.keys())

    if not all_elements:
        return 1.0

    numerator = 0
    denominator = 0

    for elem in all_elements:
        count_a = multiset_a.get(elem, 0)
        count_b = multiset_b.get(elem, 0)
        numerator += min(count_a, count_b)
        denominator += max(count_a, count_b)

    return numerator / denominator if denominator > 0 else 0.0


def text_to_multiset(text: str) -> dict[str, int]:
    """
    Convert text to a multiset (bag of words with counts).

    Args:
        text: Input text

    Returns:
        Dictionary mapping tokens to their counts

    Example:
        >>> text_to_multiset("the cat and the dog")
        {'the': 2, 'cat': 1, 'and': 1, 'dog': 1}
    """
    tokens = text.lower().split()
    multiset: dict[str, int] = {}
    for token in tokens:
        # Simple normalization: remove punctuation
        clean = "".join(c for c in token if c.isalnum())
        if clean:
            multiset[clean] = multiset.get(clean, 0) + 1
    return multiset


def multiset_jaccard_similarity(a: str, b: str) -> float:
    """
    Compute Jaccard similarity treating texts as multisets.

    Takes word frequency into account, not just presence/absence.

    Args:
        a: First string
        b: Second string

    Returns:
        Multiset Jaccard similarity in [0, 1]

    Example:
        >>> multiset_jaccard_similarity(
        ...     "the the the cat",
        ...     "the dog"
        ... )
        # Lower than set-based because "the" appears 3x vs 1x
    """
    return generalized_jaccard_similarity(
        text_to_multiset(a),
        text_to_multiset(b),
    )


def multiset_jaccard_distance(a: str, b: str) -> float:
    """
    Compute Jaccard distance treating texts as multisets.

    Args:
        a: First string
        b: Second string

    Returns:
        Multiset Jaccard distance in [0, 1]
    """
    return 1.0 - multiset_jaccard_similarity(a, b)


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    # Basic Jaccard
    "jaccard_similarity",
    "jaccard_distance",
    # Weighted Jaccard
    "weighted_jaccard_similarity",
    "weighted_jaccard_distance",
    # N-gram Jaccard
    "ngram_jaccard_similarity",
    "ngram_jaccard_distance",
    # Generalized (Multiset) Jaccard
    "generalized_jaccard_similarity",
    "text_to_multiset",
    "multiset_jaccard_similarity",
    "multiset_jaccard_distance",
]

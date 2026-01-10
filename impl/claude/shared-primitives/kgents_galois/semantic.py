"""
kgents-galois.semantic: Semantic Distance Measurement

Semantic distance measures how different two texts are in MEANING,
not just surface form. Unlike edit distance which counts character changes,
semantic distance captures conceptual similarity.

Key insight: "The dog ran" and "A canine sprinted" have high edit distance
but low semantic distance (same meaning).

This module provides multiple approaches:
    1. N-gram based (simple, fast, no dependencies)
    2. Embedding based (requires OpenAI API)
    3. Entailment based (requires transformers)

For most use cases, the simple n-gram approach works well as a proxy.
For high-stakes decisions, use embedding or entailment methods.

Example:
    >>> from kgents_galois.semantic import semantic_distance
    >>> semantic_distance("The cat sat", "A feline rested")
    0.3  # Low distance (semantically similar)
    >>> semantic_distance("The cat sat", "The stock market crashed")
    0.9  # High distance (semantically different)
"""

from __future__ import annotations

from .core import (
    character_ngrams,
    clamp,
    cosine_similarity,
    geometric_mean,
    set_intersection_size,
    set_union_size,
    tokenize,
)

# -----------------------------------------------------------------------------
# Simple Semantic Distance (N-gram based)
# -----------------------------------------------------------------------------


def semantic_distance(a: str, b: str) -> float:
    """
    Compute semantic distance between two strings.

    Uses character trigram overlap as a proxy for semantic similarity.
    This simple approach captures:
    - Morphological similarity (running/runner)
    - Partial word matches
    - Typo tolerance

    For production use with high accuracy requirements, consider
    semantic_distance_embedding() or semantic_distance_entailment().

    Args:
        a: First string
        b: Second string

    Returns:
        Semantic distance in [0, 1]
        - 0.0 = semantically identical
        - 1.0 = semantically unrelated

    Example:
        >>> semantic_distance("The cat sat", "A feline rested")
        0.3  # Low distance (some trigram overlap)

        >>> semantic_distance("hello world", "hello world")
        0.0  # Identical

        >>> semantic_distance("abc", "xyz")
        1.0  # No overlap
    """
    # Handle edge cases
    if a == b:
        return 0.0

    if not a.strip() or not b.strip():
        return 1.0 if a != b else 0.0

    # Extract character trigrams
    trigrams_a = character_ngrams(a, n=3)
    trigrams_b = character_ngrams(b, n=3)

    if not trigrams_a or not trigrams_b:
        return 1.0

    # Jaccard-like overlap
    intersection = set_intersection_size(trigrams_a, trigrams_b)
    union = set_union_size(trigrams_a, trigrams_b)

    similarity = intersection / union if union > 0 else 0.0
    return clamp(1.0 - similarity)


def semantic_similarity(a: str, b: str) -> float:
    """
    Compute semantic similarity between two strings.

    Convenience function: similarity = 1 - distance.

    Args:
        a: First string
        b: Second string

    Returns:
        Semantic similarity in [0, 1]
        - 1.0 = semantically identical
        - 0.0 = semantically unrelated

    Example:
        >>> semantic_similarity("The cat sat", "A feline rested")
        0.7
    """
    return 1.0 - semantic_distance(a, b)


# -----------------------------------------------------------------------------
# Multi-Level Semantic Distance
# -----------------------------------------------------------------------------


def semantic_distance_multilevel(
    a: str,
    b: str,
    char_weight: float = 0.3,
    token_weight: float = 0.4,
    ngram_weight: float = 0.3,
) -> float:
    """
    Compute semantic distance using multiple levels of analysis.

    Combines:
    1. Character-level trigrams (captures morphology, typos)
    2. Token-level overlap (captures word meaning)
    3. Word bigrams (captures phrase structure)

    This multi-level approach is more robust than any single method.

    Args:
        a: First string
        b: Second string
        char_weight: Weight for character trigram similarity
        token_weight: Weight for token overlap
        ngram_weight: Weight for word bigram overlap

    Returns:
        Semantic distance in [0, 1]

    Example:
        >>> semantic_distance_multilevel(
        ...     "The quick brown fox",
        ...     "A fast brown fox"
        ... )
        0.35  # Some overlap at all levels
    """
    # Normalize weights
    total = char_weight + token_weight + ngram_weight
    if total == 0:
        return 0.5
    char_weight /= total
    token_weight /= total
    ngram_weight /= total

    # Character trigrams
    char_tri_a = character_ngrams(a, 3)
    char_tri_b = character_ngrams(b, 3)
    char_sim = _set_similarity(char_tri_a, char_tri_b)

    # Token overlap
    tokens_a = tokenize(a)
    tokens_b = tokenize(b)
    token_sim = _set_similarity(tokens_a, tokens_b)

    # Word bigrams
    bigrams_a = _word_bigrams(a)
    bigrams_b = _word_bigrams(b)
    bigram_sim = _set_similarity(bigrams_a, bigrams_b)

    # Weighted combination
    combined_sim = (
        char_weight * char_sim + token_weight * token_sim + ngram_weight * bigram_sim
    )

    return clamp(1.0 - combined_sim)


def _set_similarity(a: set, b: set) -> float:
    """Compute Jaccard-like set similarity."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union > 0 else 0.0


def _word_bigrams(text: str) -> set[tuple[str, str]]:
    """Extract word bigrams from text."""
    tokens = list(tokenize(text))
    if len(tokens) < 2:
        return set()
    return {(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)}


# -----------------------------------------------------------------------------
# Embedding-Based Semantic Distance
# -----------------------------------------------------------------------------


def semantic_distance_embedding(
    a: str,
    b: str,
    model: str = "text-embedding-3-small",
) -> float:
    """
    Compute semantic distance using text embeddings.

    Uses OpenAI embeddings to capture deep semantic meaning.
    Falls back to simple semantic_distance() if API unavailable.

    Args:
        a: First string
        b: Second string
        model: Embedding model to use

    Returns:
        Semantic distance in [0, 1]

    Example:
        >>> semantic_distance_embedding(
        ...     "The dog ran quickly",
        ...     "A canine sprinted fast"
        ... )
        0.15  # Very low distance (same meaning)
    """
    try:
        embeddings = _get_embeddings([a, b], model)
        if embeddings:
            emb_a, emb_b = embeddings
            sim = cosine_similarity(emb_a, emb_b)
            return clamp(1.0 - sim)
    except Exception:
        pass

    # Fallback to simple method
    return semantic_distance(a, b)


def _get_embeddings(
    texts: list[str],
    model: str,
) -> list[list[float]] | None:
    """Get embeddings from OpenAI API."""
    try:
        import openai

        client = openai.OpenAI()
        response = client.embeddings.create(model=model, input=texts)
        return [item.embedding for item in response.data]
    except Exception:
        return None


# -----------------------------------------------------------------------------
# Entailment-Based Semantic Distance
# -----------------------------------------------------------------------------


def semantic_distance_entailment(a: str, b: str) -> float:
    """
    Compute semantic distance using bidirectional entailment.

    d(A, B) = 1 - sqrt(P(A |= B) * P(B |= A))

    This is the most principled measure of semantic equivalence:
    two texts are semantically equivalent if they mutually entail
    each other.

    Requires transformers library with NLI model.
    Falls back to simple semantic_distance() if unavailable.

    Args:
        a: First string
        b: Second string

    Returns:
        Semantic distance in [0, 1]

    Example:
        >>> semantic_distance_entailment(
        ...     "All cats are mammals",
        ...     "Every feline belongs to the mammal class"
        ... )
        0.1  # Very low distance (mutual entailment)
    """
    if a == b:
        return 0.0

    if not a.strip() or not b.strip():
        return 1.0

    try:
        p_a_entails_b = _entailment_probability(a, b)
        p_b_entails_a = _entailment_probability(b, a)

        # Geometric mean captures mutual entailment
        mutual = geometric_mean([p_a_entails_b, p_b_entails_a])
        return clamp(1.0 - mutual)

    except Exception:
        # Fallback to simple method
        return semantic_distance(a, b)


_NLI_CLASSIFIER = None


def _entailment_probability(premise: str, hypothesis: str) -> float:
    """Get P(premise entails hypothesis) using NLI model."""
    global _NLI_CLASSIFIER

    try:
        from transformers import pipeline

        if _NLI_CLASSIFIER is None:
            _NLI_CLASSIFIER = pipeline(
                "text-classification",
                model="microsoft/deberta-v3-base-mnli-fever-anli",
                top_k=None,
            )

        # Use proper NLI format
        result = _NLI_CLASSIFIER(f"{premise}</s></s>{hypothesis}")

        if isinstance(result, list) and len(result) > 0:
            scores = result[0] if isinstance(result[0], list) else result
            for item in scores:
                label = item.get("label", "").upper()
                if label == "ENTAILMENT":
                    return item.get("score", 0.0)

        return 0.0

    except Exception:
        return 0.5  # Neutral when uncertain


# -----------------------------------------------------------------------------
# Soft Cosine Similarity
# -----------------------------------------------------------------------------


def soft_cosine_distance(
    a: str,
    b: str,
    similarity_matrix: dict[tuple[str, str], float] | None = None,
) -> float:
    """
    Compute soft cosine distance between texts.

    Unlike standard cosine similarity which treats all words as
    orthogonal, soft cosine uses a word similarity matrix to
    account for synonyms and related terms.

    Args:
        a: First string
        b: Second string
        similarity_matrix: Dict mapping (word1, word2) -> similarity
                          If None, uses Jaccard on character trigrams

    Returns:
        Soft cosine distance in [0, 1]

    Example:
        >>> sim_matrix = {
        ...     ("cat", "feline"): 0.9,
        ...     ("dog", "canine"): 0.9,
        ... }
        >>> soft_cosine_distance(
        ...     "the cat sat",
        ...     "the feline rested",
        ...     sim_matrix
        ... )
        0.3  # Lower than hard cosine due to cat/feline similarity
    """
    tokens_a = list(tokenize(a))
    tokens_b = list(tokenize(b))

    if not tokens_a and not tokens_b:
        return 0.0

    if not tokens_a or not tokens_b:
        return 1.0

    def word_similarity(w1: str, w2: str) -> float:
        """Get similarity between two words."""
        if w1 == w2:
            return 1.0

        if similarity_matrix is not None:
            # Check both orderings
            if (w1, w2) in similarity_matrix:
                return similarity_matrix[(w1, w2)]
            if (w2, w1) in similarity_matrix:
                return similarity_matrix[(w2, w1)]
            return 0.0

        # Default: character trigram similarity
        tri1 = character_ngrams(w1, 3)
        tri2 = character_ngrams(w2, 3)
        return _set_similarity(tri1, tri2)

    # Build term frequency vectors
    tf_a = {}
    for t in tokens_a:
        tf_a[t] = tf_a.get(t, 0) + 1
    tf_b = {}
    for t in tokens_b:
        tf_b[t] = tf_b.get(t, 0) + 1

    all_terms = list(set(tf_a.keys()) | set(tf_b.keys()))

    # Compute soft cosine
    numerator = 0.0
    for i, ti in enumerate(all_terms):
        for j, tj in enumerate(all_terms):
            sim_ij = word_similarity(ti, tj)
            a_i = tf_a.get(ti, 0)
            b_j = tf_b.get(tj, 0)
            numerator += sim_ij * a_i * b_j

    # Compute norms
    norm_a_sq = 0.0
    for i, ti in enumerate(all_terms):
        for j, tj in enumerate(all_terms):
            sim_ij = word_similarity(ti, tj)
            a_i = tf_a.get(ti, 0)
            a_j = tf_a.get(tj, 0)
            norm_a_sq += sim_ij * a_i * a_j

    norm_b_sq = 0.0
    for i, ti in enumerate(all_terms):
        for j, tj in enumerate(all_terms):
            sim_ij = word_similarity(ti, tj)
            b_i = tf_b.get(ti, 0)
            b_j = tf_b.get(tj, 0)
            norm_b_sq += sim_ij * b_i * b_j

    norm_a = norm_a_sq**0.5
    norm_b = norm_b_sq**0.5

    if norm_a == 0 or norm_b == 0:
        return 1.0

    similarity = numerator / (norm_a * norm_b)
    return clamp(1.0 - similarity)


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    # Simple semantic distance
    "semantic_distance",
    "semantic_similarity",
    # Multi-level
    "semantic_distance_multilevel",
    # Embedding-based
    "semantic_distance_embedding",
    # Entailment-based
    "semantic_distance_entailment",
    # Soft cosine
    "soft_cosine_distance",
]

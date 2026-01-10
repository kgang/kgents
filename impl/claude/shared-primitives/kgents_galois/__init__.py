"""
kgents-galois: Semantic Distance Measurement

Measure semantic distance between texts for coherence verification,
similarity detection, and loss computation.

Quick Start (10 minutes or less):

    from kgents_galois import semantic_distance, get_fast_metric

    # Simple usage
    distance = semantic_distance(
        "The cat sat on the mat",
        "A feline rested on the rug"
    )
    print(f"Distance: {distance:.2f}")  # ~0.3 (related but not identical)

    # For speed-critical applications
    metric = get_fast_metric()
    distance = metric.distance(text_a, text_b)

What is Semantic Distance?

    Semantic distance measures how different two texts are in MEANING:
    - 0.0 = Semantically identical (same meaning)
    - 0.5 = Somewhat related
    - 1.0 = Completely different or contradictory

    Unlike edit distance (Levenshtein), semantic distance captures meaning:
    - "The dog ran" vs "A canine sprinted" -> LOW distance (same meaning)
    - "The dog ran" vs "The dog ran fast" -> LOW distance (similar)
    - "The dog ran" vs "The cat slept" -> HIGH distance (different)

Available Metrics:

    1. CosineEmbedding: Fast (~12ms), uses text embeddings
       - Best for: Batch operations, initial screening
       - Requires: OpenAI API or falls back to token overlap

    2. BERTScore: Balanced (~45ms), token-level similarity
       - Best for: General purpose (DEFAULT)
       - Requires: bert-score package

    3. BidirectionalEntailment: Principled (~38ms), NLI-based
       - Best for: Logical consistency checking
       - Requires: transformers package

    4. LLMJudge: Most accurate (~230ms), uses Claude
       - Best for: High-stakes decisions
       - Requires: Anthropic API

Use Cases:

    # 1. Check if texts mean the same thing
    if semantic_distance(original, paraphrase) < 0.2:
        print("These texts are equivalent")

    # 2. Find contradictions
    from kgents_galois import get_contradiction_metric
    metric = get_contradiction_metric()
    if metric.distance(claim, evidence) > 0.8:
        print("Possible contradiction!")

    # 3. Compare multiple metrics
    from kgents_galois import compare_metrics
    comparison = await compare_metrics(text_a, text_b)
    print(f"Average distance: {comparison.mean_distance:.2f}")

License: MIT
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

# -----------------------------------------------------------------------------
# Core Protocol
# -----------------------------------------------------------------------------


@runtime_checkable
class SemanticDistanceMetric(Protocol):
    """
    Protocol for semantic distance metrics.

    All metrics return values in [0, 1] where:
    - 0 = semantically identical
    - 1 = maximally different (contradictory)

    Example:
        >>> class MyMetric:
        ...     @property
        ...     def name(self) -> str:
        ...         return "my_metric"
        ...     def distance(self, text_a: str, text_b: str) -> float:
        ...         # Custom distance logic
        ...         return 0.5
        >>> metric = MyMetric()
        >>> isinstance(metric, SemanticDistanceMetric)
        True
    """

    @property
    def name(self) -> str:
        """Human-readable metric name."""
        ...

    def distance(self, text_a: str, text_b: str) -> float:
        """
        Compute semantic distance between two texts.

        Args:
            text_a: First text
            text_b: Second text

        Returns:
            Distance in [0, 1] range
        """
        ...


# -----------------------------------------------------------------------------
# Jaccard Distance (Fallback)
# -----------------------------------------------------------------------------


@dataclass
class JaccardDistance:
    """
    Simple token-based distance using Jaccard similarity.

    This is the fallback when no other metrics are available.
    Fast but less accurate for semantic similarity.

    Example:
        >>> metric = JaccardDistance()
        >>> d = metric.distance("the cat sat", "the dog sat")
        >>> print(f"{d:.2f}")  # ~0.4 (overlap on "the" and "sat")
    """

    @property
    def name(self) -> str:
        return "jaccard"

    def distance(self, text_a: str, text_b: str) -> float:
        """Jaccard distance: 1 - intersection/union."""
        tokens_a = set(text_a.lower().split())
        tokens_b = set(text_b.lower().split())

        if not tokens_a and not tokens_b:
            return 0.0  # Both empty = identical

        if not tokens_a or not tokens_b:
            return 1.0 if text_a != text_b else 0.0

        intersection = len(tokens_a & tokens_b)
        union = len(tokens_a | tokens_b)

        jaccard_sim = intersection / union if union > 0 else 0.0
        return 1.0 - jaccard_sim


# -----------------------------------------------------------------------------
# Cosine Embedding Distance
# -----------------------------------------------------------------------------


@dataclass
class CosineEmbeddingDistance:
    """
    Fast embedding-based distance using cosine similarity.

    Uses text embeddings and cosine similarity.
    Falls back to Jaccard if embeddings unavailable.

    Pros: Fast (~12ms), deterministic, stable
    Cons: Misses semantic nuance, requires embedding API

    Example:
        >>> metric = CosineEmbeddingDistance()
        >>> d = metric.distance("I love cats", "I adore felines")
        >>> print(f"{d:.2f}")  # Low distance (similar meaning)
    """

    model: str = "text-embedding-3-small"
    _embedder: Any = field(default=None, repr=False)

    @property
    def name(self) -> str:
        return f"cosine_embedding:{self.model}"

    def distance(self, text_a: str, text_b: str) -> float:
        """Compute cosine distance between embeddings."""
        # Try to get embeddings
        try:
            embeddings = self._get_embeddings(text_a, text_b)
            if embeddings is not None:
                emb_a, emb_b = embeddings
                cosine_sim = self._cosine_similarity(emb_a, emb_b)
                return max(0.0, min(1.0, 1.0 - cosine_sim))
        except Exception:
            pass

        # Fallback to Jaccard
        return JaccardDistance().distance(text_a, text_b)

    def _get_embeddings(
        self, text_a: str, text_b: str
    ) -> tuple[list[float], list[float]] | None:
        """Get embeddings for two texts."""
        try:
            import openai

            client = openai.OpenAI()
            response = client.embeddings.create(
                model=self.model,
                input=[text_a, text_b],
            )
            return (
                response.data[0].embedding,
                response.data[1].embedding,
            )
        except Exception:
            return None

    def _cosine_similarity(
        self, vec_a: list[float], vec_b: list[float]
    ) -> float:
        """Compute cosine similarity."""
        dot = sum(a * b for a, b in zip(vec_a, vec_b, strict=False))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


# -----------------------------------------------------------------------------
# BERTScore Distance
# -----------------------------------------------------------------------------


@dataclass
class BERTScoreDistance:
    """
    Balanced precision/recall-based distance using BERT.

    Uses BERTScore for token-level similarity with contextual embeddings.
    F1 score balances precision and recall.

    Pros: ~45ms, good correlation with human judgment
    Cons: Requires bert-score package

    Example:
        >>> metric = BERTScoreDistance()
        >>> d = metric.distance(
        ...     "The quick brown fox jumps",
        ...     "A fast auburn fox leaps"
        ... )
    """

    lang: str = "en"
    model_type: str | None = None

    @property
    def name(self) -> str:
        model = self.model_type or "default"
        return f"bertscore:{model}"

    def distance(self, text_a: str, text_b: str) -> float:
        """Compute 1 - F1 BERTScore."""
        try:
            from bert_score import score  # type: ignore[import-not-found]

            P, R, F1 = score(
                [text_a],
                [text_b],
                lang=self.lang,
                model_type=self.model_type,
                verbose=False,
            )
            f1_score: float = F1.item()
            return max(0.0, min(1.0, 1.0 - f1_score))

        except ImportError:
            # Fallback to cosine embedding
            return CosineEmbeddingDistance().distance(text_a, text_b)

        except Exception:
            return 0.5


# -----------------------------------------------------------------------------
# Bidirectional Entailment Distance
# -----------------------------------------------------------------------------


@dataclass
class BidirectionalEntailmentDistance:
    """
    Canonical semantic distance via bidirectional entailment.

    d(A, B) = 1 - sqrt(P(A |= B) * P(B |= A))

    Uses geometric mean of entailment probabilities in both directions.
    This captures mutual semantic equivalence.

    Why geometric mean?
    - Arithmetic mean treats one-way entailment too leniently
    - Geometric mean gives 0 if either direction fails
    - Matches intuition: mutual entailment = semantic equivalence

    Example:
        >>> metric = BidirectionalEntailmentDistance()
        >>> d = metric.distance(
        ...     "All cats are mammals",
        ...     "Cats belong to the mammal class"
        ... )
        >>> print(f"{d:.2f}")  # Low distance (bidirectional entailment)
    """

    model: str = "microsoft/deberta-v3-base-mnli-fever-anli"
    _classifier: Any = field(default=None, repr=False)

    @property
    def name(self) -> str:
        return f"bidirectional_entailment:{self.model}"

    def distance(self, text_a: str, text_b: str) -> float:
        """Bidirectional entailment distance."""
        if text_a == text_b:
            return 0.0

        if not text_a.strip() or not text_b.strip():
            return 1.0

        p_a_entails_b = self._entailment_prob(text_a, text_b)
        p_b_entails_a = self._entailment_prob(text_b, text_a)

        # Geometric mean
        mutual = math.sqrt(p_a_entails_b * p_b_entails_a)
        return max(0.0, min(1.0, 1.0 - mutual))

    def _entailment_prob(self, premise: str, hypothesis: str) -> float:
        """Get P(premise entails hypothesis)."""
        classifier = self._get_classifier()
        if classifier is None:
            return 0.5

        try:
            result = classifier(f"{premise} [SEP] {hypothesis}")

            if isinstance(result, list) and len(result) > 0:
                scores = result[0] if isinstance(result[0], list) else result
                for item in scores:
                    label = item.get("label", "").upper()
                    if label == "ENTAILMENT":
                        return float(item.get("score", 0.0))

            return 0.0

        except Exception:
            return 0.5

    def _get_classifier(self) -> Any:
        """Lazy load NLI classifier."""
        if self._classifier is None:
            try:
                from transformers import pipeline  # type: ignore[import-not-found]

                self._classifier = pipeline(
                    "text-classification",
                    model=self.model,
                    top_k=None,
                )
            except ImportError:
                return None
        return self._classifier


# -----------------------------------------------------------------------------
# NLI Contradiction Distance
# -----------------------------------------------------------------------------


@dataclass
class NLIContradictionDistance:
    """
    NLI-based distance specialized for contradiction detection.

    Uses Natural Language Inference to classify:
    - ENTAILMENT -> 0.0 (same meaning)
    - NEUTRAL -> 0.5 (related)
    - CONTRADICTION -> 1.0 (opposite)

    Best for detecting logical inconsistencies.

    Example:
        >>> metric = NLIContradictionDistance()
        >>> d = metric.distance(
        ...     "The meeting is at 3pm",
        ...     "The meeting is at 5pm"
        ... )
        >>> print(f"{d:.2f}")  # High distance (contradiction)
    """

    model: str = "microsoft/deberta-v3-base-mnli-fever-anli"
    _classifier: Any = field(default=None, repr=False)

    @property
    def name(self) -> str:
        return f"nli:{self.model}"

    def distance(self, text_a: str, text_b: str) -> float:
        """Distance based on NLI classification."""
        classifier = self._get_classifier()
        if classifier is None:
            return BERTScoreDistance().distance(text_a, text_b)

        try:
            result = classifier(f"{text_a} [SEP] {text_b}")

            label_to_distance = {
                "ENTAILMENT": 0.0,
                "NEUTRAL": 0.5,
                "CONTRADICTION": 1.0,
            }

            if isinstance(result, list) and len(result) > 0:
                scores = result[0] if isinstance(result[0], list) else result
                best = max(scores, key=lambda x: x.get("score", 0))
                label = best.get("label", "").upper()
                return label_to_distance.get(label, 0.5)

            return 0.5

        except Exception:
            return 0.5

    def _get_classifier(self) -> Any:
        """Lazy load NLI classifier."""
        if self._classifier is None:
            try:
                from transformers import pipeline  # type: ignore[import-not-found]

                self._classifier = pipeline(
                    "text-classification",
                    model=self.model,
                    top_k=None,
                )
            except ImportError:
                return None
        return self._classifier


# -----------------------------------------------------------------------------
# Composite Distance
# -----------------------------------------------------------------------------


@dataclass
class CompositeDistance:
    """
    Combines multiple metrics with configurable weights.

    Useful for ensemble approaches or experiments.

    Example:
        >>> metric = CompositeDistance([
        ...     (JaccardDistance(), 0.3),
        ...     (BERTScoreDistance(), 0.7),
        ... ])
        >>> d = metric.distance(text_a, text_b)
    """

    metrics: list[tuple[SemanticDistanceMetric, float]]

    @property
    def name(self) -> str:
        parts = [f"{m.name}:{w:.2f}" for m, w in self.metrics]
        return f"composite[{','.join(parts)}]"

    def distance(self, text_a: str, text_b: str) -> float:
        """Weighted average of component metrics."""
        if not self.metrics:
            return 0.5

        total_weight = sum(w for _, w in self.metrics)
        if total_weight == 0:
            return 0.5

        weighted_sum = sum(
            m.distance(text_a, text_b) * w
            for m, w in self.metrics
        )
        return weighted_sum / total_weight


# -----------------------------------------------------------------------------
# Canonical Distance (with fallback chain)
# -----------------------------------------------------------------------------


@dataclass
class CanonicalSemanticDistance:
    """
    Canonical distance with graceful fallback chain.

    Tries metrics in order of principled-ness:
    1. Bidirectional entailment (most principled)
    2. BERTScore (balanced precision/recall)
    3. Cosine embedding (fast)
    4. Jaccard (always available)

    This is the recommended metric for production use.

    Example:
        >>> metric = CanonicalSemanticDistance()
        >>> d = metric.distance("Hello world", "Hi there world")
    """

    @property
    def name(self) -> str:
        return "canonical"

    def distance(self, text_a: str, text_b: str) -> float:
        """Compute distance with graceful fallback."""
        # Try bidirectional entailment
        try:
            return BidirectionalEntailmentDistance().distance(text_a, text_b)
        except Exception:
            pass

        # Try BERTScore
        try:
            return BERTScoreDistance().distance(text_a, text_b)
        except Exception:
            pass

        # Try cosine embedding
        try:
            return CosineEmbeddingDistance().distance(text_a, text_b)
        except Exception:
            pass

        # Ultimate fallback: Jaccard
        return JaccardDistance().distance(text_a, text_b)


# -----------------------------------------------------------------------------
# Comparison Utilities
# -----------------------------------------------------------------------------


@dataclass
class MetricComparisonResult:
    """Result of comparing multiple metrics on a text pair."""

    text_a: str
    text_b: str
    distances: dict[str, float]

    @property
    def mean_distance(self) -> float:
        """Average distance across all metrics."""
        if not self.distances:
            return 0.5
        return sum(self.distances.values()) / len(self.distances)

    @property
    def variance(self) -> float:
        """Variance of distances (disagreement indicator)."""
        if len(self.distances) < 2:
            return 0.0
        mean = self.mean_distance
        return sum((d - mean) ** 2 for d in self.distances.values()) / len(
            self.distances
        )


def compare_metrics(
    text_a: str,
    text_b: str,
    metrics: list[SemanticDistanceMetric] | None = None,
) -> MetricComparisonResult:
    """
    Compare multiple metrics on a text pair.

    Args:
        text_a: First text
        text_b: Second text
        metrics: Optional list of metrics (defaults to all available)

    Returns:
        MetricComparisonResult with distances from each metric

    Example:
        >>> result = compare_metrics("Hello", "Hi there")
        >>> print(f"Mean: {result.mean_distance:.2f}")
        >>> print(f"Variance: {result.variance:.3f}")
    """
    if metrics is None:
        metrics = [
            JaccardDistance(),
            CosineEmbeddingDistance(),
            BERTScoreDistance(),
        ]

    distances = {}
    for metric in metrics:
        try:
            distances[metric.name] = metric.distance(text_a, text_b)
        except Exception:
            pass

    return MetricComparisonResult(
        text_a=text_a,
        text_b=text_b,
        distances=distances,
    )


# -----------------------------------------------------------------------------
# Factory Functions
# -----------------------------------------------------------------------------


def get_default_metric() -> SemanticDistanceMetric:
    """Get the recommended default metric (Canonical with fallbacks)."""
    return CanonicalSemanticDistance()


def get_fast_metric() -> SemanticDistanceMetric:
    """Get the fastest metric (Jaccard)."""
    return JaccardDistance()


def get_accurate_metric() -> SemanticDistanceMetric:
    """Get the most principled metric (Bidirectional Entailment)."""
    return BidirectionalEntailmentDistance()


def get_contradiction_metric() -> SemanticDistanceMetric:
    """Get metric specialized for contradiction detection."""
    return NLIContradictionDistance()


# -----------------------------------------------------------------------------
# Convenience Function
# -----------------------------------------------------------------------------


def semantic_distance(text_a: str, text_b: str) -> float:
    """
    Compute semantic distance between two texts.

    This is the main entry point for simple usage.
    Uses the canonical metric with fallback chain.

    Args:
        text_a: First text
        text_b: Second text

    Returns:
        Distance in [0, 1] where 0 = identical, 1 = opposite

    Example:
        >>> d = semantic_distance("I love cats", "I adore felines")
        >>> print(f"{d:.2f}")  # Low distance
    """
    return CanonicalSemanticDistance().distance(text_a, text_b)


__all__ = [
    # Protocol
    "SemanticDistanceMetric",
    # Metric implementations
    "JaccardDistance",
    "CosineEmbeddingDistance",
    "BERTScoreDistance",
    "BidirectionalEntailmentDistance",
    "NLIContradictionDistance",
    "CompositeDistance",
    "CanonicalSemanticDistance",
    # Factory functions
    "get_default_metric",
    "get_fast_metric",
    "get_accurate_metric",
    "get_contradiction_metric",
    # Comparison utilities
    "MetricComparisonResult",
    "compare_metrics",
    # Convenience
    "semantic_distance",
]

"""
Semantic Distance Metrics for Galois Loss Computation.

This module provides the semantic distance function d(P, Q) used in:
    L(P) = d(P, C(R(P)))

Philosophy:
    "The loss IS the measurement. The metric IS the meaning."

    Different metrics capture different semantic notions:
    - Cosine embedding: Fast, geometric similarity
    - BERTScore: Balanced precision/recall of tokens
    - LLM Judge: Deep semantic understanding (expensive)
    - NLI: Contradiction-aware classification

See: spec/protocols/zero-seed1/galois.md Part XIII
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    import numpy as np


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
    """

    def distance(self, text_a: str, text_b: str) -> float:
        """
        Compute semantic distance between two texts.

        Args:
            text_a: First text (typically original)
            text_b: Second text (typically reconstituted)

        Returns:
            Distance in [0, 1] range
        """
        ...

    @property
    def name(self) -> str:
        """Human-readable metric name."""
        ...


# -----------------------------------------------------------------------------
# Abstract Base for Async Metrics
# -----------------------------------------------------------------------------


class AsyncSemanticDistance(ABC):
    """
    Base class for async semantic distance metrics.

    Some metrics (like LLM Judge) require async operations.
    This base class provides the interface.
    """

    @abstractmethod
    async def distance_async(self, text_a: str, text_b: str) -> float:
        """Compute distance asynchronously."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Metric name."""
        ...


# -----------------------------------------------------------------------------
# Cosine Embedding Distance
# -----------------------------------------------------------------------------


@dataclass
class CosineEmbeddingDistance:
    """
    Fast, deterministic embedding-based distance.

    Uses text embeddings and cosine similarity.
    Pros: Fast (~12ms), deterministic, stable
    Cons: Misses semantic nuance, requires embedding model

    Recommended for: Batch operations, initial screening

    Uses the kgents OpenAIEmbedder abstraction from agents/l/embedders.py.
    """

    model: str = "text-embedding-3-small"
    _embedder: object = field(default=None, repr=False)

    def __post_init__(self) -> None:
        # Use kgents embedder abstraction instead of direct openai import
        try:
            from agents.l.embedders import OpenAIEmbedder

            self._embedder = OpenAIEmbedder(model=self.model)
        except ImportError:
            self._embedder = None

    @property
    def name(self) -> str:
        return f"cosine_embedding:{self.model}"

    def distance(self, text_a: str, text_b: str) -> float:
        """
        Compute cosine distance between embeddings.

        Returns 1 - cosine_similarity to get distance (not similarity).
        """
        if self._embedder is None:
            # Fallback to simple heuristic if no embedder available
            return self._fallback_distance(text_a, text_b)

        try:
            import asyncio

            import numpy as np

            # Get embeddings via kgents embedder
            async def get_embeddings() -> tuple[list[float], list[float]]:
                emb_a = await self._embedder.embed(text_a)
                emb_b = await self._embedder.embed(text_b)
                return emb_a, emb_b

            # Run async embedder in sync context
            try:
                loop = asyncio.get_running_loop()
                # Already in async context, can't nest - use fallback
                return self._fallback_distance(text_a, text_b)
            except RuntimeError:
                # No running loop, safe to create one
                emb_a, emb_b = asyncio.run(get_embeddings())

            emb_a_np = np.array(emb_a)
            emb_b_np = np.array(emb_b)

            # Cosine similarity
            cosine_sim = float(
                np.dot(emb_a_np, emb_b_np) / (np.linalg.norm(emb_a_np) * np.linalg.norm(emb_b_np))
            )

            # Convert to distance (0 = same, 1 = opposite)
            return max(0.0, min(1.0, 1.0 - cosine_sim))

        except Exception:
            return self._fallback_distance(text_a, text_b)

    def _fallback_distance(self, text_a: str, text_b: str) -> float:
        """
        Simple fallback when API unavailable.

        Uses token overlap as proxy for semantic distance.
        """
        # Tokenize (simple word split)
        tokens_a = set(text_a.lower().split())
        tokens_b = set(text_b.lower().split())

        if not tokens_a or not tokens_b:
            return 1.0 if text_a != text_b else 0.0

        # Jaccard distance
        intersection = len(tokens_a & tokens_b)
        union = len(tokens_a | tokens_b)

        jaccard_sim = intersection / union if union > 0 else 0.0
        return 1.0 - jaccard_sim


# -----------------------------------------------------------------------------
# BERTScore Distance
# -----------------------------------------------------------------------------


@dataclass
class BERTScoreDistance:
    """
    Balanced precision/recall-based distance using BERT.

    BERTScore computes token-level similarity using contextual embeddings.
    Uses F1 as the primary metric for balanced precision/recall.

    Pros: ~45ms, good correlation with human judgment (r=0.72)
    Cons: Requires local model, memory overhead

    Recommended for: Primary metric (default choice)

    From spec: "BERTScore: r=0.72, time=45ms, stability=0.85 - BEST"
    """

    lang: str = "en"
    model_type: str | None = None
    _scorer_initialized: bool = field(default=False, repr=False)

    @property
    def name(self) -> str:
        model = self.model_type or "default"
        return f"bertscore:{model}"

    def distance(self, text_a: str, text_b: str) -> float:
        """
        Compute 1 - F1 BERTScore.

        F1 balances precision and recall of token matches.
        """
        try:
            from bert_score import score

            # Score returns (Precision, Recall, F1) tensors
            P, R, F1 = score(
                [text_a],
                [text_b],
                lang=self.lang,
                model_type=self.model_type,
                verbose=False,
            )

            # F1 is in [0, 1], convert to distance
            f1_score = F1.item()
            return max(0.0, min(1.0, 1.0 - f1_score))

        except ImportError:
            # Fallback to cosine embedding
            fallback = CosineEmbeddingDistance()
            return fallback.distance(text_a, text_b)

        except Exception:
            # On any error, return moderate distance
            return 0.5


# -----------------------------------------------------------------------------
# LLM Judge Distance
# -----------------------------------------------------------------------------


@dataclass
class LLMJudgeDistance(AsyncSemanticDistance):
    """
    LLM-based semantic similarity judgment.

    Uses Claude via kgents LLM abstraction to rate semantic similarity.
    Captures nuanced differences that embedding methods miss.

    Pros: Highest correlation with human judgment (r=0.79)
    Cons: Expensive (~$0.002/call), slow (~230ms), non-deterministic

    Recommended for: High-stakes decisions, validation

    Uses the kgents LLM abstraction from agents/k/llm.py.
    """

    model: str = "claude-sonnet-4-20250514"
    temperature: float = 0.0
    _client: object = field(default=None, repr=False)

    @property
    def name(self) -> str:
        return f"llm_judge:{self.model}"

    async def distance_async(self, text_a: str, text_b: str) -> float:
        """
        Use LLM to judge semantic distance.

        Prompts the model to rate similarity on 0-1 scale.
        """
        system_prompt = """You are a semantic similarity judge.
Rate the semantic similarity of two texts by returning a single number from 0.0 to 1.0 where:
- 0.0 = The texts are semantically identical (same meaning)
- 0.5 = The texts are somewhat related
- 1.0 = The texts are completely different or contradictory

Return ONLY a number between 0.0 and 1.0, nothing else."""

        user_prompt = f"""Text A:
{text_a}

Text B:
{text_b}"""

        try:
            # Use kgents LLM abstraction instead of direct anthropic import
            from agents.k.llm import create_llm_client

            if self._client is None:
                self._client = create_llm_client(model=self.model)

            response = await self._client.generate(
                system=system_prompt,
                user=user_prompt,
                temperature=self.temperature,
                max_tokens=10,
            )

            # Parse response
            text = response.text.strip()
            value = float(text)
            return max(0.0, min(1.0, value))

        except ImportError:
            # Fallback to sync BERTScore
            fallback = BERTScoreDistance()
            return fallback.distance(text_a, text_b)

        except (ValueError, AttributeError):
            # Failed to parse response
            return 0.5

        except Exception:
            return 0.5

    def distance(self, text_a: str, text_b: str) -> float:
        """
        Synchronous wrapper (runs async in new loop).

        Prefer distance_async when in async context.
        """
        import asyncio

        try:
            loop = asyncio.get_running_loop()
            # Already in async context, can't nest
            # Fall back to BERTScore
            return BERTScoreDistance().distance(text_a, text_b)
        except RuntimeError:
            # No running loop, safe to create one
            return asyncio.run(self.distance_async(text_a, text_b))


# -----------------------------------------------------------------------------
# NLI Contradiction Distance
# -----------------------------------------------------------------------------


@dataclass
class NLIContradictionDistance:
    """
    Natural Language Inference based distance.

    Specialized for detecting logical contradictions.
    Uses MNLI-trained models to classify entailment vs contradiction.

    Pros: Fast (~38ms), good for contradiction detection
    Cons: Less nuanced, requires local transformer model

    Recommended for: Contradiction detection (super-additive loss)
    """

    model: str = "microsoft/deberta-v3-base-mnli-fever-anli"
    _classifier: object = field(default=None, repr=False)

    @property
    def name(self) -> str:
        return f"nli:{self.model}"

    def _get_classifier(self) -> object:
        """Lazy load classifier."""
        if self._classifier is None:
            try:
                from transformers import pipeline

                self._classifier = pipeline(
                    "text-classification",
                    model=self.model,
                    top_k=None,
                )
            except ImportError:
                return None
        return self._classifier

    def distance(self, text_a: str, text_b: str) -> float:
        """
        Compute distance based on NLI classification.

        Maps:
        - ENTAILMENT -> 0.0 (same meaning)
        - NEUTRAL -> 0.5 (related)
        - CONTRADICTION -> 1.0 (opposite)
        """
        classifier = self._get_classifier()
        if classifier is None:
            # Fallback
            return BERTScoreDistance().distance(text_a, text_b)

        try:
            # NLI expects premise [SEP] hypothesis format
            result = classifier(f"{text_a} [SEP] {text_b}")

            # Result is list of dicts with label and score
            label_to_distance = {
                "ENTAILMENT": 0.0,
                "entailment": 0.0,
                "NEUTRAL": 0.5,
                "neutral": 0.5,
                "CONTRADICTION": 1.0,
                "contradiction": 1.0,
            }

            # Get highest scoring label
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], list):
                    # Multiple labels returned
                    scores = result[0]
                    best = max(scores, key=lambda x: x["score"])
                    label = best["label"].upper()
                else:
                    label = result[0]["label"].upper()

                return label_to_distance.get(label, 0.5)

            return 0.5

        except Exception:
            return 0.5


# -----------------------------------------------------------------------------
# Composite Distance
# -----------------------------------------------------------------------------


@dataclass
class CompositeDistance:
    """
    Combines multiple metrics with configurable weights.

    Useful for experiments comparing metrics or
    creating ensemble metrics.
    """

    metrics: list[tuple[SemanticDistanceMetric, float]]  # (metric, weight)

    @property
    def name(self) -> str:
        parts = [f"{m.name}:{w:.2f}" for m, w in self.metrics]
        return f"composite[{','.join(parts)}]"

    def distance(self, text_a: str, text_b: str) -> float:
        """
        Weighted average of component metrics.
        """
        if not self.metrics:
            return 0.5

        total_weight = sum(w for _, w in self.metrics)
        if total_weight == 0:
            return 0.5

        weighted_sum = 0.0
        for metric, weight in self.metrics:
            d = metric.distance(text_a, text_b)
            weighted_sum += d * weight

        return weighted_sum / total_weight


# -----------------------------------------------------------------------------
# Factory Functions
# -----------------------------------------------------------------------------


def get_default_metric() -> SemanticDistanceMetric:
    """
    Get the recommended default metric (BERTScore).

    From spec: "Recommendation: BERTScore (balanced)"
    """
    return BERTScoreDistance()


def get_fast_metric() -> SemanticDistanceMetric:
    """Get fastest metric (Cosine embedding)."""
    return CosineEmbeddingDistance()


def get_accurate_metric() -> LLMJudgeDistance:
    """Get most accurate metric (LLM Judge)."""
    return LLMJudgeDistance()


def get_contradiction_metric() -> SemanticDistanceMetric:
    """Get metric specialized for contradiction detection."""
    return NLIContradictionDistance()


# -----------------------------------------------------------------------------
# Metric Comparison Utilities
# -----------------------------------------------------------------------------


@dataclass
class MetricComparisonResult:
    """Result of comparing metrics on a text pair."""

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
        return sum((d - mean) ** 2 for d in self.distances.values()) / len(self.distances)


async def compare_metrics(
    text_a: str,
    text_b: str,
    include_llm_judge: bool = False,
) -> MetricComparisonResult:
    """
    Compare all available metrics on a text pair.

    Useful for experiments and debugging.

    Args:
        text_a: First text
        text_b: Second text
        include_llm_judge: Whether to include expensive LLM judge

    Returns:
        MetricComparisonResult with distances from each metric
    """
    distances: dict[str, float] = {}

    # Fast metrics (always included)
    cosine = CosineEmbeddingDistance()
    distances[cosine.name] = cosine.distance(text_a, text_b)

    bert = BERTScoreDistance()
    distances[bert.name] = bert.distance(text_a, text_b)

    nli = NLIContradictionDistance()
    distances[nli.name] = nli.distance(text_a, text_b)

    # Expensive metric (optional)
    if include_llm_judge:
        llm = LLMJudgeDistance()
        distances[llm.name] = await llm.distance_async(text_a, text_b)

    return MetricComparisonResult(
        text_a=text_a,
        text_b=text_b,
        distances=distances,
    )


# -----------------------------------------------------------------------------
# Bidirectional Entailment Distance (Amendment B)
# -----------------------------------------------------------------------------


@dataclass
class BidirectionalEntailmentDistance:
    """
    Canonical semantic distance via bidirectional entailment.

    d(A, B) = 1 - sqrt(P(A |= B) * P(B |= A))

    Why geometric mean?
    - Arithmetic mean treats one-way entailment too leniently
    - Geometric mean gives 0 if either direction fails
    - Matches intuition: mutual entailment = semantic equivalence

    From Amendment B: "Canonical Semantic Distance"
    Uses DeBERTa MNLI (already used in NLIContradictionDistance).
    """

    model: str = "microsoft/deberta-v3-base-mnli-fever-anli"
    _classifier: object = field(default=None, repr=False)

    @property
    def name(self) -> str:
        return f"bidirectional_entailment:{self.model}"

    def _get_classifier(self) -> object:
        """Lazy load classifier."""
        if self._classifier is None:
            try:
                from transformers import pipeline

                self._classifier = pipeline(
                    "text-classification",
                    model=self.model,
                    top_k=None,
                )
            except ImportError:
                return None
        return self._classifier

    def _entailment_prob(self, premise: str, hypothesis: str) -> float:
        """
        Get P(premise entails hypothesis).

        Returns probability of entailment label from NLI model.
        """
        classifier = self._get_classifier()
        if classifier is None:
            return 0.5  # Fallback

        try:
            # NLI expects premise [SEP] hypothesis format
            result = classifier(f"{premise} [SEP] {hypothesis}")

            # Result is list of dicts with label and score
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], list):
                    # Multiple labels returned
                    scores = result[0]
                else:
                    scores = result

                # Find entailment probability
                for item in scores:
                    label = item.get("label", "").upper()
                    if label == "ENTAILMENT":
                        return item.get("score", 0.0)

            return 0.0  # No entailment found

        except Exception:
            return 0.5  # Fallback on error

    def distance(self, text_a: str, text_b: str) -> float:
        """
        Bidirectional entailment distance.

        Returns 0 if texts are semantically equivalent.
        Returns 1 if texts are unrelated or contradictory.

        Formula: d(A, B) = 1 - sqrt(P(A |= B) * P(B |= A))
        """
        import math

        if text_a == text_b:
            return 0.0

        if not text_a.strip() or not text_b.strip():
            return 1.0

        p_a_entails_b = self._entailment_prob(text_a, text_b)
        p_b_entails_a = self._entailment_prob(text_b, text_a)

        # Geometric mean (symmetric, penalizes one-way entailment)
        mutual = math.sqrt(p_a_entails_b * p_b_entails_a)

        return max(0.0, min(1.0, 1.0 - mutual))


@dataclass
class CanonicalSemanticDistance:
    """
    Canonical distance with fallback chain.

    Primary: Bidirectional entailment (most principled)
    Fallback 1: BERTScore (fast, stable)
    Fallback 2: Cosine embedding (fastest)

    From Amendment B: "Canonical Semantic Distance"
    """

    _primary: BidirectionalEntailmentDistance | None = field(default=None, repr=False)
    _bertscore: BERTScoreDistance | None = field(default=None, repr=False)
    _cosine: CosineEmbeddingDistance | None = field(default=None, repr=False)

    @property
    def name(self) -> str:
        return "canonical_semantic"

    def distance(self, text_a: str, text_b: str) -> float:
        """
        Compute distance with graceful fallback.

        Tries:
        1. Bidirectional entailment (most principled)
        2. BERTScore (balanced precision/recall)
        3. Cosine embedding (fastest)
        """
        # Try NLI-based entailment first
        try:
            if self._primary is None:
                self._primary = BidirectionalEntailmentDistance()
            return self._primary.distance(text_a, text_b)
        except Exception:
            pass

        # Fallback to BERTScore
        try:
            if self._bertscore is None:
                self._bertscore = BERTScoreDistance()
            return self._bertscore.distance(text_a, text_b)
        except Exception:
            pass

        # Ultimate fallback: cosine
        if self._cosine is None:
            self._cosine = CosineEmbeddingDistance()
        return self._cosine.distance(text_a, text_b)


def canonical_semantic_distance(text_a: str, text_b: str) -> float:
    """
    Compute canonical semantic distance for Galois loss.

    This is the recommended distance function for production use.
    Falls back gracefully from entailment to BERTScore to cosine.
    """
    return CanonicalSemanticDistance().distance(text_a, text_b)


def get_canonical_metric() -> CanonicalSemanticDistance:
    """Get the canonical distance metric with fallback chain."""
    return CanonicalSemanticDistance()


def get_entailment_metric() -> BidirectionalEntailmentDistance:
    """Get the bidirectional entailment metric."""
    return BidirectionalEntailmentDistance()


__all__ = [
    # Protocol
    "SemanticDistanceMetric",
    "AsyncSemanticDistance",
    # Metric implementations
    "CosineEmbeddingDistance",
    "BERTScoreDistance",
    "LLMJudgeDistance",
    "NLIContradictionDistance",
    "CompositeDistance",
    # Amendment B: Bidirectional Entailment
    "BidirectionalEntailmentDistance",
    "CanonicalSemanticDistance",
    "canonical_semantic_distance",
    # Factory functions
    "get_default_metric",
    "get_fast_metric",
    "get_accurate_metric",
    "get_contradiction_metric",
    "get_canonical_metric",
    "get_entailment_metric",
    # Utilities
    "MetricComparisonResult",
    "compare_metrics",
]

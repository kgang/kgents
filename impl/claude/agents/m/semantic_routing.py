"""
Semantic Routing: Locality-Aware Gradient Sensing.

Phase 6 enhancement: Instead of global sensing (all agents see all deposits),
semantic routing filters by concept similarity. An agent sensing at position P
gets stronger gradients for deposits semantically close to P.

The insight: not all pheromones should propagate equally.
Deposits about "python debugging" should be more visible to agents
at "code review" than agents at "grocery shopping".

Three approaches available (configurable):
1. Prefix matching (lightweight, no embeddings needed)
2. Graph distance (if concept topology available)
3. Embedding similarity (L-gent integration, highest quality)

Categorical insight: semantic filtering is a natural transformation
from the global sensing functor to the local sensing functor.

    η: Sense_global → Sense_local
    η_P : GlobalResults → LocalResults(P)

The locality parameter controls how fast gradients decay with semantic distance.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from .stigmergy import PheromoneField, SenseResult


# =============================================================================
# Similarity Provider Protocol
# =============================================================================


@runtime_checkable
class SimilarityProvider(Protocol):
    """Protocol for computing semantic similarity between concepts."""

    async def similarity(self, concept_a: str, concept_b: str) -> float:
        """
        Compute similarity between two concepts.

        Args:
            concept_a: First concept
            concept_b: Second concept

        Returns:
            Similarity score in [0, 1] where 1 is identical
        """
        ...


# =============================================================================
# Similarity Implementations
# =============================================================================


class PrefixSimilarity:
    """
    Lightweight similarity based on shared path prefixes.

    Works with hierarchical concept names like:
    - "code.python.debugging"
    - "code.python.testing"
    - "food.cooking.italian"

    Similarity is the fraction of shared path components.
    """

    def __init__(self, separator: str = ".") -> None:
        """
        Initialize prefix similarity.

        Args:
            separator: Path separator (default ".")
        """
        self._separator = separator

    async def similarity(self, concept_a: str, concept_b: str) -> float:
        """Compute similarity based on shared prefix."""
        if concept_a == concept_b:
            return 1.0

        parts_a = concept_a.split(self._separator)
        parts_b = concept_b.split(self._separator)

        # Count shared prefix
        shared = 0
        for pa, pb in zip(parts_a, parts_b):
            if pa == pb:
                shared += 1
            else:
                break

        # Normalize by max length
        max_len = max(len(parts_a), len(parts_b))
        if max_len == 0:
            return 0.0

        return shared / max_len


class KeywordSimilarity:
    """
    Similarity based on shared keywords (bag of words).

    Useful when concepts are natural language descriptions
    rather than hierarchical paths.
    """

    def __init__(self, stop_words: set[str] | None = None) -> None:
        """
        Initialize keyword similarity.

        Args:
            stop_words: Words to ignore in similarity computation
        """
        self._stop_words = stop_words or {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
        }

    async def similarity(self, concept_a: str, concept_b: str) -> float:
        """Compute similarity based on shared keywords."""
        if concept_a == concept_b:
            return 1.0

        # Tokenize and filter
        words_a = {
            w.lower() for w in concept_a.split() if w.lower() not in self._stop_words
        }
        words_b = {
            w.lower() for w in concept_b.split() if w.lower() not in self._stop_words
        }

        if not words_a or not words_b:
            return 0.0

        # Jaccard similarity
        intersection = len(words_a & words_b)
        union = len(words_a | words_b)

        return intersection / union if union > 0 else 0.0


class EmbeddingSimilarity:
    """
    High-quality similarity using L-gent embeddings.

    This integrates with L-gent's embedding infrastructure for
    semantic similarity computation. Cached for performance.
    """

    def __init__(
        self,
        embedder: Any,  # L-gent Embedder
        cache_size: int = 1000,
    ) -> None:
        """
        Initialize embedding similarity.

        Args:
            embedder: L-gent embedder (SentenceTransformerEmbedder, etc.)
            cache_size: Maximum number of cached embeddings
        """
        self._embedder = embedder
        self._cache: dict[str, list[float]] = {}
        self._cache_size = cache_size

    async def similarity(self, concept_a: str, concept_b: str) -> float:
        """Compute cosine similarity between concept embeddings."""
        if concept_a == concept_b:
            return 1.0

        # Get embeddings (cached)
        emb_a = await self._get_embedding(concept_a)
        emb_b = await self._get_embedding(concept_b)

        # Cosine similarity
        return self._cosine_similarity(emb_a, emb_b)

    async def _get_embedding(self, concept: str) -> list[float]:
        """Get embedding for concept, using cache."""
        if concept in self._cache:
            return self._cache[concept]

        # Evict if at capacity
        if len(self._cache) >= self._cache_size:
            # Remove oldest (simple FIFO - could use LRU)
            oldest = next(iter(self._cache))
            del self._cache[oldest]

        # Compute and cache
        embedding: list[float] = await self._embedder.embed(concept)
        self._cache[concept] = embedding
        return embedding

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)


class GraphSimilarity:
    """
    Similarity based on graph distance in concept topology.

    Requires a concept graph where nodes are concepts and
    edges represent semantic relationships.
    """

    def __init__(
        self,
        edges: dict[str, set[str]],  # Adjacency list
        max_distance: int = 5,
    ) -> None:
        """
        Initialize graph similarity.

        Args:
            edges: Adjacency list of concept graph
            max_distance: Maximum distance to consider (beyond = 0 similarity)
        """
        self._edges = edges
        self._max_distance = max_distance

    async def similarity(self, concept_a: str, concept_b: str) -> float:
        """Compute similarity based on shortest path distance."""
        if concept_a == concept_b:
            return 1.0

        distance = self._shortest_path(concept_a, concept_b)

        if distance is None or distance > self._max_distance:
            return 0.0

        # Convert distance to similarity (inverse relationship)
        return 1.0 / (1.0 + distance)

    def _shortest_path(self, start: str, end: str) -> int | None:
        """BFS shortest path between concepts."""
        if start not in self._edges or end not in self._edges:
            return None

        visited = {start}
        queue = [(start, 0)]

        while queue:
            current, distance = queue.pop(0)

            if current == end:
                return distance

            for neighbor in self._edges.get(current, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, distance + 1))

        return None


# =============================================================================
# Locality Configuration
# =============================================================================


@dataclass
class LocalityConfig:
    """
    Configuration for semantic locality filtering.

    The locality parameter controls the decay curve:
    - locality = 0: No filtering (global sensing)
    - locality = 1: Sharp cutoff (only exact matches)
    - locality in (0, 1): Gradual decay

    The formula: weight = similarity ^ (1 / (1 - locality))
    """

    locality: float = 0.5  # 0 = global, 1 = local
    threshold: float = 0.1  # Minimum similarity to include
    decay_exponent: float | None = None  # Override computed exponent

    def __post_init__(self) -> None:
        if self.locality < 0 or self.locality > 1:
            raise ValueError("locality must be in [0, 1]")
        if self.threshold < 0 or self.threshold > 1:
            raise ValueError("threshold must be in [0, 1]")

    def compute_weight(self, similarity: float) -> float:
        """
        Compute weight from similarity score.

        Higher locality = sharper decay.
        """
        if similarity < self.threshold:
            return 0.0

        if self.locality == 0:
            return 1.0  # No decay

        if self.locality >= 0.999:  # Avoid division by zero
            return 1.0 if similarity >= 0.999 else 0.0

        # Exponent determines decay steepness
        if self.decay_exponent is not None:
            exponent = self.decay_exponent
        else:
            # Compute from locality: higher locality = higher exponent
            exponent = 1.0 / (1.0 - self.locality)

        return float(similarity**exponent)


# =============================================================================
# Filtered Sense Result
# =============================================================================


@dataclass
class FilteredSenseResult:
    """
    Result of sensing with semantic filtering applied.

    Extends SenseResult with locality weighting information.
    """

    concept: str
    total_intensity: float
    trace_count: int
    dominant_depositor: str | None = None

    # Locality additions
    raw_intensity: float = 0.0  # Pre-filtering intensity
    similarity: float = 1.0  # Similarity to query position
    locality_weight: float = 1.0  # Weight applied
    query_position: str = ""  # Position from which sensing occurred


# =============================================================================
# Semantic Router
# =============================================================================


class SemanticRouter:
    """
    Locality-aware pheromone sensing and routing.

    Unlike the global CategoricalRouter, SemanticRouter filters results
    by semantic similarity to the sensing position. This creates "local"
    gradient fields where agents primarily sense deposits in their
    semantic neighborhood.

    The categorical insight: this is a natural transformation from
    global sensing to local sensing, parameterized by position.

    Example:
        router = SemanticRouter(
            field=pheromone_field,
            similarity=PrefixSimilarity(),
            locality=LocalityConfig(locality=0.5),
        )

        # Agent at "code.python" senses
        results = await router.sense("code.python")

        # Results weighted by similarity to "code.python":
        # - "code.python.debugging" → high weight
        # - "code.javascript" → medium weight
        # - "food.cooking" → low/zero weight
    """

    def __init__(
        self,
        field: "PheromoneField",
        similarity: SimilarityProvider,
        locality: LocalityConfig | None = None,
        default_agent: str = "default",
    ) -> None:
        """
        Initialize semantic router.

        Args:
            field: The pheromone field to sense
            similarity: Similarity provider for concept comparison
            locality: Locality configuration
            default_agent: Fallback agent when no gradient
        """
        self._field = field
        self._similarity = similarity
        self._locality = locality or LocalityConfig()
        self._default_agent = default_agent

        # Statistics
        self._sense_count = 0
        self._filtered_count = 0

    @property
    def field(self) -> "PheromoneField":
        """The underlying pheromone field."""
        return self._field

    @property
    def locality(self) -> LocalityConfig:
        """Current locality configuration."""
        return self._locality

    async def sense(self, position: str) -> list[FilteredSenseResult]:
        """
        Sense pheromones with locality filtering.

        Args:
            position: Current concept position

        Returns:
            List of filtered results, sorted by weighted intensity
        """
        self._sense_count += 1

        # Get global sense results
        global_results: list["SenseResult"] = await self._field.sense(position)

        # Filter by similarity
        filtered_results: list[FilteredSenseResult] = []

        for result in global_results:
            # Compute similarity to query position
            similarity = await self._similarity.similarity(position, result.concept)

            # Apply locality weighting
            weight = self._locality.compute_weight(similarity)

            if weight > 0:
                filtered_results.append(
                    FilteredSenseResult(
                        concept=result.concept,
                        total_intensity=result.total_intensity * weight,
                        trace_count=result.trace_count,
                        dominant_depositor=result.dominant_depositor,
                        raw_intensity=result.total_intensity,
                        similarity=similarity,
                        locality_weight=weight,
                        query_position=position,
                    )
                )
            else:
                self._filtered_count += 1

        # Sort by weighted intensity (descending)
        filtered_results.sort(key=lambda r: r.total_intensity, reverse=True)

        return filtered_results

    async def route(self, task_concept: str) -> str:
        """
        Route task to best agent via semantic gradients.

        Args:
            task_concept: The task's concept

        Returns:
            Agent ID to route to
        """
        results = await self.sense(task_concept)

        if not results:
            return self._default_agent

        # Best result by weighted intensity
        best = results[0]

        if best.dominant_depositor:
            return best.dominant_depositor

        return self._default_agent

    def stats(self) -> dict[str, Any]:
        """Get router statistics."""
        return {
            "sense_count": self._sense_count,
            "filtered_count": self._filtered_count,
            "filter_ratio": (self._filtered_count / max(self._sense_count, 1)),
            "locality": self._locality.locality,
            "threshold": self._locality.threshold,
        }


# =============================================================================
# Semantic Gradient Map
# =============================================================================


@dataclass
class SemanticGradientMap:
    """
    Snapshot of semantic gradients at a position.

    Similar to GradientMap but includes similarity information.
    """

    position: str
    gradients: dict[str, float]  # agent_id → weighted intensity
    similarities: dict[str, float]  # concept → similarity to position
    sensed_at: datetime = field(default_factory=datetime.now)
    total_intensity: float = 0.0
    locality_config: LocalityConfig | None = None

    def strongest(self) -> tuple[str, float] | None:
        """Get the strongest gradient."""
        if not self.gradients:
            return None
        agent_id = max(self.gradients.keys(), key=lambda k: self.gradients[k])
        return (agent_id, self.gradients[agent_id])

    def top_k(self, k: int = 3) -> list[tuple[str, float]]:
        """Get top k gradients."""
        sorted_gradients = sorted(
            self.gradients.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        return sorted_gradients[:k]

    def concepts_by_similarity(self) -> list[tuple[str, float]]:
        """Get concepts sorted by similarity to position."""
        return sorted(
            self.similarities.items(),
            key=lambda x: x[1],
            reverse=True,
        )


# =============================================================================
# Factory Functions
# =============================================================================


def create_semantic_router(
    field: "PheromoneField",
    similarity_type: str = "prefix",
    locality: float = 0.5,
    threshold: float = 0.1,
    **similarity_kwargs: Any,
) -> SemanticRouter:
    """
    Factory function to create SemanticRouter with common configurations.

    Args:
        field: The pheromone field
        similarity_type: "prefix", "keyword", "embedding", or "graph"
        locality: Locality parameter (0 = global, 1 = local)
        threshold: Minimum similarity threshold
        **similarity_kwargs: Additional arguments for similarity provider

    Returns:
        Configured SemanticRouter
    """
    # Create similarity provider
    similarity: SimilarityProvider
    if similarity_type == "prefix":
        separator = similarity_kwargs.get("separator", ".")
        similarity = PrefixSimilarity(separator=separator)
    elif similarity_type == "keyword":
        stop_words = similarity_kwargs.get("stop_words")
        similarity = KeywordSimilarity(stop_words=stop_words)
    elif similarity_type == "embedding":
        embedder = similarity_kwargs.get("embedder")
        if embedder is None:
            raise ValueError("embedding similarity requires 'embedder' argument")
        cache_size = similarity_kwargs.get("cache_size", 1000)
        similarity = EmbeddingSimilarity(embedder=embedder, cache_size=cache_size)
    elif similarity_type == "graph":
        edges = similarity_kwargs.get("edges")
        if edges is None:
            raise ValueError("graph similarity requires 'edges' argument")
        max_distance = similarity_kwargs.get("max_distance", 5)
        similarity = GraphSimilarity(edges=edges, max_distance=max_distance)
    else:
        raise ValueError(f"Unknown similarity type: {similarity_type}")

    # Create locality config
    locality_config = LocalityConfig(locality=locality, threshold=threshold)

    return SemanticRouter(
        field=field,
        similarity=similarity,
        locality=locality_config,
    )


async def create_lgent_semantic_router(
    field: "PheromoneField",
    model_name: str = "all-MiniLM-L6-v2",
    locality: float = 0.5,
    threshold: float = 0.1,
) -> SemanticRouter:
    """
    Create SemanticRouter with L-gent embedding similarity.

    This uses L-gent's SentenceTransformerEmbedder for high-quality
    semantic similarity computation.

    Args:
        field: The pheromone field
        model_name: Sentence transformer model name
        locality: Locality parameter
        threshold: Minimum similarity threshold

    Returns:
        Configured SemanticRouter with embedding similarity
    """
    try:
        from ..l.embedders import SentenceTransformerEmbedder

        embedder = SentenceTransformerEmbedder(model_name=model_name)
    except ImportError:
        raise ImportError(
            "L-gent embedders not available. "
            "Install with: pip install sentence-transformers"
        )

    return create_semantic_router(
        field=field,
        similarity_type="embedding",
        locality=locality,
        threshold=threshold,
        embedder=embedder,
    )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Protocol
    "SimilarityProvider",
    # Similarity implementations
    "PrefixSimilarity",
    "KeywordSimilarity",
    "EmbeddingSimilarity",
    "GraphSimilarity",
    # Configuration
    "LocalityConfig",
    # Results
    "FilteredSenseResult",
    "SemanticGradientMap",
    # Router
    "SemanticRouter",
    # Factory functions
    "create_semantic_router",
    "create_lgent_semantic_router",
]

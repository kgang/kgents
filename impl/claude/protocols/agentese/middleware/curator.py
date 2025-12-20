"""
Wundt Curator: Aesthetic Filtering Middleware

The Wundt Curve describes aesthetic value as an inverted U relative to novelty:
- Too simple (novelty < 0.1) = Boring
- Just right (0.1 <= novelty <= 0.9) = Interesting
- Too complex (novelty > 0.9) = Chaotic

The Curator filters Logos invocation results through this lens.

AGENTESE Context: self.judgment.*

Principle Alignment:
- Tasteful: Architectural quality filtering
- Joy-Inducing: Interesting > Boring or Chaotic
- Composable: Middleware pattern composes with any Logos operation
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Types ===

Verdict = Literal["boring", "interesting", "chaotic"]


# === Pure Functions ===


def wundt_score(novelty: float) -> float:
    """
    Compute Wundt aesthetic score from novelty.

    The Wundt Curve is an inverted U that peaks at mid-range novelty.
    Score = 4 * novelty * (1 - novelty)

    This gives:
    - novelty=0.0 -> score=0.0
    - novelty=0.5 -> score=1.0 (peak)
    - novelty=1.0 -> score=0.0

    Args:
        novelty: Value between 0.0 and 1.0

    Returns:
        Aesthetic score between 0.0 and 1.0
    """
    # Clamp to valid range
    n = max(0.0, min(1.0, novelty))
    return 4.0 * n * (1.0 - n)


def structural_surprise(output: Any, prior: Any) -> float:
    """
    Compute surprise using structural comparison.

    Fallback when embeddings are unavailable.

    Args:
        output: The generated output
        prior: The expected output (prior)

    Returns:
        Surprise value between 0.0 and 1.0
    """
    if prior is None:
        return 0.5  # Neutral surprise when no prior

    # Different types = high surprise
    if type(output) is not type(prior):
        return 0.9

    # String comparison
    if isinstance(output, str) and isinstance(prior, str):
        if not output or not prior:
            return 0.5 if output != prior else 0.0

        # Length ratio surprise
        len_ratio = len(output) / max(len(prior), 1)
        length_surprise = min(abs(1.0 - len_ratio), 1.0)

        # Character overlap (simple Jaccard-like)
        chars_out = set(output.lower())
        chars_prior = set(prior.lower())
        if chars_out or chars_prior:
            overlap = len(chars_out & chars_prior) / max(len(chars_out | chars_prior), 1)
            char_surprise = 1.0 - overlap
        else:
            char_surprise = 0.0

        return (length_surprise + char_surprise) / 2.0

    # Dict comparison
    if isinstance(output, dict) and isinstance(prior, dict):
        keys_out = set(output.keys())
        keys_prior = set(prior.keys())
        if not keys_out and not keys_prior:
            return 0.0
        overlap = len(keys_out & keys_prior) / max(len(keys_out | keys_prior), 1)
        return 1.0 - overlap

    # List comparison
    if isinstance(output, list) and isinstance(prior, list):
        if not output and not prior:
            return 0.0
        len_ratio = len(output) / max(len(prior), 1)
        return min(abs(1.0 - len_ratio), 1.0)

    # Numeric comparison
    if isinstance(output, (int, float)) and isinstance(prior, (int, float)):
        if prior == 0:
            return 1.0 if output != 0 else 0.0
        ratio = abs(output - prior) / abs(prior)
        return min(ratio, 1.0)

    # Default: equal = no surprise, different = some surprise
    return 0.0 if output == prior else 0.5


# === Semantic Distance ===


@runtime_checkable
class Embedder(Protocol):
    """Protocol for embedding text to vectors."""

    async def embed(self, text: str) -> list[float]:
        """Embed text to a vector."""
        ...


def cosine_distance(a: list[float], b: list[float]) -> float:
    """
    Compute cosine distance between two vectors.

    Returns:
        Distance between 0.0 (identical) and 1.0 (orthogonal)
    """
    if len(a) != len(b) or not a:
        return 0.5  # Fallback for mismatched vectors

    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.5  # Can't compare zero vectors

    similarity = dot_product / (norm_a * norm_b)
    # Clamp to [-1, 1] to handle floating point errors
    similarity = max(-1.0, min(1.0, similarity))
    # Convert similarity to distance
    return (1.0 - similarity) / 2.0


@dataclass
class SemanticDistance:
    """
    Computes semantic distance between texts using embeddings.

    Falls back to structural comparison if embeddings unavailable.

    Usage:
        distance = SemanticDistance(embedder=my_embedder)
        surprise = await distance("Hello world", "Greetings Earth")
    """

    embedder: Embedder | None = None
    _cache: dict[str, list[float]] = field(default_factory=dict)

    async def __call__(self, a: str, b: str) -> float:
        """
        Compute semantic distance between two texts.

        Args:
            a: First text
            b: Second text

        Returns:
            Distance between 0.0 (identical) and 1.0 (completely unrelated)
        """
        if self.embedder is None:
            return structural_surprise(a, b)

        try:
            embed_a = await self._get_embedding(a)
            embed_b = await self._get_embedding(b)
            return cosine_distance(embed_a, embed_b)
        except Exception:
            # Fall back to structural comparison
            return structural_surprise(a, b)

    async def _get_embedding(self, text: str) -> list[float]:
        """Get embedding with caching."""
        if text not in self._cache and self.embedder is not None:
            self._cache[text] = await self.embedder.embed(text)
        return self._cache.get(text, [])

    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self._cache.clear()


# === Taste Score ===


@dataclass(frozen=True)
class TasteScore:
    """
    Wundt curve evaluation result.

    Frozen to ensure immutability and enable hashing.

    Attributes:
        novelty: 0.0 = identical to prior, 1.0 = completely unexpected
        complexity: 0.0 = trivial, 1.0 = incomprehensible
        wundt_score: Inverted U score, peaks at ~0.5
        verdict: "boring", "interesting", or "chaotic"
    """

    novelty: float
    complexity: float
    wundt_score: float
    verdict: Verdict

    @classmethod
    def from_novelty(
        cls,
        novelty: float,
        complexity: float = 0.5,
        *,
        low_threshold: float = 0.1,
        high_threshold: float = 0.9,
    ) -> "TasteScore":
        """
        Create TasteScore from novelty value.

        Args:
            novelty: Measured novelty/surprise (0.0 to 1.0)
            complexity: Measured complexity (0.0 to 1.0)
            low_threshold: Below this = boring
            high_threshold: Above this = chaotic

        Returns:
            TasteScore with computed verdict
        """
        # Determine verdict
        if novelty < low_threshold:
            verdict: Verdict = "boring"
        elif novelty > high_threshold:
            verdict = "chaotic"
        else:
            verdict = "interesting"

        return cls(
            novelty=novelty,
            complexity=complexity,
            wundt_score=wundt_score(novelty),
            verdict=verdict,
        )

    @property
    def is_acceptable(self) -> bool:
        """True if verdict is interesting."""
        return self.verdict == "interesting"


# === Wundt Curator ===


# Paths exempt from aesthetic filtering
EXEMPT_PATHS = frozenset(
    {
        # Entropy operations should not be filtered
        "void.",
        # Temporal traces are factual
        "time.",
        # Avoid recursive filtering
        "self.judgment.",
        # System paths
        "world.agent.",
    }
)

EXEMPT_ASPECTS = frozenset(
    {
        # Historical data is factual
        ".witness",
        ".trace",
        # System operations
        ".list",
        ".affordances",
    }
)


@dataclass
class WundtCurator:
    """
    Logos middleware for aesthetic filtering.

    Applies the Wundt Curve to filter boring/chaotic output.

    Usage:
        curator = WundtCurator(low=0.1, high=0.9)
        result = await curator.filter(output, observer, logos)

    Or via Logos integration:
        curated_logos = logos.with_middleware(curator)
    """

    low_threshold: float = 0.1
    high_threshold: float = 0.9
    max_retries: int = 3
    distance: SemanticDistance = field(default_factory=SemanticDistance)

    def __post_init__(self) -> None:
        """Validate thresholds."""
        if not (0.0 <= self.low_threshold < self.high_threshold <= 1.0):
            raise ValueError(
                f"Thresholds must satisfy 0 <= low < high <= 1, "
                f"got low={self.low_threshold}, high={self.high_threshold}"
            )

    def is_path_exempt(self, path: str) -> bool:
        """
        Check if a path is exempt from filtering.

        Exempt paths include:
        - void.* (entropy operations)
        - time.* (temporal traces)
        - self.judgment.* (avoid recursion)
        - Paths ending in .witness, .trace
        """
        # Check prefix exemptions
        for prefix in EXEMPT_PATHS:
            if path.startswith(prefix):
                return True

        # Check suffix exemptions
        for suffix in EXEMPT_ASPECTS:
            if path.endswith(suffix):
                return True

        return False

    async def evaluate(
        self,
        content: Any,
        observer: "Umwelt[Any, Any]",
    ) -> TasteScore:
        """
        Evaluate content and return TasteScore.

        Args:
            content: The content to evaluate
            observer: The observer's Umwelt (contains expectations)

        Returns:
            TasteScore with novelty, complexity, and verdict
        """
        # Get prior expectation from observer context
        prior = self._get_expectation(observer)

        # Compute surprise/novelty
        content_str = self._to_string(content)
        prior_str = self._to_string(prior) if prior is not None else ""

        if prior is None:
            novelty = 0.5  # Neutral when no expectation
        else:
            novelty = await self.distance(content_str, prior_str)

        # Compute complexity (simple heuristic)
        complexity = self._estimate_complexity(content)

        return TasteScore.from_novelty(
            novelty=novelty,
            complexity=complexity,
            low_threshold=self.low_threshold,
            high_threshold=self.high_threshold,
        )

    async def filter(
        self,
        result: Any,
        observer: "Umwelt[Any, Any]",
        path: str,
        logos: Any = None,  # Logos type to avoid circular import
    ) -> Any:
        """
        Filter result through Wundt Curve.

        Args:
            result: The result to filter
            observer: The observer's Umwelt
            path: The AGENTESE path that produced this result
            logos: Optional Logos instance for enhancement/compression

        Returns:
            Filtered result (may be modified if boring/chaotic)
        """
        # Skip exempt paths
        if self.is_path_exempt(path):
            return result

        # Evaluate
        score = await self.evaluate(result, observer)

        # Pass through interesting content
        if score.is_acceptable:
            return result

        # Attempt remediation if Logos available
        if logos is not None:
            if score.verdict == "boring":
                return await self._enhance(result, observer, logos)
            elif score.verdict == "chaotic":
                return await self._compress(result, observer, logos)

        # Return as-is if no Logos for remediation
        return result

    async def _enhance(
        self,
        result: Any,
        observer: "Umwelt[Any, Any]",
        logos: Any,
    ) -> Any:
        """
        Enhance boring content by injecting entropy.

        Args:
            result: The boring result
            observer: The observer's Umwelt
            logos: Logos instance for invocations

        Returns:
            Enhanced result
        """
        for attempt in range(self.max_retries):
            try:
                # Get entropy
                noise = await logos.invoke("void.entropy.sip", observer)

                # Blend result with noise
                enhanced = await logos.invoke(
                    "concept.blend.forge",
                    observer,
                    inputs=[result, noise],
                )

                # Check if enhancement worked
                score = await self.evaluate(enhanced, observer)
                if score.is_acceptable:
                    return enhanced
            except Exception:
                # Enhancement failed, continue trying
                pass

        # Return original if enhancement failed
        return result

    async def _compress(
        self,
        result: Any,
        observer: "Umwelt[Any, Any]",
        logos: Any,
    ) -> Any:
        """
        Compress chaotic content toward coherence.

        Args:
            result: The chaotic result
            observer: The observer's Umwelt
            logos: Logos instance for invocations

        Returns:
            Compressed result
        """
        for attempt in range(self.max_retries):
            try:
                compressed = await logos.invoke(
                    "concept.summary.refine",
                    observer,
                    input=result,
                    target_coherence=0.7,
                )

                # Check if compression worked
                score = await self.evaluate(compressed, observer)
                if score.is_acceptable:
                    return compressed
            except Exception:
                # Compression failed, continue trying
                pass

        # Return original if compression failed
        return result

    def _get_expectation(self, observer: "Umwelt[Any, Any]") -> Any:
        """Get prior expectation from observer's context."""
        try:
            # Use getattr for type safety - Umwelt may have different implementations
            context = getattr(observer, "context", {})
            if isinstance(context, dict):
                expectations = context.get("expectations", {})
                if isinstance(expectations, dict):
                    return expectations.get("prior")
            return None
        except Exception:
            return None

    @staticmethod
    def _to_string(value: Any) -> str:
        """Convert value to string for comparison."""
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        if isinstance(value, (dict, list)):
            import json

            try:
                return json.dumps(value, default=str)
            except Exception:
                return str(value)
        return str(value)

    @staticmethod
    def _estimate_complexity(value: Any) -> float:
        """
        Estimate complexity of a value.

        Simple heuristic based on:
        - String length
        - Nested structure depth
        - Number of unique tokens

        Returns:
            Complexity between 0.0 (trivial) and 1.0 (very complex)
        """
        if value is None:
            return 0.0

        if isinstance(value, str):
            length = len(value)
            # Logarithmic scaling: short = simple, long = complex
            # 100 chars -> 0.2, 1000 chars -> 0.4, 10000 chars -> 0.6
            length_factor = min(1.0, math.log10(max(length, 1) + 1) / 5.0)

            # Word diversity
            words = set(value.lower().split())
            diversity = min(1.0, len(words) / 100.0)

            return (length_factor + diversity) / 2.0

        if isinstance(value, dict):
            # Depth + breadth
            depth = _dict_depth(value)
            breadth = len(value)
            return min(1.0, (depth * 0.2) + (breadth * 0.01))

        if isinstance(value, list):
            length = len(value)
            return min(1.0, length * 0.05)

        return 0.3  # Default moderate complexity


def _dict_depth(d: dict[str, Any], current: int = 0) -> int:
    """Compute maximum depth of nested dict."""
    if not isinstance(d, dict) or not d:
        return current
    return (
        max(_dict_depth(v, current + 1) for v in d.values() if isinstance(v, dict)) or current + 1
    )

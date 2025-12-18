"""
Semantic Similarity: Compute similarity between section contents.

Wave 5 of the Evergreen Prompt System.

Uses multiple similarity strategies:
1. Token overlap (Jaccard similarity) - fast, no external deps
2. TF-IDF cosine similarity - good for longer content
3. Structural similarity - for markdown/code structure

The default strategy combines these with weighted averaging.
LLM-based embedding similarity is available but opt-in (Wave 6).
"""

from __future__ import annotations

import logging
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable

logger = logging.getLogger(__name__)

# Constants for validation
MAX_CONTENT_LENGTH = 1_000_000  # 1MB max content size
MIN_WEIGHT = 0.0
MAX_WEIGHT = 1.0


class SimilarityError(Exception):
    """Exception raised for similarity computation errors."""

    pass


class SimilarityStrategy(Enum):
    """Strategy for computing semantic similarity."""

    JACCARD = auto()  # Token overlap (Jaccard coefficient)
    TFIDF_COSINE = auto()  # TF-IDF weighted cosine similarity
    STRUCTURAL = auto()  # Markdown/code structure similarity
    COMBINED = auto()  # Weighted combination of above
    LLM_EMBEDDING = auto()  # LLM-based embeddings (requires API)


@dataclass(frozen=True)
class SimilarityResult:
    """
    Result of comparing two content strings.

    Attributes:
        score: Similarity score from 0.0 (completely different) to 1.0 (identical)
        strategy: Strategy used to compute similarity
        reasoning: Explanation of how score was computed
        breakdown: Per-strategy scores when using COMBINED
    """

    score: float
    strategy: SimilarityStrategy
    reasoning: str
    breakdown: dict[str, float] = field(default_factory=dict)

    def is_high_similarity(self, threshold: float = 0.8) -> bool:
        """Check if similarity exceeds threshold."""
        return self.score >= threshold

    def is_low_similarity(self, threshold: float = 0.3) -> bool:
        """Check if similarity is below threshold."""
        return self.score <= threshold


class SemanticSimilarity:
    """
    Compute semantic similarity between text contents.

    Uses heuristic methods that don't require external APIs.
    For production, consider adding LLM embedding support.

    Example:
        >>> sim = SemanticSimilarity()
        >>> result = sim.compare("The quick brown fox", "A fast brown fox")
        >>> print(result.score)
        0.67
    """

    def __init__(
        self,
        strategy: SimilarityStrategy = SimilarityStrategy.COMBINED,
        weights: dict[str, float] | None = None,
    ) -> None:
        """
        Initialize similarity calculator.

        Args:
            strategy: Which similarity method to use
            weights: Weights for COMBINED strategy
                     Default: {"jaccard": 0.3, "tfidf": 0.5, "structural": 0.2}

        Raises:
            SimilarityError: If strategy is invalid or weights are out of range
        """
        # Validate strategy
        if not isinstance(strategy, SimilarityStrategy):
            raise SimilarityError(f"Invalid strategy: {strategy}. Must be SimilarityStrategy enum.")

        self.strategy = strategy
        self.weights = weights or {
            "jaccard": 0.3,
            "tfidf": 0.5,
            "structural": 0.2,
        }

        # Validate weights
        self._validate_weights()

    def _validate_weights(self) -> None:
        """Validate that weights are within acceptable range."""
        for key, value in self.weights.items():
            if not isinstance(value, (int, float)):
                raise SimilarityError(f"Weight '{key}' must be numeric, got {type(value).__name__}")
            if value < MIN_WEIGHT or value > MAX_WEIGHT:
                raise SimilarityError(
                    f"Weight '{key}' must be between {MIN_WEIGHT} and {MAX_WEIGHT}, got {value}"
                )

        # Warn if weights don't sum to ~1.0
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.1:
            logger.warning(f"Weights sum to {total:.2f}, expected ~1.0. Results may be unexpected.")

    def _validate_content(self, content: str, name: str) -> None:
        """Validate content string."""
        if content is None:
            raise SimilarityError(f"{name} cannot be None")
        if not isinstance(content, str):
            raise SimilarityError(f"{name} must be a string, got {type(content).__name__}")
        if len(content) > MAX_CONTENT_LENGTH:
            raise SimilarityError(f"{name} exceeds maximum length of {MAX_CONTENT_LENGTH} chars")

    def compare(self, content_a: str, content_b: str) -> SimilarityResult:
        """
        Compare two content strings for semantic similarity.

        Args:
            content_a: First content string
            content_b: Second content string

        Returns:
            SimilarityResult with score and reasoning

        Raises:
            SimilarityError: If content is invalid (None, wrong type, too large)
        """
        # Validate inputs
        self._validate_content(content_a, "content_a")
        self._validate_content(content_b, "content_b")

        logger.debug(
            f"Comparing content: {len(content_a)} chars vs {len(content_b)} chars using {self.strategy.name}"
        )

        # Handle edge cases
        if not content_a and not content_b:
            return SimilarityResult(
                score=1.0,
                strategy=self.strategy,
                reasoning="Both contents are empty",
            )

        if not content_a or not content_b:
            return SimilarityResult(
                score=0.0,
                strategy=self.strategy,
                reasoning="One content is empty",
            )

        if content_a == content_b:
            return SimilarityResult(
                score=1.0,
                strategy=self.strategy,
                reasoning="Contents are identical",
            )

        # Dispatch to strategy
        if self.strategy == SimilarityStrategy.JACCARD:
            return self._jaccard_similarity(content_a, content_b)
        elif self.strategy == SimilarityStrategy.TFIDF_COSINE:
            return self._tfidf_similarity(content_a, content_b)
        elif self.strategy == SimilarityStrategy.STRUCTURAL:
            return self._structural_similarity(content_a, content_b)
        elif self.strategy == SimilarityStrategy.COMBINED:
            return self._combined_similarity(content_a, content_b)
        else:
            # Default to combined
            return self._combined_similarity(content_a, content_b)

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into lowercase words."""
        # Remove markdown/code artifacts and split on whitespace/punctuation
        cleaned = re.sub(r"[`#*_\[\](){}]", " ", text.lower())
        tokens = re.findall(r"\b\w+\b", cleaned)
        return tokens

    def _jaccard_similarity(self, a: str, b: str) -> SimilarityResult:
        """
        Compute Jaccard similarity (token overlap).

        Jaccard = |A ∩ B| / |A ∪ B|
        """
        tokens_a = set(self._tokenize(a))
        tokens_b = set(self._tokenize(b))

        if not tokens_a and not tokens_b:
            return SimilarityResult(
                score=1.0,
                strategy=SimilarityStrategy.JACCARD,
                reasoning="Both tokenize to empty sets",
            )

        intersection = tokens_a & tokens_b
        union = tokens_a | tokens_b

        score = len(intersection) / len(union) if union else 0.0

        return SimilarityResult(
            score=score,
            strategy=SimilarityStrategy.JACCARD,
            reasoning=f"Jaccard: {len(intersection)} shared / {len(union)} total tokens",
        )

    def _tfidf_similarity(self, a: str, b: str) -> SimilarityResult:
        """
        Compute TF-IDF weighted cosine similarity.

        More sophisticated than Jaccard - weights rare terms higher.
        Uses a modified IDF that doesn't zero out shared terms.
        """
        tokens_a = self._tokenize(a)
        tokens_b = self._tokenize(b)

        if not tokens_a or not tokens_b:
            return SimilarityResult(
                score=0.0,
                strategy=SimilarityStrategy.TFIDF_COSINE,
                reasoning="One or both tokenize to empty",
            )

        # Build term frequencies
        tf_a = Counter(tokens_a)
        tf_b = Counter(tokens_b)

        # All unique terms (our "corpus" is just these two docs)
        all_terms = set(tf_a.keys()) | set(tf_b.keys())

        # For a 2-doc corpus, use modified IDF that still values shared terms:
        # IDF = log(2 / df) for unique terms, 1.0 for shared terms
        # This ensures shared terms contribute to similarity
        idf: dict[str, float] = {}
        for term in all_terms:
            in_a = term in tf_a
            in_b = term in tf_b
            if in_a and in_b:
                # Shared terms: use a positive weight to capture similarity
                idf[term] = 1.0
            else:
                # Unique terms: higher weight (they differentiate docs)
                idf[term] = math.log(2.0)  # ~0.69

        # TF-IDF vectors (normalized TF * IDF)
        def tfidf_vector(tf: Counter[str]) -> dict[str, float]:
            total = sum(tf.values())
            if total == 0:
                return {}
            return {term: (count / total) * idf[term] for term, count in tf.items()}

        vec_a = tfidf_vector(tf_a)
        vec_b = tfidf_vector(tf_b)

        # Cosine similarity
        dot = sum(vec_a.get(t, 0) * vec_b.get(t, 0) for t in all_terms)
        mag_a = math.sqrt(sum(v**2 for v in vec_a.values()))
        mag_b = math.sqrt(sum(v**2 for v in vec_b.values()))

        if mag_a == 0 or mag_b == 0:
            score = 0.0
        else:
            score = dot / (mag_a * mag_b)

        # Clamp to [0, 1] (can sometimes exceed due to numerical issues)
        score = max(0.0, min(1.0, score))

        return SimilarityResult(
            score=score,
            strategy=SimilarityStrategy.TFIDF_COSINE,
            reasoning=f"TF-IDF cosine: {len(all_terms)} terms, score={score:.3f}",
        )

    def _structural_similarity(self, a: str, b: str) -> SimilarityResult:
        """
        Compute structural similarity based on markdown/code patterns.

        Compares:
        - Header structure (## sections)
        - Code block presence
        - List patterns
        - Line count ratio
        """

        # Extract structural features
        def extract_features(text: str) -> dict[str, int | float | bool]:
            lines = text.split("\n")
            return {
                "headers": len(re.findall(r"^#+\s", text, re.MULTILINE)),
                "code_blocks": len(re.findall(r"```", text)),
                "list_items": len(re.findall(r"^\s*[-*]\s", text, re.MULTILINE)),
                "line_count": len(lines),
                "avg_line_len": sum(len(l) for l in lines) / max(len(lines), 1),
                "has_table": "|" in text and "---" in text,
            }

        feat_a = extract_features(a)
        feat_b = extract_features(b)

        # Compare features
        scores: list[float] = []
        reasons: list[str] = []

        # Header similarity
        max_headers = max(feat_a["headers"], feat_b["headers"], 1)
        header_sim = 1 - abs(feat_a["headers"] - feat_b["headers"]) / max_headers
        scores.append(header_sim)
        reasons.append(f"headers: {header_sim:.2f}")

        # Code block similarity
        max_code = max(feat_a["code_blocks"], feat_b["code_blocks"], 1)
        code_sim = 1 - abs(feat_a["code_blocks"] - feat_b["code_blocks"]) / max_code
        scores.append(code_sim)
        reasons.append(f"code: {code_sim:.2f}")

        # Line count ratio
        max_lines = max(feat_a["line_count"], feat_b["line_count"], 1)
        min_lines = min(feat_a["line_count"], feat_b["line_count"], 1)
        line_sim = min_lines / max_lines
        scores.append(line_sim)
        reasons.append(f"lines: {line_sim:.2f}")

        # Table presence (binary match)
        table_sim = 1.0 if feat_a["has_table"] == feat_b["has_table"] else 0.5
        scores.append(table_sim)

        score = sum(scores) / len(scores)

        return SimilarityResult(
            score=score,
            strategy=SimilarityStrategy.STRUCTURAL,
            reasoning=f"Structural: {', '.join(reasons)}",
        )

    def _combined_similarity(self, a: str, b: str) -> SimilarityResult:
        """
        Compute weighted combination of all strategies.

        Default weights prioritize TF-IDF for semantic content,
        with Jaccard for quick overlap and structural for format.
        """
        jaccard = self._jaccard_similarity(a, b)
        tfidf = self._tfidf_similarity(a, b)
        structural = self._structural_similarity(a, b)

        w_j = self.weights.get("jaccard", 0.3)
        w_t = self.weights.get("tfidf", 0.5)
        w_s = self.weights.get("structural", 0.2)

        score = jaccard.score * w_j + tfidf.score * w_t + structural.score * w_s

        breakdown = {
            "jaccard": jaccard.score,
            "tfidf": tfidf.score,
            "structural": structural.score,
        }

        return SimilarityResult(
            score=score,
            strategy=SimilarityStrategy.COMBINED,
            reasoning=f"Combined: jaccard={jaccard.score:.2f}*{w_j}, tfidf={tfidf.score:.2f}*{w_t}, struct={structural.score:.2f}*{w_s}",
            breakdown=breakdown,
        )


def compute_similarity(
    content_a: str,
    content_b: str,
    strategy: SimilarityStrategy = SimilarityStrategy.COMBINED,
) -> SimilarityResult:
    """
    Convenience function to compute similarity between two strings.

    Args:
        content_a: First content
        content_b: Second content
        strategy: Similarity strategy to use

    Returns:
        SimilarityResult with score and reasoning

    Raises:
        SimilarityError: If content is invalid or computation fails
    """
    try:
        calculator = SemanticSimilarity(strategy=strategy)
        return calculator.compare(content_a, content_b)
    except SimilarityError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in similarity computation: {e}")
        raise SimilarityError(f"Failed to compute similarity: {e}") from e


__all__ = [
    "SimilarityStrategy",
    "SimilarityResult",
    "SimilarityError",
    "SemanticSimilarity",
    "compute_similarity",
    "MAX_CONTENT_LENGTH",
]

"""
Galois Loss Computation Module

Measures information loss during restructuring via the Galois connection:
    R: Content → ModularContent (restructure)
    C: ModularContent → Content (reconstitute)
    L(content) = d(content, C(R(content)))

Low loss = high coherence = self-justifying
Constitutional reward R = 1 - L (inverse Galois loss)

Spec: spec/theory/galois-modularization.md
Plan: plans/dgent-crystal-unification.md Phase 2
"""

import hashlib
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Any, Callable

from .crystal import Crystal

# =============================================================================
# Evidence Tier Classification
# =============================================================================


def classify_tier_by_loss(loss: float) -> str:
    """
    Map Galois loss to evidence tier.

    Args:
        loss: Galois loss in [0, 1] range

    Returns:
        Evidence tier string

    Tiers (from spec/theory/galois-modularization.md):
    - CATEGORICAL (< 0.1): Logical necessity, axiomatic truth
    - EMPIRICAL (< 0.3): Data-driven, reproducible evidence
    - AESTHETIC (< 0.5): Taste-based, subjective judgment
    - SOMATIC (< 0.7): Gut feeling, intuition
    - CHAOTIC (>= 0.7): Incoherent, high loss
    """
    if loss < 0.1:
        return "CATEGORICAL"
    elif loss < 0.3:
        return "EMPIRICAL"
    elif loss < 0.5:
        return "AESTHETIC"
    elif loss < 0.7:
        return "SOMATIC"
    else:
        return "CHAOTIC"


# =============================================================================
# Modular Content Representation
# =============================================================================


@dataclass(frozen=True)
class ModularContent:
    """
    Modular representation of content after restructuring.

    This is the intermediate form between R (restructure) and C (reconstitute).
    Contains both the decomposed units and their structural relationships.
    """

    modules: tuple[str, ...]
    """Individual content units (immutable tuple)."""

    structure: dict[str, Any]
    """Relationship metadata (composition order, dependencies, etc.)."""

    original_hash: str
    """Hash of original content for tracking."""

    @classmethod
    def from_content(cls, content: str, modules: list[str]) -> "ModularContent":
        """
        Create ModularContent from original content and modules.

        Args:
            content: Original content
            modules: List of module strings

        Returns:
            New ModularContent instance
        """
        return cls(
            modules=tuple(modules),
            structure={"composition": "sequential", "count": len(modules)},
            original_hash=hashlib.sha256(content.encode()).hexdigest()[:8],
        )


# =============================================================================
# Semantic Distance Metrics
# =============================================================================


def character_distance(a: str, b: str) -> float:
    """
    Character-level edit distance (Levenshtein-like).

    Fast, deterministic fallback when no embeddings available.

    Args:
        a: First string
        b: Second string

    Returns:
        Normalized distance in [0, 1]
    """
    if not a and not b:
        return 0.0
    if not a or not b:
        return 1.0

    matcher = SequenceMatcher(None, a, b)
    similarity = matcher.ratio()
    return 1.0 - similarity


def token_overlap_distance(a: str, b: str) -> float:
    """
    Token-level Jaccard distance.

    Better than character distance for semantic content.

    Args:
        a: First string
        b: Second string

    Returns:
        Normalized distance in [0, 1]
    """

    # Tokenize (simple whitespace + punctuation split)
    def tokenize(s: str) -> set[str]:
        tokens = re.findall(r"\w+", s.lower())
        return set(tokens)

    tokens_a = tokenize(a)
    tokens_b = tokenize(b)

    if not tokens_a and not tokens_b:
        return 0.0
    if not tokens_a or not tokens_b:
        return 1.0

    intersection = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)

    jaccard_similarity = intersection / union if union > 0 else 0.0
    return 1.0 - jaccard_similarity


def cosine_embedding_distance(a: str, b: str) -> float:
    """
    Cosine distance using embeddings (if available).

    Requires sentence-transformers or similar library.
    Falls back to token_overlap_distance if not available.

    Args:
        a: First string
        b: Second string

    Returns:
        Normalized distance in [0, 1]
    """
    try:
        # Try to import sentence-transformers
        import numpy as np
        from sentence_transformers import SentenceTransformer

        # Use cached model if available (global singleton pattern)
        if not hasattr(cosine_embedding_distance, "_model"):
            # Use small, fast model for MVP
            cosine_embedding_distance._model = SentenceTransformer("all-MiniLM-L6-v2")

        model = cosine_embedding_distance._model
        emb_a = model.encode(a)
        emb_b = model.encode(b)

        # Cosine similarity -> distance
        dot_product = np.dot(emb_a, emb_b)
        norm_a = np.linalg.norm(emb_a)
        norm_b = np.linalg.norm(emb_b)

        if norm_a == 0 or norm_b == 0:
            return 1.0

        cosine_sim = dot_product / (norm_a * norm_b)
        return 1.0 - cosine_sim

    except ImportError:
        # Fallback to token overlap
        return token_overlap_distance(a, b)


def bertscore_distance(a: str, b: str) -> float:
    """
    BERTScore-based distance (if available).

    Balanced accuracy/speed. Falls back to cosine_embedding_distance.

    Args:
        a: First string
        b: Second string

    Returns:
        Normalized distance in [0, 1]
    """
    try:
        from bert_score import score

        # Compute BERTScore
        _, _, F1 = score([a], [b], lang="en", verbose=False)
        return 1.0 - F1.item()

    except ImportError:
        # Fallback to embedding distance
        return cosine_embedding_distance(a, b)


async def llm_judge_distance(a: str, b: str, llm=None) -> float:
    """
    LLM-judged semantic distance (expensive but accurate).

    Requires an LLM instance. Optional fallback.

    Args:
        a: First string
        b: Second string
        llm: LLM instance (optional)

    Returns:
        Normalized distance in [0, 1]
    """
    if llm is None:
        # Fallback to embedding distance
        return cosine_embedding_distance(a, b)

    prompt = f"""Rate the semantic similarity of these two texts from 0.0 (identical meaning) to 1.0 (completely different meaning).
Focus on semantic content, not surface form.

Text A: {a}

Text B: {b}

Return only a number between 0.0 and 1.0."""

    try:
        response = await llm.generate(prompt, temperature=0.0)
        distance = float(response.strip())
        # Clamp to [0, 1]
        return max(0.0, min(1.0, distance))
    except Exception:
        # Fallback on error
        return cosine_embedding_distance(a, b)


# =============================================================================
# Metric Registry
# =============================================================================

METRICS: dict[str, Callable[[str, str], float]] = {
    "character": character_distance,
    "token": token_overlap_distance,
    "cosine": cosine_embedding_distance,
    "bertscore": bertscore_distance,
}


# =============================================================================
# Galois Loss Computer
# =============================================================================


@dataclass
class GaloisLossComputer:
    """
    Compute Galois loss L(P) = d(P, C(R(P))).

    This is the core implementation of the Galois connection for content:
    - R: Content → ModularContent (restructure, decompose)
    - C: ModularContent → Content (reconstitute, flatten)
    - L: Galois loss = semantic distance after round-trip

    Low loss means high coherence (content survives modularization).
    High loss means structure was lost (implicit knowledge disappeared).

    Philosophy (from spec/theory/galois-modularization.md):
    - Loss < 0.1: Axiomatic, self-evident (CATEGORICAL)
    - Loss < 0.3: Empirical, data-driven (EMPIRICAL)
    - Loss < 0.5: Aesthetic, taste-based (AESTHETIC)
    - Loss < 0.7: Somatic, gut-feeling (SOMATIC)
    - Loss >= 0.7: Chaotic, incoherent (CHAOTIC)
    """

    metric: str = "token"
    """Which distance metric to use (default: token overlap)."""

    llm: Any | None = None
    """Optional LLM for restructure/reconstitute (if None, uses heuristics)."""

    _metric_fn: Callable[[str, str], float] = field(init=False, repr=False)

    def __post_init__(self):
        """Validate and set metric function."""
        if self.metric not in METRICS:
            raise ValueError(f"Unknown metric '{self.metric}'. Choose from: {list(METRICS.keys())}")
        # Use object.__setattr__ since dataclass is frozen
        object.__setattr__(self, "_metric_fn", METRICS[self.metric])

    async def compute(self, content: str) -> float:
        """
        Compute Galois loss of content.

        This is the main entry point: L(content) = d(content, C(R(content)))

        Args:
            content: String content to measure

        Returns:
            Galois loss in [0, 1]

        Example:
            >>> computer = GaloisLossComputer()
            >>> await computer.compute("Earth is round")
            0.15  # Low loss = high coherence
        """
        if not content or not content.strip():
            return 0.0  # Empty content has zero loss

        # Restructure
        modular = await self.restructure(content)

        # Reconstitute
        reconstituted = await self.reconstitute(modular)

        # Measure distance
        return self._metric_fn(content, reconstituted)

    async def restructure(self, content: str) -> ModularContent:
        """
        R: Content → ModularContent (decompose into modules).

        If LLM available: Use LLM to intelligently decompose
        If no LLM: Use simple heuristic (split by sentences/paragraphs)

        Args:
            content: Original content

        Returns:
            ModularContent with decomposed units
        """
        if self.llm is not None:
            # LLM-based restructuring (future enhancement)
            # For now, fall through to heuristic
            pass

        # Heuristic restructuring: split by sentences/paragraphs
        modules = self._heuristic_split(content)
        return ModularContent.from_content(content, modules)

    async def reconstitute(self, modular: ModularContent) -> str:
        """
        C: ModularContent → Content (flatten modules back to content).

        If LLM available: Use LLM to intelligently reconstitute
        If no LLM: Use simple heuristic (join modules)

        Args:
            modular: ModularContent to flatten

        Returns:
            Reconstituted content string
        """
        if self.llm is not None:
            # LLM-based reconstitution (future enhancement)
            # For now, fall through to heuristic
            pass

        # Heuristic reconstitution: join modules
        return self._heuristic_join(modular)

    def _heuristic_split(self, content: str) -> list[str]:
        """
        Simple heuristic to split content into modules.

        Strategy:
        1. Try paragraph split (double newline)
        2. Fall back to sentence split (period + space)
        3. Fall back to single module

        Args:
            content: Content to split

        Returns:
            List of module strings
        """
        content = content.strip()

        # Try paragraph split
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        if len(paragraphs) > 1:
            return paragraphs

        # Try sentence split (crude)
        sentences = [s.strip() for s in re.split(r"\.\s+", content) if s.strip()]
        if len(sentences) > 1:
            # Re-add periods
            return [s + "." if not s.endswith(".") else s for s in sentences]

        # Single module
        return [content]

    def _heuristic_join(self, modular: ModularContent) -> str:
        """
        Simple heuristic to join modules back to content.

        Strategy: Join with appropriate separators based on content

        Args:
            modular: ModularContent to join

        Returns:
            Joined content string
        """
        if not modular.modules:
            return ""

        # Check if modules look like paragraphs (longer text)
        avg_length = sum(len(m) for m in modular.modules) / len(modular.modules)
        if avg_length > 100:
            # Join with paragraph separators
            return "\n\n".join(modular.modules)
        else:
            # Join with sentence separators
            return " ".join(modular.modules)


# =============================================================================
# Crystal Integration
# =============================================================================


async def compute_crystal_loss(
    crystal: "Crystal[Any]", metric: str = "token", llm: Any = None
) -> float:
    """
    Compute Galois loss for a Crystal.

    Extracts content from crystal, computes loss, and returns result.

    Args:
        crystal: Crystal to measure
        metric: Distance metric to use (default: token)
        llm: Optional LLM instance

    Returns:
        Galois loss in [0, 1]

    Example:
        >>> from agents.d.schemas.witness import WITNESS_MARK_SCHEMA
        >>> mark = WitnessMark(action="test", reasoning="example")
        >>> crystal = Crystal.create(mark, WITNESS_MARK_SCHEMA)
        >>> loss = await compute_crystal_loss(crystal)
        >>> tier = classify_tier_by_loss(loss)
    """
    # Extract content from crystal (convert value to string)
    # For WitnessMark: concatenate action + reasoning
    # For other types: use string representation
    value = crystal.value

    if hasattr(value, "action") and hasattr(value, "reasoning"):
        # WitnessMark-like structure
        content = f"{value.action}. {value.reasoning}"
    elif hasattr(value, "content"):
        # Content-like structure
        content = value.content
    else:
        # Generic: use string representation
        content = str(value)

    # Compute loss
    computer = GaloisLossComputer(metric=metric, llm=llm)
    return await computer.compute(content)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Core types
    "ModularContent",
    "GaloisLossComputer",
    # Metrics
    "character_distance",
    "token_overlap_distance",
    "cosine_embedding_distance",
    "bertscore_distance",
    "llm_judge_distance",
    "METRICS",
    # Classification
    "classify_tier_by_loss",
    # Crystal integration
    "compute_crystal_loss",
]

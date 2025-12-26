"""
Fixed-Point Detection with Rigor (Amendment F).

The problem: Fixed-point detection claims "content with L < 0.05 is a fixed point"
but doesn't verify stability under repeated application.

The fix: Verified fixed-point detection that checks both:
1. Initial loss < threshold
2. Stability under repeated R-C (variance < stability_threshold)

Philosophy:
    "A true fixed point doesn't just pass once--it remains stable.
     The axiom IS the stability. The proof IS the convergence."

Mathematical Formulation:
    A content P is a semantic fixed point iff:
    1. L(P) < epsilon (threshold)
    2. Var(L(R^n(P))) < delta for n in [1, max_iterations]

    This verifies the mathematical property: CR(P) ~= P

See: spec/protocols/zero-seed1/galois.md
See: plans/enlightened-synthesis/01-theoretical-amendments.md (Amendment F)
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .galois_loss import (
    FIXED_POINT_THRESHOLD,
    GaloisLossComputer,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

# Default stability threshold (variance must be below this)
STABILITY_THRESHOLD: float = 0.02

# Default max iterations for stability check
MAX_STABILITY_ITERATIONS: int = 3


# -----------------------------------------------------------------------------
# Fixed Point Result
# -----------------------------------------------------------------------------


@dataclass
class FixedPointResult:
    """
    Result of verified fixed-point detection.

    A true fixed point satisfies:
    1. Initial loss < threshold
    2. Remains stable (loss variance < stability_threshold) under repeated R-C

    Attributes:
        is_fixed_point: Whether content is a verified fixed point
        loss: Initial loss value
        stability: Standard deviation of losses across iterations (lower = more stable)
        iterations: Number of R-C iterations performed
        losses: List of loss values at each iteration
    """

    is_fixed_point: bool
    loss: float
    stability: float
    iterations: int
    losses: list[float] = field(default_factory=list)

    @property
    def is_axiom_candidate(self) -> bool:
        """
        True if this content qualifies as an axiom candidate.

        Axiom candidates are fixed points with very low initial loss.
        """
        return self.is_fixed_point and self.loss < 0.01

    @property
    def convergence_depth(self) -> int:
        """
        Depth at which content converges (first iteration below threshold).

        Returns -1 if never converges.
        """
        for i, loss in enumerate(self.losses):
            if loss < FIXED_POINT_THRESHOLD:
                return i + 1
        return -1

    @property
    def mean_loss(self) -> float:
        """Mean loss across all iterations."""
        if not self.losses:
            return self.loss
        return statistics.mean(self.losses)

    def to_dict(self) -> dict[str, object]:
        """Serialize to dictionary."""
        return {
            "is_fixed_point": self.is_fixed_point,
            "loss": self.loss,
            "stability": self.stability,
            "iterations": self.iterations,
            "losses": self.losses,
            "is_axiom_candidate": self.is_axiom_candidate,
            "convergence_depth": self.convergence_depth,
            "mean_loss": self.mean_loss,
        }


# -----------------------------------------------------------------------------
# Fixed Point Detection
# -----------------------------------------------------------------------------


async def detect_fixed_point(
    content: str,
    computer: GaloisLossComputer,
    threshold: float = FIXED_POINT_THRESHOLD,
    stability_threshold: float = STABILITY_THRESHOLD,
    max_iterations: int = MAX_STABILITY_ITERATIONS,
) -> FixedPointResult:
    """
    Detect if content is a semantic fixed point.

    A true fixed point:
    1. Has initial loss < threshold
    2. Remains stable (loss variance < stability_threshold) under repeated R-C

    This verifies the mathematical property: CR(P) ~= P

    Args:
        content: The content to test for fixed-point status
        computer: GaloisLossComputer for computing losses
        threshold: Maximum loss for fixed-point candidacy (default: 0.05)
        stability_threshold: Maximum standard deviation for stability (default: 0.02)
        max_iterations: Number of R-C iterations to verify stability (default: 3)

    Returns:
        FixedPointResult with verification details

    Example:
        >>> computer = GaloisLossComputer()
        >>> result = await detect_fixed_point("Agency requires justification", computer)
        >>> if result.is_fixed_point:
        ...     print(f"Axiom candidate with stability {result.stability:.3f}")
    """
    losses: list[float] = []
    current_content = content

    # First iteration: check if even a candidate
    initial_loss = await computer.compute_loss(current_content, use_cache=False)
    losses.append(initial_loss)

    if initial_loss >= threshold:
        # Not even a candidate - fail fast
        return FixedPointResult(
            is_fixed_point=False,
            loss=initial_loss,
            stability=1.0,  # Max instability
            iterations=1,
            losses=losses,
        )

    # Apply R-C repeatedly to check stability
    # Note: GaloisLossComputer.__post_init__ ensures llm is not None
    llm = computer.llm
    assert llm is not None, "GaloisLossComputer.llm must be initialized"

    for _ in range(max_iterations - 1):
        # Restructure and reconstitute
        modular = await llm.restructure(current_content)
        reconstituted = await llm.reconstitute(modular)

        # Compute loss on reconstituted content
        loss = await computer.compute_loss(reconstituted, use_cache=False)
        losses.append(loss)

        # Update content for next iteration
        current_content = reconstituted

    # Calculate stability (standard deviation of losses)
    if len(losses) >= 2:
        stability = statistics.stdev(losses)
    else:
        stability = 0.0

    # Fixed point requires:
    # 1. All losses below threshold
    # 2. Stability below threshold
    all_below_threshold = all(loss < threshold for loss in losses)
    stable = stability < stability_threshold

    is_fixed = all_below_threshold and stable

    return FixedPointResult(
        is_fixed_point=is_fixed,
        loss=losses[0],  # Initial loss
        stability=stability,
        iterations=len(losses),
        losses=losses,
    )


# -----------------------------------------------------------------------------
# Axiom Extraction
# -----------------------------------------------------------------------------


async def extract_axioms(
    corpus: Sequence[str],
    computer: GaloisLossComputer,
    top_k: int = 5,
    threshold: float = FIXED_POINT_THRESHOLD,
    stability_threshold: float = STABILITY_THRESHOLD,
) -> list[tuple[str, FixedPointResult]]:
    """
    Extract axiom candidates from a corpus.

    Returns top_k content items most likely to be semantic fixed points.
    Axiom candidates are sorted by initial loss (lower = more axiom-like).

    Args:
        corpus: Collection of content strings to analyze
        computer: GaloisLossComputer for computing losses
        top_k: Number of top candidates to return (default: 5)
        threshold: Maximum loss for fixed-point candidacy
        stability_threshold: Maximum stability (std dev) for candidates

    Returns:
        List of (content, FixedPointResult) tuples, sorted by loss

    Example:
        >>> corpus = [
        ...     "Agency requires justification",
        ...     "Composition is primary",
        ...     "Build a system that surfaces contradictions",
        ... ]
        >>> computer = GaloisLossComputer()
        >>> axioms = await extract_axioms(corpus, computer, top_k=2)
        >>> for content, result in axioms:
        ...     print(f"L={result.loss:.3f}: {content[:40]}...")
    """
    candidates: list[tuple[str, FixedPointResult]] = []

    for content in corpus:
        result = await detect_fixed_point(
            content,
            computer,
            threshold=threshold,
            stability_threshold=stability_threshold,
        )
        if result.is_fixed_point:
            candidates.append((content, result))

    # Sort by loss (lower = more axiom-like)
    candidates.sort(key=lambda x: x[1].loss)

    return candidates[:top_k]


# -----------------------------------------------------------------------------
# Batch Fixed Point Detection
# -----------------------------------------------------------------------------


async def batch_detect_fixed_points(
    corpus: Sequence[str],
    computer: GaloisLossComputer,
    threshold: float = FIXED_POINT_THRESHOLD,
    stability_threshold: float = STABILITY_THRESHOLD,
) -> dict[str, FixedPointResult]:
    """
    Batch detect fixed points across a corpus.

    Unlike extract_axioms, this returns results for ALL content items,
    not just those that qualify as fixed points.

    Args:
        corpus: Collection of content strings to analyze
        computer: GaloisLossComputer for computing losses
        threshold: Maximum loss for fixed-point candidacy
        stability_threshold: Maximum stability for candidates

    Returns:
        Dictionary mapping content to FixedPointResult
    """
    results: dict[str, FixedPointResult] = {}

    for content in corpus:
        result = await detect_fixed_point(
            content,
            computer,
            threshold=threshold,
            stability_threshold=stability_threshold,
        )
        results[content] = result

    return results


# -----------------------------------------------------------------------------
# Fixed Point Metrics
# -----------------------------------------------------------------------------


@dataclass
class FixedPointMetrics:
    """
    Aggregate metrics for fixed-point detection across a corpus.

    Useful for analyzing the quality of a corpus's foundational content.
    """

    total_analyzed: int
    fixed_point_count: int
    axiom_candidate_count: int
    mean_loss: float
    mean_stability: float
    loss_distribution: list[float]

    @property
    def fixed_point_ratio(self) -> float:
        """Ratio of content that qualifies as fixed points."""
        if self.total_analyzed == 0:
            return 0.0
        return self.fixed_point_count / self.total_analyzed

    @property
    def axiom_candidate_ratio(self) -> float:
        """Ratio of content that qualifies as axiom candidates."""
        if self.total_analyzed == 0:
            return 0.0
        return self.axiom_candidate_count / self.total_analyzed


async def compute_fixed_point_metrics(
    results: dict[str, FixedPointResult],
) -> FixedPointMetrics:
    """
    Compute aggregate metrics from batch fixed-point detection.

    Args:
        results: Dictionary from batch_detect_fixed_points

    Returns:
        FixedPointMetrics with aggregate statistics
    """
    if not results:
        return FixedPointMetrics(
            total_analyzed=0,
            fixed_point_count=0,
            axiom_candidate_count=0,
            mean_loss=0.0,
            mean_stability=0.0,
            loss_distribution=[],
        )

    all_results = list(results.values())
    losses = [r.loss for r in all_results]
    stabilities = [r.stability for r in all_results]

    return FixedPointMetrics(
        total_analyzed=len(all_results),
        fixed_point_count=sum(1 for r in all_results if r.is_fixed_point),
        axiom_candidate_count=sum(1 for r in all_results if r.is_axiom_candidate),
        mean_loss=statistics.mean(losses) if losses else 0.0,
        mean_stability=statistics.mean(stabilities) if stabilities else 0.0,
        loss_distribution=sorted(losses),
    )


# -----------------------------------------------------------------------------
# Module Exports
# -----------------------------------------------------------------------------

__all__ = [
    # Constants
    "STABILITY_THRESHOLD",
    "MAX_STABILITY_ITERATIONS",
    # Core types
    "FixedPointResult",
    "FixedPointMetrics",
    # Functions
    "detect_fixed_point",
    "extract_axioms",
    "batch_detect_fixed_points",
    "compute_fixed_point_metrics",
]

"""
Difficulty Measure for Galois Loss Calibration.

This module defines the ground-truth difficulty D(P) for prompts, used to
validate the core Galois bet: L(P) ∝ D(P).

Philosophy:
    "Difficulty = entropy × failure. The hybrid grounds both theory and practice."

The hybrid formula combines:
- H(P): Entropy of solution space (mathematical rigor)
- S(P): Success rate over trials (empirical grounding)

D(P) = H(P) × (1 - S(P))

Axioms:
- A_D1: D(P) ∈ [0, ∞) — non-negative
- A_D2: D(trivial) ≈ 0 — trivial prompts have near-zero difficulty
- A_D3: D(P₁ ∘ P₂) ≤ D(P₁) + D(P₂) — composition sub-additive
- A_D4: D(impossible) = ∞ — impossible tasks have infinite difficulty

See: plans/theory-operationalization/02-galois-theory.md (D(P) Axiomatization)
See: spec/protocols/zero-seed1/galois.md Part VII
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol, Sequence, runtime_checkable

if TYPE_CHECKING:
    from typing import Awaitable, Callable


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

# Default number of samples for entropy estimation
DEFAULT_ENTROPY_SAMPLES = 10

# Default number of trials for success rate measurement
DEFAULT_SUCCESS_TRIALS = 10

# Similarity threshold for clustering responses
DEFAULT_CLUSTER_THRESHOLD = 0.8

# Epsilon for numerical stability (avoid log(0))
EPSILON = 1e-10


# -----------------------------------------------------------------------------
# Core Data Types
# -----------------------------------------------------------------------------


@dataclass
class DifficultyMeasure:
    """
    Ground-truth difficulty measurement for a prompt.

    Combines entropy H(P) and success rate S(P) into hybrid difficulty:
    D(P) = H(P) × (1 - S(P))

    Attributes:
        entropy: H(P) - entropy of solution space in bits
        success_rate: S(P) - proportion of successful trials
        n_samples: Number of samples used for entropy estimation
        n_trials: Number of trials used for success rate
    """

    entropy: float  # H(P) in bits
    success_rate: float  # S(P) in [0, 1]
    n_samples: int = DEFAULT_ENTROPY_SAMPLES
    n_trials: int = DEFAULT_SUCCESS_TRIALS

    @property
    def difficulty(self) -> float:
        """
        Compute hybrid difficulty D(P) = H(P) × (1 - S(P)).

        Returns:
            Non-negative difficulty value
        """
        return self.entropy * (1.0 - self.success_rate)

    @property
    def failure_rate(self) -> float:
        """Convenience: 1 - success_rate."""
        return 1.0 - self.success_rate

    def validate_axioms(self) -> dict[str, bool]:
        """
        Validate the four difficulty axioms.

        Returns:
            Dict mapping axiom name to whether it holds
        """
        return {
            "A_D1_non_negative": self.difficulty >= 0,
            "A_D2_trivial_low": (self.success_rate < 0.99 or self.difficulty < 0.1),
            # A_D3 requires composition (checked externally)
            "A_D3_sub_additive": True,  # Placeholder - checked in composition
            # A_D4 requires impossible detection (checked externally)
            "A_D4_impossible_infinite": True,  # Placeholder - asymptotic check
        }

    def is_trivial(self, threshold: float = 0.1) -> bool:
        """Check if this represents a trivial prompt (D ≈ 0)."""
        return self.difficulty < threshold

    def is_difficult(self, threshold: float = 2.0) -> bool:
        """Check if this represents a difficult prompt (D > threshold)."""
        return self.difficulty > threshold

    def __str__(self) -> str:
        return f"D(P)={self.difficulty:.3f} (H={self.entropy:.3f} bits, S={self.success_rate:.2%})"


@dataclass
class DifficultyComparison:
    """
    Comparison of difficulty between two prompts.

    Used to verify A_D3 (sub-additivity under composition).
    """

    d1: DifficultyMeasure
    d2: DifficultyMeasure
    d_composed: DifficultyMeasure | None = None

    @property
    def sum_difficulty(self) -> float:
        """D(P₁) + D(P₂)."""
        return self.d1.difficulty + self.d2.difficulty

    @property
    def is_sub_additive(self) -> bool | None:
        """
        Check if A_D3 holds: D(P₁ ∘ P₂) ≤ D(P₁) + D(P₂).

        Returns None if composed difficulty not measured.
        """
        if self.d_composed is None:
            return None
        return self.d_composed.difficulty <= self.sum_difficulty + EPSILON


# -----------------------------------------------------------------------------
# Entropy Estimation
# -----------------------------------------------------------------------------


def compute_shannon_entropy(probabilities: Sequence[float]) -> float:
    """
    Compute Shannon entropy from probability distribution.

    H = -Σᵢ p(sᵢ) log₂ p(sᵢ)

    Args:
        probabilities: Probability distribution (should sum to 1)

    Returns:
        Entropy in bits (non-negative)
    """
    entropy = 0.0
    for p in probabilities:
        if p > EPSILON:
            entropy -= p * math.log2(p)
    return max(0.0, entropy)


def estimate_entropy_from_clusters(
    cluster_sizes: Sequence[int],
    total: int | None = None,
) -> float:
    """
    Estimate entropy from cluster sizes.

    Used when responses are grouped by semantic similarity.

    Args:
        cluster_sizes: Number of items in each cluster
        total: Total number of items (sum of cluster_sizes if None)

    Returns:
        Entropy in bits
    """
    if not cluster_sizes:
        return 0.0

    if total is None:
        total = sum(cluster_sizes)

    if total == 0:
        return 0.0

    probabilities = [size / total for size in cluster_sizes]
    return compute_shannon_entropy(probabilities)


# -----------------------------------------------------------------------------
# Difficulty Computer Protocol
# -----------------------------------------------------------------------------


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol for LLM completion providers."""

    async def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
    ) -> str:
        """Generate completion for a prompt."""
        ...


@runtime_checkable
class SimilarityMetric(Protocol):
    """Protocol for semantic similarity computation."""

    def distance(self, text_a: str, text_b: str) -> float:
        """Compute semantic distance in [0, 1]."""
        ...


@runtime_checkable
class SuccessEvaluator(Protocol):
    """Protocol for evaluating prompt response success."""

    async def evaluate(self, prompt: str, response: str) -> bool:
        """Evaluate if response is successful for prompt."""
        ...


# -----------------------------------------------------------------------------
# Difficulty Computer
# -----------------------------------------------------------------------------


@dataclass
class DifficultyComputer:
    """
    Computes ground-truth difficulty D(P) for prompts.

    Combines entropy estimation and success rate measurement into
    the hybrid difficulty formula.

    Example:
        computer = DifficultyComputer(llm=my_llm, evaluator=my_evaluator)
        measure = await computer.compute("Write a haiku about loss")
        print(f"Difficulty: {measure.difficulty}")
    """

    llm: LLMProvider
    evaluator: SuccessEvaluator
    similarity: SimilarityMetric | None = None
    n_samples: int = DEFAULT_ENTROPY_SAMPLES
    n_trials: int = DEFAULT_SUCCESS_TRIALS
    cluster_threshold: float = DEFAULT_CLUSTER_THRESHOLD

    async def compute(self, prompt: str) -> DifficultyMeasure:
        """
        Compute complete difficulty measure for a prompt.

        Performs:
        1. Entropy estimation via LLM sampling diversity
        2. Success rate measurement via N trials
        3. Hybrid difficulty calculation

        Args:
            prompt: The prompt to measure difficulty for

        Returns:
            DifficultyMeasure with entropy, success_rate, and difficulty
        """
        # Step 1: Estimate entropy
        entropy = await self.estimate_entropy(prompt)

        # Step 2: Measure success rate
        success_rate = await self.measure_success_rate(prompt)

        return DifficultyMeasure(
            entropy=entropy,
            success_rate=success_rate,
            n_samples=self.n_samples,
            n_trials=self.n_trials,
        )

    async def estimate_entropy(self, prompt: str) -> float:
        """
        Estimate solution space entropy via LLM sampling diversity.

        Generates multiple responses at high temperature, clusters by
        semantic similarity, and computes entropy over cluster distribution.

        Args:
            prompt: The prompt to estimate entropy for

        Returns:
            Entropy in bits (higher = more diverse solution space)
        """
        # Generate diverse samples
        responses: list[str] = []
        for _ in range(self.n_samples):
            response = await self.llm.complete(prompt, temperature=1.0)
            responses.append(response)

        # Cluster by similarity
        clusters = self._cluster_responses(responses)

        # Compute entropy over cluster distribution
        cluster_sizes = [len(c) for c in clusters]
        return estimate_entropy_from_clusters(cluster_sizes)

    async def measure_success_rate(self, prompt: str) -> float:
        """
        Measure success rate over N independent trials.

        Uses the configured evaluator to determine if each response
        is successful.

        Args:
            prompt: The prompt to measure success for

        Returns:
            Success rate in [0, 1]
        """
        successes = 0
        for _ in range(self.n_trials):
            response = await self.llm.complete(prompt, temperature=0.7)
            if await self.evaluator.evaluate(prompt, response):
                successes += 1
        return successes / self.n_trials

    def _cluster_responses(self, responses: list[str]) -> list[list[str]]:
        """
        Cluster responses by semantic similarity.

        Uses greedy clustering: assign each response to the first
        cluster within threshold, or create new cluster.

        Args:
            responses: List of response strings

        Returns:
            List of clusters (each cluster is a list of responses)
        """
        if not responses:
            return []

        if self.similarity is None:
            # Fallback: each response is its own cluster
            return [[r] for r in responses]

        clusters: list[list[str]] = []

        for response in responses:
            assigned = False
            for cluster in clusters:
                # Check similarity to first element (cluster centroid proxy)
                dist = self.similarity.distance(response, cluster[0])
                if dist < (1.0 - self.cluster_threshold):
                    cluster.append(response)
                    assigned = True
                    break

            if not assigned:
                clusters.append([response])

        return clusters


# -----------------------------------------------------------------------------
# Axiom Verification
# -----------------------------------------------------------------------------


def verify_sub_additivity(
    d1: DifficultyMeasure,
    d2: DifficultyMeasure,
    d_composed: DifficultyMeasure,
) -> bool:
    """
    Verify A_D3: D(P₁ ∘ P₂) ≤ D(P₁) + D(P₂).

    Args:
        d1: Difficulty of first prompt
        d2: Difficulty of second prompt
        d_composed: Difficulty of composed prompt

    Returns:
        True if sub-additivity holds
    """
    return d_composed.difficulty <= d1.difficulty + d2.difficulty + EPSILON


def verify_trivial_grounding(measure: DifficultyMeasure) -> bool:
    """
    Verify A_D2: Trivial prompts have near-zero difficulty.

    A prompt is trivial if success_rate ≈ 1.0.
    In that case, D(P) should ≈ 0.

    Args:
        measure: The difficulty measure to verify

    Returns:
        True if axiom holds
    """
    if measure.success_rate >= 0.99:
        return measure.difficulty < 0.1
    return True  # Not a trivial prompt, axiom doesn't apply


def verify_impossible_singularity(
    measures: Sequence[DifficultyMeasure],
) -> bool:
    """
    Verify A_D4: As S(P) → 0 and H(P) → ∞, D(P) → ∞.

    Checks that the trend is consistent with the asymptotic behavior.

    Args:
        measures: Sequence of difficulty measures ordered by increasing difficulty

    Returns:
        True if trend is consistent with A_D4
    """
    if len(measures) < 2:
        return True  # Can't verify trend with < 2 points

    # Check that difficulty increases as success_rate decreases
    # and entropy increases
    for i in range(1, len(measures)):
        prev = measures[i - 1]
        curr = measures[i]

        # If both success rate decreased and entropy increased,
        # difficulty should have increased
        if curr.success_rate < prev.success_rate and curr.entropy > prev.entropy:
            if curr.difficulty <= prev.difficulty:
                return False

    return True


# -----------------------------------------------------------------------------
# Factory Functions
# -----------------------------------------------------------------------------


def create_difficulty_measure(
    entropy: float,
    success_rate: float,
) -> DifficultyMeasure:
    """
    Create a DifficultyMeasure from known entropy and success rate.

    Useful for testing or when values are pre-computed.

    Args:
        entropy: H(P) in bits
        success_rate: S(P) in [0, 1]

    Returns:
        DifficultyMeasure instance
    """
    return DifficultyMeasure(
        entropy=max(0.0, entropy),
        success_rate=max(0.0, min(1.0, success_rate)),
    )


# -----------------------------------------------------------------------------
# Module Exports
# -----------------------------------------------------------------------------

__all__ = [
    # Constants
    "DEFAULT_ENTROPY_SAMPLES",
    "DEFAULT_SUCCESS_TRIALS",
    "DEFAULT_CLUSTER_THRESHOLD",
    "EPSILON",
    # Core types
    "DifficultyMeasure",
    "DifficultyComparison",
    # Entropy utilities
    "compute_shannon_entropy",
    "estimate_entropy_from_clusters",
    # Protocols
    "LLMProvider",
    "SimilarityMetric",
    "SuccessEvaluator",
    # Computer
    "DifficultyComputer",
    # Axiom verification
    "verify_sub_additivity",
    "verify_trivial_grounding",
    "verify_impossible_singularity",
    # Factory
    "create_difficulty_measure",
]

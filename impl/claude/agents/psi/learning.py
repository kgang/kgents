"""
Psi-gent v3.0 Learning System.

Thompson sampling for metaphor selection.
The key insight: metaphor selection is a contextual bandit problem.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Protocol

from .types import Feedback, Metaphor, Outcome, Problem, ProblemFeatures

# =============================================================================
# Reward Mapping
# =============================================================================


def outcome_to_reward(outcome: Outcome, distortion: float | None) -> float:
    """Convert outcome to reward signal."""
    base_rewards = {
        Outcome.SUCCESS: 1.0,
        Outcome.PARTIAL: 0.3,
        Outcome.CHALLENGE_FAILED: -0.3,
        Outcome.PROJECTION_FAILED: -0.5,
        Outcome.SOLVE_FAILED: -0.2,
        Outcome.VERIFY_FAILED: -0.1,
    }

    reward = base_rewards.get(outcome, 0.0)

    # Bonus/penalty based on distortion
    if outcome == Outcome.SUCCESS and distortion is not None:
        # Lower distortion = higher reward
        reward += (1.0 - distortion) * 0.3

    return reward


# =============================================================================
# Feature Extraction
# =============================================================================


def extract_features(problem: Problem) -> ProblemFeatures:
    """Extract learning features from a problem."""
    # Domain cluster via simple hashing
    domain_cluster = hash(problem.domain) % 100

    # Embedding cluster if available (placeholder - would use actual clustering)
    embedding_cluster = None
    if problem.embedding:
        # Simple hash-based cluster for now
        embedding_cluster = int(sum(problem.embedding[:10]) * 100) % 50

    return ProblemFeatures(
        domain=problem.domain,
        domain_cluster=domain_cluster,
        complexity=problem.complexity,
        constraint_count=len(problem.constraints),
        description_length=len(problem.description),
        has_embedding=problem.embedding is not None,
        embedding_cluster=embedding_cluster,
    )


# =============================================================================
# Retrieval Model Protocol
# =============================================================================


class RetrievalModel(Protocol):
    """Interface for learned metaphor retrieval."""

    def predict(self, features: ProblemFeatures, metaphor_id: str) -> float:
        """Predict expected reward for (features, metaphor) pair."""
        ...

    def predict_with_uncertainty(
        self, features: ProblemFeatures, metaphor_id: str
    ) -> tuple[float, float]:
        """Predict expected reward and uncertainty."""
        ...

    def update(self, feedback: Feedback) -> None:
        """Update model with new feedback."""
        ...

    @property
    def is_trained(self) -> bool:
        """Has the model seen enough data to be useful?"""
        ...


# =============================================================================
# Frequency Model (Simple Baseline)
# =============================================================================


@dataclass
class FrequencyModel:
    """Simple frequency-based model."""

    counts: dict[tuple[str, str], tuple[int, int]] = field(default_factory=dict)
    # (domain, metaphor_id) -> (successes, total)

    min_samples: int = 5
    _total_updates: int = 0

    def predict(self, features: ProblemFeatures, metaphor_id: str) -> float:
        """Predict success rate for this pairing."""
        key = (features.domain, metaphor_id)
        if key not in self.counts:
            return 0.5  # Prior: uncertain
        successes, total = self.counts[key]
        if total < self.min_samples:
            return 0.5  # Not enough data
        return successes / total

    def predict_with_uncertainty(
        self, features: ProblemFeatures, metaphor_id: str
    ) -> tuple[float, float]:
        """Predict with uncertainty estimate."""
        key = (features.domain, metaphor_id)
        if key not in self.counts:
            return 0.5, 0.5  # High uncertainty

        successes, total = self.counts[key]
        if total < self.min_samples:
            return 0.5, 0.4

        mean = successes / total
        # Approximate uncertainty via sample variance
        variance = mean * (1 - mean) / max(1, total - 1)
        return mean, variance**0.5

    def update(self, feedback: Feedback) -> None:
        """Update with new feedback."""
        key = (feedback.problem_features.domain, feedback.metaphor_id)
        successes, total = self.counts.get(key, (0, 0))
        if feedback.outcome == Outcome.SUCCESS:
            successes += 1
        total += 1
        self.counts[key] = (successes, total)
        self._total_updates += 1

    @property
    def is_trained(self) -> bool:
        """Has enough data been seen?"""
        return self._total_updates >= 20


# =============================================================================
# Thompson Sampling Model
# =============================================================================


@dataclass
class ThompsonSamplingModel:
    """Thompson sampling for exploration/exploitation balance."""

    # Per (domain, metaphor) Beta distribution parameters
    alphas: dict[tuple[str, str], float] = field(default_factory=dict)
    betas: dict[tuple[str, str], float] = field(default_factory=dict)

    prior_alpha: float = 1.0  # Initial optimism
    prior_beta: float = 1.0

    def _get_params(self, key: tuple[str, str]) -> tuple[float, float]:
        """Get Beta distribution parameters for a key."""
        alpha = self.alphas.get(key, self.prior_alpha)
        beta = self.betas.get(key, self.prior_beta)
        return alpha, beta

    def predict(self, features: ProblemFeatures, metaphor_id: str) -> float:
        """Return mean of Beta distribution (expected reward)."""
        key = (features.domain, metaphor_id)
        alpha, beta = self._get_params(key)
        return alpha / (alpha + beta)

    def predict_with_uncertainty(
        self, features: ProblemFeatures, metaphor_id: str
    ) -> tuple[float, float]:
        """Return mean and standard deviation."""
        key = (features.domain, metaphor_id)
        alpha, beta = self._get_params(key)
        mean = alpha / (alpha + beta)
        variance = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
        return mean, variance**0.5

    def sample(self, features: ProblemFeatures, metaphor_id: str) -> float:
        """Sample from the posterior (for Thompson sampling)."""
        key = (features.domain, metaphor_id)
        alpha, beta = self._get_params(key)
        return random.betavariate(alpha, beta)

    def update(self, feedback: Feedback) -> None:
        """Update Beta parameters with new feedback."""
        key = (feedback.problem_features.domain, feedback.metaphor_id)
        alpha, beta = self._get_params(key)

        # Binary reward for Beta distribution
        if feedback.outcome == Outcome.SUCCESS:
            self.alphas[key] = alpha + 1
            self.betas[key] = beta
        else:
            self.alphas[key] = alpha
            self.betas[key] = beta + 1

    @property
    def is_trained(self) -> bool:
        """Has enough data been seen?"""
        total_observations = sum(
            self.alphas.get(k, 1) + self.betas.get(k, 1) - 2
            for k in set(self.alphas.keys()) | set(self.betas.keys())
        )
        return total_observations >= 20

    def decay(self, rate: float = 0.99) -> None:
        """Decay historical influence toward prior."""
        for key in list(self.alphas.keys()):
            self.alphas[key] = max(self.prior_alpha, self.alphas[key] * rate)
            self.betas[key] = max(self.prior_beta, self.betas[key] * rate)


# =============================================================================
# Abstraction Model
# =============================================================================


@dataclass
class AbstractionModel:
    """Learn optimal abstraction level per problem type."""

    # (domain_cluster, complexity_bucket) -> successful abstraction levels
    history: dict[tuple[int, int], list[float]] = field(default_factory=dict)

    def _bucket_complexity(self, complexity: float) -> int:
        """Bucket complexity into discrete levels."""
        return int(complexity * 5)  # 0, 1, 2, 3, 4

    def suggest_abstraction(self, features: ProblemFeatures) -> float:
        """Suggest abstraction level based on history."""
        key = (features.domain_cluster, self._bucket_complexity(features.complexity))

        if key not in self.history or not self.history[key]:
            # Default: scale with complexity
            return 0.3 + features.complexity * 0.4

        # Return median of successful abstractions
        successful = sorted(self.history[key])
        mid = len(successful) // 2
        return successful[mid]

    def update(self, feedback: Feedback) -> None:
        """Record successful abstraction levels."""
        if feedback.outcome != Outcome.SUCCESS:
            return

        key = (
            feedback.problem_features.domain_cluster,
            self._bucket_complexity(feedback.problem_features.complexity),
        )

        if key not in self.history:
            self.history[key] = []
        self.history[key].append(feedback.abstraction)

        # Keep only recent history
        if len(self.history[key]) > 100:
            self.history[key] = self.history[key][-50:]


# =============================================================================
# Combined Retrieval with Learning
# =============================================================================


def retrieve_with_learning(
    problem: Problem,
    corpus: list[Metaphor],
    model: RetrievalModel,
    strategy: str = "thompson",
) -> list[tuple[Metaphor, float]]:
    """Retrieval informed by learning model."""
    features = extract_features(problem)
    scored: list[tuple[Metaphor, float]] = []

    for metaphor in corpus:
        if strategy == "thompson" and hasattr(model, "sample"):
            # Thompson sampling: sample from posterior
            score = model.sample(features, metaphor.id)
        elif strategy == "ucb":
            # Upper confidence bound
            mean, std = model.predict_with_uncertainty(features, metaphor.id)
            score = mean + 2.0 * std
        else:
            # Greedy: use expected reward
            score = model.predict(features, metaphor.id)

        scored.append((metaphor, score))

    return sorted(scored, key=lambda x: x[1], reverse=True)


# =============================================================================
# Cold Start
# =============================================================================


def cold_start_retrieval(
    problem: Problem,
    corpus: list[Metaphor],
) -> list[tuple[Metaphor, float]]:
    """Retrieval when learning model has no data."""
    # Fall back to domain keyword overlap
    problem_words = set(problem.description.lower().split())

    scored: list[tuple[Metaphor, float]] = []
    for metaphor in corpus:
        metaphor_words = set(metaphor.description.lower().split())
        overlap = len(problem_words & metaphor_words)
        # Normalize by metaphor description length
        score = overlap / max(1, len(metaphor_words))
        scored.append((metaphor, score))

    return sorted(scored, key=lambda x: x[1], reverse=True)

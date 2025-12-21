"""
ASHC Causal Graph Learning

Learn nudge → outcome relationships from accumulated evidence.
Predict outcomes for new nudges based on historical patterns.

This is complementary to causal_penalty.py:
- causal_penalty.py: "What principles caused this failure?" (retroactive blame)
- causal_graph.py: "What will happen if I apply this nudge?" (proactive prediction)

> "Run the tree a thousand times, and the pattern of nudges IS the proof."

Heritage: Bayesian structure learning, causal inference, SCM (Pearl)
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .evidence import Evidence, Run

from .evidence import Nudge

# =============================================================================
# CausalEdge: A Single Nudge → Outcome Relationship
# =============================================================================


@dataclass(frozen=True)
class CausalEdge:
    """
    A tracked relationship between a nudge and its outcome.

    Each edge represents observed causality:
    "When this nudge was applied, the pass rate changed by this much."

    Confidence increases with more observations of similar nudges.
    """

    nudge: Nudge
    outcome_delta: float  # Change in pass rate (-1.0 to +1.0)
    confidence: float  # How confident in this relationship (0.0 to 1.0)
    runs_observed: int  # How many runs inform this edge

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    @property
    def is_beneficial(self) -> bool:
        """Did this nudge improve outcomes?"""
        return self.outcome_delta > 0

    @property
    def is_harmful(self) -> bool:
        """Did this nudge harm outcomes?"""
        return self.outcome_delta < 0

    @property
    def is_neutral(self) -> bool:
        """Did this nudge have no significant effect?"""
        return abs(self.outcome_delta) < 0.05

    @property
    def effect_size(self) -> str:
        """Categorize the effect size."""
        delta = abs(self.outcome_delta)
        if delta < 0.05:
            return "negligible"
        elif delta < 0.15:
            return "small"
        elif delta < 0.30:
            return "medium"
        else:
            return "large"

    def with_observation(
        self,
        new_delta: float,
        weight: float = 1.0,
    ) -> "CausalEdge":
        """
        Update edge with a new observation.

        Uses exponential moving average to incorporate new data
        while preserving historical knowledge.
        """
        new_runs = self.runs_observed + 1

        # Confidence increases with more observations (asymptotic to 1.0)
        # Uses the count to boost confidence, preserving minimum of original
        count_confidence = 1.0 - (1.0 / (1.0 + new_runs * 0.2))
        new_confidence = max(self.confidence, count_confidence)

        # Weighted update of outcome delta
        alpha = weight / new_runs  # Newer observations get diminishing weight
        new_outcome = (1 - alpha) * self.outcome_delta + alpha * new_delta

        return CausalEdge(
            nudge=self.nudge,
            outcome_delta=new_outcome,
            confidence=new_confidence,
            runs_observed=new_runs,
            created_at=self.created_at,
            last_updated=datetime.now(),
        )


# =============================================================================
# Similarity Functions
# =============================================================================


def text_similarity(a: str, b: str) -> float:
    """
    Compute text similarity between two strings.

    Uses SequenceMatcher for simple but effective similarity.
    Returns 0.0 to 1.0.
    """
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def nudge_similarity(n1: Nudge, n2: Nudge) -> float:
    """
    Compute similarity between two nudges.

    Considers:
    - Location similarity (where in the spec)
    - Content similarity (what changed)
    - Reason similarity (why it changed)

    Returns 0.0 to 1.0.
    """
    # Weight different aspects
    location_weight = 0.3
    before_weight = 0.2
    after_weight = 0.3
    reason_weight = 0.2

    location_sim = text_similarity(n1.location, n2.location)
    before_sim = text_similarity(n1.before, n2.before)
    after_sim = text_similarity(n1.after, n2.after)
    reason_sim = text_similarity(n1.reason, n2.reason)

    return (
        location_weight * location_sim
        + before_weight * before_sim
        + after_weight * after_sim
        + reason_weight * reason_sim
    )


def is_similar_nudge(n1: Nudge, n2: Nudge, threshold: float = 0.7) -> bool:
    """Check if two nudges are similar enough to be considered related."""
    return nudge_similarity(n1, n2) >= threshold


# =============================================================================
# CausalGraph: Accumulated Edges with Prediction
# =============================================================================


@dataclass(frozen=True)
class CausalGraph:
    """
    Graph of nudge → outcome relationships.

    The graph accumulates edges from observed runs and can predict
    outcomes for new nudges based on similarity to historical nudges.

    Laws:
    - Causal Monotonicity: similar nudges should predict similar outcomes
    - Stability: small nudges should have small effects (on average)
    """

    edges: tuple[CausalEdge, ...] = ()

    # Configuration
    similarity_threshold: float = 0.7  # Min similarity for prediction
    min_confidence: float = 0.3  # Min confidence to use edge

    @property
    def edge_count(self) -> int:
        """Number of edges in the graph."""
        return len(self.edges)

    @property
    def total_observations(self) -> int:
        """Total number of run observations across all edges."""
        return sum(e.runs_observed for e in self.edges)

    def predict_outcome(self, proposed_nudge: Nudge) -> float:
        """
        Predict outcome of a new nudge based on history.

        Finds similar nudges in the graph and computes weighted average
        of their outcome deltas, weighted by similarity and confidence.

        Returns:
            Predicted delta (-1.0 to +1.0), or 0.0 if no similar nudges.
        """
        similar_edges = self._find_similar_edges(proposed_nudge)

        if not similar_edges:
            return 0.0  # No data, predict no change

        # Weighted average by similarity × confidence
        total_weight = 0.0
        weighted_sum = 0.0

        for edge, similarity in similar_edges:
            weight = similarity * edge.confidence
            weighted_sum += weight * edge.outcome_delta
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return weighted_sum / total_weight

    def predict_with_confidence(
        self,
        proposed_nudge: Nudge,
    ) -> tuple[float, float]:
        """
        Predict outcome with confidence interval.

        Returns:
            (predicted_delta, confidence) where confidence is 0.0 to 1.0.
        """
        similar_edges = self._find_similar_edges(proposed_nudge)

        if not similar_edges:
            return (0.0, 0.0)  # No data, no confidence

        # Aggregate confidence from similar edges
        prediction = self.predict_outcome(proposed_nudge)
        avg_similarity = statistics.mean(sim for _, sim in similar_edges)
        avg_edge_confidence = statistics.mean(e.confidence for e, _ in similar_edges)

        # Overall confidence = f(similarity, edge confidence, count)
        count_factor = 1.0 - (1.0 / (1.0 + len(similar_edges)))
        confidence = avg_similarity * avg_edge_confidence * count_factor

        return (prediction, confidence)

    def _find_similar_edges(
        self,
        nudge: Nudge,
    ) -> list[tuple[CausalEdge, float]]:
        """Find edges with similar nudges, above threshold."""
        similar = []
        for edge in self.edges:
            if edge.confidence < self.min_confidence:
                continue
            similarity = nudge_similarity(edge.nudge, nudge)
            if similarity >= self.similarity_threshold:
                similar.append((edge, similarity))
        return similar

    @property
    def stability_score(self) -> float:
        """
        How stable are outcomes under small nudges?

        High stability = small nudges cause small effects.
        Low stability = small nudges cause large effects (fragile).

        Returns 0.0 to 1.0.
        """
        # Consider nudges with small "after" content as "small nudges"
        small_nudges = [e for e in self.edges if len(e.nudge.after) < 100 and e.confidence > 0.3]

        if len(small_nudges) < 2:
            return 1.0  # Not enough data, assume stable

        deltas = [e.outcome_delta for e in small_nudges]
        variance = statistics.variance(deltas)

        # Transform variance to 0-1 score (high variance = low stability)
        return 1.0 / (1.0 + variance)

    @property
    def beneficial_edges(self) -> list[CausalEdge]:
        """Get edges where the nudge improved outcomes."""
        return [e for e in self.edges if e.is_beneficial]

    @property
    def harmful_edges(self) -> list[CausalEdge]:
        """Get edges where the nudge harmed outcomes."""
        return [e for e in self.edges if e.is_harmful]

    def with_edge(self, edge: CausalEdge) -> "CausalGraph":
        """Add or update an edge in the graph."""
        # Check if we have a similar existing edge
        for i, existing in enumerate(self.edges):
            if nudge_similarity(existing.nudge, edge.nudge) > 0.9:
                # Update existing edge
                updated = existing.with_observation(edge.outcome_delta)
                new_edges = list(self.edges)
                new_edges[i] = updated
                return CausalGraph(
                    edges=tuple(new_edges),
                    similarity_threshold=self.similarity_threshold,
                    min_confidence=self.min_confidence,
                )

        # Add new edge
        return CausalGraph(
            edges=self.edges + (edge,),
            similarity_threshold=self.similarity_threshold,
            min_confidence=self.min_confidence,
        )

    def merge(self, other: "CausalGraph") -> "CausalGraph":
        """Merge another graph into this one."""
        result = self
        for edge in other.edges:
            result = result.with_edge(edge)
        return result

    # =========================================================================
    # Law Verification
    # =========================================================================

    def verify_causal_monotonicity(self, tolerance: float = 0.15) -> bool:
        """
        Verify the Causal Monotonicity law.

        ∀ nudges n₁, n₂:
          similarity(n₁, n₂) > 0.9 ⟹ |predict(n₁) - predict(n₂)| < tolerance

        Similar nudges should predict similar outcomes.
        """
        for i, e1 in enumerate(self.edges):
            for e2 in self.edges[i + 1 :]:
                similarity = nudge_similarity(e1.nudge, e2.nudge)
                if similarity > 0.9:
                    delta_diff = abs(e1.outcome_delta - e2.outcome_delta)
                    if delta_diff >= tolerance:
                        return False
        return True

    def causal_monotonicity_violations(
        self,
        tolerance: float = 0.15,
    ) -> list[tuple[CausalEdge, CausalEdge, float]]:
        """
        Find all violations of causal monotonicity.

        Returns list of (edge1, edge2, delta_difference).
        """
        violations = []
        for i, e1 in enumerate(self.edges):
            for e2 in self.edges[i + 1 :]:
                similarity = nudge_similarity(e1.nudge, e2.nudge)
                if similarity > 0.9:
                    delta_diff = abs(e1.outcome_delta - e2.outcome_delta)
                    if delta_diff >= tolerance:
                        violations.append((e1, e2, delta_diff))
        return violations


# =============================================================================
# CausalLearner: Build Graph from Runs
# =============================================================================


@dataclass
class CausalLearner:
    """
    Learn causal relationships from evidence runs.

    Observes runs with nudges and builds up the CausalGraph
    by tracking which nudges lead to which outcomes.
    """

    graph: CausalGraph = field(default_factory=CausalGraph)

    # For computing deltas, we need a baseline
    baseline_pass_rate: float = 0.5

    def observe_run(
        self,
        run: "Run",
        baseline_pass_rate: float | None = None,
    ) -> None:
        """
        Observe a run and update the causal graph.

        For each nudge in the run, compute the outcome delta
        relative to baseline and add/update the corresponding edge.
        """
        if not run.nudges:
            return  # No nudges to learn from

        baseline = baseline_pass_rate or self.baseline_pass_rate
        outcome_delta = run.test_pass_rate - baseline

        for nudge in run.nudges:
            edge = CausalEdge(
                nudge=nudge,
                outcome_delta=outcome_delta,
                confidence=0.5,  # Initial confidence
                runs_observed=1,
            )
            self.graph = self.graph.with_edge(edge)

    def observe_evidence(
        self,
        evidence: "Evidence",
        baseline_pass_rate: float | None = None,
    ) -> None:
        """
        Observe all runs in an evidence corpus.

        Computes baseline from runs without nudges if not provided.
        """
        # Compute baseline from runs without nudges
        if baseline_pass_rate is None:
            no_nudge_runs = [r for r in evidence.runs if not r.nudges]
            if no_nudge_runs:
                baseline_pass_rate = statistics.mean(r.test_pass_rate for r in no_nudge_runs)
            else:
                baseline_pass_rate = self.baseline_pass_rate

        # Observe runs with nudges
        for run in evidence.runs:
            if run.nudges:
                self.observe_run(run, baseline_pass_rate)

    def compare_with_without(
        self,
        runs_with_nudge: list["Run"],
        runs_without_nudge: list["Run"],
        nudge: Nudge,
    ) -> CausalEdge:
        """
        Compare runs with and without a nudge to compute causal effect.

        This is the gold standard for causal inference:
        run the same spec with and without the nudge.
        """
        if not runs_with_nudge or not runs_without_nudge:
            raise ValueError("Need both with and without runs")

        # Compute average pass rates
        with_rate = statistics.mean(r.test_pass_rate for r in runs_with_nudge)
        without_rate = statistics.mean(r.test_pass_rate for r in runs_without_nudge)

        # Effect is the difference
        outcome_delta = with_rate - without_rate

        # Confidence based on sample sizes
        n_total = len(runs_with_nudge) + len(runs_without_nudge)
        confidence = 1.0 - (1.0 / (1.0 + n_total * 0.1))

        return CausalEdge(
            nudge=nudge,
            outcome_delta=outcome_delta,
            confidence=confidence,
            runs_observed=n_total,
        )

    def suggest_nudge(self, goal: str = "improve") -> Nudge | None:
        """
        Suggest a nudge based on historical effectiveness.

        Args:
            goal: "improve" for beneficial nudges, "stabilize" for neutral

        Returns:
            The most effective nudge for the goal, or None if no data.
        """
        if goal == "improve":
            candidates = sorted(
                self.graph.beneficial_edges,
                key=lambda e: e.outcome_delta * e.confidence,
                reverse=True,
            )
        elif goal == "stabilize":
            candidates = sorted(
                [e for e in self.graph.edges if e.is_neutral],
                key=lambda e: e.confidence,
                reverse=True,
            )
        else:
            candidates = sorted(
                self.graph.edges,
                key=lambda e: e.confidence,
                reverse=True,
            )

        return candidates[0].nudge if candidates else None


# =============================================================================
# Convenience Functions
# =============================================================================


def create_edge(
    location: str,
    before: str,
    after: str,
    reason: str,
    outcome_delta: float,
    confidence: float = 0.5,
    runs_observed: int = 1,
) -> CausalEdge:
    """Convenience function to create a CausalEdge."""
    nudge = Nudge(
        location=location,
        before=before,
        after=after,
        reason=reason,
    )
    return CausalEdge(
        nudge=nudge,
        outcome_delta=outcome_delta,
        confidence=confidence,
        runs_observed=runs_observed,
    )


def build_graph_from_edges(edges: list[CausalEdge]) -> CausalGraph:
    """Build a CausalGraph from a list of edges."""
    return CausalGraph(edges=tuple(edges))


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Core types
    "CausalEdge",
    "CausalGraph",
    "CausalLearner",
    # Similarity functions
    "text_similarity",
    "nudge_similarity",
    "is_similar_nudge",
    # Convenience
    "create_edge",
    "build_graph_from_edges",
]

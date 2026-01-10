"""
MarkConstitutionalEvaluator: Evaluate Marks Against Constitutional Principles.

This service evaluates individual marks against the 7 constitutional principles,
producing a ConstitutionalAlignment that can be attached to the mark.

Philosophy:
    "Every action justifies itself. Every mark carries its constitutional signature."

    The evaluator doesn't just score—it witnesses. Each evaluation creates a trace
    of how well an action adhered to the principles. Over time, these traces
    accumulate into constitutional trust.

Integration:
    - Called by ConstitutionalMarkReactor when marks are created
    - Uses Constitution.evaluate() from services/categorical/constitution.py
    - Produces ConstitutionalAlignment attached to marks
    - Feeds into ConstitutionalTrustComputer for trust level calculation

The Seven Principles:
    - ETHICAL: GATE (≥0.6 floor constraint, Amendment A) — safety first
    - COMPOSABLE: 1.5 weight — architecture second
    - JOY_INDUCING: 1.2 weight — Kent's aesthetic
    - TASTEFUL, CURATED, HETERARCHICAL, GENERATIVE: 1.0 weight each

Note: ETHICAL is NOT a weighted score. It's a floor constraint.
If ETHICAL < 0.6, action is REJECTED regardless of other scores.

See: spec/principles.md
See: services/categorical/constitution.py
See: services/witness/mark.py → ConstitutionalAlignment
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Protocol

from services.categorical.constitution import Constitution, ConstitutionalEvaluation, Principle
from services.witness.mark import ConstitutionalAlignment, Mark

logger = logging.getLogger("kgents.witness.constitutional_evaluator")


# =============================================================================
# Evaluator Protocol (for DI)
# =============================================================================


class ConstitutionalEvaluatorProtocol(Protocol):
    """Protocol for constitutional evaluators (enables DI for testing)."""

    async def evaluate(self, mark: Mark) -> ConstitutionalAlignment:
        """Evaluate a mark against constitutional principles."""
        ...

    def evaluate_sync(self, mark: Mark) -> ConstitutionalAlignment:
        """Synchronous evaluation (for non-async contexts)."""
        ...


# =============================================================================
# MarkConstitutionalEvaluator
# =============================================================================


@dataclass
class MarkConstitutionalEvaluator:
    """
    Evaluate marks against the 7 constitutional principles.

    This evaluator bridges the Mark system to the Constitution reward function.
    It extracts state/action/context from marks and computes principle scores.

    Usage:
        >>> evaluator = MarkConstitutionalEvaluator()
        >>> alignment = await evaluator.evaluate(mark)
        >>> enriched_mark = mark.with_constitutional(alignment)

    Scoring Strategy:
        1. Extract state_before from mark.stimulus
        2. Extract action from mark.response
        3. Build context from mark.metadata, umwelt, tags
        4. Call Constitution.evaluate(state_before, action, state_after, context)
        5. Convert ConstitutionalEvaluation to ConstitutionalAlignment

    Configuration:
        - threshold: Compliance threshold (default 0.5)
        - include_galois: Whether to compute Galois loss (expensive, default False)
    """

    threshold: float = 0.5
    include_galois: bool = False

    async def evaluate(self, mark: Mark) -> ConstitutionalAlignment:
        """
        Evaluate a mark against constitutional principles.

        This is the primary async interface. For most use cases,
        the sync version is sufficient since Constitution.evaluate()
        is synchronous.

        Args:
            mark: The mark to evaluate

        Returns:
            ConstitutionalAlignment with principle scores
        """
        return self.evaluate_sync(mark)

    def evaluate_sync(self, mark: Mark) -> ConstitutionalAlignment:
        """
        Synchronous evaluation of a mark.

        Extracts state/action/context from mark and runs constitutional
        evaluation via Constitution.evaluate().

        Args:
            mark: The mark to evaluate

        Returns:
            ConstitutionalAlignment with principle scores
        """
        # Extract state_before from stimulus
        state_before = self._extract_state_before(mark)

        # Extract action from response
        action = self._extract_action(mark)

        # Extract state_after (often same as action result for marks)
        state_after = self._extract_state_after(mark)

        # Build context from mark metadata
        context = self._build_context(mark)

        # Evaluate against constitution
        evaluation = Constitution.evaluate(state_before, action, state_after, context)

        # Convert to ConstitutionalAlignment
        return self._to_alignment(evaluation, mark)

    def _extract_state_before(self, mark: Mark) -> Any:
        """Extract state_before from mark stimulus."""
        return {
            "kind": mark.stimulus.kind,
            "content": mark.stimulus.content,
            "source": mark.stimulus.source,
        }

    def _extract_action(self, mark: Mark) -> Any:
        """Extract action from mark response."""
        return {
            "kind": mark.response.kind,
            "content": mark.response.content,
            "success": mark.response.success,
        }

    def _extract_state_after(self, mark: Mark) -> Any:
        """Extract state_after from mark (typically response metadata)."""
        return mark.response.metadata.get("state", mark.response.content)

    def _build_context(self, mark: Mark) -> dict[str, Any]:
        """
        Build evaluation context from mark metadata.

        This context is passed to Constitution.evaluate() and affects
        how principles are scored. Key context fields:

        - intentional: Was this action intentional? (affects CURATED)
        - preserves_human_agency: Does action preserve agency? (affects ETHICAL)
        - deterministic: Is action deterministic? (affects ETHICAL)
        - satisfies_identity: Does action satisfy identity law? (affects COMPOSABLE)
        - satisfies_associativity: Does action satisfy associativity? (affects COMPOSABLE)
        - has_spec: Is action specified? (affects GENERATIVE)
        - joyful: Is action delightful? (affects JOY_INDUCING)
        """
        context = dict(mark.metadata)

        # Add trust level from umwelt
        context["trust_level"] = mark.umwelt.trust_level

        # Add observer capabilities
        context["capabilities"] = list(mark.umwelt.capabilities)

        # Add phase context
        if mark.phase:
            context["phase"] = mark.phase.value
            context["phase_family"] = mark.phase.family

        # Add domain context
        context["domain"] = mark.domain

        # Add tags as hints
        context["tags"] = list(mark.tags)

        # Add proof information if available
        if mark.proof:
            context["has_proof"] = True
            context["proof_tier"] = mark.proof.tier.name
            context["proof_principles"] = list(mark.proof.principles)
            context["proof_qualifier"] = mark.proof.qualifier
        else:
            context["has_proof"] = False

        # Derive some common context flags
        context.setdefault("intentional", bool(mark.proof))
        context.setdefault("preserves_human_agency", mark.umwelt.trust_level < 3)
        context.setdefault("deterministic", mark.response.success)

        return context

    def _to_alignment(
        self,
        evaluation: ConstitutionalEvaluation,
        mark: Mark,
    ) -> ConstitutionalAlignment:
        """
        Convert ConstitutionalEvaluation to ConstitutionalAlignment.

        Maps the evaluation's PrincipleScore objects to the alignment's
        principle_scores dict, preserving weighted_total.
        """
        # Build principle scores dict
        principle_scores = {
            ps.principle.name: ps.score for ps in evaluation.scores
        }

        # Determine evidence tier from mark proof (if available)
        tier = "EMPIRICAL"
        if mark.proof:
            tier = mark.proof.tier.name

        return ConstitutionalAlignment.from_scores(
            principle_scores=principle_scores,
            galois_loss=None,  # Computed separately if include_galois=True
            tier=tier,
            threshold=self.threshold,
        )


# =============================================================================
# Batch Evaluator
# =============================================================================


class BatchConstitutionalEvaluator:
    """
    Evaluate multiple marks efficiently.

    For large trace analysis, this batch evaluator processes marks
    in parallel and provides aggregate statistics.

    Usage:
        >>> batch = BatchConstitutionalEvaluator()
        >>> alignments = await batch.evaluate_batch(marks)
        >>> print(f"Average alignment: {batch.average_alignment}")
    """

    def __init__(
        self,
        evaluator: MarkConstitutionalEvaluator | None = None,
    ):
        """Initialize with optional custom evaluator."""
        self.evaluator = evaluator or MarkConstitutionalEvaluator()
        self._results: list[ConstitutionalAlignment] = []

    async def evaluate_batch(
        self,
        marks: list[Mark],
    ) -> list[ConstitutionalAlignment]:
        """
        Evaluate a batch of marks.

        Args:
            marks: List of marks to evaluate

        Returns:
            List of ConstitutionalAlignment objects
        """
        self._results = []
        for mark in marks:
            alignment = await self.evaluator.evaluate(mark)
            self._results.append(alignment)
        return self._results

    @property
    def average_alignment(self) -> float:
        """Average weighted_total across all evaluated marks."""
        if not self._results:
            return 0.0
        return sum(a.weighted_total for a in self._results) / len(self._results)

    @property
    def compliance_rate(self) -> float:
        """Percentage of marks that are compliant."""
        if not self._results:
            return 0.0
        compliant = sum(1 for a in self._results if a.is_compliant)
        return compliant / len(self._results)

    @property
    def violation_count(self) -> int:
        """Total violations across all marks."""
        return sum(a.violation_count for a in self._results)

    @property
    def principle_averages(self) -> dict[str, float]:
        """Average score per principle."""
        if not self._results:
            return {}

        totals: dict[str, float] = {}
        counts: dict[str, int] = {}

        for alignment in self._results:
            for principle, score in alignment.principle_scores.items():
                totals[principle] = totals.get(principle, 0.0) + score
                counts[principle] = counts.get(principle, 0) + 1

        return {p: totals[p] / counts[p] for p in totals if counts[p] > 0}


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "ConstitutionalEvaluatorProtocol",
    "MarkConstitutionalEvaluator",
    "BatchConstitutionalEvaluator",
]

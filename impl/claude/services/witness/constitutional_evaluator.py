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
from services.verification.lean_import import (
    LeanProofChecker,
    LeanVerificationEvidence,
    get_constitutional_evidence,
)
from services.witness.mark import ConstitutionalAlignment, Mark
from services.zero_seed.galois.galois_loss import compute_galois_loss_async

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
        - include_galois: Whether to compute Galois loss (default True for full constitutional integration)
    """

    threshold: float = 0.5
    include_galois: bool = True

    async def evaluate(self, mark: Mark) -> ConstitutionalAlignment:
        """
        Evaluate a mark against constitutional principles.

        This is the primary async interface. When include_galois=True,
        this method computes the Galois loss asynchronously.

        Args:
            mark: The mark to evaluate

        Returns:
            ConstitutionalAlignment with principle scores and optional Galois loss
        """
        # Extract state/action/context synchronously
        state_before = self._extract_state_before(mark)
        action = self._extract_action(mark)
        state_after = self._extract_state_after(mark)
        context = self._build_context(mark)

        # Evaluate against constitution
        evaluation = Constitution.evaluate(state_before, action, state_after, context)

        # Compute Galois loss if requested
        galois_loss: float | None = None
        if self.include_galois:
            galois_loss = await self._compute_galois_loss(mark)

        # Convert to ConstitutionalAlignment
        return self._to_alignment(evaluation, mark, galois_loss=galois_loss)

    async def _compute_galois_loss(self, mark: Mark) -> float:
        """
        Compute Galois loss for a mark.

        The Galois loss measures semantic preservation through the
        restructure-reconstitute cycle: L(P) = d(P, C(R(P)))

        For marks, we compute loss on the combined stimulus+response content,
        which captures the full action signature.

        Args:
            mark: The mark to compute loss for

        Returns:
            Galois loss in [0, 1] where 0 = perfect preservation
        """
        # Build content from mark's stimulus and response
        content = self._build_galois_content(mark)

        try:
            result = await compute_galois_loss_async(content)
            logger.debug(
                f"Galois loss computed for mark {mark.id}: "
                f"loss={result.loss:.3f}, method={result.method}"
            )
            return result.loss
        except Exception as e:
            logger.warning(f"Failed to compute Galois loss for mark {mark.id}: {e}")
            # Return moderate loss on failure (not zero, not one)
            return 0.5

    def _build_galois_content(self, mark: Mark) -> str:
        """
        Build content string for Galois loss computation.

        Combines stimulus and response into a coherent representation
        that captures the mark's semantic signature.
        """
        parts = []

        # Add stimulus
        if mark.stimulus.content:
            parts.append(f"Stimulus ({mark.stimulus.kind}): {mark.stimulus.content}")

        # Add response
        if mark.response.content:
            parts.append(f"Response ({mark.response.kind}): {mark.response.content}")

        # Add proof if present (proofs are significant for constitutional alignment)
        if mark.proof and mark.proof.warrant:
            parts.append(f"Warrant: {mark.proof.warrant}")

        return "\n".join(parts) if parts else "empty mark"

    def _tier_from_galois(self, galois_loss: float) -> str:
        """
        Map Galois loss to evidence tier (Kent-calibrated 2025-12-28).

        The Galois loss measures semantic preservation through the
        restructure-reconstitute cycle. Lower loss = higher confidence
        in the constitutional evaluation.

        Evidence Tiers:
            CATEGORICAL: L < 0.10 (axiom-level, fixed point)
            EMPIRICAL: L < 0.38 (strong empirical evidence)
            AESTHETIC: L < 0.45 (Kent sees derivation paths)
            SOMATIC: L < 0.65 (felt sense, Mirror test)
            CHAOTIC: L >= 0.65 (high loss, low confidence)

        Args:
            galois_loss: The computed Galois loss in [0, 1]

        Returns:
            Evidence tier name as string
        """
        if galois_loss < 0.10:
            return "CATEGORICAL"
        elif galois_loss < 0.38:
            return "EMPIRICAL"
        elif galois_loss < 0.45:
            return "AESTHETIC"
        elif galois_loss < 0.65:
            return "SOMATIC"
        else:
            return "CHAOTIC"

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
        galois_loss: float | None = None,
    ) -> ConstitutionalAlignment:
        """
        Convert ConstitutionalEvaluation to ConstitutionalAlignment.

        Maps the evaluation's PrincipleScore objects to the alignment's
        principle_scores dict, preserving weighted_total.

        When galois_loss is provided, the evidence tier is derived from the
        Galois loss using Kent-calibrated thresholds. This provides a more
        rigorous tier assignment based on semantic preservation quality.

        Args:
            evaluation: The constitutional evaluation result
            mark: The mark being evaluated
            galois_loss: Optional pre-computed Galois loss

        Returns:
            ConstitutionalAlignment with principle scores and optional Galois loss
        """
        # Build principle scores dict
        principle_scores = {ps.principle.name: ps.score for ps in evaluation.scores}

        # Determine evidence tier:
        # 1. If galois_loss is provided, use Kent-calibrated thresholds
        # 2. Otherwise, fall back to mark proof tier or default EMPIRICAL
        if galois_loss is not None:
            tier = self._tier_from_galois(galois_loss)
        elif mark.proof:
            tier = mark.proof.tier.name
        else:
            tier = "EMPIRICAL"

        return ConstitutionalAlignment.from_scores(
            principle_scores=principle_scores,
            galois_loss=galois_loss,
            tier=tier,
            threshold=self.threshold,
        )


# =============================================================================
# Batch Evaluator
# =============================================================================


# =============================================================================
# Lean Formal Verification Integration
# =============================================================================

# Cache for Lean verification (expensive, only check once)
_lean_verification_cache: LeanVerificationEvidence | None = None


async def get_lean_verified_composable() -> LeanVerificationEvidence:
    """
    Get Lean-verified evidence for COMPOSABLE principle (L2.5).

    This provides CATEGORICAL tier evidence for the COMPOSABLE principle
    by formally verifying that kgents' categorical laws hold in Lean 4.

    The verification covers:
    - Category laws: associativity, left/right identity
    - Functor laws: preservation of identity and composition
    - Natural transformation laws: naturality squares
    - Operad laws: agent composition monoid (MOONSHOT)

    Returns:
        LeanVerificationEvidence with formal proof status

    Note:
        Results are cached after first call (expensive Lean build).
    """
    global _lean_verification_cache

    if _lean_verification_cache is not None:
        return _lean_verification_cache

    try:
        _lean_verification_cache = await get_constitutional_evidence()
        logger.info(
            f"Lean verification complete: "
            f"verified={_lean_verification_cache.verified}, "
            f"theorems={_lean_verification_cache.report.verified_theorems}/"
            f"{_lean_verification_cache.report.total_theorems}"
        )
    except Exception as e:
        logger.warning(f"Lean verification failed: {e}")
        # Create a failed evidence result
        from services.verification.lean_import import VerificationReport

        _lean_verification_cache = LeanVerificationEvidence(
            verified=False,
            report=VerificationReport(errors=[str(e)]),
        )

    return _lean_verification_cache


def get_lean_verified_composable_sync() -> LeanVerificationEvidence | None:
    """
    Synchronous getter for cached Lean verification.

    Returns None if verification hasn't been run yet.
    Use get_lean_verified_composable() to trigger verification.
    """
    return _lean_verification_cache


def clear_lean_verification_cache() -> None:
    """Clear the Lean verification cache (for testing)."""
    global _lean_verification_cache
    _lean_verification_cache = None


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
    # Lean Formal Verification
    "get_lean_verified_composable",
    "get_lean_verified_composable_sync",
    "clear_lean_verification_cache",
]

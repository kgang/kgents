"""
ASHC Evidence Accumulation Engine

The compiler is a trace accumulator, not a code generator.
Evidence is gathered through repeated runs with verification.

> "The proof is not formal—it's empirical. Run the tree a thousand times,
>  and the pattern of nudges IS the proof."
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Awaitable, Callable

from .primitives import TraceWitnessResult
from .verify import (
    LintReport,
    TestReport,
    TypeReport,
    verify_code,
)

logger = logging.getLogger("kgents.ashc.evidence")

# =============================================================================
# Nudge Type (for causal tracking)
# =============================================================================


@dataclass(frozen=True)
class Nudge:
    """A single adjustment to the prompt/spec."""

    location: str  # Where in spec/prompt
    before: str  # Original content
    after: str  # Modified content
    reason: str  # Why this nudge


# =============================================================================
# Run Type (single execution with all results)
# =============================================================================


@dataclass(frozen=True)
class Run:
    """
    A single execution of spec → implementation with verification.

    Each run captures:
    - The spec and prompt used
    - The generated implementation
    - Verification results (tests, types, lint)
    - Execution metadata
    """

    run_id: str
    spec_hash: str
    prompt_used: str
    implementation: str
    test_results: TestReport
    type_results: TypeReport
    lint_results: LintReport
    witnesses: tuple[TraceWitnessResult, ...] = ()
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0
    nudges: tuple[Nudge, ...] = ()

    @property
    def passed(self) -> bool:
        """Did this run pass all verification?"""
        return self.test_results.success and self.type_results.passed and self.lint_results.passed

    @property
    def test_pass_rate(self) -> float:
        """Fraction of tests that passed."""
        total = self.test_results.total
        if total == 0:
            return 1.0  # No tests = vacuously passing
        return self.test_results.passed / total

    @property
    def verification_score(self) -> float:
        """
        Combined verification score (0.0 - 1.0).

        Weighted: 60% tests, 20% types, 20% lint
        """
        test_score = 1.0 if self.test_results.success else self.test_pass_rate
        type_score = 1.0 if self.type_results.passed else 0.0
        lint_score = 1.0 if self.lint_results.passed else 0.0

        return test_score * 0.6 + type_score * 0.2 + lint_score * 0.2


# =============================================================================
# Evidence Type (accumulated runs)
# =============================================================================


@dataclass(frozen=True)
class Evidence:
    """
    Accumulated evidence for spec↔impl equivalence with Galois integration.

    The evidence combines:
    - Empirical verification (tests, types, lint)
    - Galois coherence (structure preservation under R o C)

    When galois_loss is provided:
        equivalence_score = galois_coherence * empirical_weight

    Where:
        galois_coherence = 1 - galois_loss
        empirical_weight = pass_rate * 0.7 + volume_factor * 0.3
    """

    runs: tuple[Run, ...]
    created_at: datetime = field(default_factory=datetime.now)
    spec_content: str = ""
    best_impl_content: str = ""
    galois_loss: float | None = None

    @property
    def run_count(self) -> int:
        """Number of runs in the corpus."""
        return len(self.runs)

    @property
    def pass_count(self) -> int:
        """Number of runs that passed all verification."""
        return sum(1 for r in self.runs if r.passed)

    @property
    def pass_rate(self) -> float:
        """Fraction of runs that passed (0.0 - 1.0)."""
        if not self.runs:
            return 0.0
        return self.pass_count / len(self.runs)

    @property
    def galois_coherence(self) -> float:
        """
        Galois coherence = 1 - galois_loss.

        Returns 0.0 if galois_loss not computed.
        """
        if self.galois_loss is None:
            return 0.0
        return 1.0 - self.galois_loss

    @property
    def equivalence_score(self) -> float:
        """
        Overall equivalence score (0.0 - 1.0) with Galois integration.

        When galois_loss is available:
            Score = galois_coherence * empirical_weight

        Where:
            galois_coherence = 1 - L (structure preservation)
            empirical_weight = pass_rate * 0.7 + volume_factor * 0.3
            volume_factor = min(1.0, run_count / 100)

        Falls back to legacy weighted score when galois_loss unavailable.
        """
        if self.galois_loss is None:
            return self._legacy_equivalence_score()

        galois_coherence = 1.0 - self.galois_loss
        empirical_weight = self._compute_empirical_weight()
        return galois_coherence * empirical_weight

    def _compute_empirical_weight(self) -> float:
        """
        Compute empirical weight from test results.

        Weight = pass_rate * 0.7 + volume_factor * 0.3

        This rewards both passing tests AND having many runs.
        """
        if not self.runs:
            return 0.0

        pass_rate = sum(1 for r in self.runs if r.test_results.success) / len(self.runs)
        volume_factor = min(1.0, len(self.runs) / 100)

        return pass_rate * 0.7 + volume_factor * 0.3

    def _legacy_equivalence_score(self) -> float:
        """
        Legacy equivalence score without Galois loss.

        Computed as weighted average of:
        - Test pass rate (60%)
        - Type pass rate (20%)
        - Lint pass rate (20%)
        """
        if not self.runs:
            return 0.0

        test_passed = sum(1 for r in self.runs if r.test_results.success)
        type_passed = sum(1 for r in self.runs if r.type_results.passed)
        lint_passed = sum(1 for r in self.runs if r.lint_results.passed)

        n = len(self.runs)
        test_rate = test_passed / n
        type_rate = type_passed / n
        lint_rate = lint_passed / n

        return test_rate * 0.6 + type_rate * 0.2 + lint_rate * 0.2

    @property
    def average_verification_score(self) -> float:
        """Average verification score across all runs."""
        if not self.runs:
            return 0.0
        return sum(r.verification_score for r in self.runs) / len(self.runs)

    def best_run(self) -> Run | None:
        """Return the run with highest verification score."""
        if not self.runs:
            return None
        return max(self.runs, key=lambda r: r.verification_score)

    def with_galois_loss(self, loss: float) -> "Evidence":
        """
        Create new Evidence with Galois loss attached.

        This is the preferred way to add Galois loss since Evidence is frozen.

        Args:
            loss: Galois loss value in [0, 1]

        Returns:
            New Evidence instance with galois_loss set
        """
        return Evidence(
            runs=self.runs,
            created_at=self.created_at,
            spec_content=self.spec_content,
            best_impl_content=self.best_impl_content,
            galois_loss=loss,
        )


# =============================================================================
# ASHCOutput Type (compiler output)
# =============================================================================


@dataclass(frozen=True)
class ASHCOutput:
    """
    The compiler's output: executable + evidence with Galois verification.

    An output is "verified" when there's sufficient evidence
    that the spec and implementation are equivalent.

    With Galois integration, verification requires:
    - Galois coherence >= 0.85 (structure preservation)
    - At least 10 runs (statistical confidence)
    - equivalence_score >= 0.8 (combined metric)
    """

    executable: str  # Best implementation code
    evidence: Evidence
    spec_hash: str

    @property
    def is_verified(self) -> bool:
        """
        Is there sufficient evidence for this executable?

        When Galois loss available:
        - galois_coherence >= 0.85 (structure preservation)
        - At least 10 runs
        - equivalence_score >= 0.8

        Legacy mode (no Galois):
        - equivalence_score >= 0.8
        - At least 10 runs
        """
        # Minimum runs required
        if len(self.evidence.runs) < 10:
            return False

        # Galois-enhanced verification
        if self.evidence.galois_loss is not None:
            # Galois coherence must be high
            if self.evidence.galois_coherence < 0.85:
                return False
            # Combined score must meet threshold
            if self.evidence.equivalence_score < 0.8:
                return False
            return True

        # Legacy verification
        return self.evidence.equivalence_score >= 0.8

    @property
    def confidence(self) -> float:
        """Confidence level (0.0 - 1.0)."""
        return self.evidence.equivalence_score

    @property
    def galois_verified(self) -> bool:
        """
        Is this output verified via Galois coherence?

        True only when:
        - galois_loss is available
        - galois_coherence >= 0.85
        - is_verified is True
        """
        if self.evidence.galois_loss is None:
            return False
        return self.is_verified and self.evidence.galois_coherence >= 0.85


# =============================================================================
# Evidence Compiler
# =============================================================================


def _hash_spec(spec: str) -> str:
    """Compute content-addressed hash of spec."""
    return hashlib.sha256(spec.encode()).hexdigest()[:12]


class EvidenceCompiler:
    """
    Compile spec to executable with evidence accumulation.

    The compiler generates N implementations, verifies each,
    and accumulates evidence about spec↔impl equivalence.

    Now with witness integration: every run emits marks for audit trail.

    > "Writing prompts is easy. Gathering evidence is hard."
    """

    def __init__(
        self,
        generate_fn: Callable[[str], Awaitable[str]] | None = None,
        mark_store: Any | None = None,
        evaluate_constitutional: bool = True,
    ):
        """
        Initialize the compiler.

        Args:
            generate_fn: Optional function to generate implementation from spec.
                        If not provided, uses identity (spec = impl).
            mark_store: Optional MarkStore for witness integration.
                       If not provided, uses global mark store.
            evaluate_constitutional: Whether to compute constitutional alignment
                                    for each witness (default True).
        """
        self._generate_fn = generate_fn
        self._mark_store = mark_store
        self._evaluate_constitutional = evaluate_constitutional

    async def compile(
        self,
        spec: str,
        n_variations: int = 10,
        test_code: str | None = None,
        run_tests: bool = True,
        run_types: bool = True,
        run_lint: bool = True,
        timeout: float = 60.0,
    ) -> ASHCOutput:
        """
        Main compilation loop.

        1. Generate N implementations from spec
        2. Verify each with pytest/mypy/ruff
        3. Accumulate into Evidence
        4. Select best implementation

        Args:
            spec: The specification to compile
            n_variations: Number of implementation variations to generate
            test_code: Optional test code for pytest
            run_tests: Whether to run pytest verification
            run_types: Whether to run mypy verification
            run_lint: Whether to run ruff verification
            timeout: Timeout per verification run

        Returns:
            ASHCOutput with best executable and accumulated evidence
        """
        spec_hash = _hash_spec(spec)
        runs: list[Run] = []

        # Generate and verify N variations
        for i in range(n_variations):
            run = await self._run_variation(
                spec=spec,
                spec_hash=spec_hash,
                variation_index=i,
                test_code=test_code,
                run_tests=run_tests,
                run_types=run_types,
                run_lint=run_lint,
                timeout=timeout,
            )
            runs.append(run)

        # Build evidence corpus
        evidence = Evidence(
            runs=tuple(runs),
            created_at=datetime.now(),
        )

        # Select best implementation
        best_run = evidence.best_run()
        executable = best_run.implementation if best_run else spec

        return ASHCOutput(
            executable=executable,
            evidence=evidence,
            spec_hash=spec_hash,
        )

    async def _run_variation(
        self,
        spec: str,
        spec_hash: str,
        variation_index: int,
        test_code: str | None,
        run_tests: bool,
        run_types: bool,
        run_lint: bool,
        timeout: float,
    ) -> Run:
        """Run a single variation through generation and verification."""
        import time

        start = time.monotonic()
        run_id = str(uuid.uuid4())

        # Generate implementation
        if self._generate_fn:
            implementation = await self._generate_fn(spec)
            prompt_used = f"Generated implementation #{variation_index + 1}"
        else:
            # Identity: spec is implementation
            implementation = spec
            prompt_used = "Identity (spec = impl)"

        # Verify the implementation
        verification = await verify_code(
            code=implementation,
            test_code=test_code,
            run_tests=run_tests,
            run_types=run_types,
            run_lint=run_lint,
            timeout=timeout,
        )

        duration_ms = (time.monotonic() - start) * 1000

        # Collect witnesses via witness bridge
        witnesses = await self._emit_verification_witnesses(
            verification=verification,
            spec_hash=spec_hash,
            run_id=run_id,
            variation_index=variation_index,
        )

        return Run(
            run_id=run_id,
            spec_hash=spec_hash,
            prompt_used=prompt_used,
            implementation=implementation,
            test_results=verification.test_report,
            type_results=verification.type_report,
            lint_results=verification.lint_report,
            witnesses=tuple(witnesses),  # NOW POPULATED!
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            nudges=(),
        )

    async def _emit_verification_witnesses(
        self,
        verification: Any,
        spec_hash: str,
        run_id: str,
        variation_index: int,
    ) -> list[TraceWitnessResult]:
        """
        Emit marks for verification results and return TraceWitnessResults.

        This is the integration point between ASHC evidence and the witness system.
        Each verification type (test, type, lint) emits a separate mark.
        """
        witnesses: list[TraceWitnessResult] = []

        try:
            from .paths.witness_bridge import WitnessType, emit_ashc_mark

            # Emit mark for test verification
            if verification.test_report:
                test_evidence = {
                    "total": verification.test_report.total,
                    "passed": verification.test_report.passed,
                    "failed": verification.test_report.failed,
                    "success": verification.test_report.success,
                }
                action = (
                    f"Verified tests: {verification.test_report.passed}/{verification.test_report.total} passed"
                    if verification.test_report.total > 0
                    else "No tests to run"
                )

                mark, witness = await emit_ashc_mark(
                    action=action,
                    evidence=test_evidence,
                    witness_type=WitnessType.TEST,
                    mark_store=self._mark_store,
                    spec_hash=spec_hash,
                    run_id=run_id,
                    evaluate_constitutional=self._evaluate_constitutional,
                )

                witnesses.append(
                    TraceWitnessResult(
                        witness_id=witness.witness_id,
                        agent_path=f"ashc.evidence.test.variation_{variation_index}",
                        input_data={"spec_hash": spec_hash, "variation": variation_index},
                        output_data=test_evidence,
                        properties_verified=("tests_pass",)
                        if verification.test_report.success
                        else (),
                        violations_found=()
                        if verification.test_report.success
                        else ({"type": "test_failure", "count": verification.test_report.failed},),
                    )
                )

            # Emit mark for type verification
            if verification.type_report:
                type_evidence = {
                    "passed": verification.type_report.passed,
                    "errors": len(verification.type_report.errors),
                }
                action = (
                    "Type check passed"
                    if verification.type_report.passed
                    else f"Type check failed: {len(verification.type_report.errors)} errors"
                )

                mark, witness = await emit_ashc_mark(
                    action=action,
                    evidence=type_evidence,
                    witness_type=WitnessType.TEST,
                    mark_store=self._mark_store,
                    spec_hash=spec_hash,
                    run_id=run_id,
                    evaluate_constitutional=self._evaluate_constitutional,
                )

                witnesses.append(
                    TraceWitnessResult(
                        witness_id=witness.witness_id,
                        agent_path=f"ashc.evidence.types.variation_{variation_index}",
                        input_data={"spec_hash": spec_hash, "variation": variation_index},
                        output_data=type_evidence,
                        properties_verified=("types_valid",)
                        if verification.type_report.passed
                        else (),
                        violations_found=()
                        if verification.type_report.passed
                        else tuple(
                            {"type": "type_error", "message": e}
                            for e in verification.type_report.errors[:3]
                        ),
                    )
                )

            # Emit mark for lint verification
            if verification.lint_report:
                lint_evidence = {
                    "passed": verification.lint_report.passed,
                    "errors": len(verification.lint_report.errors),
                }
                action = (
                    "Lint check passed"
                    if verification.lint_report.passed
                    else f"Lint check failed: {len(verification.lint_report.errors)} errors"
                )

                mark, witness = await emit_ashc_mark(
                    action=action,
                    evidence=lint_evidence,
                    witness_type=WitnessType.TEST,
                    mark_store=self._mark_store,
                    spec_hash=spec_hash,
                    run_id=run_id,
                    evaluate_constitutional=self._evaluate_constitutional,
                )

                witnesses.append(
                    TraceWitnessResult(
                        witness_id=witness.witness_id,
                        agent_path=f"ashc.evidence.lint.variation_{variation_index}",
                        input_data={"spec_hash": spec_hash, "variation": variation_index},
                        output_data=lint_evidence,
                        properties_verified=("lint_clean",)
                        if verification.lint_report.passed
                        else (),
                        violations_found=()
                        if verification.lint_report.passed
                        else tuple(
                            {"type": "lint_error", "message": e}
                            for e in verification.lint_report.errors[:3]
                        ),
                    )
                )

            logger.debug(f"Emitted {len(witnesses)} witnesses for run {run_id}")

        except ImportError as e:
            logger.warning(f"Witness bridge not available, skipping mark emission: {e}")
        except Exception as e:
            logger.error(f"Failed to emit verification witnesses: {e}")

        return witnesses

    async def compile_with_nudges(
        self,
        spec: str,
        nudges: list[Nudge],
        n_variations: int = 10,
        test_code: str | None = None,
    ) -> ASHCOutput:
        """
        Compile with tracked nudges for causal analysis.

        This allows tracking which nudges led to which outcomes,
        building the causal graph over time.
        """
        # Apply nudges to spec
        modified_spec = spec
        for nudge in nudges:
            modified_spec = modified_spec.replace(nudge.before, nudge.after)

        # Compile the modified spec
        output = await self.compile(
            spec=modified_spec,
            n_variations=n_variations,
            test_code=test_code,
        )

        # Add nudges to all runs
        runs_with_nudges = tuple(
            Run(
                run_id=run.run_id,
                spec_hash=run.spec_hash,
                prompt_used=run.prompt_used,
                implementation=run.implementation,
                test_results=run.test_results,
                type_results=run.type_results,
                lint_results=run.lint_results,
                witnesses=run.witnesses,
                timestamp=run.timestamp,
                duration_ms=run.duration_ms,
                nudges=tuple(nudges),
            )
            for run in output.evidence.runs
        )

        return ASHCOutput(
            executable=output.executable,
            evidence=Evidence(runs=runs_with_nudges),
            spec_hash=output.spec_hash,
        )


# =============================================================================
# Convenience Functions
# =============================================================================


async def compile_spec(
    spec: str,
    n_variations: int = 10,
    test_code: str | None = None,
) -> ASHCOutput:
    """
    Convenience function to compile a spec with evidence.

    Uses identity generation (spec = impl).
    """
    compiler = EvidenceCompiler()
    return await compiler.compile(
        spec=spec,
        n_variations=n_variations,
        test_code=test_code,
    )


async def quick_verify(
    code: str,
    test_code: str | None = None,
) -> Run | None:
    """
    Quick verification of a single implementation.

    Returns a Run with verification results, or None if no runs.
    """
    compiler = EvidenceCompiler()
    output = await compiler.compile(
        spec=code,
        n_variations=1,
        test_code=test_code,
    )
    return output.evidence.runs[0] if output.evidence.runs else None

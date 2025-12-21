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
    Accumulated evidence for spec↔impl equivalence.

    The evidence is empirical: many runs, statistical confidence.
    """

    runs: tuple[Run, ...]
    created_at: datetime = field(default_factory=datetime.now)

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
    def equivalence_score(self) -> float:
        """
        Overall equivalence score (0.0 - 1.0).

        How confident are we that spec matches impl?

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


# =============================================================================
# ASHCOutput Type (compiler output)
# =============================================================================


@dataclass(frozen=True)
class ASHCOutput:
    """
    The compiler's output: executable + evidence.

    An output is "verified" when there's sufficient evidence
    that the spec and implementation are equivalent.
    """

    executable: str  # Best implementation code
    evidence: Evidence
    spec_hash: str

    @property
    def is_verified(self) -> bool:
        """
        Is there sufficient evidence for this executable?

        Requires:
        - equivalence_score >= 0.8
        - At least 10 runs
        """
        return self.evidence.equivalence_score >= 0.8 and len(self.evidence.runs) >= 10

    @property
    def confidence(self) -> float:
        """Confidence level (0.0 - 1.0)."""
        return self.evidence.equivalence_score


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

    > "Writing prompts is easy. Gathering evidence is hard."
    """

    def __init__(
        self,
        generate_fn: Callable[[str], Awaitable[str]] | None = None,
    ):
        """
        Initialize the compiler.

        Args:
            generate_fn: Optional function to generate implementation from spec.
                        If not provided, uses identity (spec = impl).
        """
        self._generate_fn = generate_fn

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

        return Run(
            run_id=str(uuid.uuid4()),
            spec_hash=spec_hash,
            prompt_used=prompt_used,
            implementation=implementation,
            test_results=verification.test_report,
            type_results=verification.type_report,
            lint_results=verification.lint_report,
            witnesses=(),  # L0 witnesses added separately if needed
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            nudges=(),
        )

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

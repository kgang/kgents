"""
Tests for ASHC Evidence Accumulation Engine

Tests the Run, Evidence, ASHCOutput types and EvidenceCompiler.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from ..evidence import (
    ASHCOutput,
    Evidence,
    EvidenceCompiler,
    Nudge,
    Run,
    compile_spec,
    quick_verify,
)
from ..verify import LintReport, TestReport, TypeReport

# =============================================================================
# Test Fixtures
# =============================================================================


def make_test_report(
    passed: int = 5,
    failed: int = 0,
    skipped: int = 0,
) -> TestReport:
    """Create a test report for testing."""
    return TestReport(
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=() if failed == 0 else ("error",),
        duration_ms=100.0,
    )


def make_type_report(passed: bool = True) -> TypeReport:
    """Create a type report for testing."""
    return TypeReport(
        passed=passed,
        error_count=0 if passed else 1,
        errors=() if passed else ("type error",),
    )


def make_lint_report(passed: bool = True) -> LintReport:
    """Create a lint report for testing."""
    return LintReport(
        passed=passed,
        violation_count=0 if passed else 1,
        violations=() if passed else ("lint violation",),
    )


def make_run(
    passed: bool = True,
    test_passed: int = 5,
    test_failed: int = 0,
    type_passed: bool = True,
    lint_passed: bool = True,
    run_id: str = "test-run",
) -> Run:
    """Create a run for testing."""
    return Run(
        run_id=run_id,
        spec_hash="abc123",
        prompt_used="test prompt",
        implementation="def foo(): pass",
        test_results=make_test_report(passed=test_passed, failed=test_failed),
        type_results=make_type_report(passed=type_passed),
        lint_results=make_lint_report(passed=lint_passed),
        witnesses=(),
        timestamp=datetime.now(),
        duration_ms=100.0,
    )


# =============================================================================
# Test Run Type
# =============================================================================


class TestRun:
    """Tests for Run type."""

    def test_passed_property_all_pass(self) -> None:
        """Run.passed is True when all verifications pass."""
        run = make_run(test_passed=5, test_failed=0, type_passed=True, lint_passed=True)
        assert run.passed

    def test_passed_property_test_failure(self) -> None:
        """Run.passed is False when tests fail."""
        run = make_run(test_passed=3, test_failed=2)
        assert not run.passed

    def test_passed_property_type_failure(self) -> None:
        """Run.passed is False when type check fails."""
        run = make_run(type_passed=False)
        assert not run.passed

    def test_passed_property_lint_failure(self) -> None:
        """Run.passed is False when lint fails."""
        run = make_run(lint_passed=False)
        assert not run.passed

    def test_test_pass_rate(self) -> None:
        """Test Run.test_pass_rate computation."""
        run = make_run(test_passed=3, test_failed=2)
        assert run.test_pass_rate == 0.6  # 3/5

    def test_test_pass_rate_no_tests(self) -> None:
        """Test pass rate is 1.0 when no tests."""
        run = Run(
            run_id="test",
            spec_hash="abc",
            prompt_used="",
            implementation="",
            test_results=make_test_report(passed=0, failed=0, skipped=0),
            type_results=make_type_report(),
            lint_results=make_lint_report(),
        )
        assert run.test_pass_rate == 1.0  # No tests = vacuously passing

    def test_verification_score_all_pass(self) -> None:
        """Verification score is 1.0 when all pass."""
        run = make_run(test_passed=5, test_failed=0, type_passed=True, lint_passed=True)
        assert run.verification_score == 1.0

    def test_verification_score_partial(self) -> None:
        """Verification score reflects partial passing."""
        # Test fails, type and lint pass
        run = make_run(test_passed=3, test_failed=2, type_passed=True, lint_passed=True)
        # Score: 0.6*0.6 + 0.2*1.0 + 0.2*1.0 = 0.36 + 0.4 = 0.76
        expected = 0.6 * 0.6 + 0.2 * 1.0 + 0.2 * 1.0
        assert abs(run.verification_score - expected) < 0.01


# =============================================================================
# Test Evidence Type
# =============================================================================


class TestEvidence:
    """Tests for Evidence type."""

    def test_empty_evidence(self) -> None:
        """Empty evidence has zero scores."""
        evidence = Evidence(runs=())
        assert evidence.run_count == 0
        assert evidence.pass_count == 0
        assert evidence.pass_rate == 0.0
        assert evidence.equivalence_score == 0.0

    def test_all_passing_evidence(self) -> None:
        """All passing runs give score of 1.0."""
        runs = tuple(make_run(run_id=f"run-{i}") for i in range(10))
        evidence = Evidence(runs=runs)

        assert evidence.run_count == 10
        assert evidence.pass_count == 10
        assert evidence.pass_rate == 1.0
        assert evidence.equivalence_score == 1.0

    def test_mixed_evidence(self) -> None:
        """Mixed results give proportional scores."""
        # 6 passing, 4 failing (test failures)
        runs = [make_run(run_id=f"pass-{i}") for i in range(6)]
        runs += [make_run(run_id=f"fail-{i}", test_passed=0, test_failed=1) for i in range(4)]
        evidence = Evidence(runs=tuple(runs))

        assert evidence.run_count == 10
        assert evidence.pass_count == 6
        assert evidence.pass_rate == 0.6

    def test_best_run(self) -> None:
        """best_run returns the run with highest score."""
        runs = (
            make_run(run_id="low", test_passed=1, test_failed=4),
            make_run(run_id="high", test_passed=5, test_failed=0),
            make_run(run_id="mid", test_passed=3, test_failed=2),
        )
        evidence = Evidence(runs=runs)

        best = evidence.best_run()
        assert best is not None
        assert best.run_id == "high"

    def test_best_run_empty(self) -> None:
        """best_run returns None for empty evidence."""
        evidence = Evidence(runs=())
        assert evidence.best_run() is None

    def test_average_verification_score(self) -> None:
        """Average verification score is computed correctly."""
        runs = (
            make_run(run_id="perfect"),  # score = 1.0
            make_run(run_id="partial", test_passed=3, test_failed=2),  # score ~ 0.76
        )
        evidence = Evidence(runs=runs)

        avg = evidence.average_verification_score
        assert 0.8 < avg < 1.0  # Should be average of 1.0 and ~0.76


# =============================================================================
# Test ASHCOutput Type
# =============================================================================


class TestASHCOutput:
    """Tests for ASHCOutput type."""

    def test_is_verified_true(self) -> None:
        """is_verified is True with sufficient evidence."""
        runs = tuple(make_run(run_id=f"run-{i}") for i in range(10))
        evidence = Evidence(runs=runs)

        output = ASHCOutput(
            executable="def foo(): pass",
            evidence=evidence,
            spec_hash="abc123",
        )

        assert output.is_verified
        assert output.confidence == 1.0

    def test_is_verified_false_low_score(self) -> None:
        """is_verified is False with low equivalence score."""
        # All runs fail
        runs = tuple(make_run(run_id=f"run-{i}", test_passed=0, test_failed=5) for i in range(10))
        evidence = Evidence(runs=runs)

        output = ASHCOutput(
            executable="def foo(): pass",
            evidence=evidence,
            spec_hash="abc123",
        )

        assert not output.is_verified

    def test_is_verified_false_few_runs(self) -> None:
        """is_verified is False with too few runs."""
        runs = tuple(make_run(run_id=f"run-{i}") for i in range(5))  # Only 5 runs
        evidence = Evidence(runs=runs)

        output = ASHCOutput(
            executable="def foo(): pass",
            evidence=evidence,
            spec_hash="abc123",
        )

        assert not output.is_verified  # Need >= 10 runs


# =============================================================================
# Test Nudge Type
# =============================================================================


class TestNudge:
    """Tests for Nudge type."""

    def test_nudge_creation(self) -> None:
        """Create a nudge."""
        nudge = Nudge(
            location="line 5",
            before="return a + b",
            after="return a - b",
            reason="Fix subtraction bug",
        )

        assert nudge.location == "line 5"
        assert nudge.before == "return a + b"
        assert nudge.after == "return a - b"
        assert nudge.reason == "Fix subtraction bug"

    def test_nudge_frozen(self) -> None:
        """Nudge is immutable."""
        nudge = Nudge(
            location="test",
            before="a",
            after="b",
            reason="test",
        )

        with pytest.raises(AttributeError):
            nudge.location = "changed"  # type: ignore[misc]


# =============================================================================
# Test EvidenceCompiler
# =============================================================================


class TestEvidenceCompiler:
    """Tests for EvidenceCompiler."""

    @pytest.mark.asyncio
    async def test_compile_identity(self) -> None:
        """Compile with identity (spec = impl)."""
        spec = """
def add(a: int, b: int) -> int:
    \"\"\"Add two integers.\"\"\"
    return a + b
"""
        compiler = EvidenceCompiler()
        output = await compiler.compile(
            spec=spec,
            n_variations=3,
            run_tests=False,  # Skip actual tests for speed
            run_types=False,
            run_lint=False,
        )

        assert output.spec_hash is not None
        assert len(output.evidence.runs) == 3
        assert output.executable == spec

    @pytest.mark.asyncio
    async def test_compile_with_custom_generator(self) -> None:
        """Compile with custom generation function."""

        async def generator(spec: str) -> str:
            return f"# Generated from spec\n{spec}"

        compiler = EvidenceCompiler(generate_fn=generator)
        output = await compiler.compile(
            spec="def foo(): pass",
            n_variations=2,
            run_tests=False,
            run_types=False,
            run_lint=False,
        )

        assert "# Generated from spec" in output.executable

    @pytest.mark.asyncio
    async def test_compile_accumulates_evidence(self) -> None:
        """Compile accumulates evidence from all runs."""
        compiler = EvidenceCompiler()
        output = await compiler.compile(
            spec="def foo(): pass",
            n_variations=5,
            run_tests=False,
            run_types=False,
            run_lint=False,
        )

        # Should have 5 runs
        assert output.evidence.run_count == 5

        # Each run should have unique ID
        run_ids = {r.run_id for r in output.evidence.runs}
        assert len(run_ids) == 5

    @pytest.mark.asyncio
    async def test_compile_with_nudges(self) -> None:
        """Compile with nudges for causal tracking."""
        spec = "def add(a, b): return a + b"
        nudges = [
            Nudge(
                location="function",
                before="return a + b",
                after="return a - b",
                reason="Test nudge",
            )
        ]

        compiler = EvidenceCompiler()
        output = await compiler.compile_with_nudges(
            spec=spec,
            nudges=nudges,
            n_variations=2,
        )

        # All runs should have the nudges
        for run in output.evidence.runs:
            assert len(run.nudges) == 1
            assert run.nudges[0].reason == "Test nudge"


# =============================================================================
# Test Convenience Functions
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.asyncio
    async def test_compile_spec(self) -> None:
        """Test compile_spec convenience function."""
        output = await compile_spec(
            spec="def foo(): pass",
            n_variations=2,
        )

        assert isinstance(output, ASHCOutput)
        assert output.evidence.run_count == 2

    @pytest.mark.asyncio
    async def test_quick_verify(self) -> None:
        """Test quick_verify convenience function."""
        run = await quick_verify(
            code="def foo(): pass",
        )

        assert run is not None
        assert isinstance(run, Run)


# =============================================================================
# Test Equivalence Score Computation
# =============================================================================


class TestEquivalenceScore:
    """Tests for equivalence score computation."""

    def test_score_weights(self) -> None:
        """Verify score weighting: 60% tests, 20% types, 20% lint."""
        # All tests pass, type fails, lint passes
        runs = (
            Run(
                run_id="test",
                spec_hash="abc",
                prompt_used="",
                implementation="",
                test_results=make_test_report(passed=5, failed=0),
                type_results=make_type_report(passed=False),
                lint_results=make_lint_report(passed=True),
            ),
        )
        evidence = Evidence(runs=runs)

        # Expected: 1.0*0.6 + 0.0*0.2 + 1.0*0.2 = 0.8
        assert evidence.equivalence_score == 0.8

    def test_score_all_fail(self) -> None:
        """Score is 0 when all verifications fail."""
        runs = (
            Run(
                run_id="test",
                spec_hash="abc",
                prompt_used="",
                implementation="",
                test_results=make_test_report(passed=0, failed=5),
                type_results=make_type_report(passed=False),
                lint_results=make_lint_report(passed=False),
            ),
        )
        evidence = Evidence(runs=runs)

        assert evidence.equivalence_score == 0.0

    def test_score_threshold(self) -> None:
        """Verify 0.8 threshold for is_verified."""
        # Create evidence just at threshold
        runs = tuple(
            Run(
                run_id=f"run-{i}",
                spec_hash="abc",
                prompt_used="",
                implementation="",
                test_results=make_test_report(passed=5, failed=0),
                type_results=make_type_report(passed=True),
                lint_results=make_lint_report(passed=True),
            )
            for i in range(10)
        )
        evidence = Evidence(runs=runs)

        output = ASHCOutput(
            executable="",
            evidence=evidence,
            spec_hash="abc",
        )

        assert output.is_verified  # Score = 1.0 >= 0.8


# =============================================================================
# Test Spec Hash
# =============================================================================


class TestSpecHash:
    """Tests for spec hashing."""

    @pytest.mark.asyncio
    async def test_same_spec_same_hash(self) -> None:
        """Same spec produces same hash."""
        spec = "def foo(): pass"
        compiler = EvidenceCompiler()

        output1 = await compiler.compile(
            spec, n_variations=1, run_tests=False, run_types=False, run_lint=False
        )
        output2 = await compiler.compile(
            spec, n_variations=1, run_tests=False, run_types=False, run_lint=False
        )

        assert output1.spec_hash == output2.spec_hash

    @pytest.mark.asyncio
    async def test_different_spec_different_hash(self) -> None:
        """Different specs produce different hashes."""
        compiler = EvidenceCompiler()

        output1 = await compiler.compile(
            "def foo(): pass", n_variations=1, run_tests=False, run_types=False, run_lint=False
        )
        output2 = await compiler.compile(
            "def bar(): pass", n_variations=1, run_tests=False, run_types=False, run_lint=False
        )

        assert output1.spec_hash != output2.spec_hash


# =============================================================================
# Test Galois Integration
# =============================================================================


class TestGaloisIntegration:
    """Tests for Galois loss integration in Evidence and ASHCOutput."""

    def test_galois_coherence_without_loss(self) -> None:
        """galois_coherence returns 0.0 when galois_loss is None."""
        evidence = Evidence(runs=())
        assert evidence.galois_coherence == 0.0

    def test_galois_coherence_with_loss(self) -> None:
        """galois_coherence = 1 - galois_loss."""
        runs = tuple(make_run(run_id=f"run-{i}") for i in range(10))
        evidence = Evidence(runs=runs, galois_loss=0.15)

        assert evidence.galois_coherence == 0.85

    def test_with_galois_loss_creates_new_evidence(self) -> None:
        """with_galois_loss creates a new Evidence with loss attached."""
        runs = tuple(make_run(run_id=f"run-{i}") for i in range(10))
        evidence = Evidence(runs=runs)

        assert evidence.galois_loss is None

        evidence_with_loss = evidence.with_galois_loss(0.10)
        assert evidence_with_loss.galois_loss == 0.10
        assert evidence_with_loss.galois_coherence == 0.90

        # Original should be unchanged
        assert evidence.galois_loss is None

    def test_equivalence_score_uses_galois_when_available(self) -> None:
        """equivalence_score uses Galois formula when loss available."""
        runs = tuple(make_run(run_id=f"run-{i}") for i in range(100))  # 100 runs for max volume
        evidence = Evidence(runs=runs, galois_loss=0.10)

        # galois_coherence = 1.0 - 0.10 = 0.90
        # pass_rate = 1.0 (all pass)
        # volume_factor = min(1.0, 100/100) = 1.0
        # empirical_weight = 1.0 * 0.7 + 1.0 * 0.3 = 1.0
        # equivalence_score = 0.90 * 1.0 = 0.90
        assert abs(evidence.equivalence_score - 0.90) < 0.01

    def test_equivalence_score_legacy_without_galois(self) -> None:
        """equivalence_score uses legacy formula when no galois_loss."""
        runs = tuple(make_run(run_id=f"run-{i}") for i in range(10))
        evidence = Evidence(runs=runs)  # No galois_loss

        # Legacy: all pass -> 1.0
        assert evidence.equivalence_score == 1.0

    def test_is_verified_requires_galois_coherence(self) -> None:
        """is_verified with Galois requires coherence >= 0.85."""
        runs = tuple(make_run(run_id=f"run-{i}") for i in range(100))

        # High coherence (0.90) - should verify
        evidence_high = Evidence(runs=runs, galois_loss=0.10)
        output_high = ASHCOutput(executable="", evidence=evidence_high, spec_hash="abc")
        assert output_high.is_verified

        # Low coherence (0.80) - should NOT verify
        evidence_low = Evidence(runs=runs, galois_loss=0.20)
        output_low = ASHCOutput(executable="", evidence=evidence_low, spec_hash="abc")
        assert not output_low.is_verified

    def test_galois_verified_property(self) -> None:
        """galois_verified is True only with Galois + verified."""
        runs = tuple(make_run(run_id=f"run-{i}") for i in range(100))

        # With Galois and verified
        evidence = Evidence(runs=runs, galois_loss=0.10)
        output = ASHCOutput(executable="", evidence=evidence, spec_hash="abc")
        assert output.galois_verified

        # Without Galois (legacy)
        evidence_legacy = Evidence(runs=runs)
        output_legacy = ASHCOutput(executable="", evidence=evidence_legacy, spec_hash="abc")
        assert not output_legacy.galois_verified

    def test_empirical_weight_scaling(self) -> None:
        """empirical_weight scales with runs up to 100."""
        # Few runs -> lower volume factor
        runs_10 = tuple(make_run(run_id=f"run-{i}") for i in range(10))
        evidence_10 = Evidence(runs=runs_10, galois_loss=0.0)  # Perfect coherence

        # volume_factor = 10/100 = 0.1
        # empirical_weight = 1.0 * 0.7 + 0.1 * 0.3 = 0.73
        # equivalence_score = 1.0 * 0.73 = 0.73
        assert abs(evidence_10.equivalence_score - 0.73) < 0.01

        # Many runs -> higher volume factor
        runs_100 = tuple(make_run(run_id=f"run-{i}") for i in range(100))
        evidence_100 = Evidence(runs=runs_100, galois_loss=0.0)

        # volume_factor = 1.0, empirical_weight = 1.0
        assert evidence_100.equivalence_score == 1.0

    def test_spec_and_impl_content_preserved(self) -> None:
        """spec_content and best_impl_content are preserved."""
        runs = tuple(make_run(run_id=f"run-{i}") for i in range(10))
        evidence = Evidence(
            runs=runs,
            spec_content="def add(a, b): return a + b",
            best_impl_content="def add(a: int, b: int) -> int: return a + b",
            galois_loss=0.05,
        )

        assert evidence.spec_content == "def add(a, b): return a + b"
        assert evidence.best_impl_content == "def add(a: int, b: int) -> int: return a + b"
        assert evidence.galois_loss == 0.05

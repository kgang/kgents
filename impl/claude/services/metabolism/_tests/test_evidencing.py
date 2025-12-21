"""
Tests for Background Evidence Accumulator.

Checkpoint 2.1 of Metabolic Development Protocol.

Key verification criteria:
- 100 identical runs ≠ 100× confidence (diversity scoring)
- Silent accumulation (only critical failures surface)
- Causal insight learning from nudge → outcome patterns
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from services.metabolism.evidencing import (
    BackgroundEvidencing,
    CausalInsight,
    DiversityScore,
    EvidenceRun,
    InputSignature,
    StoredEvidence,
    get_background_evidencing,
    reset_background_evidencing,
    set_background_evidencing,
)

# =============================================================================
# InputSignature Tests
# =============================================================================


class TestInputSignature:
    """Test input signature generation for diversity tracking."""

    def test_same_content_same_signature(self) -> None:
        """Identical content produces identical signatures."""
        sig1 = InputSignature.from_run(file_content="def foo(): pass")
        sig2 = InputSignature.from_run(file_content="def foo(): pass")

        assert sig1.file_hash == sig2.file_hash
        assert sig1 == sig2

    def test_different_content_different_signature(self) -> None:
        """Different content produces different signatures."""
        sig1 = InputSignature.from_run(file_content="def foo(): pass")
        sig2 = InputSignature.from_run(file_content="def bar(): pass")

        assert sig1.file_hash != sig2.file_hash
        assert sig1 != sig2

    def test_same_content_different_tests_different_signature(self) -> None:
        """Same content but different test focus = different signature."""
        sig1 = InputSignature.from_run(
            file_content="def foo(): pass",
            test_files=["test_a.py"],
        )
        sig2 = InputSignature.from_run(
            file_content="def foo(): pass",
            test_files=["test_b.py"],
        )

        assert sig1.file_hash == sig2.file_hash  # Same content
        assert sig1.test_focus != sig2.test_focus  # Different tests
        assert sig1 != sig2

    def test_context_affects_signature(self) -> None:
        """Context changes affect signature."""
        sig1 = InputSignature.from_run(
            file_content="def foo(): pass",
            context={"env": "dev"},
        )
        sig2 = InputSignature.from_run(
            file_content="def foo(): pass",
            context={"env": "prod"},
        )

        assert sig1.context_hash != sig2.context_hash
        assert sig1 != sig2


# =============================================================================
# DiversityScore Tests
# =============================================================================


class TestDiversityScore:
    """Test diversity scoring for evidence accumulation."""

    def test_empty_score_is_zero(self) -> None:
        """No runs = zero diversity score."""
        score = DiversityScore()
        assert score.score == 0.0
        assert score.total_runs == 0
        assert score.unique_count == 0

    def test_single_run_is_full_diversity(self) -> None:
        """One unique run = 100% diversity."""
        score = DiversityScore()
        sig = InputSignature.from_run("def foo(): pass")

        is_new = score.add_run(sig)

        assert is_new is True
        assert score.score == 1.0
        assert score.total_runs == 1
        assert score.unique_count == 1

    def test_duplicate_runs_reduce_diversity(self) -> None:
        """Duplicate inputs reduce diversity score."""
        score = DiversityScore()
        sig = InputSignature.from_run("def foo(): pass")

        # First run is new
        assert score.add_run(sig) is True
        assert score.score == 1.0

        # Second run is duplicate
        assert score.add_run(sig) is False
        assert score.score == 0.5  # 1 unique / 2 total

        # Third run is duplicate
        assert score.add_run(sig) is False
        assert score.score == pytest.approx(1 / 3)  # 1 unique / 3 total

    def test_diversity_beats_count(self) -> None:
        """
        10 diverse runs > 100 identical runs in terms of confidence.

        This is the core insight: unique_inputs / total_runs matters.
        """
        # 100 identical runs
        identical = DiversityScore()
        sig = InputSignature.from_run("def foo(): pass")
        for _ in range(100):
            identical.add_run(sig)

        # 10 diverse runs
        diverse = DiversityScore()
        for i in range(10):
            sig = InputSignature.from_run(f"def foo{i}(): pass")
            diverse.add_run(sig)

        # Diversity score comparison
        assert identical.score == 0.01  # 1/100
        assert diverse.score == 1.0  # 10/10

        # 10 diverse runs have 100x better diversity score
        assert diverse.score > identical.score * 50

    def test_to_dict(self) -> None:
        """Serialization includes all key metrics."""
        score = DiversityScore()
        sig1 = InputSignature.from_run("def a(): pass")
        sig2 = InputSignature.from_run("def b(): pass")
        score.add_run(sig1)
        score.add_run(sig2)
        score.add_run(sig1)  # Duplicate

        data = score.to_dict()

        assert data["unique_count"] == 2
        assert data["total_runs"] == 3
        assert data["score"] == pytest.approx(2 / 3, rel=0.01)


# =============================================================================
# EvidenceRun Tests
# =============================================================================


class TestEvidenceRun:
    """Test individual evidence run records."""

    def test_critical_failure_detection(self) -> None:
        """Critical failures are detected based on fail rate."""
        sig = InputSignature.from_run("def foo(): pass")

        # Passing run is not critical
        passing = EvidenceRun(
            run_id="1",
            task_pattern="test",
            passed=True,
            test_count=10,
            failed_tests=(),
            duration_ms=100,
            signature=sig,
        )
        assert passing.is_critical_failure is False

        # Minor failure (<50%) is not critical
        minor_fail = EvidenceRun(
            run_id="2",
            task_pattern="test",
            passed=False,
            test_count=10,
            failed_tests=("test_a",),  # 10% failure
            duration_ms=100,
            signature=sig,
        )
        assert minor_fail.is_critical_failure is False

        # Major failure (>50%) IS critical
        major_fail = EvidenceRun(
            run_id="3",
            task_pattern="test",
            passed=False,
            test_count=10,
            failed_tests=tuple(f"test_{i}" for i in range(6)),  # 60% failure
            duration_ms=100,
            signature=sig,
        )
        assert major_fail.is_critical_failure is True

    def test_to_dict(self) -> None:
        """Serialization preserves key fields."""
        sig = InputSignature.from_run("def foo(): pass")
        run = EvidenceRun(
            run_id="abc123",
            task_pattern="verification",
            passed=True,
            test_count=5,
            failed_tests=(),
            duration_ms=150.5,
            signature=sig,
            nudges=("type hints",),
        )

        data = run.to_dict()

        assert data["run_id"] == "abc123"
        assert data["task_pattern"] == "verification"
        assert data["passed"] is True
        assert data["test_count"] == 5
        assert data["nudges"] == ["type hints"]


# =============================================================================
# StoredEvidence Tests
# =============================================================================


class TestStoredEvidence:
    """Test accumulated evidence for a task pattern."""

    def test_empty_evidence(self) -> None:
        """Empty evidence has sensible defaults."""
        evidence = StoredEvidence(task_pattern="test")

        assert evidence.run_count == 0
        assert evidence.pass_rate == 0.0
        assert evidence.diversity_score == 0.0

    def test_add_runs(self) -> None:
        """Adding runs updates statistics."""
        evidence = StoredEvidence(task_pattern="verification")
        sig = InputSignature.from_run("def foo(): pass")

        # Add passing run
        run1 = EvidenceRun(
            run_id="1",
            task_pattern="verification",
            passed=True,
            test_count=10,
            failed_tests=(),
            duration_ms=100,
            signature=sig,
        )
        evidence.add_run(run1)

        assert evidence.run_count == 1
        assert evidence.pass_rate == 1.0

        # Add failing run with different signature
        sig2 = InputSignature.from_run("def bar(): pass")
        run2 = EvidenceRun(
            run_id="2",
            task_pattern="verification",
            passed=False,
            test_count=10,
            failed_tests=("test_a",),
            duration_ms=100,
            signature=sig2,
        )
        evidence.add_run(run2)

        assert evidence.run_count == 2
        assert evidence.pass_rate == 0.5
        assert evidence.diversity_score == 1.0  # 2 unique / 2 total


# =============================================================================
# CausalInsight Tests
# =============================================================================


class TestCausalInsight:
    """Test causal insight tracking."""

    def test_insight_creation(self) -> None:
        """Create a causal insight."""
        insight = CausalInsight(
            nudge_pattern="add type hints",
            outcome_delta=0.08,  # +8% pass rate
            observation_count=5,
            confidence=0.75,
        )

        assert insight.nudge_pattern == "add type hints"
        assert insight.outcome_delta == 0.08
        assert insight.observation_count == 5
        assert insight.confidence == 0.75

    def test_to_dict(self) -> None:
        """Serialization rounds floats appropriately."""
        insight = CausalInsight(
            nudge_pattern="test",
            outcome_delta=0.12345,
            observation_count=10,
            confidence=0.87654,
        )

        data = insight.to_dict()

        assert data["outcome_delta"] == pytest.approx(0.1235, rel=0.01)
        assert data["confidence"] == pytest.approx(0.8765, rel=0.01)


# =============================================================================
# BackgroundEvidencing Tests
# =============================================================================


class TestBackgroundEvidencing:
    """Test the main evidence accumulator service."""

    @pytest.fixture
    def temp_store(self) -> Path:
        """Create a temporary store path."""
        with TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "evidence.json"

    @pytest.fixture
    def accumulator(self, temp_store: Path) -> BackgroundEvidencing:
        """Create a fresh accumulator for testing."""
        return BackgroundEvidencing(store_path=temp_store)

    def test_find_matching_evidence_empty(self, accumulator: BackgroundEvidencing) -> None:
        """Empty accumulator returns no matches."""
        matches = accumulator.find_matching_evidence("verification")
        assert matches == []

    def test_accumulate_evidence(self, accumulator: BackgroundEvidencing) -> None:
        """Evidence is accumulated correctly."""
        sig = InputSignature.from_run("def foo(): pass")
        run = EvidenceRun(
            run_id="1",
            task_pattern="verification",
            passed=True,
            test_count=10,
            failed_tests=(),
            duration_ms=100,
            signature=sig,
        )

        # Directly call internal accumulation
        accumulator._accumulate(run)

        evidence = accumulator.get_evidence("verification")
        assert evidence is not None
        assert evidence.run_count == 1
        assert evidence.pass_rate == 1.0

    def test_find_matching_by_substring(self, accumulator: BackgroundEvidencing) -> None:
        """Find evidence by substring match."""
        sig = InputSignature.from_run("def foo(): pass")

        # Add evidence for different patterns
        for pattern in ["verification integration", "brain vectors", "stigmergy"]:
            run = EvidenceRun(
                run_id=pattern[:4],
                task_pattern=pattern,
                passed=True,
                test_count=10,
                failed_tests=(),
                duration_ms=100,
                signature=sig,
            )
            accumulator._accumulate(run)

        # Search for "verification"
        matches = accumulator.find_matching_evidence("verification")
        assert len(matches) == 1
        assert matches[0].task_pattern == "verification integration"

        # Search for "veri" (partial)
        matches = accumulator.find_matching_evidence("veri")
        assert len(matches) == 1

    def test_find_matching_by_word(self, accumulator: BackgroundEvidencing) -> None:
        """Find evidence by word match."""
        sig = InputSignature.from_run("def foo(): pass")

        # Add evidence
        run = EvidenceRun(
            run_id="1",
            task_pattern="verification integration",
            passed=True,
            test_count=10,
            failed_tests=(),
            duration_ms=100,
            signature=sig,
        )
        accumulator._accumulate(run)

        # Search for "integration" (word in pattern)
        matches = accumulator.find_matching_evidence("integration tests")
        assert len(matches) == 1

    def test_causal_insight_recording(self, accumulator: BackgroundEvidencing) -> None:
        """Record and retrieve causal insights."""
        # Record initial observation
        accumulator.record_nudge_outcome(
            nudge_pattern="add type hints",
            before_pass_rate=0.80,
            after_pass_rate=0.88,
        )

        insights = accumulator.get_insights("type hints")
        assert len(insights) == 1
        assert insights[0].nudge_pattern == "add type hints"
        assert insights[0].outcome_delta == pytest.approx(0.08)
        assert insights[0].observation_count == 1
        assert insights[0].confidence == 0.5  # Initial confidence

        # Record second observation
        accumulator.record_nudge_outcome(
            nudge_pattern="add type hints",
            before_pass_rate=0.75,
            after_pass_rate=0.85,
        )

        insights = accumulator.get_insights("type hints")
        assert len(insights) == 1
        assert insights[0].observation_count == 2
        # Confidence increases with observations
        assert insights[0].confidence > 0.5
        # Delta is weighted average: (0.08 + 0.10) / 2 = 0.09
        assert insights[0].outcome_delta == pytest.approx(0.09, rel=0.01)

    def test_critical_failure_tracking(self, accumulator: BackgroundEvidencing) -> None:
        """Critical failures are tracked and can be acknowledged."""
        sig = InputSignature.from_run("def foo(): pass")

        # Critical failure: >50% tests failed
        run = EvidenceRun(
            run_id="critical-1",
            task_pattern="verification",
            passed=False,
            test_count=10,
            failed_tests=tuple(f"test_{i}" for i in range(6)),
            duration_ms=100,
            signature=sig,
        )

        # Add to critical failures manually (simulating background detection)
        accumulator._critical_failures.append(run)

        # Get critical failures
        failures = accumulator.get_critical_failures()
        assert len(failures) == 1
        assert failures[0].run_id == "critical-1"

        # Acknowledge
        ack = accumulator.acknowledge_failure("critical-1")
        assert ack is True
        assert len(accumulator.get_critical_failures()) == 0

        # Re-acknowledge returns False
        assert accumulator.acknowledge_failure("critical-1") is False

    @pytest.mark.asyncio
    async def test_persistence(self, temp_store: Path) -> None:
        """Evidence persists across service restarts."""
        # Create and populate accumulator
        acc1 = BackgroundEvidencing(store_path=temp_store)
        sig = InputSignature.from_run("def foo(): pass")
        run = EvidenceRun(
            run_id="1",
            task_pattern="verification",
            passed=True,
            test_count=10,
            failed_tests=(),
            duration_ms=100,
            signature=sig,
        )
        acc1._accumulate(run)
        acc1.record_nudge_outcome("type hints", 0.8, 0.9)

        # Save
        await acc1.save()
        assert temp_store.exists()

        # Load into new accumulator
        acc2 = BackgroundEvidencing(store_path=temp_store)
        await acc2.load()

        # Evidence pattern exists (metadata restored)
        assert "verification" in acc2._evidence

        # Insights restored
        insights = acc2.get_insights("type hints")
        assert len(insights) == 1
        assert insights[0].outcome_delta == pytest.approx(0.1)

    def test_max_runs_eviction(self) -> None:
        """Oldest runs are evicted when limit exceeded."""
        with TemporaryDirectory() as tmpdir:
            acc = BackgroundEvidencing(
                store_path=Path(tmpdir) / "evidence.json",
                max_runs_per_pattern=5,
            )

            # Add 10 runs
            for i in range(10):
                sig = InputSignature.from_run(f"def foo{i}(): pass")
                run = EvidenceRun(
                    run_id=f"run-{i}",
                    task_pattern="test",
                    passed=True,
                    test_count=10,
                    failed_tests=(),
                    duration_ms=100,
                    signature=sig,
                )
                acc._accumulate(run)

            # Only 5 most recent kept
            evidence = acc.get_evidence("test")
            assert evidence is not None
            assert evidence.run_count == 5
            # First runs evicted
            assert evidence.runs[0].run_id == "run-5"
            assert evidence.runs[-1].run_id == "run-9"

    def test_stats(self, accumulator: BackgroundEvidencing) -> None:
        """Stats provide accumulator overview."""
        sig = InputSignature.from_run("def foo(): pass")

        # Add some evidence
        for pattern in ["verification", "integration"]:
            run = EvidenceRun(
                run_id=pattern[:4],
                task_pattern=pattern,
                passed=True,
                test_count=10,
                failed_tests=(),
                duration_ms=100,
                signature=sig,
            )
            accumulator._accumulate(run)

        accumulator.record_nudge_outcome("test", 0.8, 0.9)

        stats = accumulator.stats()

        assert stats["pattern_count"] == 2
        assert stats["total_runs"] == 2
        assert stats["pending_tasks"] == 0
        assert stats["critical_failures"] == 0
        assert stats["insight_count"] == 1


# =============================================================================
# Factory Tests
# =============================================================================


class TestFactory:
    """Test the global factory functions."""

    def teardown_method(self) -> None:
        """Reset global state after each test."""
        reset_background_evidencing()

    def test_get_creates_singleton(self) -> None:
        """get_background_evidencing creates singleton."""
        acc1 = get_background_evidencing()
        acc2 = get_background_evidencing()

        assert acc1 is acc2

    def test_set_replaces_singleton(self) -> None:
        """set_background_evidencing replaces singleton."""
        with TemporaryDirectory() as tmpdir:
            custom = BackgroundEvidencing(store_path=Path(tmpdir) / "test.json")
            set_background_evidencing(custom)

            assert get_background_evidencing() is custom

    def test_reset_clears_singleton(self) -> None:
        """reset_background_evidencing clears singleton."""
        acc1 = get_background_evidencing()
        reset_background_evidencing()
        acc2 = get_background_evidencing()

        assert acc1 is not acc2


# =============================================================================
# Integration with brain_adapter
# =============================================================================


class TestBrainAdapterIntegration:
    """Test integration with brain_adapter.find_prior_evidence()."""

    def teardown_method(self) -> None:
        """Reset global state after each test."""
        reset_background_evidencing()

    @pytest.mark.asyncio
    async def test_find_prior_evidence_returns_ashc_evidence(self) -> None:
        """brain_adapter.find_prior_evidence returns ASHCEvidence from accumulator."""
        # Set up accumulator with evidence
        with TemporaryDirectory() as tmpdir:
            acc = BackgroundEvidencing(store_path=Path(tmpdir) / "test.json")
            set_background_evidencing(acc)

            # Add evidence
            sig = InputSignature.from_run("def verify(): pass")
            run = EvidenceRun(
                run_id="1",
                task_pattern="verification integration",
                passed=True,
                test_count=10,
                failed_tests=(),
                duration_ms=100,
                signature=sig,
            )
            acc._accumulate(run)

            # Add causal insight
            acc.record_nudge_outcome("type hints", 0.8, 0.88)

            # Query via brain_adapter
            from services.living_docs.brain_adapter import HydrationBrainAdapter

            adapter = HydrationBrainAdapter()
            evidence_list = await adapter.find_prior_evidence("verification")

            assert len(evidence_list) == 1
            evidence = evidence_list[0]

            assert evidence.task_pattern == "verification integration"
            assert evidence.run_count == 1
            assert evidence.pass_rate == 1.0
            assert evidence.diversity_score == 1.0

    @pytest.mark.asyncio
    async def test_empty_accumulator_returns_empty(self) -> None:
        """Empty accumulator returns empty list."""
        from services.living_docs.brain_adapter import HydrationBrainAdapter

        adapter = HydrationBrainAdapter()
        evidence = await adapter.find_prior_evidence("nonexistent")

        assert evidence == []

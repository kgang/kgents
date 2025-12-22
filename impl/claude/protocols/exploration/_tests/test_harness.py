"""
Tests for the Exploration Harness.

These tests verify:
1. Budget enforcement
2. Loop detection
3. Evidence collection
4. Commitment protocol
"""

import pytest

from ..budget import NavigationBudget, quick_budget, standard_budget
from ..commitment import ASHCCommitment
from ..evidence import EvidenceCollector, TrailAsEvidence
from ..harness import ExplorationHarness, create_harness
from ..loops import LoopDetector, cosine_similarity
from ..types import (
    Claim,
    CommitmentLevel,
    CommitmentResult,
    ContextGraph,
    ContextNode,
    Evidence,
    EvidenceStrength,
    LoopStatus,
    Observer,
    Trail,
)

# =============================================================================
# Budget Tests
# =============================================================================


class TestNavigationBudget:
    """Tests for NavigationBudget."""

    def test_fresh_budget_can_navigate(self) -> None:
        """Fresh budget should allow navigation."""
        budget = standard_budget()
        assert budget.can_navigate()

    def test_consume_increases_usage(self) -> None:
        """Consuming budget should increase usage."""
        budget = NavigationBudget(max_steps=10)
        new_budget = budget.consume("world.foo", depth=1)

        assert new_budget.steps_taken == 1
        assert "world.foo" in new_budget.nodes_visited

    def test_exhausted_budget_blocks_navigation(self) -> None:
        """Exhausted budget should block navigation."""
        budget = NavigationBudget(max_steps=1)
        budget = budget.consume("world.foo", depth=1)

        assert not budget.can_navigate()

    def test_budget_extension(self) -> None:
        """Budget can be extended."""
        budget = NavigationBudget(max_steps=10)
        extended = budget.extend(steps=10)

        assert extended.max_steps == 20


# =============================================================================
# Loop Detection Tests
# =============================================================================


class TestLoopDetector:
    """Tests for LoopDetector."""

    def test_no_loop_on_new_nodes(self) -> None:
        """New nodes should not trigger loop detection."""
        detector = LoopDetector()
        node = ContextNode(path="world.foo", holon="foo")

        status = detector.check(node, "tests")
        assert status == LoopStatus.OK

    def test_exact_loop_detection(self) -> None:
        """Revisiting same node should trigger exact loop."""
        detector = LoopDetector()
        node = ContextNode(path="world.foo", holon="foo")

        # First visit
        detector.check(node, "tests")
        # Second visit
        status = detector.check(node, "tests")

        assert status == LoopStatus.EXACT_LOOP

    def test_structural_loop_detection(self) -> None:
        """Repeating patterns should trigger structural loop."""
        detector = LoopDetector()

        # Create pattern: A, B, A, B, A, B
        for i in range(6):
            node = ContextNode(path=f"world.node{i}", holon=f"node{i}")
            edge = "a" if i % 2 == 0 else "b"
            status = detector.check(node, edge)

        # Last check should detect structural loop
        assert status == LoopStatus.STRUCTURAL_LOOP


class TestCosineSimilarity:
    """Tests for cosine similarity."""

    def test_identical_vectors(self) -> None:
        """Identical vectors should have similarity 1.0."""
        a = [1.0, 0.0, 0.0]
        b = [1.0, 0.0, 0.0]
        assert cosine_similarity(a, b) == pytest.approx(1.0)

    def test_orthogonal_vectors(self) -> None:
        """Orthogonal vectors should have similarity 0.0."""
        a = [1.0, 0.0, 0.0]
        b = [0.0, 1.0, 0.0]
        assert cosine_similarity(a, b) == pytest.approx(0.0)

    def test_empty_vectors(self) -> None:
        """Empty vectors should return 0.0."""
        assert cosine_similarity([], []) == 0.0


# =============================================================================
# Trail Tests
# =============================================================================


class TestTrail:
    """Tests for Trail."""

    def test_trail_immutability(self) -> None:
        """Adding steps should return new trail."""
        trail = Trail(name="test")
        new_trail = trail.add_step("world.foo", "tests")

        assert len(trail.steps) == 0
        assert len(new_trail.steps) == 1

    def test_trail_serialization(self) -> None:
        """Trail should serialize to readable format."""
        trail = Trail(name="investigation")
        trail = trail.add_step("world.auth", None)
        trail = trail.add_step("world.auth.tests", "tests")

        serialized = trail.serialize()
        assert "investigation" in serialized
        assert "world.auth" in serialized


# =============================================================================
# Evidence Tests
# =============================================================================


class TestTrailAsEvidence:
    """Tests for TrailAsEvidence."""

    def test_short_trail_weak_evidence(self) -> None:
        """Short trails should produce weak evidence."""
        converter = TrailAsEvidence()
        trail = Trail().add_step("world.foo", None)

        evidence = converter.to_evidence(trail, "Test claim")
        assert evidence.strength == EvidenceStrength.WEAK

    def test_long_varied_trail_strong_evidence(self) -> None:
        """Long, varied trails should produce strong evidence."""
        converter = TrailAsEvidence()
        trail = Trail()

        # Add many steps with different edge types
        edges = ["tests", "imports", "calls", "evidence", "related"]
        for i in range(12):
            trail = trail.add_step(f"world.node{i}", edges[i % len(edges)])

        evidence = converter.to_evidence(trail, "Test claim")
        assert evidence.strength == EvidenceStrength.STRONG


# =============================================================================
# Commitment Tests
# =============================================================================


class TestASHCCommitment:
    """Tests for ASHCCommitment."""

    def test_insufficient_evidence_rejected(self) -> None:
        """Claims without enough evidence should be rejected."""
        commitment = ASHCCommitment()
        claim = Claim(statement="Test claim")
        trail = Trail().add_step("world.foo", None)
        evidence: list[Evidence] = []

        result = commitment.can_commit(
            claim, trail, evidence, target_level=CommitmentLevel.MODERATE
        )

        assert result.result == CommitmentResult.INSUFFICIENT_QUANTITY

    def test_sufficient_evidence_approved(self) -> None:
        """Claims with enough evidence should be approved."""
        commitment = ASHCCommitment()
        claim = Claim(statement="Test claim")
        trail = Trail()
        trail = trail.add_step("world.foo", None)
        trail = trail.add_step("world.bar", "tests")

        # Create sufficient evidence
        evidence = [
            Evidence(
                claim="Test claim",
                content=f"Evidence {i}",
                strength=EvidenceStrength.STRONG if i == 0 else EvidenceStrength.MODERATE,
                metadata={"node_path": "world.foo"},
            )
            for i in range(5)
        ]

        result = commitment.can_commit(
            claim, trail, evidence, target_level=CommitmentLevel.MODERATE
        )

        assert result.result == CommitmentResult.APPROVED


# =============================================================================
# Harness Integration Tests
# =============================================================================


class TestExplorationHarness:
    """Integration tests for ExplorationHarness."""

    def test_harness_creation(self) -> None:
        """Harness should be creatable from a node."""
        node = ContextNode(path="world.auth", holon="auth")
        observer = Observer(id="test", archetype="developer")
        harness = create_harness(node, observer)

        assert harness.graph.focus == {node}
        assert harness.observer.id == "test"

    def test_harness_state_tracking(self) -> None:
        """Harness should track exploration state."""
        node = ContextNode(path="world.auth", holon="auth")
        harness = create_harness(node)

        state = harness.get_state()
        assert state.steps_taken == 0
        # Budget starts fresh - nodes are counted as consumed during navigation
        assert state.nodes_visited == 0
        # But the focus set has the start node
        assert len(harness.focus) == 1

    def test_harness_observation_recording(self) -> None:
        """Harness should record observations as evidence."""
        node = ContextNode(path="world.auth", holon="auth")
        harness = create_harness(node)

        evidence = harness.record_observation("Found good test coverage")

        assert evidence.content == "Found good test coverage"
        assert harness.evidence_collector.evidence_count == 1


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

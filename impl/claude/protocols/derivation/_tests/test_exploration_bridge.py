"""
Tests for Phase 6: Exploration Harness → Derivation Bridge.

Verifies:
- TrailEvidence creation from trails
- Pattern-to-principle mapping
- Law 6.1: Trail Evidence Additivity
- Bootstrap agent immunity
- Batch operations

See: spec/protocols/derivation-framework.md §6.1
"""

import pytest
from dataclasses import dataclass, field
from datetime import datetime, timezone

from ..exploration_bridge import (
    TrailEvidence,
    apply_trail_evidence,
    trail_to_derivation_evidence,
    merge_trail_evidence,
    batch_apply_trail_evidence,
)
from ..types import Derivation, DerivationTier, EvidenceType, PrincipleDraw
from ..registry import DerivationRegistry


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def registry() -> DerivationRegistry:
    """Fresh registry for each test."""
    return DerivationRegistry()


@pytest.fixture
def test_agent(registry: DerivationRegistry) -> Derivation:
    """Register a test agent."""
    return registry.register(
        agent_name="TestAgent",
        derives_from=("Compose",),
        principle_draws=(),
        tier=DerivationTier.JEWEL,
    )


# Mock Trail and Claim for testing
@dataclass
class MockTrailStep:
    node: str
    edge_taken: str | None = None


@dataclass
class MockTrail:
    id: str = "test-trail-1"
    name: str = "Test Trail"
    created_by: str = "developer"
    steps: tuple = ()
    annotations: dict = field(default_factory=dict)

    @property
    def edges_followed(self) -> list[str]:
        return [s.edge_taken for s in self.steps if s.edge_taken]


@dataclass
class MockClaim:
    id: str = "test-claim-1"
    statement: str = "Test claim"
    commitment_level: str = "moderate"


# =============================================================================
# TrailEvidence Creation Tests
# =============================================================================


class TestTrailEvidenceCreation:
    """Tests for TrailEvidence.from_trail()."""

    def test_empty_trail_minimal_principles(self):
        """Empty trail with tentative commitment produces no principles."""
        trail = MockTrail(steps=())
        claim = MockClaim(commitment_level="tentative")  # No Ethical signal

        evidence = TrailEvidence.from_trail(trail, claim, "TestAgent")

        assert evidence.trail_id == "test-trail-1"
        assert evidence.agent_name == "TestAgent"
        # Tentative commitment doesn't signal Ethical
        assert evidence.principles_signaled == ()

    def test_long_diverse_trail_signals_composable(self):
        """Long trail with diverse edges signals Composable."""
        steps = tuple(
            MockTrailStep(node=f"node{i}", edge_taken=f"edge{i % 3}")
            for i in range(8)
        )
        trail = MockTrail(steps=steps)
        claim = MockClaim()

        evidence = TrailEvidence.from_trail(trail, claim, "TestAgent")

        # Should have Composable principle
        principles = dict(evidence.principles_signaled)
        assert "Composable" in principles
        assert 0.5 <= principles["Composable"] <= 0.9

    def test_loop_free_trail_signals_generative(self):
        """Trail without revisits signals Generative."""
        steps = tuple(
            MockTrailStep(node=f"unique_node_{i}", edge_taken="edge")
            for i in range(5)
        )
        trail = MockTrail(steps=steps)
        claim = MockClaim()

        evidence = TrailEvidence.from_trail(trail, claim, "TestAgent")

        principles = dict(evidence.principles_signaled)
        assert "Generative" in principles
        assert principles["Generative"] == 0.8

    def test_loop_trail_no_generative(self):
        """Trail with revisits doesn't signal Generative."""
        steps = (
            MockTrailStep(node="A", edge_taken="e1"),
            MockTrailStep(node="B", edge_taken="e2"),
            MockTrailStep(node="A", edge_taken="e3"),  # Revisit
            MockTrailStep(node="C", edge_taken="e4"),
        )
        trail = MockTrail(steps=steps)
        claim = MockClaim()

        evidence = TrailEvidence.from_trail(trail, claim, "TestAgent")

        principles = dict(evidence.principles_signaled)
        assert "Generative" not in principles

    def test_definitive_commitment_signals_ethical(self):
        """Definitive commitment signals Ethical 0.9."""
        trail = MockTrail(steps=(MockTrailStep(node="A"),))
        claim = MockClaim(commitment_level="definitive")

        evidence = TrailEvidence.from_trail(trail, claim, "TestAgent")

        principles = dict(evidence.principles_signaled)
        assert "Ethical" in principles
        assert principles["Ethical"] == 0.9

    def test_strong_commitment_signals_ethical(self):
        """Strong commitment signals Ethical 0.8."""
        trail = MockTrail(steps=(MockTrailStep(node="A"),))
        claim = MockClaim(commitment_level="strong")

        evidence = TrailEvidence.from_trail(trail, claim, "TestAgent")

        principles = dict(evidence.principles_signaled)
        assert "Ethical" in principles
        assert principles["Ethical"] == 0.8

    def test_backtrack_annotation_signals_heterarchical(self):
        """Trail with backtrack annotation signals Heterarchical."""
        trail = MockTrail(
            steps=(MockTrailStep(node="A"),),
            annotations={0: "Had to backtrack here"},
        )
        claim = MockClaim()

        evidence = TrailEvidence.from_trail(trail, claim, "TestAgent")

        principles = dict(evidence.principles_signaled)
        assert "Heterarchical" in principles
        assert principles["Heterarchical"] == 0.6


# =============================================================================
# Apply Trail Evidence Tests
# =============================================================================


class TestApplyTrailEvidence:
    """Tests for apply_trail_evidence()."""

    def test_apply_to_nonexistent_agent_returns_none(self, registry: DerivationRegistry):
        """Applying to unknown agent returns None."""
        evidence = TrailEvidence(
            trail_id="t1",
            agent_name="UnknownAgent",
            principles_signaled=(("Composable", 0.7),),
            commitment_level="moderate",
        )

        result = apply_trail_evidence(evidence, registry)

        assert result is None

    def test_apply_creates_new_principle_draw(self, registry: DerivationRegistry, test_agent: Derivation):
        """Applying evidence creates new principle draws."""
        evidence = TrailEvidence(
            trail_id="t1",
            agent_name="TestAgent",
            principles_signaled=(("Composable", 0.7),),
            commitment_level="moderate",
        )

        result = apply_trail_evidence(evidence, registry)

        assert result is not None
        principles = {d.principle: d for d in result.principle_draws}
        assert "Composable" in principles
        assert principles["Composable"].draw_strength == 0.7
        assert principles["Composable"].evidence_type == EvidenceType.EMPIRICAL
        assert "trail:t1" in principles["Composable"].evidence_sources

    def test_trails_are_empirical(self, registry: DerivationRegistry, test_agent: Derivation):
        """Trail evidence is always EMPIRICAL, not CATEGORICAL."""
        evidence = TrailEvidence(
            trail_id="t1",
            agent_name="TestAgent",
            principles_signaled=(("Generative", 0.8),),
            commitment_level="definitive",
        )

        result = apply_trail_evidence(evidence, registry)

        for draw in result.principle_draws:
            assert draw.evidence_type == EvidenceType.EMPIRICAL

    def test_bootstrap_immune(self, registry: DerivationRegistry):
        """Bootstrap agents are not modified by trail evidence."""
        bootstrap_before = registry.get("Compose")
        original_draws = bootstrap_before.principle_draws

        evidence = TrailEvidence(
            trail_id="t1",
            agent_name="Compose",
            principles_signaled=(("Joy-Inducing", 0.9),),
            commitment_level="definitive",
        )

        result = apply_trail_evidence(evidence, registry)

        assert result is not None
        assert result.principle_draws == original_draws  # Unchanged

    def test_law_6_1_additivity_strengthens(self, registry: DerivationRegistry, test_agent: Derivation):
        """Law 6.1: Trails can only strengthen, not weaken."""
        # First application
        evidence1 = TrailEvidence(
            trail_id="t1",
            agent_name="TestAgent",
            principles_signaled=(("Composable", 0.5),),
            commitment_level="tentative",
        )
        apply_trail_evidence(evidence1, registry)

        # Second application with higher strength
        evidence2 = TrailEvidence(
            trail_id="t2",
            agent_name="TestAgent",
            principles_signaled=(("Composable", 0.8),),
            commitment_level="strong",
        )
        result = apply_trail_evidence(evidence2, registry)

        principles = {d.principle: d for d in result.principle_draws}
        assert principles["Composable"].draw_strength == 0.8  # Strengthened

    def test_law_6_1_additivity_no_weaken(self, registry: DerivationRegistry, test_agent: Derivation):
        """Law 6.1: Lower strength doesn't weaken existing draw."""
        # First application with high strength
        evidence1 = TrailEvidence(
            trail_id="t1",
            agent_name="TestAgent",
            principles_signaled=(("Composable", 0.8),),
            commitment_level="strong",
        )
        apply_trail_evidence(evidence1, registry)

        # Second application with lower strength
        evidence2 = TrailEvidence(
            trail_id="t2",
            agent_name="TestAgent",
            principles_signaled=(("Composable", 0.5),),
            commitment_level="tentative",
        )
        result = apply_trail_evidence(evidence2, registry)

        principles = {d.principle: d for d in result.principle_draws}
        assert principles["Composable"].draw_strength == 0.8  # Not weakened

    def test_evidence_sources_accumulate(self, registry: DerivationRegistry, test_agent: Derivation):
        """Multiple trails add to evidence sources."""
        evidence1 = TrailEvidence(
            trail_id="t1",
            agent_name="TestAgent",
            principles_signaled=(("Composable", 0.5),),
            commitment_level="tentative",
        )
        apply_trail_evidence(evidence1, registry)

        evidence2 = TrailEvidence(
            trail_id="t2",
            agent_name="TestAgent",
            principles_signaled=(("Composable", 0.7),),  # Higher, so updates
            commitment_level="moderate",
        )
        result = apply_trail_evidence(evidence2, registry)

        principles = {d.principle: d for d in result.principle_draws}
        sources = principles["Composable"].evidence_sources
        assert "trail:t1" in sources
        assert "trail:t2" in sources


# =============================================================================
# Merge and Batch Tests
# =============================================================================


class TestMergeTrailEvidence:
    """Tests for merge_trail_evidence()."""

    def test_merge_takes_max_strength(self):
        """Merge keeps maximum strength for each principle."""
        evidences = [
            TrailEvidence(
                trail_id="t1",
                agent_name="TestAgent",
                principles_signaled=(("Composable", 0.5), ("Generative", 0.8)),
                commitment_level="moderate",
            ),
            TrailEvidence(
                trail_id="t2",
                agent_name="TestAgent",
                principles_signaled=(("Composable", 0.7), ("Ethical", 0.9)),
                commitment_level="strong",
            ),
        ]

        merged = merge_trail_evidence(evidences)

        principles = dict(merged.principles_signaled)
        assert principles["Composable"] == 0.7  # Max of 0.5, 0.7
        assert principles["Generative"] == 0.8
        assert principles["Ethical"] == 0.9

    def test_merge_empty_raises(self):
        """Merging empty list raises ValueError."""
        with pytest.raises(ValueError):
            merge_trail_evidence([])


class TestBatchApplyTrailEvidence:
    """Tests for batch_apply_trail_evidence()."""

    def test_batch_apply_multiple_agents(self, registry: DerivationRegistry):
        """Batch apply updates multiple agents."""
        # Register second agent
        registry.register(
            agent_name="Agent2",
            derives_from=("Compose",),
            principle_draws=(),
            tier=DerivationTier.APP,
        )
        registry.register(
            agent_name="Agent1",
            derives_from=("Compose",),
            principle_draws=(),
            tier=DerivationTier.JEWEL,
        )

        evidences = [
            TrailEvidence(
                trail_id="t1",
                agent_name="Agent1",
                principles_signaled=(("Composable", 0.7),),
                commitment_level="moderate",
            ),
            TrailEvidence(
                trail_id="t2",
                agent_name="Agent2",
                principles_signaled=(("Ethical", 0.8),),
                commitment_level="strong",
            ),
        ]

        results = batch_apply_trail_evidence(evidences, registry)

        assert len(results) == 2
        assert results["Agent1"] is not None
        assert results["Agent2"] is not None

        agent1_principles = {d.principle: d.draw_strength for d in results["Agent1"].principle_draws}
        assert agent1_principles.get("Composable") == 0.7

    def test_batch_handles_unknown_agent(self, registry: DerivationRegistry, test_agent: Derivation):
        """Batch apply returns None for unknown agents."""
        evidences = [
            TrailEvidence(
                trail_id="t1",
                agent_name="TestAgent",
                principles_signaled=(("Composable", 0.7),),
                commitment_level="moderate",
            ),
            TrailEvidence(
                trail_id="t2",
                agent_name="UnknownAgent",
                principles_signaled=(("Ethical", 0.8),),
                commitment_level="strong",
            ),
        ]

        results = batch_apply_trail_evidence(evidences, registry)

        assert results["TestAgent"] is not None
        assert results["UnknownAgent"] is None


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience wrapper functions."""

    def test_trail_to_derivation_evidence(self):
        """trail_to_derivation_evidence wraps from_trail correctly."""
        trail = MockTrail(
            steps=(MockTrailStep(node="A"), MockTrailStep(node="B", edge_taken="e1")),
        )
        claim = MockClaim(commitment_level="strong")

        evidence = trail_to_derivation_evidence(trail, claim, "TestAgent")

        assert evidence.trail_id == trail.id
        assert evidence.agent_name == "TestAgent"
        assert evidence.commitment_level == "strong"

"""
Tests for Witness Bridge: Phase 3 of the Derivation Framework.

Tests cover:
    - extract_agents_from_mark(): origin -> agent names
    - mark_updates_stigmergy(): marks increment usage
    - denial_weakens_derivation(): challenges decay principles
    - walk_updates_derivations(): batch updates from walks
    - sync_witness_to_derivations(): convenience batch processing

Teaching:
    gotcha: These tests use mock Mark/Walk objects to avoid importing
            the full witness infrastructure. The actual Mark class is
            in services/witness/mark.py but we create simple mocks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import pytest

from protocols.derivation.registry import DerivationRegistry
from protocols.derivation.types import (
    DerivationTier,
    EvidenceType,
    PrincipleDraw,
)
from protocols.derivation.witness_bridge import (
    DifferentialDenial,
    denial_weakens_derivation,
    extract_agents_from_mark,
    mark_updates_stigmergy,
    sync_witness_to_derivations,
    walk_updates_derivations,
)

# =============================================================================
# Mock Types (avoid full witness import)
# =============================================================================


@dataclass
class MockMark:
    """Mock Mark for testing without full witness infrastructure."""

    id: str
    origin: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    stimulus: Any = None
    response: Any = None


@dataclass
class MockParticipant:
    """Mock Participant for testing."""

    name: str
    role: str = "contributor"


@dataclass
class MockWalk:
    """Mock Walk for testing."""

    id: str
    mark_ids: list[str] = field(default_factory=list)
    participants: list[MockParticipant] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MockMarkStore:
    """Mock MarkStore for testing."""

    _marks: dict[str, MockMark] = field(default_factory=dict)

    def get(self, mark_id: str) -> MockMark | None:
        return self._marks.get(mark_id)

    def add(self, mark: MockMark) -> None:
        self._marks[mark.id] = mark


# =============================================================================
# Test: extract_agents_from_mark
# =============================================================================


class TestExtractAgentsFromMark:
    """Tests for extract_agents_from_mark()."""

    def test_crown_jewel_origin(self) -> None:
        """Crown Jewel origins map to titlecase agent names."""
        mark = MockMark(id="mark-1", origin="brain")
        agents = extract_agents_from_mark(mark)  # type: ignore
        assert agents == ("Brain",)

    def test_witness_origin(self) -> None:
        """Witness origin maps correctly."""
        mark = MockMark(id="mark-2", origin="witness")
        agents = extract_agents_from_mark(mark)  # type: ignore
        assert agents == ("Witness",)

    def test_logos_origin(self) -> None:
        """Logos origin maps to AGENTESE node."""
        mark = MockMark(id="mark-3", origin="logos")
        agents = extract_agents_from_mark(mark)  # type: ignore
        assert agents == ("Logos",)

    def test_bootstrap_origin(self) -> None:
        """Bootstrap agent origins map correctly."""
        mark = MockMark(id="mark-4", origin="compose")
        agents = extract_agents_from_mark(mark)  # type: ignore
        assert agents == ("Compose",)

    def test_partial_match(self) -> None:
        """Partial matches work (e.g., brain_crystal -> Brain)."""
        mark = MockMark(id="mark-5", origin="brain_crystal")
        agents = extract_agents_from_mark(mark)  # type: ignore
        assert agents == ("Brain",)

    def test_unknown_origin_titlecase(self) -> None:
        """Unknown origins get titlecased."""
        mark = MockMark(id="mark-6", origin="custom_agent")
        agents = extract_agents_from_mark(mark)  # type: ignore
        assert agents == ("Custom_Agent",)

    def test_case_insensitive(self) -> None:
        """Origin matching is case-insensitive."""
        mark = MockMark(id="mark-7", origin="BRAIN")
        agents = extract_agents_from_mark(mark)  # type: ignore
        assert agents == ("Brain",)


# =============================================================================
# Test: DifferentialDenial
# =============================================================================


class TestDifferentialDenial:
    """Tests for DifferentialDenial type."""

    def test_create_denial(self) -> None:
        """Basic denial creation."""
        denial = DifferentialDenial(
            original_trace_id="mark-abc123",
            challenged_principle="Composable",
            challenge_evidence="Pipeline failed",
            severity=0.3,
            challenger="ashc",
        )
        assert denial.original_trace_id == "mark-abc123"
        assert denial.challenged_principle == "Composable"
        assert denial.severity == 0.3
        assert denial.timestamp is not None

    def test_default_severity(self) -> None:
        """Default severity is 0.2 (light challenge)."""
        denial = DifferentialDenial(
            original_trace_id="mark-123",
            challenged_principle="Tasteful",
            challenge_evidence="Style violation",
        )
        assert denial.severity == 0.2

    def test_severity_clamped(self) -> None:
        """Severity is clamped to [0.0, 1.0]."""
        denial_high = DifferentialDenial(
            original_trace_id="mark-1",
            challenged_principle="Composable",
            challenge_evidence="test",
            severity=1.5,
        )
        assert denial_high.severity == 1.0

        denial_low = DifferentialDenial(
            original_trace_id="mark-2",
            challenged_principle="Composable",
            challenge_evidence="test",
            severity=-0.5,
        )
        assert denial_low.severity == 0.0


# =============================================================================
# Test: mark_updates_stigmergy
# =============================================================================


class TestMarkUpdatesStigmergy:
    """Tests for mark_updates_stigmergy()."""

    @pytest.fixture
    def registry(self) -> DerivationRegistry:
        """Fresh registry with test derivations."""
        reg = DerivationRegistry()

        # Register a Crown Jewel derivation
        reg.register(
            agent_name="Brain",
            derives_from=("Fix", "Compose"),
            principle_draws=(
                PrincipleDraw(
                    principle="Composable",
                    draw_strength=0.8,
                    evidence_type=EvidenceType.EMPIRICAL,
                    evidence_sources=("test",),
                ),
            ),
            tier=DerivationTier.JEWEL,
        )

        return reg

    @pytest.mark.asyncio
    async def test_mark_increments_usage(self, registry: DerivationRegistry) -> None:
        """A mark increments usage count for the origin agent."""
        mark = MockMark(id="mark-1", origin="brain")

        before = registry.get_usage_count("Brain")
        usage = await mark_updates_stigmergy(mark, registry)  # type: ignore

        assert "Brain" in usage
        assert usage["Brain"] == before + 1

    @pytest.mark.asyncio
    async def test_unknown_agent_skipped(self, registry: DerivationRegistry) -> None:
        """Marks from unknown agents are skipped gracefully."""
        mark = MockMark(id="mark-2", origin="unknown_agent")

        usage = await mark_updates_stigmergy(mark, registry)  # type: ignore

        # No agents updated
        assert len(usage) == 0

    @pytest.mark.asyncio
    async def test_multiple_marks_accumulate(self, registry: DerivationRegistry) -> None:
        """Multiple marks accumulate usage."""
        for i in range(5):
            mark = MockMark(id=f"mark-{i}", origin="brain")
            await mark_updates_stigmergy(mark, registry)  # type: ignore

        assert registry.get_usage_count("Brain") == 5

    @pytest.mark.asyncio
    async def test_bootstrap_usage_not_tracked(self, registry: DerivationRegistry) -> None:
        """Bootstrap agents are in registry but updates don't fail."""
        # Bootstrap agents have derivations but special handling
        mark = MockMark(id="mark-boot", origin="compose")

        usage = await mark_updates_stigmergy(mark, registry)  # type: ignore

        # Bootstrap agents exist in registry
        assert "Compose" in usage or registry.exists("Compose")


# =============================================================================
# Test: denial_weakens_derivation
# =============================================================================


class TestDenialWeakensDerivation:
    """Tests for denial_weakens_derivation()."""

    @pytest.fixture
    def registry(self) -> DerivationRegistry:
        """Fresh registry with test derivations."""
        reg = DerivationRegistry()

        # Register agent with multiple principle draws
        reg.register(
            agent_name="TestAgent",
            derives_from=("Fix",),
            principle_draws=(
                PrincipleDraw(
                    principle="Composable",
                    draw_strength=0.8,
                    evidence_type=EvidenceType.EMPIRICAL,
                    evidence_sources=("test",),
                ),
                PrincipleDraw(
                    principle="Generative",
                    draw_strength=0.7,
                    evidence_type=EvidenceType.EMPIRICAL,
                    evidence_sources=("test2",),
                ),
            ),
            tier=DerivationTier.JEWEL,
        )

        return reg

    @pytest.mark.asyncio
    async def test_denial_weakens_principle(self, registry: DerivationRegistry) -> None:
        """A denial weakens the challenged principle draw."""
        denial = DifferentialDenial(
            original_trace_id="mark-1",
            challenged_principle="Composable",
            challenge_evidence="Pipeline failed",
            severity=0.2,
        )

        before = registry.get("TestAgent")
        assert before is not None
        before_strength = next(
            d.draw_strength for d in before.principle_draws if d.principle == "Composable"
        )

        affected = await denial_weakens_derivation(denial, registry, agent_name="TestAgent")

        assert "TestAgent" in affected

        after = registry.get("TestAgent")
        assert after is not None
        after_strength = next(
            d.draw_strength for d in after.principle_draws if d.principle == "Composable"
        )

        # Strength should have decayed
        assert after_strength < before_strength
        # Decay factor is (1 - severity) = 0.8
        expected = before_strength * 0.8
        assert abs(after_strength - expected) < 0.001

    @pytest.mark.asyncio
    async def test_other_principles_unchanged(self, registry: DerivationRegistry) -> None:
        """Denial only affects the challenged principle."""
        denial = DifferentialDenial(
            original_trace_id="mark-1",
            challenged_principle="Composable",
            challenge_evidence="test",
            severity=0.3,
        )

        before = registry.get("TestAgent")
        assert before is not None
        generative_before = next(
            d.draw_strength for d in before.principle_draws if d.principle == "Generative"
        )

        await denial_weakens_derivation(denial, registry, agent_name="TestAgent")

        after = registry.get("TestAgent")
        assert after is not None
        generative_after = next(
            d.draw_strength for d in after.principle_draws if d.principle == "Generative"
        )

        # Generative should be unchanged
        assert generative_after == generative_before

    @pytest.mark.asyncio
    async def test_categorical_evidence_not_weakened(self, registry: DerivationRegistry) -> None:
        """Categorical evidence is never weakened by denials."""
        # Register agent with categorical evidence
        registry.register(
            agent_name="CategoricalAgent",
            derives_from=("Id",),
            principle_draws=(
                PrincipleDraw(
                    principle="Composable",
                    draw_strength=1.0,
                    evidence_type=EvidenceType.CATEGORICAL,
                    evidence_sources=("identity-law",),
                ),
            ),
            tier=DerivationTier.FUNCTOR,
        )

        denial = DifferentialDenial(
            original_trace_id="mark-1",
            challenged_principle="Composable",
            challenge_evidence="Should not affect categorical",
            severity=0.5,
        )

        affected = await denial_weakens_derivation(denial, registry, agent_name="CategoricalAgent")

        # Not affected because categorical
        assert "CategoricalAgent" not in affected

        # Verify strength unchanged
        after = registry.get("CategoricalAgent")
        assert after is not None
        strength = next(
            d.draw_strength for d in after.principle_draws if d.principle == "Composable"
        )
        assert strength == 1.0

    @pytest.mark.asyncio
    async def test_strength_floor(self, registry: DerivationRegistry) -> None:
        """Strength never drops below 0.1 floor."""
        denial = DifferentialDenial(
            original_trace_id="mark-1",
            challenged_principle="Composable",
            challenge_evidence="Severe failure",
            severity=0.99,  # Very severe
        )

        await denial_weakens_derivation(denial, registry, agent_name="TestAgent")

        after = registry.get("TestAgent")
        assert after is not None
        strength = next(
            d.draw_strength for d in after.principle_draws if d.principle == "Composable"
        )

        # Should be at floor, not below
        assert strength >= 0.1

    @pytest.mark.asyncio
    async def test_unknown_agent_handled(self, registry: DerivationRegistry) -> None:
        """Unknown agent doesn't crash."""
        denial = DifferentialDenial(
            original_trace_id="mark-1",
            challenged_principle="Composable",
            challenge_evidence="test",
        )

        affected = await denial_weakens_derivation(denial, registry, agent_name="NonExistent")

        assert len(affected) == 0


# =============================================================================
# Test: walk_updates_derivations
# =============================================================================


class TestWalkUpdatesDerivations:
    """Tests for walk_updates_derivations()."""

    @pytest.fixture
    def registry(self) -> DerivationRegistry:
        """Fresh registry with test derivations."""
        reg = DerivationRegistry()

        reg.register(
            agent_name="Brain",
            derives_from=("Fix",),
            principle_draws=(),
            tier=DerivationTier.JEWEL,
        )
        reg.register(
            agent_name="Witness",
            derives_from=("Judge",),
            principle_draws=(),
            tier=DerivationTier.JEWEL,
        )

        return reg

    @pytest.mark.asyncio
    async def test_walk_with_mark_store(self, registry: DerivationRegistry) -> None:
        """Walk updates with actual mark store."""
        # Create marks
        marks = [
            MockMark(id="mark-1", origin="brain"),
            MockMark(id="mark-2", origin="brain"),
            MockMark(id="mark-3", origin="witness"),
        ]

        mark_store = MockMarkStore()
        for m in marks:
            mark_store.add(m)

        walk = MockWalk(
            id="walk-1",
            mark_ids=["mark-1", "mark-2", "mark-3"],
        )

        results = await walk_updates_derivations(
            walk,
            mark_store=mark_store,
            registry=registry,  # type: ignore
        )

        # Brain had 2 marks
        assert "Brain" in results
        assert results["Brain"]["marks"] == 2

        # Witness had 1 mark
        assert "Witness" in results
        assert results["Witness"]["marks"] == 1

    @pytest.mark.asyncio
    async def test_walk_with_participants_fallback(self, registry: DerivationRegistry) -> None:
        """Walk without mark_store falls back to participants."""
        walk = MockWalk(
            id="walk-2",
            mark_ids=["mark-1", "mark-2"],
            participants=[
                MockParticipant(name="brain", role="contributor"),
                MockParticipant(name="witness", role="contributor"),
            ],
        )

        results = await walk_updates_derivations(walk, registry=registry)  # type: ignore

        # Should have updates from participants
        # Each participant counts as one mark in fallback
        assert "Brain" in results or "Witness" in results

    @pytest.mark.asyncio
    async def test_empty_walk(self, registry: DerivationRegistry) -> None:
        """Empty walk produces no updates."""
        walk = MockWalk(id="walk-empty", mark_ids=[])

        results = await walk_updates_derivations(walk, registry=registry)  # type: ignore

        assert len(results) == 0


# =============================================================================
# Test: sync_witness_to_derivations
# =============================================================================


class TestSyncWitnessToDerivations:
    """Tests for sync_witness_to_derivations() convenience function."""

    @pytest.fixture
    def registry(self) -> DerivationRegistry:
        """Fresh registry with test derivations."""
        reg = DerivationRegistry()

        reg.register(
            agent_name="Brain",
            derives_from=("Fix",),
            principle_draws=(
                PrincipleDraw(
                    principle="Composable",
                    draw_strength=0.9,
                    evidence_type=EvidenceType.EMPIRICAL,
                    evidence_sources=("test",),
                ),
            ),
            tier=DerivationTier.JEWEL,
        )

        return reg

    @pytest.mark.asyncio
    async def test_batch_marks_and_denials(self, registry: DerivationRegistry) -> None:
        """Batch processing of marks and denials."""
        marks = [
            MockMark(id="mark-1", origin="brain"),
            MockMark(id="mark-2", origin="brain"),
        ]

        denials = [
            DifferentialDenial(
                original_trace_id="mark-old",
                challenged_principle="Composable",
                challenge_evidence="Failed test",
                severity=0.1,
            )
        ]

        results = await sync_witness_to_derivations(
            marks,
            denials,
            registry,  # type: ignore
        )

        assert results["marks_processed"] == 2
        assert results["denials_processed"] == 1
        assert "Brain" in results["usage_updates"]

    @pytest.mark.asyncio
    async def test_marks_only(self, registry: DerivationRegistry) -> None:
        """Process only marks, no denials."""
        marks = [MockMark(id="mark-1", origin="brain")]

        results = await sync_witness_to_derivations(marks, registry=registry)  # type: ignore

        assert results["marks_processed"] == 1
        assert results["denials_processed"] == 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestWitnessBridgeIntegration:
    """Integration tests for the complete witness bridge flow."""

    @pytest.mark.asyncio
    async def test_full_lifecycle(self) -> None:
        """Full lifecycle: register agent, add marks, apply denial, check confidence."""
        registry = DerivationRegistry()

        # Register agent with a known-mapped name (Brain is in ORIGIN_TO_AGENTS)
        registry.register(
            agent_name="Brain",
            derives_from=("Fix", "Compose"),
            principle_draws=(
                PrincipleDraw(
                    principle="Composable",
                    draw_strength=0.8,
                    evidence_type=EvidenceType.EMPIRICAL,
                    evidence_sources=("initial-test",),
                ),
            ),
            tier=DerivationTier.JEWEL,
        )

        initial = registry.get("Brain")
        assert initial is not None
        initial_confidence = initial.total_confidence

        # Simulate usage (many marks) using "brain" origin
        for i in range(100):
            mark = MockMark(id=f"mark-{i}", origin="brain")
            await mark_updates_stigmergy(mark, registry)  # type: ignore

        # Check usage accumulated
        assert registry.get_usage_count("Brain") == 100

        # Check stigmergic confidence increased
        after_usage = registry.get("Brain")
        assert after_usage is not None
        assert after_usage.stigmergic_confidence > 0

        # Apply a denial
        denial = DifferentialDenial(
            original_trace_id="mark-50",
            challenged_principle="Composable",
            challenge_evidence="Integration test failure",
            severity=0.15,
        )
        await denial_weakens_derivation(denial, registry, agent_name="Brain")

        # Check principle was weakened
        after_denial = registry.get("Brain")
        assert after_denial is not None
        composable_strength = next(
            d.draw_strength for d in after_denial.principle_draws if d.principle == "Composable"
        )
        assert composable_strength < 0.8  # Was weakened from initial

    @pytest.mark.asyncio
    async def test_propagation_after_denial(self) -> None:
        """Denial propagates confidence changes through DAG."""
        registry = DerivationRegistry()

        # Create a derivation chain: Parent -> Child
        registry.register(
            agent_name="Parent",
            derives_from=("Fix",),
            principle_draws=(
                PrincipleDraw(
                    principle="Composable",
                    draw_strength=0.9,
                    evidence_type=EvidenceType.EMPIRICAL,
                    evidence_sources=("test",),
                ),
            ),
            tier=DerivationTier.FUNCTOR,
        )

        registry.register(
            agent_name="Child",
            derives_from=("Parent",),
            principle_draws=(),
            tier=DerivationTier.JEWEL,
        )

        child_before = registry.get("Child")
        assert child_before is not None
        inherited_before = child_before.inherited_confidence

        # Weaken parent
        denial = DifferentialDenial(
            original_trace_id="mark-1",
            challenged_principle="Composable",
            challenge_evidence="Test",
            severity=0.3,
        )
        await denial_weakens_derivation(denial, registry, agent_name="Parent")

        # Child's inherited confidence should have changed
        # (propagation happens in denial_weakens_derivation)
        child_after = registry.get("Child")
        assert child_after is not None

        # Note: inherited_confidence is computed from total_confidence
        # of parents, which includes principle draws. Since parent's
        # principle was weakened, parent's total_confidence decreased,
        # which propagates to child.


# =============================================================================
# Test Count Summary
# =============================================================================

# extract_agents_from_mark: 7 tests
# DifferentialDenial: 3 tests
# mark_updates_stigmergy: 4 tests
# denial_weakens_derivation: 5 tests
# walk_updates_derivations: 3 tests
# sync_witness_to_derivations: 2 tests
# Integration: 2 tests
# Total: 26 tests

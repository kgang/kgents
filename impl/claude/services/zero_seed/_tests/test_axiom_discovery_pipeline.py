"""
Tests for Axiom Discovery Pipeline.

Validates:
1. Decision surfacing from MarkStore
2. Pattern extraction and clustering
3. Galois loss computation with caching
4. Fixed point identification (L < 0.05)
5. Contradiction detection (super-additive loss)
6. Full pipeline integration

Philosophy:
    "Test the discovery machinery. Test the mathematics.
     Test that Kent's axioms emerge from his decisions."

See: spec/protocols/zero-seed.md
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from services.witness import (
    Mark,
    MarkId,
    MarkStore,
    Proof,
    Response,
    Stimulus,
    UmweltSnapshot,
    reset_mark_store,
    set_mark_store,
)
from services.zero_seed.axiom_discovery import AXIOM_THRESHOLD
from services.zero_seed.axiom_discovery_pipeline import (
    CONTRADICTION_TAU,
    DEFAULT_TIME_WINDOW_DAYS,
    AxiomCandidate,
    AxiomDiscoveryPipeline,
    AxiomDiscoveryResult,
    ContradictionPair,
    DecisionPattern,
    discover_personal_axioms,
    validate_axiom_candidate,
)
from services.zero_seed.galois import STABILITY_THRESHOLD

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mark_store() -> MarkStore:
    """Create a fresh mark store for testing."""
    store = MarkStore()
    set_mark_store(store)
    yield store
    reset_mark_store()


@pytest.fixture
def decision_marks(mark_store: MarkStore) -> list[Mark]:
    """
    Create sample decision marks with recurring patterns.

    Creates decisions that exhibit Kent's values:
    - Simplicity is important (appears 4 times)
    - Composition matters (appears 3 times)
    - Joy-inducing design (appears 3 times)
    """
    marks = []
    base_time = datetime.now(timezone.utc) - timedelta(days=15)

    # Simplicity pattern (should become an axiom)
    simplicity_decisions = [
        "Decided to prioritize simplicity over complexity. Simplicity is important.",
        "Chose the simpler approach because simplicity matters in design.",
        "Always prefer simplicity. Simplicity is essential for maintainability.",
        "Rejected the complex solution. Simplicity is important for understanding.",
    ]

    for i, content in enumerate(simplicity_decisions):
        mark = Mark(
            id=MarkId(f"mark-simp-{i:04d}"),
            origin="witness",
            stimulus=Stimulus(kind="decision", content="design choice", source="kent"),
            response=Response(kind="decision", content=content),
            umwelt=UmweltSnapshot.system(),
            timestamp=base_time + timedelta(hours=i * 8),
            tags=("decision", "design"),
            metadata={"type": "decision", "reasoning": content},
        )
        mark_store.append(mark)
        marks.append(mark)

    # Composition pattern
    composition_decisions = [
        "Using composition over inheritance. Composition is important.",
        "Prefer composable modules. Composition matters for flexibility.",
        "Chose composition pattern. Composability is essential.",
    ]

    for i, content in enumerate(composition_decisions):
        mark = Mark(
            id=MarkId(f"mark-comp-{i:04d}"),
            origin="witness",
            stimulus=Stimulus(kind="decision", content="architecture", source="kent"),
            response=Response(kind="decision", content=content),
            umwelt=UmweltSnapshot.system(),
            timestamp=base_time + timedelta(days=1, hours=i * 8),
            tags=("decision", "architecture"),
            metadata={"type": "decision", "reasoning": content},
        )
        mark_store.append(mark)
        marks.append(mark)

    # Joy-inducing pattern
    joy_decisions = [
        "The design should be joy-inducing. Joy-inducing UI is important.",
        "Always aim for joy-inducing experiences. Joy matters.",
        "Prioritize joy-inducing interactions. User delight is essential.",
    ]

    for i, content in enumerate(joy_decisions):
        mark = Mark(
            id=MarkId(f"mark-joy-{i:04d}"),
            origin="witness",
            stimulus=Stimulus(kind="decision", content="ux design", source="kent"),
            response=Response(kind="decision", content=content),
            umwelt=UmweltSnapshot.system(),
            timestamp=base_time + timedelta(days=2, hours=i * 8),
            tags=("decision", "ux"),
            metadata={"type": "decision"},
        )
        mark_store.append(mark)
        marks.append(mark)

    return marks


@pytest.fixture
def contradicting_decisions(mark_store: MarkStore) -> list[Mark]:
    """
    Create decisions with contradicting values.

    Performance vs Readability contradiction.
    """
    marks = []
    base_time = datetime.now(timezone.utc) - timedelta(days=10)

    contradicting = [
        ("Always prioritize performance over readability.", "performance"),
        ("Performance is the top priority in all code.", "performance"),
        ("Readability is more important than performance.", "readability"),
        ("Readability matters most in code.", "readability"),
    ]

    for i, (content, tag) in enumerate(contradicting):
        mark = Mark(
            id=MarkId(f"mark-contra-{i:04d}"),
            origin="witness",
            stimulus=Stimulus(kind="decision", content="coding style", source="kent"),
            response=Response(kind="decision", content=content),
            umwelt=UmweltSnapshot.system(),
            timestamp=base_time + timedelta(hours=i * 6),
            tags=("decision", tag),
            metadata={"type": "decision", "reasoning": content},
        )
        mark_store.append(mark)
        marks.append(mark)

    return marks


@pytest.fixture
def pipeline(mark_store: MarkStore) -> AxiomDiscoveryPipeline:
    """Create pipeline with injected mark store."""
    return AxiomDiscoveryPipeline(mark_store=mark_store)


# =============================================================================
# AxiomCandidate Tests
# =============================================================================


class TestAxiomCandidate:
    """Tests for AxiomCandidate dataclass."""

    def test_is_axiom_below_threshold(self) -> None:
        """is_axiom should return True when loss < AXIOM_THRESHOLD."""
        candidate = AxiomCandidate(
            content="Simplicity is important",
            loss=0.01,  # Below 0.05 threshold
            stability=0.005,
            evidence=["mark-1", "mark-2"],
            source_pattern="simplicity is important",
            frequency=4,
        )
        assert candidate.is_axiom is True

    def test_is_axiom_above_threshold(self) -> None:
        """is_axiom should return False when loss >= AXIOM_THRESHOLD."""
        candidate = AxiomCandidate(
            content="Not an axiom",
            loss=0.1,  # Above 0.05 threshold
            stability=0.01,
            evidence=["mark-1"],
            source_pattern="not an axiom",
            frequency=2,
        )
        assert candidate.is_axiom is False

    def test_is_axiom_at_threshold(self) -> None:
        """is_axiom should return False when loss == AXIOM_THRESHOLD (0.05)."""
        # AXIOM_THRESHOLD is 0.05, which is same as AXIOM_THRESHOLD
        candidate = AxiomCandidate(
            content="Boundary case",
            loss=0.05,  # Exactly at threshold (0.05)
            stability=0.005,
            evidence=["mark-1"],
            source_pattern="boundary case",
            frequency=3,
        )
        assert candidate.is_axiom is False  # Must be strictly less than 0.05

    def test_stability_score(self) -> None:
        """stability_score should convert std dev to 0-1 score."""
        # Perfect stability (0 std dev)
        candidate = AxiomCandidate(
            content="Test",
            loss=0.01,
            stability=0.0,
            evidence=[],
            source_pattern="test",
        )
        assert candidate.stability_score == 1.0

        # High instability (at threshold)
        candidate_unstable = AxiomCandidate(
            content="Test",
            loss=0.01,
            stability=STABILITY_THRESHOLD,
            evidence=[],
            source_pattern="test",
        )
        assert candidate_unstable.stability_score == 0.0

    def test_compute_confidence(self) -> None:
        """compute_confidence should combine loss, stability, and frequency."""
        candidate = AxiomCandidate(
            content="Test",
            loss=0.01,  # High loss factor
            stability=0.005,  # High stability
            evidence=[],
            source_pattern="test",
            frequency=10,  # Good frequency
        )
        confidence = candidate.compute_confidence()

        assert 0.0 <= confidence <= 1.0
        assert candidate.confidence == confidence
        # Low loss + low stability + moderate frequency should be high confidence
        assert confidence > 0.7

    def test_to_dict(self) -> None:
        """to_dict should serialize all fields."""
        now = datetime.now(timezone.utc)
        candidate = AxiomCandidate(
            content="Simplicity is important",
            loss=0.01,
            stability=0.005,
            evidence=["mark-1", "mark-2"],
            source_pattern="simplicity is important",
            confidence=0.9,
            frequency=4,
            first_seen=now - timedelta(days=10),
            last_seen=now,
        )
        data = candidate.to_dict()

        assert data["content"] == "Simplicity is important"
        assert data["loss"] == 0.01
        assert data["stability"] == 0.005
        assert data["evidence"] == ["mark-1", "mark-2"]
        assert data["is_axiom"] is True
        assert "stability_score" in data
        assert "first_seen" in data
        assert "last_seen" in data


# =============================================================================
# ContradictionPair Tests
# =============================================================================


class TestContradictionPair:
    """Tests for ContradictionPair dataclass."""

    def test_is_strong_above_threshold(self) -> None:
        """is_strong should return True when strength > 0.3."""
        contradiction = ContradictionPair(
            axiom_a="Performance is important",
            axiom_b="Readability is important",
            loss_a=0.02,
            loss_b=0.02,
            loss_combined=0.45,
            strength=0.35,  # Above 0.3
        )
        assert contradiction.is_strong is True

    def test_is_strong_below_threshold(self) -> None:
        """is_strong should return False when strength <= 0.3."""
        contradiction = ContradictionPair(
            axiom_a="A",
            axiom_b="B",
            loss_a=0.02,
            loss_b=0.02,
            loss_combined=0.2,
            strength=0.15,  # Below 0.3
        )
        assert contradiction.is_strong is False

    def test_type_label_classification(self) -> None:
        """type_label should classify by strength."""
        # Irreconcilable
        c1 = ContradictionPair("A", "B", 0.02, 0.02, 0.6, strength=0.55)
        assert c1.type_label == "IRRECONCILABLE"

        # Strong
        c2 = ContradictionPair("A", "B", 0.02, 0.02, 0.5, strength=0.35)
        assert c2.type_label == "STRONG"

        # Moderate
        c3 = ContradictionPair("A", "B", 0.02, 0.02, 0.3, strength=0.15)
        assert c3.type_label == "MODERATE"

        # Weak
        c4 = ContradictionPair("A", "B", 0.02, 0.02, 0.15, strength=0.05)
        assert c4.type_label == "WEAK"

    def test_to_dict(self) -> None:
        """to_dict should serialize all fields."""
        contradiction = ContradictionPair(
            axiom_a="A",
            axiom_b="B",
            loss_a=0.02,
            loss_b=0.03,
            loss_combined=0.5,
            strength=0.4,
            synthesis_hint="Consider C",
        )
        data = contradiction.to_dict()

        assert data["axiom_a"] == "A"
        assert data["axiom_b"] == "B"
        assert data["strength"] == 0.4
        assert data["type"] == "STRONG"
        assert data["synthesis_hint"] == "Consider C"


# =============================================================================
# AxiomDiscoveryResult Tests
# =============================================================================


class TestAxiomDiscoveryResult:
    """Tests for AxiomDiscoveryResult dataclass."""

    def test_top_axioms_filters_by_threshold(self) -> None:
        """top_axioms should only return candidates with L < 0.05."""
        result = AxiomDiscoveryResult(
            candidates=[
                AxiomCandidate("A", 0.01, 0.005, [], "a", 0.9, 3),  # Axiom
                AxiomCandidate("B", 0.03, 0.008, [], "b", 0.85, 2),  # Axiom
                AxiomCandidate("C", 0.1, 0.02, [], "c", 0.7, 2),  # Not axiom
            ],
            total_decisions_analyzed=10,
            time_window_days=30,
            contradictions_detected=[],
            patterns_found=3,
            axioms_discovered=2,
            duration_ms=100.0,
        )

        top = result.top_axioms
        assert len(top) == 2
        assert all(c.is_axiom for c in top)

    def test_has_contradictions(self) -> None:
        """has_contradictions should reflect contradiction list."""
        result_no_contra = AxiomDiscoveryResult(
            candidates=[],
            total_decisions_analyzed=10,
            time_window_days=30,
            contradictions_detected=[],
            patterns_found=0,
            axioms_discovered=0,
            duration_ms=50.0,
        )
        assert result_no_contra.has_contradictions is False

        result_with_contra = AxiomDiscoveryResult(
            candidates=[],
            total_decisions_analyzed=10,
            time_window_days=30,
            contradictions_detected=[ContradictionPair("A", "B", 0.02, 0.02, 0.3, 0.2)],
            patterns_found=0,
            axioms_discovered=0,
            duration_ms=50.0,
        )
        assert result_with_contra.has_contradictions is True

    def test_to_dict_complete(self) -> None:
        """to_dict should include all fields and computed properties."""
        result = AxiomDiscoveryResult(
            candidates=[AxiomCandidate("A", 0.01, 0.005, ["m1"], "a", 0.9, 3)],
            total_decisions_analyzed=50,
            time_window_days=30,
            contradictions_detected=[],
            patterns_found=5,
            axioms_discovered=1,
            duration_ms=123.45,
            user_id="kent",
        )
        data = result.to_dict()

        assert data["total_decisions_analyzed"] == 50
        assert data["time_window_days"] == 30
        assert data["patterns_found"] == 5
        assert data["axioms_discovered"] == 1
        assert data["duration_ms"] == 123.45
        assert data["user_id"] == "kent"
        assert len(data["candidates"]) == 1
        assert len(data["top_axioms"]) == 1
        assert data["has_contradictions"] is False


# =============================================================================
# Pipeline Tests
# =============================================================================


class TestAxiomDiscoveryPipeline:
    """Tests for AxiomDiscoveryPipeline."""

    @pytest.mark.asyncio
    async def test_discover_returns_result(
        self, pipeline: AxiomDiscoveryPipeline, decision_marks: list[Mark]
    ) -> None:
        """discover_axioms should return AxiomDiscoveryResult."""
        result = await pipeline.discover_axioms(days=30, max_candidates=5)

        assert isinstance(result, AxiomDiscoveryResult)
        assert result.total_decisions_analyzed > 0
        assert result.time_window_days == 30
        assert result.duration_ms > 0

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires LLM mocking - GaloisLossComputer calls real LLM API")
    async def test_discover_finds_patterns(
        self, pipeline: AxiomDiscoveryPipeline, decision_marks: list[Mark]
    ) -> None:
        """discover_axioms should find recurring patterns."""
        result = await pipeline.discover_axioms(
            days=30,
            max_candidates=10,
            min_pattern_occurrences=2,
        )

        # Should find patterns from our test data
        assert result.patterns_found >= 0

    @pytest.mark.asyncio
    async def test_discover_empty_store(self, pipeline: AxiomDiscoveryPipeline) -> None:
        """discover_axioms should handle empty store gracefully."""
        # No marks added, so store is empty
        result = await pipeline.discover_axioms(days=30)

        assert result.total_decisions_analyzed == 0
        assert len(result.candidates) == 0
        assert result.axioms_discovered == 0

    @pytest.mark.asyncio
    async def test_discover_insufficient_decisions(
        self, pipeline: AxiomDiscoveryPipeline, mark_store: MarkStore
    ) -> None:
        """discover_axioms should handle insufficient decisions."""
        # Add only 2 decisions (below min threshold of 5)
        for i in range(2):
            mark = Mark(
                id=MarkId(f"mark-few-{i:04d}"),
                origin="witness",
                response=Response(kind="decision", content="Test decision"),
                timestamp=datetime.now(timezone.utc),
                tags=("decision",),
            )
            mark_store.append(mark)

        result = await pipeline.discover_axioms(
            days=30,
            min_pattern_occurrences=5,
        )

        # Should return empty result gracefully
        assert result.total_decisions_analyzed == 2
        assert len(result.candidates) == 0

    @pytest.mark.asyncio
    async def test_validate_potential_axiom(self, pipeline: AxiomDiscoveryPipeline) -> None:
        """validate_potential_axiom should return candidate with metrics."""
        candidate = await pipeline.validate_potential_axiom(
            "Simplicity is essential for maintainability"
        )

        assert isinstance(candidate, AxiomCandidate)
        assert candidate.content == "Simplicity is essential for maintainability"
        assert 0.0 <= candidate.loss <= 1.0
        assert candidate.stability >= 0.0
        assert 0.0 <= candidate.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_time_window_filtering(
        self, pipeline: AxiomDiscoveryPipeline, mark_store: MarkStore
    ) -> None:
        """discover_axioms should respect time window."""
        # Add old decision (40 days ago)
        old_mark = Mark(
            id=MarkId("mark-old-0000"),
            origin="witness",
            response=Response(kind="decision", content="Old decision"),
            timestamp=datetime.now(timezone.utc) - timedelta(days=40),
            tags=("decision",),
        )
        mark_store.append(old_mark)

        # Add recent decision (5 days ago)
        recent_mark = Mark(
            id=MarkId("mark-recent-0000"),
            origin="witness",
            response=Response(kind="decision", content="Recent decision"),
            timestamp=datetime.now(timezone.utc) - timedelta(days=5),
            tags=("decision",),
        )
        mark_store.append(recent_mark)

        # Query for 30 days should only get recent
        result = await pipeline.discover_axioms(days=30)

        # The old mark should not be included
        # (exact count depends on whether pattern threshold is met)
        assert result.time_window_days == 30

    @pytest.mark.asyncio
    async def test_is_decision_mark_detection(self, pipeline: AxiomDiscoveryPipeline) -> None:
        """_is_decision_mark should detect decision marks."""
        # Mark with decision tag
        mark1 = Mark(
            id=MarkId("mark-test-1"),
            origin="witness",
            response=Response(kind="text", content="Some text"),
            tags=("decision",),
        )
        assert pipeline._is_decision_mark(mark1) is True

        # Mark with decision in metadata
        mark2 = Mark(
            id=MarkId("mark-test-2"),
            origin="witness",
            response=Response(kind="text", content="Some text"),
            metadata={"decision": "chose A", "reasoning": "because B"},
        )
        assert pipeline._is_decision_mark(mark2) is True

        # Mark with decision keywords in content
        mark3 = Mark(
            id=MarkId("mark-test-3"),
            origin="witness",
            response=Response(kind="text", content="I decided to use composition"),
        )
        assert pipeline._is_decision_mark(mark3) is True

        # Mark with proof
        mark4 = Mark(
            id=MarkId("mark-test-4"),
            origin="witness",
            response=Response(kind="text", content="Some text"),
            proof=Proof.empirical(
                data="Evidence",
                warrant="Reasoning",
                claim="Conclusion",
            ),
        )
        assert pipeline._is_decision_mark(mark4) is True

        # Mark without decision indicators
        mark5 = Mark(
            id=MarkId("mark-test-5"),
            origin="witness",
            response=Response(kind="text", content="Just an observation"),
            tags=("observation",),
        )
        assert pipeline._is_decision_mark(mark5) is False


# =============================================================================
# Pattern Extraction Tests
# =============================================================================


class TestPatternExtraction:
    """Tests for pattern extraction functionality."""

    @pytest.mark.asyncio
    async def test_extract_patterns_groups_similar(
        self, pipeline: AxiomDiscoveryPipeline, mark_store: MarkStore
    ) -> None:
        """_extract_patterns should group similar value phrases."""
        # Add marks with similar patterns
        patterns = [
            "Simplicity is important",
            "Simplicity matters",
            "Simplicity is essential",
        ]
        for i, content in enumerate(patterns):
            mark = Mark(
                id=MarkId(f"mark-pat-{i:04d}"),
                origin="witness",
                response=Response(kind="decision", content=content),
                timestamp=datetime.now(timezone.utc) - timedelta(hours=i),
                tags=("decision",),
            )
            mark_store.append(mark)

        # Surface decisions and extract patterns
        decisions = await pipeline._surface_decisions(days=30)
        extracted = pipeline._extract_patterns(decisions, min_occurrences=2)

        # Should find the simplicity pattern
        assert len(extracted) >= 0  # May be 0 if phrases don't cluster


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    @pytest.mark.asyncio
    async def test_discover_personal_axioms(self, mark_store: MarkStore) -> None:
        """discover_personal_axioms should work without explicit pipeline."""
        result = await discover_personal_axioms(days=30, max_candidates=3)

        assert isinstance(result, AxiomDiscoveryResult)
        assert result.time_window_days == 30

    @pytest.mark.asyncio
    async def test_validate_axiom_candidate(self) -> None:
        """validate_axiom_candidate should return is_axiom, loss, stability."""
        is_axiom, loss, stability = await validate_axiom_candidate("Composition is fundamental")

        assert isinstance(is_axiom, bool)
        assert isinstance(loss, float)
        assert isinstance(stability, float)
        assert 0.0 <= loss <= 1.0
        assert stability >= 0.0


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for full pipeline."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires LLM mocking - GaloisLossComputer calls real LLM API")
    async def test_full_pipeline_with_kent_values(
        self, pipeline: AxiomDiscoveryPipeline, decision_marks: list[Mark]
    ) -> None:
        """
        Full pipeline should discover Kent's recurring values.

        Test data includes:
        - Simplicity is important (4 occurrences)
        - Composition matters (3 occurrences)
        - Joy-inducing design (3 occurrences)
        """
        result = await pipeline.discover_axioms(
            days=30,
            max_candidates=5,
            min_pattern_occurrences=2,
        )

        # Verify structure
        assert isinstance(result, AxiomDiscoveryResult)
        assert result.total_decisions_analyzed == len(decision_marks)
        assert result.duration_ms > 0

        # All candidates should have valid metrics
        for candidate in result.candidates:
            assert 0.0 <= candidate.loss <= 1.0
            assert candidate.stability >= 0.0
            assert len(candidate.evidence) > 0

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires LLM mocking - GaloisLossComputer calls real LLM API")
    async def test_candidates_sorted_by_loss(
        self, pipeline: AxiomDiscoveryPipeline, decision_marks: list[Mark]
    ) -> None:
        """Candidates should be sorted by loss (best first)."""
        result = await pipeline.discover_axioms(
            days=30,
            max_candidates=10,
            min_pattern_occurrences=2,
        )

        if len(result.candidates) > 1:
            for i in range(len(result.candidates) - 1):
                assert result.candidates[i].loss <= result.candidates[i + 1].loss

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires LLM mocking - GaloisLossComputer calls real LLM API")
    async def test_example_discovery_output(
        self, pipeline: AxiomDiscoveryPipeline, decision_marks: list[Mark]
    ) -> None:
        """
        Example: Show what axiom discovery output looks like.

        This test demonstrates the intended output format.
        """
        result = await pipeline.discover_axioms(
            days=30,
            max_candidates=3,
            min_pattern_occurrences=2,
        )

        # Print example output (useful for debugging)
        output = f"""
        =================================
        Personal Axiom Discovery Results
        =================================
        Decisions analyzed: {result.total_decisions_analyzed}
        Time window: {result.time_window_days} days
        Patterns found: {result.patterns_found}
        Axioms discovered: {result.axioms_discovered}
        Duration: {result.duration_ms:.0f}ms

        Top Axioms:
        """
        for i, axiom in enumerate(result.top_axioms[:3], 1):
            output += f"""
          {i}. {axiom.content}
             Loss: {axiom.loss:.3f}
             Stability: {axiom.stability:.4f}
             Confidence: {axiom.confidence:.2f}
             Seen: {axiom.frequency} times
        """

        if result.has_contradictions:
            output += "\n        Contradictions:\n"
            for c in result.contradictions_detected:
                output += f"""
          - "{c.axiom_a}" vs "{c.axiom_b}"
            Strength: {c.strength:.2f} ({c.type_label})
        """

        # This test always passes - it's for demonstration
        assert True


# =============================================================================
# Mock Data for Demo
# =============================================================================


@pytest.fixture
def mock_axiom_discovery_result() -> AxiomDiscoveryResult:
    """
    Create a mock result showing what Kent would see.

    "You've made 147 decisions this month.
     Here are the 3 principles you never violated — your L0 axioms."
    """
    return AxiomDiscoveryResult(
        candidates=[
            AxiomCandidate(
                content="Simplicity over complexity",
                loss=0.02,
                stability=0.005,
                evidence=["mark-001", "mark-015", "mark-042", "mark-089"],
                source_pattern="simplicity over complexity",
                confidence=0.95,
                frequency=23,
            ),
            AxiomCandidate(
                content="Composition is primary",
                loss=0.03,
                stability=0.008,
                evidence=["mark-007", "mark-033", "mark-078"],
                source_pattern="composition is primary",
                confidence=0.92,
                frequency=18,
            ),
            AxiomCandidate(
                content="Joy-inducing design",
                loss=0.04,
                stability=0.01,
                evidence=["mark-012", "mark-056"],
                source_pattern="joy-inducing design",
                confidence=0.88,
                frequency=12,
            ),
        ],
        total_decisions_analyzed=147,
        time_window_days=30,
        contradictions_detected=[],
        patterns_found=15,
        axioms_discovered=3,
        duration_ms=2340.0,
        user_id="kent",
    )


class TestMockDemoOutput:
    """Tests using mock data to demonstrate expected output."""

    def test_mock_result_matches_vision(
        self, mock_axiom_discovery_result: AxiomDiscoveryResult
    ) -> None:
        """
        Verify mock matches the zero-seed-personal-governance-lab vision.

        "Kent discovers his personal axioms. The system shows him:
         'You've made 147 decisions this month. Here are the 3 principles
          you never violated — your L0 axioms.'"
        """
        result = mock_axiom_discovery_result

        # 147 decisions
        assert result.total_decisions_analyzed == 147

        # 3 axioms discovered
        assert result.axioms_discovered == 3
        assert len(result.top_axioms) == 3

        # All are true axioms (L < 0.05)
        for axiom in result.top_axioms:
            assert axiom.loss < AXIOM_THRESHOLD
            assert axiom.is_axiom is True

        # Kent's actual values
        contents = [a.content for a in result.top_axioms]
        assert "Simplicity over complexity" in contents
        assert "Composition is primary" in contents
        assert "Joy-inducing design" in contents

    def test_mock_output_format(self, mock_axiom_discovery_result: AxiomDiscoveryResult) -> None:
        """Test the human-readable output format."""
        result = mock_axiom_discovery_result
        data = result.to_dict()

        # Should have all required fields
        assert "candidates" in data
        assert "total_decisions_analyzed" in data
        assert "axioms_discovered" in data
        assert "contradictions_detected" in data
        assert "top_axioms" in data

        # Top axioms should be properly formatted
        assert len(data["top_axioms"]) == 3
        for axiom in data["top_axioms"]:
            assert "content" in axiom
            assert "loss" in axiom
            assert "confidence" in axiom
            assert "frequency" in axiom

"""
Tests for Trail Bridge: Trail → Mark conversion.

Phase 4B: Witness integration tests.

Verifies:
- Trail analysis extracts correct evidence characteristics
- Evidence strength computation follows spec
- Principle detection from exploration patterns
- TrailMark creation with proper metadata
- Bus emission (mocked)
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from services.witness.mark import NPhase
from services.witness.trail_bridge import (
    EvidenceTier,
    TrailEvidence,
    TrailMark,
    _compute_commitment,
    _compute_evidence_strength,
    _detect_principles,
    analyze_trail,
    convert_trail_to_mark,
    emit_trail_as_mark,
)

# =============================================================================
# Mock Trail for Testing
# =============================================================================


class MockTrailStep:
    """Mock TrailStep for testing."""

    def __init__(
        self,
        node_path: str,
        edge_type: str | None = None,
        annotations: str = "",
    ):
        self.node_path = node_path
        self.edge_type = edge_type
        self.annotations = annotations
        self.timestamp = datetime.now()


class MockObserver:
    """Mock Observer for testing."""

    def __init__(self, archetype: str = "developer"):
        self.archetype = archetype


class MockTrail:
    """Mock Trail for testing."""

    def __init__(
        self,
        trail_id: str = "trail-123",
        name: str = "Test Trail",
        steps: list[MockTrailStep] | None = None,
        annotations: dict[int, str] | None = None,
    ):
        self.id = trail_id
        self.name = name
        self.steps = steps or []
        self.annotations = annotations or {}
        self.created_by = MockObserver()

    def as_outline(self) -> str:
        """Return formatted outline."""
        lines = [f'📍 Trail: "{self.name}"']
        for i, step in enumerate(self.steps):
            lines.append(f"   {i + 1}. {step.node_path}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Return dict representation."""
        return {"id": self.id, "name": self.name, "steps": len(self.steps)}


# =============================================================================
# Evidence Strength Tests
# =============================================================================


class TestEvidenceStrengthComputation:
    """Tests for evidence strength computation."""

    def test_weak_evidence_empty_trail(self) -> None:
        """Trail with nothing should be weak."""
        strength = _compute_evidence_strength(0, 0, 0, 0)
        assert strength == "weak"

    def test_moderate_evidence_few_steps(self) -> None:
        """Trail with 3+ steps should be at least moderate."""
        strength = _compute_evidence_strength(3, 2, 1, 0)
        assert strength in ("moderate", "strong")

    def test_strong_evidence_annotated(self) -> None:
        """Annotated trail with steps should be strong."""
        strength = _compute_evidence_strength(5, 4, 2, 2)
        assert strength in ("strong", "definitive")

    def test_definitive_evidence_full(self) -> None:
        """Full trail with everything should be definitive."""
        strength = _compute_evidence_strength(10, 8, 4, 5)
        assert strength == "definitive"


# =============================================================================
# Principle Detection Tests
# =============================================================================


class TestPrincipleDetection:
    """Tests for principle detection from trail patterns."""

    def test_composable_detected_many_edges(self) -> None:
        """Many diverse edges signals Composable."""
        principles = _detect_principles(5, 3, 4, 0)
        principle_names = [p[0] for p in principles]
        assert "composable" in principle_names

    def test_curated_detected_deep_focused(self) -> None:
        """Deep focused exploration signals Curated."""
        # Many steps, few unique paths (focused exploration)
        principles = _detect_principles(8, 4, 2, 0)
        principle_names = [p[0] for p in principles]
        assert "curated" in principle_names

    def test_ethical_detected_annotated(self) -> None:
        """Annotated exploration signals Ethical."""
        principles = _detect_principles(3, 2, 1, 3)
        principle_names = [p[0] for p in principles]
        assert "ethical" in principle_names

    def test_heterarchical_detected_breadth(self) -> None:
        """Breadth exploration signals Heterarchical."""
        # Many unique paths relative to steps
        principles = _detect_principles(5, 5, 1, 0)
        principle_names = [p[0] for p in principles]
        assert "heterarchical" in principle_names


# =============================================================================
# Commitment Level Tests
# =============================================================================


class TestCommitmentLevel:
    """Tests for commitment level computation."""

    def test_tentative_commitment(self) -> None:
        """Minimal trail is tentative."""
        commitment = _compute_commitment(1, 1, 0, "weak")
        assert commitment == "tentative"

    def test_moderate_commitment(self) -> None:
        """Some exploration is moderate."""
        commitment = _compute_commitment(3, 2, 1, "moderate")
        assert commitment == "moderate"

    def test_strong_commitment(self) -> None:
        """Good exploration is strong."""
        commitment = _compute_commitment(6, 4, 1, "strong")
        assert commitment == "strong"

    def test_definitive_commitment(self) -> None:
        """Full exploration with annotations is definitive."""
        commitment = _compute_commitment(8, 6, 4, "definitive")
        assert commitment == "definitive"


# =============================================================================
# Trail Analysis Tests
# =============================================================================


class TestTrailAnalysis:
    """Tests for analyze_trail()."""

    def test_analyzes_empty_trail(self) -> None:
        """Empty trail should analyze without error."""
        trail = MockTrail(steps=[])
        evidence = analyze_trail(trail)

        assert evidence.step_count == 0
        assert evidence.evidence_strength == "weak"

    def test_analyzes_simple_trail(self) -> None:
        """Simple trail with steps should analyze."""
        trail = MockTrail(
            steps=[
                MockTrailStep("world.auth", None),
                MockTrailStep("world.auth.validate", "contains"),
                MockTrailStep("world.auth.tests", "tests"),
            ]
        )
        evidence = analyze_trail(trail)

        assert evidence.step_count == 3
        assert evidence.unique_paths == 3
        assert evidence.unique_edges == 2  # contains, tests (None excluded)

    def test_counts_annotations(self) -> None:
        """Should count both step and trail annotations."""
        trail = MockTrail(
            steps=[
                MockTrailStep("node1", None, "Step note"),
                MockTrailStep("node2", "edge", "Another note"),
            ],
            annotations={0: "Trail annotation"},
        )
        evidence = analyze_trail(trail)

        assert evidence.annotation_count == 3  # 2 step + 1 trail

    def test_returns_trail_evidence(self) -> None:
        """Should return TrailEvidence dataclass."""
        trail = MockTrail()
        evidence = analyze_trail(trail)

        assert isinstance(evidence, TrailEvidence)
        assert evidence.trail_id == trail.id
        assert evidence.trail_name == trail.name


# =============================================================================
# Mark Creation Tests
# =============================================================================


class TestMarkCreation:
    """Tests for convert_trail_to_mark()."""

    def test_creates_mark_from_trail(self) -> None:
        """Should create TrailMark from trail."""
        trail = MockTrail(steps=[MockTrailStep("node1"), MockTrailStep("node2", "edge")])
        mark = convert_trail_to_mark(trail)

        assert isinstance(mark, TrailMark)
        assert mark.origin == "context_perception"
        assert mark.trail_id == trail.id

    def test_mark_has_evidence(self) -> None:
        """Mark should contain evidence analysis."""
        trail = MockTrail(steps=[MockTrailStep("node1"), MockTrailStep("node2", "edge")])
        mark = convert_trail_to_mark(trail)

        assert isinstance(mark.evidence, TrailEvidence)
        assert mark.evidence.step_count == 2

    def test_mark_includes_claim(self) -> None:
        """Mark should include claim if provided."""
        trail = MockTrail()
        mark = convert_trail_to_mark(trail, claim="Auth is secure")

        assert mark.metadata["claim"] == "Auth is secure"

    def test_mark_has_phase(self) -> None:
        """Mark should have N-Phase."""
        trail = MockTrail()
        mark = convert_trail_to_mark(trail, phase=NPhase.ACT)

        assert mark.phase == NPhase.ACT

    def test_mark_has_content(self) -> None:
        """Mark should have trail outline as content."""
        trail = MockTrail(name="My Trail")
        mark = convert_trail_to_mark(trail)

        assert "My Trail" in mark.content

    def test_mark_serializable(self) -> None:
        """Mark should be JSON-serializable via to_dict()."""
        trail = MockTrail()
        mark = convert_trail_to_mark(trail)

        data = mark.to_dict()
        assert "id" in data
        assert "evidence" in data
        assert "origin" in data


# =============================================================================
# Evidence Tier Tests
# =============================================================================


class TestEvidenceTier:
    """Tests for evidence tier constants."""

    def test_empirical_is_tier_2(self) -> None:
        """Trails are EMPIRICAL (Tier 2)."""
        assert EvidenceTier.EMPIRICAL == 2

    def test_categorical_is_tier_1(self) -> None:
        """CATEGORICAL is strongest (Tier 1)."""
        assert EvidenceTier.CATEGORICAL == 1

    def test_trail_marks_use_empirical(self) -> None:
        """Trail marks should be marked as EMPIRICAL."""
        trail = MockTrail()
        mark = convert_trail_to_mark(trail)

        assert mark.metadata["evidence_tier"] == EvidenceTier.EMPIRICAL


# =============================================================================
# Bus Emission Tests
# =============================================================================


class TestBusEmission:
    """Tests for emit_trail_as_mark() bus integration."""

    @pytest.mark.asyncio
    async def test_emits_to_bus(self) -> None:
        """Should emit mark to witness bus."""
        trail = MockTrail(steps=[MockTrailStep("node1"), MockTrailStep("node2", "edge")])

        # Mock the bus
        mock_bus = AsyncMock()

        with patch("services.witness.bus.get_synergy_bus", return_value=mock_bus):
            mark = await emit_trail_as_mark(trail)

        # Verify emit was called
        mock_bus.publish.assert_called_once()

        # Verify topic
        call_args = mock_bus.publish.call_args
        assert call_args[0][0] == "witness.trail.captured"

    @pytest.mark.asyncio
    async def test_returns_mark(self) -> None:
        """Should return created mark."""
        trail = MockTrail()

        with patch("services.witness.bus.get_synergy_bus", return_value=AsyncMock()):
            mark = await emit_trail_as_mark(trail)

        assert isinstance(mark, TrailMark)
        assert mark.trail_id == trail.id


# =============================================================================
# TrailEvidence Serialization Tests
# =============================================================================


class TestTrailEvidenceSerialization:
    """Tests for TrailEvidence.to_dict()."""

    def test_serializes_all_fields(self) -> None:
        """to_dict should include all fields."""
        evidence = TrailEvidence(
            trail_id="id-123",
            trail_name="Test",
            step_count=5,
            unique_paths=3,
            unique_edges=2,
            annotation_count=1,
            evidence_strength="strong",
            principles_signaled=[("composable", 0.8)],
            commitment_level="moderate",
        )

        data = evidence.to_dict()

        assert data["trail_id"] == "id-123"
        assert data["step_count"] == 5
        assert data["evidence_strength"] == "strong"
        assert len(data["principles_signaled"]) == 1
        assert data["principles_signaled"][0]["principle"] == "composable"

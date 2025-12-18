"""
Tests for N-gent Phase 6: Epistemic Features.

Tests cover:
- ConfidenceLevel and ReliabilityAnnotation
- UnreliableTrace
- HallucinationType and HallucinationIndicator
- HallucinationDetector
- UnreliableNarrator
- PerspectiveSpec and Contradiction
- RashomonNarrative and RashomonNarrator
- GroundTruth and GroundTruthReconciler

Target: 30+ tests
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from agents.n.bard import (
    Narrative,
    NarrativeGenre,
    NarrativeRequest,
    Perspective,
    SimpleLLMProvider,
)
from agents.n.epistemic import (
    ConfidenceLevel,
    Contradiction,
    GroundTruth,
    GroundTruthReconciler,
    HallucinationDetector,
    HallucinationIndicator,
    HallucinationType,
    PerspectiveSpec,
    RashomonNarrative,
    RashomonNarrator,
    ReliabilityAnnotation,
    UnreliableNarrative,
    UnreliableNarrator,
    UnreliableTrace,
)
from agents.n.types import Determinism, SemanticTrace

# =============================================================================
# Fixtures
# =============================================================================


def make_trace(
    trace_id: str = "trace-1",
    agent_id: str = "Agent",
    action: str = "INVOKE",
    timestamp: datetime | None = None,
    determinism: Determinism = Determinism.DETERMINISTIC,
    duration_ms: int = 100,
    inputs: dict[str, Any] | None = None,
    outputs: dict[str, Any] | None = None,
) -> SemanticTrace:
    """Create a test trace."""
    return SemanticTrace(
        trace_id=trace_id,
        parent_id=None,
        agent_id=agent_id,
        agent_genus="Test",
        action=action,
        timestamp=timestamp or datetime.now(timezone.utc),
        duration_ms=duration_ms,
        gas_consumed=10,
        inputs=inputs or {},
        outputs=outputs,
        input_hash="hash-" + trace_id,
        input_snapshot=b"snapshot",
        output_hash="output-hash" if outputs else None,
        determinism=determinism,
    )


def make_traces(count: int, base_time: datetime | None = None) -> list[SemanticTrace]:
    """Create multiple test traces."""
    base = base_time or datetime.now(timezone.utc)
    return [
        make_trace(
            trace_id=f"trace-{i}",
            agent_id=f"Agent-{i % 2}",
            timestamp=base + timedelta(seconds=i),
        )
        for i in range(count)
    ]


# =============================================================================
# ConfidenceLevel Tests
# =============================================================================


class TestConfidenceLevel:
    """Tests for ConfidenceLevel enum."""

    def test_all_levels_defined(self) -> None:
        """All confidence levels should be defined."""
        levels = [
            ConfidenceLevel.CERTAIN,
            ConfidenceLevel.HIGH,
            ConfidenceLevel.MODERATE,
            ConfidenceLevel.LOW,
            ConfidenceLevel.UNCERTAIN,
        ]
        assert len(levels) == 5

    def test_from_score_certain(self) -> None:
        """Score >= 0.95 should be CERTAIN."""
        assert ConfidenceLevel.from_score(1.0) == ConfidenceLevel.CERTAIN
        assert ConfidenceLevel.from_score(0.95) == ConfidenceLevel.CERTAIN
        assert ConfidenceLevel.from_score(0.99) == ConfidenceLevel.CERTAIN

    def test_from_score_high(self) -> None:
        """Score 0.8-0.95 should be HIGH."""
        assert ConfidenceLevel.from_score(0.94) == ConfidenceLevel.HIGH
        assert ConfidenceLevel.from_score(0.8) == ConfidenceLevel.HIGH
        assert ConfidenceLevel.from_score(0.85) == ConfidenceLevel.HIGH

    def test_from_score_moderate(self) -> None:
        """Score 0.5-0.8 should be MODERATE."""
        assert ConfidenceLevel.from_score(0.79) == ConfidenceLevel.MODERATE
        assert ConfidenceLevel.from_score(0.5) == ConfidenceLevel.MODERATE
        assert ConfidenceLevel.from_score(0.6) == ConfidenceLevel.MODERATE

    def test_from_score_low(self) -> None:
        """Score 0.2-0.5 should be LOW."""
        assert ConfidenceLevel.from_score(0.49) == ConfidenceLevel.LOW
        assert ConfidenceLevel.from_score(0.2) == ConfidenceLevel.LOW
        assert ConfidenceLevel.from_score(0.35) == ConfidenceLevel.LOW

    def test_from_score_uncertain(self) -> None:
        """Score < 0.2 should be UNCERTAIN."""
        assert ConfidenceLevel.from_score(0.19) == ConfidenceLevel.UNCERTAIN
        assert ConfidenceLevel.from_score(0.0) == ConfidenceLevel.UNCERTAIN
        assert ConfidenceLevel.from_score(0.1) == ConfidenceLevel.UNCERTAIN


# =============================================================================
# ReliabilityAnnotation Tests
# =============================================================================


class TestReliabilityAnnotation:
    """Tests for ReliabilityAnnotation."""

    def test_creation_basic(self) -> None:
        """Should create annotation with basic fields."""
        annotation = ReliabilityAnnotation(confidence=0.8)
        assert annotation.confidence == 0.8
        assert annotation.corroborated_by == []
        assert annotation.contradicted_by == []
        assert annotation.source_reliability == 1.0

    def test_level_property(self) -> None:
        """Should return correct confidence level."""
        annotation = ReliabilityAnnotation(confidence=0.9)
        assert annotation.level == ConfidenceLevel.HIGH

    def test_adjusted_confidence_no_modifiers(self) -> None:
        """Adjusted confidence should equal base without modifiers."""
        annotation = ReliabilityAnnotation(confidence=0.8)
        assert annotation.adjusted_confidence == 0.8

    def test_adjusted_confidence_with_corroboration(self) -> None:
        """Corroboration should boost confidence."""
        annotation = ReliabilityAnnotation(
            confidence=0.7,
            corroborated_by=["trace-1", "trace-2"],
        )
        # +5% per corroborating trace = +10%
        assert annotation.adjusted_confidence == pytest.approx(0.8)

    def test_adjusted_confidence_with_contradiction(self) -> None:
        """Contradiction should penalize confidence."""
        annotation = ReliabilityAnnotation(
            confidence=0.8,
            contradicted_by=["trace-1"],
        )
        # -15% per contradicting trace
        assert annotation.adjusted_confidence == pytest.approx(0.65)

    def test_adjusted_confidence_capped(self) -> None:
        """Adjusted confidence should be capped at 0-1."""
        annotation = ReliabilityAnnotation(
            confidence=0.95,
            corroborated_by=["t1", "t2", "t3", "t4", "t5"],  # +25% but capped at +20%
        )
        assert annotation.adjusted_confidence <= 1.0

    def test_is_contested(self) -> None:
        """Should detect contested annotations."""
        not_contested = ReliabilityAnnotation(confidence=0.8)
        contested = ReliabilityAnnotation(
            confidence=0.8,
            contradicted_by=["trace-1"],
        )
        assert not not_contested.is_contested
        assert contested.is_contested

    def test_source_reliability_factor(self) -> None:
        """Source reliability should factor into adjusted confidence."""
        annotation = ReliabilityAnnotation(
            confidence=0.8,
            source_reliability=0.5,
        )
        assert annotation.adjusted_confidence == 0.4


# =============================================================================
# UnreliableTrace Tests
# =============================================================================


class TestUnreliableTrace:
    """Tests for UnreliableTrace."""

    def test_creation(self) -> None:
        """Should create unreliable trace from semantic trace."""
        trace = make_trace()
        reliability = ReliabilityAnnotation(confidence=0.8)
        unreliable = UnreliableTrace(
            trace=trace,
            reliability=reliability,
            interpretation="Agent performed action",
        )

        assert unreliable.trace_id == "trace-1"
        assert unreliable.agent_id == "Agent"
        assert unreliable.confidence == 0.8

    def test_confidence_uses_adjusted(self) -> None:
        """Confidence property should use adjusted confidence."""
        trace = make_trace()
        reliability = ReliabilityAnnotation(
            confidence=0.7,
            corroborated_by=["other-trace"],
        )
        unreliable = UnreliableTrace(trace=trace, reliability=reliability)

        # 0.7 + 0.05 (corroboration) = 0.75
        assert unreliable.confidence == 0.75

    def test_level_property(self) -> None:
        """Level should map to confidence level."""
        trace = make_trace()
        reliability = ReliabilityAnnotation(confidence=0.9)
        unreliable = UnreliableTrace(trace=trace, reliability=reliability)

        assert unreliable.level == ConfidenceLevel.HIGH


# =============================================================================
# HallucinationType Tests
# =============================================================================


class TestHallucinationType:
    """Tests for HallucinationType enum."""

    def test_all_types_defined(self) -> None:
        """All hallucination types should be defined."""
        types = [
            HallucinationType.CONFABULATION,
            HallucinationType.OVERCONFIDENCE,
            HallucinationType.CONTRADICTION,
            HallucinationType.TEMPORAL,
            HallucinationType.ATTRIBUTION,
            HallucinationType.SPECIFICITY,
        ]
        assert len(types) == 6


# =============================================================================
# HallucinationIndicator Tests
# =============================================================================


class TestHallucinationIndicator:
    """Tests for HallucinationIndicator."""

    def test_creation(self) -> None:
        """Should create indicator with all fields."""
        indicator = HallucinationIndicator(
            type=HallucinationType.OVERCONFIDENCE,
            description="High confidence without evidence",
            affected_traces=["trace-1"],
            severity=0.5,
            evidence="No corroborating traces",
        )

        assert indicator.type == HallucinationType.OVERCONFIDENCE
        assert indicator.severity == 0.5
        assert len(indicator.affected_traces) == 1

    def test_is_severe(self) -> None:
        """Should detect severe indicators."""
        mild = HallucinationIndicator(
            type=HallucinationType.OVERCONFIDENCE,
            description="",
            affected_traces=[],
            severity=0.3,
        )
        severe = HallucinationIndicator(
            type=HallucinationType.CONTRADICTION,
            description="",
            affected_traces=[],
            severity=0.8,
        )

        assert not mild.is_severe
        assert severe.is_severe

    def test_to_dict(self) -> None:
        """Should convert to dictionary."""
        indicator = HallucinationIndicator(
            type=HallucinationType.TEMPORAL,
            description="Timeline issue",
            affected_traces=["t1", "t2"],
            severity=0.6,
        )
        d = indicator.to_dict()

        assert d["type"] == "temporal"
        assert d["description"] == "Timeline issue"
        assert len(d["affected_traces"]) == 2


# =============================================================================
# HallucinationDetector Tests
# =============================================================================


class TestHallucinationDetector:
    """Tests for HallucinationDetector."""

    def test_detect_overconfidence(self) -> None:
        """Should detect overconfidence pattern."""
        detector = HallucinationDetector()
        trace = make_trace()

        unreliable = UnreliableTrace(
            trace=trace,
            reliability=ReliabilityAnnotation(
                confidence=0.9,
                corroborated_by=[],  # No corroboration
            ),
        )

        indicators = detector.detect([unreliable])

        assert len(indicators) > 0
        assert any(i.type == HallucinationType.OVERCONFIDENCE for i in indicators)

    def test_detect_contradiction(self) -> None:
        """Should detect contradictions."""
        detector = HallucinationDetector()
        trace = make_trace(agent_id="AgentA")

        # Create a trace that has a contradiction marked
        unreliable = UnreliableTrace(
            trace=trace,
            reliability=ReliabilityAnnotation(
                confidence=0.7,
                contradicted_by=["other-trace"],  # This trace has a known contradiction
            ),
        )

        # Add another trace from the same agent to trigger detection
        trace2 = make_trace(trace_id="other-trace", agent_id="AgentA")
        unreliable2 = UnreliableTrace(
            trace=trace2,
            reliability=ReliabilityAnnotation(confidence=0.8),
        )

        indicators = detector.detect([unreliable, unreliable2])

        # Should detect the contradiction
        assert any(i.type == HallucinationType.CONTRADICTION for i in indicators)

    def test_check_ground_truth(self) -> None:
        """Should check against ground truth."""
        detector = HallucinationDetector()
        trace = make_trace(trace_id="t1")

        unreliable = UnreliableTrace(
            trace=trace,
            reliability=ReliabilityAnnotation(confidence=0.8),
            interpretation="Agent performed action X",
        )

        ground_truth = [
            GroundTruth(
                trace_id="t1",
                verified_interpretation="Agent performed action Y",  # Different!
            )
        ]

        indicators = detector.detect([unreliable], ground_truth)

        assert any(i.type == HallucinationType.CONFABULATION for i in indicators)

    def test_no_issues_detected(self) -> None:
        """Should return empty for clean traces."""
        detector = HallucinationDetector()
        trace = make_trace()

        unreliable = UnreliableTrace(
            trace=trace,
            reliability=ReliabilityAnnotation(
                confidence=0.7,
                corroborated_by=["other"],  # Has corroboration
            ),
        )

        indicators = detector.detect([unreliable])

        # Should not flag overconfidence since confidence is moderate and corroborated
        overconfidence_indicators = [
            i for i in indicators if i.type == HallucinationType.OVERCONFIDENCE
        ]
        assert len(overconfidence_indicators) == 0


# =============================================================================
# UnreliableNarrative Tests
# =============================================================================


class TestUnreliableNarrative:
    """Tests for UnreliableNarrative."""

    def test_overall_confidence(self) -> None:
        """Should calculate overall confidence."""
        narrative = Narrative(
            text="Story",
            genre=NarrativeGenre.TECHNICAL,
            traces_used=[],
            chapters=[],
        )

        traces = [
            UnreliableTrace(
                trace=make_trace(trace_id="t1"),
                reliability=ReliabilityAnnotation(confidence=0.8),
            ),
            UnreliableTrace(
                trace=make_trace(trace_id="t2"),
                reliability=ReliabilityAnnotation(confidence=0.6),
            ),
        ]

        unreliable_narrative = UnreliableNarrative(
            narrative=narrative,
            annotated_traces=traces,
            hallucination_indicators=[],
        )

        # Average of 0.8 and 0.6
        assert unreliable_narrative.overall_confidence == pytest.approx(0.7)

    def test_confidence_level(self) -> None:
        """Should map to confidence level."""
        narrative = Narrative(
            text="Story",
            genre=NarrativeGenre.TECHNICAL,
            traces_used=[],
            chapters=[],
        )

        traces = [
            UnreliableTrace(
                trace=make_trace(),
                reliability=ReliabilityAnnotation(confidence=0.9),
            ),
        ]

        unreliable_narrative = UnreliableNarrative(
            narrative=narrative,
            annotated_traces=traces,
            hallucination_indicators=[],
        )

        assert unreliable_narrative.confidence_level == ConfidenceLevel.HIGH

    def test_has_hallucination_warnings(self) -> None:
        """Should detect hallucination warnings."""
        narrative = Narrative(
            text="Story",
            genre=NarrativeGenre.TECHNICAL,
            traces_used=[],
            chapters=[],
        )

        no_warnings = UnreliableNarrative(
            narrative=narrative,
            annotated_traces=[],
            hallucination_indicators=[],
        )

        with_warnings = UnreliableNarrative(
            narrative=narrative,
            annotated_traces=[],
            hallucination_indicators=[
                HallucinationIndicator(
                    type=HallucinationType.OVERCONFIDENCE,
                    description="Test",
                    affected_traces=[],
                    severity=0.5,
                )
            ],
        )

        assert not no_warnings.has_hallucination_warnings
        assert with_warnings.has_hallucination_warnings

    def test_contested_traces(self) -> None:
        """Should identify contested traces."""
        narrative = Narrative(
            text="Story",
            genre=NarrativeGenre.TECHNICAL,
            traces_used=[],
            chapters=[],
        )

        traces = [
            UnreliableTrace(
                trace=make_trace(trace_id="t1"),
                reliability=ReliabilityAnnotation(
                    confidence=0.8,
                    contradicted_by=["other"],  # Contested
                ),
            ),
            UnreliableTrace(
                trace=make_trace(trace_id="t2"),
                reliability=ReliabilityAnnotation(confidence=0.8),  # Not contested
            ),
        ]

        unreliable_narrative = UnreliableNarrative(
            narrative=narrative,
            annotated_traces=traces,
            hallucination_indicators=[],
        )

        contested = unreliable_narrative.contested_traces
        assert len(contested) == 1
        assert contested[0].trace_id == "t1"


# =============================================================================
# UnreliableNarrator Tests
# =============================================================================


class TestUnreliableNarrator:
    """Tests for UnreliableNarrator."""

    @pytest.mark.asyncio
    async def test_narrate_produces_unreliable_narrative(self) -> None:
        """Should produce UnreliableNarrative."""
        narrator = UnreliableNarrator(SimpleLLMProvider())
        traces = make_traces(3)
        request = NarrativeRequest(traces=traces)

        result = await narrator.narrate(request)

        assert isinstance(result, UnreliableNarrative)
        assert len(result.annotated_traces) == 3

    @pytest.mark.asyncio
    async def test_narrate_adds_confidence(self) -> None:
        """Should add confidence annotations."""
        narrator = UnreliableNarrator(SimpleLLMProvider(), base_confidence=0.7)
        traces = [make_trace()]
        request = NarrativeRequest(traces=traces)

        result = await narrator.narrate(request)

        # Each trace should have a confidence annotation
        for t in result.annotated_traces:
            assert t.reliability.confidence > 0

    @pytest.mark.asyncio
    async def test_narrate_with_ground_truth(self) -> None:
        """Should check against ground truth when provided."""
        narrator = UnreliableNarrator(SimpleLLMProvider())
        trace = make_trace(trace_id="t1")
        request = NarrativeRequest(traces=[trace])

        ground_truth = [
            GroundTruth(
                trace_id="t1",
                verified_interpretation="Ground truth says X",
            )
        ]

        result = await narrator.narrate(request, ground_truth)

        assert result.metadata["ground_truth_provided"] is True

    @pytest.mark.asyncio
    async def test_deterministic_traces_higher_confidence(self) -> None:
        """Deterministic traces should have higher confidence."""
        narrator = UnreliableNarrator(SimpleLLMProvider(), base_confidence=0.7)

        det_trace = make_trace(trace_id="t1", determinism=Determinism.DETERMINISTIC)
        chaotic_trace = make_trace(trace_id="t2", determinism=Determinism.CHAOTIC)

        request = NarrativeRequest(traces=[det_trace, chaotic_trace])
        result = await narrator.narrate(request)

        det_conf = next(
            t for t in result.annotated_traces if t.trace_id == "t1"
        ).reliability.confidence
        chaotic_conf = next(
            t for t in result.annotated_traces if t.trace_id == "t2"
        ).reliability.confidence

        assert det_conf > chaotic_conf


# =============================================================================
# PerspectiveSpec Tests
# =============================================================================


class TestPerspectiveSpec:
    """Tests for PerspectiveSpec."""

    def test_creation(self) -> None:
        """Should create perspective spec."""
        spec = PerspectiveSpec(
            narrator_id="tech",
            genre=NarrativeGenre.TECHNICAL,
            reliability=0.9,
        )

        assert spec.narrator_id == "tech"
        assert spec.genre == NarrativeGenre.TECHNICAL
        assert spec.reliability == 0.9

    def test_defaults(self) -> None:
        """Should have sensible defaults."""
        spec = PerspectiveSpec(
            narrator_id="test",
            genre=NarrativeGenre.MINIMAL,
        )

        assert spec.perspective == Perspective.THIRD_PERSON
        assert spec.reliability == 1.0
        assert spec.focus_agents is None


# =============================================================================
# Contradiction Tests
# =============================================================================


class TestContradiction:
    """Tests for Contradiction."""

    def test_creation(self) -> None:
        """Should create contradiction."""
        contradiction = Contradiction(
            trace_id="t1",
            perspectives={
                "tech": "Technical interpretation",
                "noir": "Noir interpretation",
            },
            severity=0.5,
        )

        assert contradiction.trace_id == "t1"
        assert len(contradiction.perspectives) == 2
        assert contradiction.severity == 0.5

    def test_narrator_ids(self) -> None:
        """Should list narrator IDs."""
        contradiction = Contradiction(
            trace_id="t1",
            perspectives={"a": "...", "b": "...", "c": "..."},
            severity=0.3,
        )

        assert set(contradiction.narrator_ids) == {"a", "b", "c"}

    def test_to_dict(self) -> None:
        """Should convert to dict."""
        contradiction = Contradiction(
            trace_id="t1",
            perspectives={"a": "interp"},
            severity=0.5,
        )

        d = contradiction.to_dict()
        assert d["trace_id"] == "t1"
        assert d["severity"] == 0.5


# =============================================================================
# RashomonNarrative Tests
# =============================================================================


class TestRashomonNarrative:
    """Tests for RashomonNarrative."""

    def _make_narrative(self, narrator_id: str, confidence: float) -> UnreliableNarrative:
        """Helper to create unreliable narrative."""
        narrative = Narrative(
            text=f"Story from {narrator_id}",
            genre=NarrativeGenre.TECHNICAL,
            traces_used=[],
            chapters=[],
        )
        traces = [
            UnreliableTrace(
                trace=make_trace(trace_id="t1"),
                reliability=ReliabilityAnnotation(confidence=confidence),
                interpretation=f"{narrator_id} interpretation",
            )
        ]
        return UnreliableNarrative(
            narrative=narrative,
            annotated_traces=traces,
            hallucination_indicators=[],
        )

    def test_weighted_confidence(self) -> None:
        """Should calculate weighted confidence."""
        perspectives = {
            "high": self._make_narrative("high", 0.9),
            "low": self._make_narrative("low", 0.5),
        }
        specs = {
            "high": PerspectiveSpec("high", NarrativeGenre.TECHNICAL, reliability=1.0),
            "low": PerspectiveSpec("low", NarrativeGenre.NOIR, reliability=0.5),
        }

        rashomon = RashomonNarrative(
            perspectives=perspectives,
            specs=specs,
            traces=[],
        )

        # Weighted: (0.9 * 1.0 + 0.5 * 0.5) / (1.0 + 0.5) = 1.15 / 1.5 = 0.767
        assert rashomon.weighted_confidence() == pytest.approx(0.767, rel=0.01)

    def test_consensus_similar_confidence(self) -> None:
        """Should find consensus traces."""
        trace = make_trace(trace_id="t1")

        perspectives = {
            "a": UnreliableNarrative(
                narrative=Narrative("", NarrativeGenre.TECHNICAL, [], []),
                annotated_traces=[
                    UnreliableTrace(
                        trace=trace,
                        reliability=ReliabilityAnnotation(confidence=0.8),
                    )
                ],
                hallucination_indicators=[],
            ),
            "b": UnreliableNarrative(
                narrative=Narrative("", NarrativeGenre.NOIR, [], []),
                annotated_traces=[
                    UnreliableTrace(
                        trace=trace,
                        reliability=ReliabilityAnnotation(confidence=0.75),  # Similar
                    )
                ],
                hallucination_indicators=[],
            ),
        }

        rashomon = RashomonNarrative(
            perspectives=perspectives,
            specs={},
            traces=[trace],
        )

        consensus = rashomon.consensus
        assert len(consensus) == 1

    def test_contradictions_different_confidence(self) -> None:
        """Should find contradictions when confidence differs significantly."""
        trace = make_trace(trace_id="t1")

        perspectives = {
            "a": UnreliableNarrative(
                narrative=Narrative("", NarrativeGenre.TECHNICAL, [], []),
                annotated_traces=[
                    UnreliableTrace(
                        trace=trace,
                        reliability=ReliabilityAnnotation(confidence=0.9),
                        interpretation="A says X",
                    )
                ],
                hallucination_indicators=[],
            ),
            "b": UnreliableNarrative(
                narrative=Narrative("", NarrativeGenre.NOIR, [], []),
                annotated_traces=[
                    UnreliableTrace(
                        trace=trace,
                        reliability=ReliabilityAnnotation(confidence=0.3),  # Very different
                        interpretation="B says Y",
                    )
                ],
                hallucination_indicators=[],
            ),
        }

        rashomon = RashomonNarrative(
            perspectives=perspectives,
            specs={},
            traces=[trace],
        )

        contradictions = rashomon.contradictions
        assert len(contradictions) == 1
        assert contradictions[0].severity > 0.3


# =============================================================================
# RashomonNarrator Tests
# =============================================================================


class TestRashomonNarrator:
    """Tests for RashomonNarrator."""

    @pytest.mark.asyncio
    async def test_narrate_produces_multiple_perspectives(self) -> None:
        """Should produce narratives from all perspectives."""
        specs = [
            PerspectiveSpec("tech", NarrativeGenre.TECHNICAL),
            PerspectiveSpec("noir", NarrativeGenre.NOIR),
        ]

        narrator = RashomonNarrator(SimpleLLMProvider(), specs)
        traces = make_traces(3)
        request = NarrativeRequest(traces=traces)

        result = await narrator.narrate(request)

        assert len(result.perspectives) == 2
        assert "tech" in result.perspectives
        assert "noir" in result.perspectives

    @pytest.mark.asyncio
    async def test_add_perspective(self) -> None:
        """Should add new perspective."""
        narrator = RashomonNarrator(SimpleLLMProvider())

        narrator.add_perspective(PerspectiveSpec("new", NarrativeGenre.MINIMAL))

        assert "new" in narrator.specs
        assert "new" in narrator.narrators

    @pytest.mark.asyncio
    async def test_each_perspective_uses_its_genre(self) -> None:
        """Each perspective should use its configured genre."""
        specs = [
            PerspectiveSpec("tech", NarrativeGenre.TECHNICAL),
            PerspectiveSpec("minimal", NarrativeGenre.MINIMAL),
        ]

        narrator = RashomonNarrator(SimpleLLMProvider(), specs)
        traces = make_traces(1)
        request = NarrativeRequest(traces=traces)

        result = await narrator.narrate(request)

        assert result.perspectives["tech"].narrative.genre == NarrativeGenre.TECHNICAL
        assert result.perspectives["minimal"].narrative.genre == NarrativeGenre.MINIMAL


# =============================================================================
# GroundTruth Tests
# =============================================================================


class TestGroundTruth:
    """Tests for GroundTruth."""

    def test_creation(self) -> None:
        """Should create ground truth."""
        gt = GroundTruth(
            trace_id="t1",
            verified_interpretation="The truth",
            source="human",
        )

        assert gt.trace_id == "t1"
        assert gt.verified_interpretation == "The truth"
        assert gt.confidence == 1.0

    def test_to_dict(self) -> None:
        """Should convert to dict."""
        gt = GroundTruth(
            trace_id="t1",
            verified_interpretation="Truth",
        )

        d = gt.to_dict()
        assert d["trace_id"] == "t1"
        assert "verified_at" in d


# =============================================================================
# GroundTruthReconciler Tests
# =============================================================================


class TestGroundTruthReconciler:
    """Tests for GroundTruthReconciler."""

    def test_reconcile_perfect_match(self) -> None:
        """Should identify matches."""
        reconciler = GroundTruthReconciler(
            [
                GroundTruth("t1", "Agent performed action"),
            ]
        )

        narrative = UnreliableNarrative(
            narrative=Narrative("", NarrativeGenre.TECHNICAL, [], []),
            annotated_traces=[
                UnreliableTrace(
                    trace=make_trace(trace_id="t1"),
                    reliability=ReliabilityAnnotation(confidence=0.8),
                    interpretation="Agent performed action",  # Matches
                )
            ],
            hallucination_indicators=[],
        )

        result = reconciler.reconcile(narrative)

        assert len(result.matches) == 1
        assert len(result.mismatches) == 0
        assert result.accuracy == 1.0

    def test_reconcile_mismatch(self) -> None:
        """Should identify mismatches."""
        reconciler = GroundTruthReconciler(
            [
                GroundTruth("t1", "The truth"),
            ]
        )

        narrative = UnreliableNarrative(
            narrative=Narrative("", NarrativeGenre.TECHNICAL, [], []),
            annotated_traces=[
                UnreliableTrace(
                    trace=make_trace(trace_id="t1"),
                    reliability=ReliabilityAnnotation(confidence=0.8),
                    interpretation="Something completely different",  # Doesn't match
                )
            ],
            hallucination_indicators=[],
        )

        result = reconciler.reconcile(narrative)

        assert len(result.matches) == 0
        assert len(result.mismatches) == 1
        assert result.accuracy == 0.0

    def test_reconcile_unverified(self) -> None:
        """Should track unverified traces."""
        reconciler = GroundTruthReconciler([])  # No ground truth

        narrative = UnreliableNarrative(
            narrative=Narrative("", NarrativeGenre.TECHNICAL, [], []),
            annotated_traces=[
                UnreliableTrace(
                    trace=make_trace(trace_id="t1"),
                    reliability=ReliabilityAnnotation(confidence=0.8),
                )
            ],
            hallucination_indicators=[],
        )

        result = reconciler.reconcile(narrative)

        assert len(result.unverified) == 1
        assert "t1" in result.unverified

    def test_add_ground_truth(self) -> None:
        """Should add ground truth dynamically."""
        reconciler = GroundTruthReconciler()
        reconciler.add_ground_truth(GroundTruth("t1", "Truth"))

        assert "t1" in reconciler.ground_truths

    def test_partial_match_similar(self) -> None:
        """Should match similar interpretations."""
        reconciler = GroundTruthReconciler(
            [
                GroundTruth("t1", "Agent performed action successfully"),
            ]
        )

        narrative = UnreliableNarrative(
            narrative=Narrative("", NarrativeGenre.TECHNICAL, [], []),
            annotated_traces=[
                UnreliableTrace(
                    trace=make_trace(trace_id="t1"),
                    reliability=ReliabilityAnnotation(confidence=0.8),
                    interpretation="Agent performed action",  # Subset
                )
            ],
            hallucination_indicators=[],
        )

        result = reconciler.reconcile(narrative)

        # Should match because one contains the other
        assert len(result.matches) == 1

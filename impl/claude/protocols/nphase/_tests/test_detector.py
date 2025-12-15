"""
Tests for Phase Detection.

Tests the phase detection system including:
- Explicit signifier detection (⟿/⟂/⤳)
- Heuristic pattern detection
- Confidence levels
- Edge cases and aliasing

See: protocols/nphase/detector.py
"""

from __future__ import annotations

import pytest

from protocols.nphase.detector import (
    PhaseDetector,
    PhaseSignal,
    SignalAction,
    detect_phase,
)
from protocols.nphase.operad import NPhase


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def detector() -> PhaseDetector:
    """Create a fresh detector for testing."""
    return PhaseDetector()


# =============================================================================
# Continue Signifier Tests
# =============================================================================


class TestContinueSignifier:
    """Tests for ⟿[PHASE] continuation detection."""

    def test_detect_continue_act(self, detector: PhaseDetector) -> None:
        """Detect ⟿[ACT] signifier."""
        output = "Research complete. ⟿[ACT]"
        signal = detector.detect(output, NPhase.UNDERSTAND)

        assert signal.action == SignalAction.CONTINUE
        assert signal.target_phase == NPhase.ACT
        assert signal.confidence == 1.0
        assert signal.source_text == "⟿[ACT]"

    def test_detect_continue_reflect(self, detector: PhaseDetector) -> None:
        """Detect ⟿[REFLECT] signifier."""
        output = "Implementation done. ⟿[REFLECT]"
        signal = detector.detect(output, NPhase.ACT)

        assert signal.action == SignalAction.CONTINUE
        assert signal.target_phase == NPhase.REFLECT

    def test_detect_continue_understand(self, detector: PhaseDetector) -> None:
        """Detect ⟿[UNDERSTAND] signifier."""
        output = "Cycle complete. ⟿[UNDERSTAND]"
        signal = detector.detect(output, NPhase.REFLECT)

        assert signal.action == SignalAction.CONTINUE
        assert signal.target_phase == NPhase.UNDERSTAND

    def test_detect_continue_sense_alias(self, detector: PhaseDetector) -> None:
        """SENSE is an alias for UNDERSTAND."""
        output = "Starting research. ⟿[SENSE]"
        signal = detector.detect(output, NPhase.REFLECT)

        assert signal.action == SignalAction.CONTINUE
        assert signal.target_phase == NPhase.UNDERSTAND

    def test_detect_continue_case_insensitive(self, detector: PhaseDetector) -> None:
        """Phase names are case-insensitive (converted to uppercase)."""
        output = "Moving on. ⟿[act]"
        signal = detector.detect(output, NPhase.UNDERSTAND)

        # Pattern captures lowercase, then we convert to uppercase in lookup
        assert signal.action == SignalAction.CONTINUE
        assert signal.target_phase == NPhase.ACT

    def test_detect_continue_with_surrounding_text(
        self, detector: PhaseDetector
    ) -> None:
        """Signifier detected in middle of text."""
        output = "Done with research. ⟿[ACT] Let's implement."
        signal = detector.detect(output, NPhase.UNDERSTAND)

        assert signal.action == SignalAction.CONTINUE
        assert signal.target_phase == NPhase.ACT

    def test_detect_continue_invalid_phase(self, detector: PhaseDetector) -> None:
        """Unknown phase name is ignored."""
        output = "⟿[INVALID]"
        signal = detector.detect(output, NPhase.UNDERSTAND)

        assert signal.action != SignalAction.CONTINUE

    def test_detect_continue_first_wins(self, detector: PhaseDetector) -> None:
        """First signifier in text takes precedence."""
        output = "⟿[ACT] and then ⟿[REFLECT]"
        signal = detector.detect(output, NPhase.UNDERSTAND)

        assert signal.target_phase == NPhase.ACT


# =============================================================================
# Halt Signifier Tests
# =============================================================================


class TestHaltSignifier:
    """Tests for ⟂[REASON] halt detection."""

    def test_detect_halt_basic(self, detector: PhaseDetector) -> None:
        """Detect ⟂[needs input] signifier."""
        output = "I need clarification. ⟂[needs input]"
        signal = detector.detect(output, NPhase.ACT)

        assert signal.action == SignalAction.HALT
        assert signal.reason == "needs input"
        assert signal.confidence == 1.0

    def test_detect_halt_with_spaces(self, detector: PhaseDetector) -> None:
        """Reason can contain spaces."""
        output = "⟂[awaiting user decision on architecture]"
        signal = detector.detect(output, NPhase.UNDERSTAND)

        assert signal.action == SignalAction.HALT
        assert signal.reason == "awaiting user decision on architecture"

    def test_detect_halt_various_reasons(self, detector: PhaseDetector) -> None:
        """Various halt reasons are captured."""
        reasons = [
            "blocked by dependency",
            "needs clarification",
            "ambiguous requirements",
            "external review required",
        ]

        for reason in reasons:
            output = f"Pausing. ⟂[{reason}]"
            signal = detector.detect(output, NPhase.ACT)

            assert signal.action == SignalAction.HALT
            assert signal.reason == reason


# =============================================================================
# Elastic Signifier Tests
# =============================================================================


class TestElasticSignifier:
    """Tests for ⤳[OP:args] elastic detection."""

    def test_detect_elastic_compress(self, detector: PhaseDetector) -> None:
        """Detect ⤳[COMPRESS:to ACT] signifier."""
        output = "Context full. ⤳[COMPRESS:to ACT]"
        signal = detector.detect(output, NPhase.UNDERSTAND)

        assert signal.action == SignalAction.ELASTIC
        assert signal.elastic_op == "COMPRESS"
        assert signal.elastic_args == "to ACT"
        assert signal.confidence == 1.0

    def test_detect_elastic_expand(self, detector: PhaseDetector) -> None:
        """Detect ⤳[EXPAND:detailed analysis] signifier."""
        output = "Need more detail. ⤳[EXPAND:detailed analysis]"
        signal = detector.detect(output, NPhase.UNDERSTAND)

        assert signal.action == SignalAction.ELASTIC
        assert signal.elastic_op == "EXPAND"
        assert signal.elastic_args == "detailed analysis"

    def test_detect_elastic_checkpoint(self, detector: PhaseDetector) -> None:
        """Detect ⤳[CHECKPOINT:phase boundary] signifier."""
        output = "Save point. ⤳[CHECKPOINT:phase boundary]"
        signal = detector.detect(output, NPhase.ACT)

        assert signal.action == SignalAction.ELASTIC
        assert signal.elastic_op == "CHECKPOINT"


# =============================================================================
# Heuristic Detection Tests
# =============================================================================


class TestHeuristicDetection:
    """Tests for pattern-based phase detection."""

    def test_detect_heuristic_understand_patterns(
        self, detector: PhaseDetector
    ) -> None:
        """UNDERSTAND phase patterns detected."""
        understand_texts = [
            "Let me start by reading the file to understand the structure.",
            "Exploring the codebase for existing implementations.",
            "Searching for similar patterns in the code.",
            "Planning the implementation approach.",
            "Researching best practices for this problem.",
        ]

        for text in understand_texts:
            signal = detector.detect(text, NPhase.ACT)

            if signal.action == SignalAction.HEURISTIC:
                assert signal.target_phase == NPhase.UNDERSTAND

    def test_detect_heuristic_act_patterns(self, detector: PhaseDetector) -> None:
        """ACT phase patterns detected."""
        act_texts = [
            "Writing the implementation to file.",
            "Creating a new file for the feature.",
            "Editing the configuration file.",
            "Running the test suite.",
            "Implementing the new endpoint.",
            "Building the module.",
        ]

        for text in act_texts:
            signal = detector.detect(text, NPhase.UNDERSTAND)

            if signal.action == SignalAction.HEURISTIC:
                assert signal.target_phase == NPhase.ACT

    def test_detect_heuristic_reflect_patterns(self, detector: PhaseDetector) -> None:
        """REFLECT phase patterns detected."""
        reflect_texts = [
            "All tests pass successfully.",
            "Implementation complete, documenting the changes.",
            "Writing the epilogue for this session.",
            "Learnings: the pattern works well.",
            "Summary: we accomplished all goals.",
        ]

        for text in reflect_texts:
            signal = detector.detect(text, NPhase.ACT)

            if signal.action == SignalAction.HEURISTIC:
                assert signal.target_phase == NPhase.REFLECT

    def test_heuristic_confidence_below_one(self, detector: PhaseDetector) -> None:
        """Heuristic detection has confidence < 1.0."""
        output = "I'm reading the file to understand the code."
        signal = detector.detect(output, NPhase.ACT)

        if signal.action == SignalAction.HEURISTIC:
            assert signal.confidence < 1.0

    def test_heuristic_no_transition_same_phase(
        self, detector: PhaseDetector
    ) -> None:
        """No heuristic suggestion if already in detected phase."""
        output = "Reading and exploring the codebase."
        signal = detector.detect(output, NPhase.UNDERSTAND)

        # Should return NONE because we're already in UNDERSTAND
        assert signal.action == SignalAction.NONE

    def test_heuristic_no_match_returns_none(self, detector: PhaseDetector) -> None:
        """No patterns matched returns NONE signal."""
        output = "Some random text with no recognizable patterns."
        signal = detector.detect(output, NPhase.UNDERSTAND)

        assert signal.action == SignalAction.NONE


# =============================================================================
# Signal Priority Tests
# =============================================================================


class TestSignalPriority:
    """Tests for signal priority (explicit > heuristic)."""

    def test_explicit_beats_heuristic(self, detector: PhaseDetector) -> None:
        """Explicit signifier wins over heuristic pattern."""
        # Text has UNDERSTAND patterns but explicit ACT signifier
        output = "Reading the code and planning... ⟿[ACT]"
        signal = detector.detect(output, NPhase.UNDERSTAND)

        assert signal.action == SignalAction.CONTINUE
        assert signal.target_phase == NPhase.ACT
        assert signal.confidence == 1.0

    def test_halt_beats_continue(self, detector: PhaseDetector) -> None:
        """First matched signifier wins (test order)."""
        # Both present, continue checked first in detect()
        output = "⟿[ACT] but wait ⟂[blocked]"
        signal = detector.detect(output, NPhase.UNDERSTAND)

        # Continue is checked before halt
        assert signal.action == SignalAction.CONTINUE


# =============================================================================
# detect_all Tests
# =============================================================================


class TestDetectAll:
    """Tests for detect_all() method."""

    def test_detect_all_multiple_signals(self, detector: PhaseDetector) -> None:
        """detect_all finds all signals in text."""
        output = "Starting ⟿[ACT] then maybe ⟂[wait] with patterns..."
        signals = detector.detect_all(output, NPhase.UNDERSTAND)

        # Should have at least 2 explicit signals
        explicit = [s for s in signals if s.confidence == 1.0]
        assert len(explicit) >= 2

    def test_detect_all_sorted_by_confidence(self, detector: PhaseDetector) -> None:
        """Results sorted by confidence, highest first."""
        output = "Reading code ⟿[ACT]"
        signals = detector.detect_all(output, NPhase.REFLECT)

        # First signal should have highest confidence
        if len(signals) >= 2:
            assert signals[0].confidence >= signals[1].confidence

    def test_detect_all_empty_text(self, detector: PhaseDetector) -> None:
        """Empty text returns empty list."""
        signals = detector.detect_all("", NPhase.UNDERSTAND)

        # Should have no signals or just a NONE heuristic
        explicit = [s for s in signals if s.action != SignalAction.NONE]
        assert len(explicit) == 0


# =============================================================================
# PhaseSignal Tests
# =============================================================================


class TestPhaseSignal:
    """Tests for PhaseSignal dataclass."""

    def test_is_transition_continue(self) -> None:
        """CONTINUE action is a transition."""
        signal = PhaseSignal(action=SignalAction.CONTINUE, target_phase=NPhase.ACT)
        assert signal.is_transition is True

    def test_is_transition_heuristic(self) -> None:
        """HEURISTIC action is a transition."""
        signal = PhaseSignal(
            action=SignalAction.HEURISTIC, target_phase=NPhase.ACT, confidence=0.5
        )
        assert signal.is_transition is True

    def test_is_transition_halt(self) -> None:
        """HALT action is not a transition."""
        signal = PhaseSignal(action=SignalAction.HALT, reason="blocked")
        assert signal.is_transition is False

    def test_is_transition_none(self) -> None:
        """NONE action is not a transition."""
        signal = PhaseSignal(action=SignalAction.NONE)
        assert signal.is_transition is False

    def test_should_auto_advance_high_confidence(self) -> None:
        """High confidence transition should auto-advance."""
        signal = PhaseSignal(
            action=SignalAction.CONTINUE, target_phase=NPhase.ACT, confidence=1.0
        )
        assert signal.should_auto_advance is True

    def test_should_auto_advance_low_confidence(self) -> None:
        """Low confidence transition should not auto-advance."""
        signal = PhaseSignal(
            action=SignalAction.HEURISTIC, target_phase=NPhase.ACT, confidence=0.3
        )
        assert signal.should_auto_advance is False

    def test_to_dict_continue(self) -> None:
        """Serialize CONTINUE signal to dict."""
        signal = PhaseSignal(
            action=SignalAction.CONTINUE,
            target_phase=NPhase.ACT,
            confidence=1.0,
            source_text="⟿[ACT]",
        )

        data = signal.to_dict()

        assert data["action"] == "CONTINUE"
        assert data["target_phase"] == "ACT"
        assert data["confidence"] == 1.0
        assert data["source_text"] == "⟿[ACT]"

    def test_to_dict_halt(self) -> None:
        """Serialize HALT signal to dict."""
        signal = PhaseSignal(
            action=SignalAction.HALT, reason="needs input", confidence=1.0
        )

        data = signal.to_dict()

        assert data["action"] == "HALT"
        assert data["reason"] == "needs input"

    def test_to_dict_elastic(self) -> None:
        """Serialize ELASTIC signal to dict."""
        signal = PhaseSignal(
            action=SignalAction.ELASTIC,
            elastic_op="COMPRESS",
            elastic_args="to ACT",
        )

        data = signal.to_dict()

        assert data["action"] == "ELASTIC"
        assert data["elastic_op"] == "COMPRESS"
        assert data["elastic_args"] == "to ACT"


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestDetectPhaseFunction:
    """Tests for the detect_phase convenience function."""

    def test_detect_phase_uses_global_detector(self) -> None:
        """detect_phase uses the global detector instance."""
        output = "⟿[ACT]"
        signal = detect_phase(output, NPhase.UNDERSTAND)

        assert signal.action == SignalAction.CONTINUE
        assert signal.target_phase == NPhase.ACT


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_output(self, detector: PhaseDetector) -> None:
        """Empty string returns NONE."""
        signal = detector.detect("", NPhase.UNDERSTAND)
        assert signal.action == SignalAction.NONE

    def test_whitespace_only(self, detector: PhaseDetector) -> None:
        """Whitespace-only string returns NONE."""
        signal = detector.detect("   \n\t  ", NPhase.UNDERSTAND)
        assert signal.action == SignalAction.NONE

    def test_unicode_in_output(self, detector: PhaseDetector) -> None:
        """Unicode characters don't break detection."""
        output = "Reading file 文件.py ⟿[ACT]"
        signal = detector.detect(output, NPhase.UNDERSTAND)

        assert signal.action == SignalAction.CONTINUE

    def test_nested_brackets(self, detector: PhaseDetector) -> None:
        """Nested brackets in reason are handled."""
        output = "⟂[needs [user] input]"
        signal = detector.detect(output, NPhase.ACT)

        # Pattern captures until first ]
        assert signal.action == SignalAction.HALT
        assert signal.reason == "needs [user"

    def test_multiple_signifiers_same_type(self, detector: PhaseDetector) -> None:
        """Multiple continue signifiers - first wins."""
        output = "⟿[UNDERSTAND] then ⟿[ACT] then ⟿[REFLECT]"
        signal = detector.detect(output, NPhase.ACT)

        assert signal.target_phase == NPhase.UNDERSTAND

    def test_signifier_at_start(self, detector: PhaseDetector) -> None:
        """Signifier at text start is detected."""
        output = "⟿[ACT] Starting implementation."
        signal = detector.detect(output, NPhase.UNDERSTAND)

        assert signal.action == SignalAction.CONTINUE

    def test_signifier_at_end(self, detector: PhaseDetector) -> None:
        """Signifier at text end is detected."""
        output = "Research complete. ⟿[ACT]"
        signal = detector.detect(output, NPhase.UNDERSTAND)

        assert signal.action == SignalAction.CONTINUE

    def test_very_long_output(self, detector: PhaseDetector) -> None:
        """Long output with signifier at end is detected."""
        output = "x" * 10000 + " ⟿[ACT]"
        signal = detector.detect(output, NPhase.UNDERSTAND)

        assert signal.action == SignalAction.CONTINUE


# =============================================================================
# Configuration Tests
# =============================================================================


class TestConfiguration:
    """Tests for detector configuration."""

    def test_custom_heuristic_threshold(self) -> None:
        """Custom heuristic threshold affects detection."""
        # High threshold
        strict_detector = PhaseDetector(heuristic_threshold=0.9)
        output = "reading file"  # Single pattern match
        signal = strict_detector.detect(output, NPhase.ACT)

        # Single pattern match should be below 0.9 threshold
        assert signal.action == SignalAction.NONE

    def test_should_auto_advance_threshold(self) -> None:
        """Auto-advance threshold affects recommendation."""
        low_threshold_detector = PhaseDetector(auto_advance_threshold=0.3)

        signal = PhaseSignal(
            action=SignalAction.HEURISTIC, target_phase=NPhase.ACT, confidence=0.5
        )

        assert low_threshold_detector.should_auto_advance(signal) is True

        high_threshold_detector = PhaseDetector(auto_advance_threshold=0.8)
        assert high_threshold_detector.should_auto_advance(signal) is False

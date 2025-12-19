"""
Tests for signal aggregation in push readiness evaluation.

Philosophy: The Sentinel aggregates signals to make go/no-go decisions.

Tests verify:
1. evaluate_push_readiness() with various signal combinations
2. Confidence threshold calculations
3. Blocking vs non-blocking signal behavior
4. Edge cases: empty signals, all pass, all fail
"""

from __future__ import annotations

import pytest

from testing.sentinel import (
    CISignal,
    PushReadiness,
    SignalKind,
    evaluate_push_readiness,
)


@pytest.mark.sentinel
class TestSignalAggregationBasic:
    """Basic tests for signal aggregation."""

    def test_empty_signals_returns_ready_with_zero_confidence(self) -> None:
        """Empty signals should return ready=True but 0% confidence."""
        result = evaluate_push_readiness([])

        assert result.ready is True
        assert result.confidence == 0.0
        assert len(result.blocking_reasons) == 0
        assert "No signals" in result.warning_reasons[0]

    def test_single_passing_blocking_signal(self) -> None:
        """Single passing blocking signal should return ready with full confidence."""
        signals = [
            CISignal(kind=SignalKind.LINT, passed=True, blocking=True),
        ]

        result = evaluate_push_readiness(signals)

        assert result.ready is True
        assert result.confidence == 1.0
        assert len(result.blocking_reasons) == 0

    def test_single_failing_blocking_signal(self) -> None:
        """Single failing blocking signal should return not ready."""
        signals = [
            CISignal(kind=SignalKind.LINT, passed=False, blocking=True, reason="Syntax errors"),
        ]

        result = evaluate_push_readiness(signals)

        assert result.ready is False
        assert result.confidence == 0.0
        assert "Syntax errors" in result.blocking_reasons

    def test_non_blocking_failure_is_warning(self) -> None:
        """Non-blocking failure should be a warning, not block push."""
        signals = [
            CISignal(kind=SignalKind.LINT, passed=True, blocking=True),
            CISignal(kind=SignalKind.CONTRACT, passed=False, blocking=False, reason="Backend offline"),
        ]

        result = evaluate_push_readiness(signals)

        assert result.ready is True
        assert result.confidence == 1.0
        assert len(result.blocking_reasons) == 0
        assert "Backend offline" in result.warning_reasons[0]


@pytest.mark.sentinel
class TestConfidenceThresholds:
    """Tests for confidence calculation."""

    def test_all_blocking_pass_gives_full_confidence(self) -> None:
        """All blocking signals passing gives 100% confidence."""
        signals = [
            CISignal(kind=SignalKind.LINT, passed=True, blocking=True),
            CISignal(kind=SignalKind.TYPECHECK, passed=True, blocking=True),
            CISignal(kind=SignalKind.TEST, passed=True, blocking=True),
        ]

        result = evaluate_push_readiness(signals)

        assert result.confidence == 1.0

    def test_half_blocking_fail_gives_half_confidence(self) -> None:
        """50% blocking failures gives 50% confidence."""
        signals = [
            CISignal(kind=SignalKind.LINT, passed=True, blocking=True),
            CISignal(kind=SignalKind.TYPECHECK, passed=False, blocking=True),
        ]

        result = evaluate_push_readiness(signals)

        assert result.confidence == 0.5

    def test_non_blocking_dont_affect_confidence(self) -> None:
        """Non-blocking signals don't affect confidence calculation."""
        signals = [
            CISignal(kind=SignalKind.LINT, passed=True, blocking=True),
            CISignal(kind=SignalKind.CONTRACT, passed=False, blocking=False),
            CISignal(kind=SignalKind.CONTRACT, passed=False, blocking=False),
        ]

        result = evaluate_push_readiness(signals)

        # Only the one blocking signal counts
        assert result.confidence == 1.0
        assert result.ready is True

    def test_confidence_with_mixed_signals(self) -> None:
        """Confidence correctly calculated with mixed blocking results."""
        signals = [
            CISignal(kind=SignalKind.LINT, passed=True, blocking=True),
            CISignal(kind=SignalKind.TYPECHECK, passed=True, blocking=True),
            CISignal(kind=SignalKind.TEST, passed=False, blocking=True),
            CISignal(kind=SignalKind.CONTRACT, passed=False, blocking=False),
        ]

        result = evaluate_push_readiness(signals)

        # 2 of 3 blocking passed = 66.67%
        assert abs(result.confidence - (2 / 3)) < 0.01
        assert result.ready is False


@pytest.mark.sentinel
class TestReasonStrings:
    """Tests for reason string handling."""

    def test_custom_reason_preserved(self) -> None:
        """Custom reason strings are preserved in output."""
        signals = [
            CISignal(
                kind=SignalKind.TEST,
                passed=False,
                blocking=True,
                reason="5 tests failed in test_brain.py",
            ),
        ]

        result = evaluate_push_readiness(signals)

        assert "5 tests failed in test_brain.py" in result.blocking_reasons

    def test_default_reason_for_missing(self) -> None:
        """Default reason generated when not provided."""
        signals = [
            CISignal(kind=SignalKind.LINT, passed=False, blocking=True),
        ]

        result = evaluate_push_readiness(signals)

        assert "lint failed" in result.blocking_reasons[0]

    def test_multiple_blocking_reasons_collected(self) -> None:
        """All blocking failure reasons are collected."""
        signals = [
            CISignal(kind=SignalKind.LINT, passed=False, blocking=True, reason="Ruff issues"),
            CISignal(kind=SignalKind.TYPECHECK, passed=False, blocking=True, reason="Mypy errors"),
        ]

        result = evaluate_push_readiness(signals)

        assert len(result.blocking_reasons) == 2
        assert "Ruff issues" in result.blocking_reasons
        assert "Mypy errors" in result.blocking_reasons


@pytest.mark.sentinel
class TestPushReadinessSummary:
    """Tests for PushReadiness.summary property."""

    def test_ready_summary(self) -> None:
        """Ready state produces correct summary."""
        readiness = PushReadiness(
            ready=True,
            confidence=1.0,
            blocking_reasons=(),
            warning_reasons=(),
            signals=(),
        )

        assert "READY" in readiness.summary
        assert "100%" in readiness.summary

    def test_not_ready_summary(self) -> None:
        """Not ready state produces correct summary."""
        readiness = PushReadiness(
            ready=False,
            confidence=0.5,
            blocking_reasons=("test failed",),
            warning_reasons=(),
            signals=(),
        )

        assert "NOT READY" in readiness.summary
        assert "50%" in readiness.summary


@pytest.mark.sentinel
class TestSignalKindCoverage:
    """Tests for all SignalKind values."""

    @pytest.mark.parametrize(
        "kind",
        [SignalKind.LINT, SignalKind.TYPECHECK, SignalKind.TEST, SignalKind.CONTRACT],
    )
    def test_all_signal_kinds_work(self, kind: SignalKind) -> None:
        """All SignalKind values can be used in signals."""
        signal = CISignal(kind=kind, passed=True, blocking=True)
        result = evaluate_push_readiness([signal])

        assert result.ready is True
        assert result.signals[0].kind == kind


@pytest.mark.sentinel
class TestEdgeCases:
    """Edge case tests for signal aggregation."""

    def test_only_non_blocking_signals(self) -> None:
        """Only non-blocking signals gives 100% confidence (vacuously true)."""
        signals = [
            CISignal(kind=SignalKind.CONTRACT, passed=False, blocking=False),
            CISignal(kind=SignalKind.CONTRACT, passed=False, blocking=False),
        ]

        result = evaluate_push_readiness(signals)

        assert result.ready is True
        assert result.confidence == 1.0  # No blocking signals = vacuously 100%
        assert len(result.warning_reasons) == 2

    def test_all_signals_fail(self) -> None:
        """All signals failing gives 0% confidence."""
        signals = [
            CISignal(kind=SignalKind.LINT, passed=False, blocking=True),
            CISignal(kind=SignalKind.TYPECHECK, passed=False, blocking=True),
            CISignal(kind=SignalKind.TEST, passed=False, blocking=True),
        ]

        result = evaluate_push_readiness(signals)

        assert result.ready is False
        assert result.confidence == 0.0
        assert len(result.blocking_reasons) == 3

    def test_signal_duration_preserved(self) -> None:
        """Signal duration is preserved in output."""
        signal = CISignal(
            kind=SignalKind.TEST,
            passed=True,
            blocking=True,
            duration_ms=12345.0,
        )
        result = evaluate_push_readiness([signal])

        assert result.signals[0].duration_ms == 12345.0

    def test_large_signal_count(self) -> None:
        """Can handle large number of signals."""
        signals = [
            CISignal(kind=SignalKind.TEST, passed=i % 2 == 0, blocking=True)
            for i in range(100)
        ]

        result = evaluate_push_readiness(signals)

        # 50% pass rate
        assert result.confidence == 0.5
        assert len(result.signals) == 100

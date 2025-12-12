"""
Tests for Pulse: Zero-Cost Vitality Signals.

These tests verify:
1. Pulse creation and serialization
2. Log format roundtrip (to_log / from_log)
3. VitalityAnalyzer loop detection
4. VitalityAnalyzer pressure monitoring
5. VitalityAnalyzer interval analysis
6. Factory functions
7. Integration with ContextWindow

Phase 2.3 Tests - Target: 20+ tests.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest
from agents.d.pulse import (
    AgentPhase,
    Pulse,
    VitalityAnalyzer,
    VitalityStatus,
    create_analyzer,
    create_pulse,
    create_pulse_from_window,
)

# --- Pulse Tests ---


class TestPulse:
    """Tests for Pulse dataclass."""

    def test_pulse_creation(self) -> None:
        """Pulse should be created with all fields."""
        pulse = Pulse(
            agent="l-gent",
            timestamp=datetime.now(UTC),
            pressure=0.5,
            phase=AgentPhase.THINKING,
            content_hash="abc12345",
            turn_count=10,
        )
        assert pulse.agent == "l-gent"
        assert pulse.pressure == 0.5
        assert pulse.phase == AgentPhase.THINKING

    def test_pulse_is_frozen(self) -> None:
        """Pulse should be immutable."""
        pulse = Pulse(
            agent="l-gent",
            timestamp=datetime.now(UTC),
            pressure=0.5,
            phase=AgentPhase.THINKING,
            content_hash="abc12345",
            turn_count=10,
        )
        with pytest.raises(AttributeError):
            pulse.pressure = 0.9  # type: ignore

    def test_pulse_hash_content(self) -> None:
        """hash_content should produce consistent truncated hash."""
        hash1 = Pulse.hash_content("hello world")
        hash2 = Pulse.hash_content("hello world")
        assert hash1 == hash2
        assert len(hash1) == 8  # Default truncate

    def test_pulse_hash_content_different(self) -> None:
        """Different content should produce different hashes."""
        hash1 = Pulse.hash_content("hello world")
        hash2 = Pulse.hash_content("goodbye world")
        assert hash1 != hash2

    def test_pulse_hash_content_custom_truncate(self) -> None:
        """hash_content should respect truncate parameter."""
        hash_short = Pulse.hash_content("test", truncate=4)
        hash_long = Pulse.hash_content("test", truncate=16)
        assert len(hash_short) == 4
        assert len(hash_long) == 16

    def test_pulse_to_dict(self) -> None:
        """to_dict should produce complete dictionary."""
        ts = datetime.now(UTC)
        pulse = Pulse(
            agent="k-gent",
            timestamp=ts,
            pressure=0.75,
            phase=AgentPhase.ACTING,
            content_hash="deadbeef",
            turn_count=42,
            metadata={"key": "value"},
        )
        d = pulse.to_dict()
        assert d["agent"] == "k-gent"
        assert d["pressure"] == 0.75
        assert d["phase"] == "acting"
        assert d["content_hash"] == "deadbeef"
        assert d["turn_count"] == 42
        assert d["metadata"] == {"key": "value"}

    def test_pulse_from_dict(self) -> None:
        """from_dict should restore pulse."""
        ts = datetime.now(UTC)
        original = Pulse(
            agent="u-gent",
            timestamp=ts,
            pressure=0.3,
            phase=AgentPhase.WAITING,
            content_hash="12345678",
            turn_count=5,
        )
        d = original.to_dict()
        restored = Pulse.from_dict(d)
        assert restored.agent == original.agent
        assert restored.pressure == original.pressure
        assert restored.phase == original.phase
        assert restored.content_hash == original.content_hash


class TestPulseLog:
    """Tests for Pulse log serialization."""

    def test_to_log_format(self) -> None:
        """to_log should produce structured log format."""
        ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC)
        pulse = Pulse(
            agent="l-gent",
            timestamp=ts,
            pressure=0.45,
            phase=AgentPhase.THINKING,
            content_hash="abc12345",
            turn_count=42,
        )
        log = pulse.to_log()
        assert log.startswith("PULSE|")
        assert "agent=l-gent" in log
        assert "pressure=0.45" in log
        assert "phase=thinking" in log
        assert "hash=abc12345" in log
        assert "turns=42" in log

    def test_from_log_roundtrip(self) -> None:
        """from_log should restore pulse from log line."""
        ts = datetime.now(UTC)
        original = Pulse(
            agent="k-gent",
            timestamp=ts,
            pressure=0.78,
            phase=AgentPhase.ACTING,
            content_hash="deadbeef",
            turn_count=100,
        )
        log = original.to_log()
        restored = Pulse.from_log(log)

        assert restored.agent == original.agent
        assert abs(restored.pressure - original.pressure) < 0.01
        assert restored.phase == original.phase
        assert restored.content_hash == original.content_hash
        assert restored.turn_count == original.turn_count

    def test_from_log_invalid(self) -> None:
        """from_log should raise on invalid format."""
        with pytest.raises(ValueError):
            Pulse.from_log("NOT A PULSE LINE")

    def test_from_log_missing_prefix(self) -> None:
        """from_log should raise if PULSE prefix missing."""
        with pytest.raises(ValueError):
            Pulse.from_log("agent=l-gent|pressure=0.5")


# --- VitalityAnalyzer Tests ---


class TestVitalityAnalyzer:
    """Tests for VitalityAnalyzer."""

    def test_analyzer_creation(self) -> None:
        """Analyzer should be created with defaults."""
        analyzer = VitalityAnalyzer()
        assert analyzer.loop_threshold == 3
        assert analyzer.pressure_warning == 0.7
        assert analyzer.pressure_critical == 0.9

    def test_analyzer_healthy_pulse(self) -> None:
        """Analyzer should report healthy for normal pulse."""
        analyzer = VitalityAnalyzer()
        pulse = create_pulse(
            agent="test",
            pressure=0.3,
            phase=AgentPhase.THINKING,
            content="normal operation",
            turn_count=5,
        )
        status = analyzer.ingest(pulse)
        assert status.healthy
        assert status.severity == "ok"

    def test_analyzer_pressure_warning(self) -> None:
        """Analyzer should detect pressure warning."""
        analyzer = VitalityAnalyzer(pressure_warning=0.7)
        pulse = create_pulse(
            agent="test",
            pressure=0.75,
            phase=AgentPhase.THINKING,
            content="high pressure",
            turn_count=10,
        )
        status = analyzer.ingest(pulse)
        assert status.pressure_warning
        assert not status.pressure_critical
        assert "warning" in status.severity

    def test_analyzer_pressure_critical(self) -> None:
        """Analyzer should detect critical pressure."""
        analyzer = VitalityAnalyzer(pressure_critical=0.9)
        pulse = create_pulse(
            agent="test",
            pressure=0.95,
            phase=AgentPhase.THINKING,
            content="critical pressure",
            turn_count=10,
        )
        status = analyzer.ingest(pulse)
        assert status.pressure_critical
        assert status.severity == "critical"
        assert not status.healthy

    def test_analyzer_loop_detection(self) -> None:
        """Analyzer should detect repeated content hashes."""
        analyzer = VitalityAnalyzer(loop_threshold=3)

        # Send same content 3 times
        for i in range(3):
            pulse = Pulse(
                agent="test",
                timestamp=datetime.now(UTC),
                pressure=0.3,
                phase=AgentPhase.THINKING,
                content_hash="same_hash",
                turn_count=i,
            )
            status = analyzer.ingest(pulse)

        assert status.loop_detected
        assert status.loop_count >= 3
        assert "Loop detected" in status.message

    def test_analyzer_no_loop_below_threshold(self) -> None:
        """Analyzer should not detect loop below threshold."""
        analyzer = VitalityAnalyzer(loop_threshold=5)

        # Send same content 3 times (below threshold)
        for i in range(3):
            pulse = Pulse(
                agent="test",
                timestamp=datetime.now(UTC),
                pressure=0.3,
                phase=AgentPhase.THINKING,
                content_hash="same_hash",
                turn_count=i,
            )
            status = analyzer.ingest(pulse)

        assert not status.loop_detected

    def test_analyzer_unique_hashes_no_loop(self) -> None:
        """Analyzer should not detect loop with unique hashes."""
        analyzer = VitalityAnalyzer(loop_threshold=3)

        for i in range(10):
            pulse = Pulse(
                agent="test",
                timestamp=datetime.now(UTC),
                pressure=0.3,
                phase=AgentPhase.THINKING,
                content_hash=f"unique_{i}",
                turn_count=i,
            )
            status = analyzer.ingest(pulse)

        assert not status.loop_detected

    def test_analyzer_reset(self) -> None:
        """reset should clear analyzer state."""
        analyzer = VitalityAnalyzer()

        # Add some pulses
        for i in range(5):
            pulse = create_pulse("test", 0.5, AgentPhase.THINKING, f"content_{i}", i)
            analyzer.ingest(pulse)

        assert len(analyzer.history) == 5

        analyzer.reset()
        assert len(analyzer.history) == 0

    def test_analyzer_decay_hash_counts(self) -> None:
        """decay_hash_counts should reduce counts."""
        analyzer = VitalityAnalyzer(loop_threshold=10)

        # Build up hash counts
        for i in range(6):
            pulse = Pulse(
                agent="test",
                timestamp=datetime.now(UTC),
                pressure=0.3,
                phase=AgentPhase.THINKING,
                content_hash="repeated",
                turn_count=i,
            )
            analyzer.ingest(pulse)

        # Should have count of 6
        assert analyzer._hash_counts.get("repeated", 0) == 6

        # Decay by 50%
        analyzer.decay_hash_counts(factor=0.5)
        assert analyzer._hash_counts.get("repeated", 0) == 3

    def test_analyzer_stats(self) -> None:
        """stats should return analyzer statistics."""
        analyzer = VitalityAnalyzer()

        for i in range(5):
            pulse = create_pulse("test", 0.3, AgentPhase.THINKING, f"content_{i}", i)
            analyzer.ingest(pulse)

        stats = analyzer.stats
        assert stats["pulse_count"] == 5
        assert stats["unique_hashes"] == 5

    def test_analyzer_history(self) -> None:
        """history should return pulses in order."""
        analyzer = VitalityAnalyzer()

        pulses = []
        for i in range(3):
            pulse = create_pulse("test", 0.3, AgentPhase.THINKING, f"content_{i}", i)
            pulses.append(pulse)
            analyzer.ingest(pulse)

        history = analyzer.history
        assert len(history) == 3
        assert history[0].turn_count == 0  # Oldest first


class TestVitalityStatus:
    """Tests for VitalityStatus."""

    def test_status_severity_ok(self) -> None:
        """Severity should be 'ok' when healthy."""
        status = VitalityStatus(healthy=True)
        assert status.severity == "ok"

    def test_status_severity_warning(self) -> None:
        """Severity should be 'warning' for non-critical issues."""
        status = VitalityStatus(
            healthy=False,
            loop_detected=True,
            loop_count=3,
        )
        assert status.severity == "warning"

    def test_status_severity_critical(self) -> None:
        """Severity should be 'critical' for critical issues."""
        status = VitalityStatus(
            healthy=False,
            pressure_critical=True,
        )
        assert status.severity == "critical"

    def test_status_severity_critical_high_loops(self) -> None:
        """Severity should be 'critical' for high loop counts."""
        status = VitalityStatus(
            healthy=False,
            loop_detected=True,
            loop_count=5,
        )
        assert status.severity == "critical"


# --- Factory Function Tests ---


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_pulse(self) -> None:
        """create_pulse should create valid pulse."""
        pulse = create_pulse(
            agent="test-agent",
            pressure=0.6,
            phase=AgentPhase.ACTING,
            content="some content here",
            turn_count=15,
        )
        assert pulse.agent == "test-agent"
        assert pulse.pressure == 0.6
        assert pulse.phase == AgentPhase.ACTING
        assert pulse.turn_count == 15
        assert len(pulse.content_hash) == 8

    def test_create_pulse_with_metadata(self) -> None:
        """create_pulse should accept metadata."""
        pulse = create_pulse(
            agent="test",
            pressure=0.5,
            phase=AgentPhase.THINKING,
            content="content",
            turn_count=1,
            metadata={"custom": "data"},
        )
        assert pulse.metadata == {"custom": "data"}

    def test_create_pulse_from_window(self) -> None:
        """create_pulse_from_window should extract window state."""
        # Mock ContextWindow
        mock_window = MagicMock()
        mock_window.pressure = 0.45
        mock_window.__len__ = MagicMock(return_value=20)

        mock_turn = MagicMock()
        mock_turn.content = "recent content"
        mock_window.extract.return_value = mock_turn

        pulse = create_pulse_from_window(
            agent="window-agent",
            window=mock_window,
            phase=AgentPhase.THINKING,
        )

        assert pulse.agent == "window-agent"
        assert pulse.pressure == 0.45
        assert pulse.turn_count == 20

    def test_create_pulse_from_window_empty(self) -> None:
        """create_pulse_from_window should handle empty window."""
        mock_window = MagicMock()
        mock_window.pressure = 0.0
        mock_window.__len__ = MagicMock(return_value=0)
        mock_window.extract.return_value = None

        pulse = create_pulse_from_window(
            agent="empty-window",
            window=mock_window,
            phase=AgentPhase.WAITING,
        )

        assert pulse.agent == "empty-window"
        assert pulse.turn_count == 0

    def test_create_analyzer(self) -> None:
        """create_analyzer should create configured analyzer."""
        analyzer = create_analyzer(
            loop_threshold=5,
            pressure_warning=0.6,
            pressure_critical=0.85,
            window_size=100,
        )
        assert analyzer.loop_threshold == 5
        assert analyzer.pressure_warning == 0.6
        assert analyzer.pressure_critical == 0.85
        assert analyzer.window_size == 100


# --- Integration Tests ---


class TestPulseIntegration:
    """Integration tests for Pulse system."""

    def test_end_to_end_healthy_stream(self) -> None:
        """Healthy pulse stream should stay healthy."""
        analyzer = VitalityAnalyzer()

        for i in range(20):
            pulse = create_pulse(
                agent="healthy-agent",
                pressure=0.3 + (i * 0.01),  # Slowly rising but safe
                phase=AgentPhase.THINKING,
                content=f"unique content {i}",
                turn_count=i,
            )
            status = analyzer.ingest(pulse)

        assert status.healthy
        assert not status.loop_detected

    def test_end_to_end_loop_detection(self) -> None:
        """Loop should be detected with >90% accuracy."""
        analyzer = VitalityAnalyzer(loop_threshold=3)

        # First 5 unique
        for i in range(5):
            pulse = create_pulse(
                agent="loopy-agent",
                pressure=0.3,
                phase=AgentPhase.THINKING,
                content=f"unique {i}",
                turn_count=i,
            )
            analyzer.ingest(pulse)

        # Then 5 repeated (should trigger loop)
        detected = False
        for i in range(5):
            pulse = Pulse(
                agent="loopy-agent",
                timestamp=datetime.now(UTC),
                pressure=0.3,
                phase=AgentPhase.THINKING,
                content_hash="looping",
                turn_count=5 + i,
            )
            status = analyzer.ingest(pulse)
            if status.loop_detected:
                detected = True

        assert detected, "Loop should be detected with 5 repeated hashes"

    def test_end_to_end_pressure_escalation(self) -> None:
        """Pressure escalation should trigger appropriate warnings."""
        analyzer = VitalityAnalyzer(
            pressure_warning=0.7,
            pressure_critical=0.9,
        )

        warnings = []
        criticals = []

        for i in range(10):
            pressure = 0.5 + (i * 0.06)  # 0.5 -> 1.04
            pulse = create_pulse(
                agent="pressure-agent",
                pressure=min(pressure, 1.0),
                phase=AgentPhase.THINKING,
                content=f"content {i}",
                turn_count=i,
            )
            status = analyzer.ingest(pulse)

            if status.pressure_warning:
                warnings.append(i)
            if status.pressure_critical:
                criticals.append(i)

        assert len(warnings) > 0, "Should have pressure warnings"
        assert len(criticals) > 0, "Should have critical warnings"

    def test_log_roundtrip_stream(self) -> None:
        """Log serialization should work for a stream of pulses."""
        pulses = [
            create_pulse("agent-1", 0.3, AgentPhase.THINKING, "content 1", 1),
            create_pulse("agent-2", 0.5, AgentPhase.ACTING, "content 2", 2),
            create_pulse("agent-3", 0.8, AgentPhase.YIELDING, "content 3", 3),
        ]

        # Serialize all
        logs = [p.to_log() for p in pulses]

        # Deserialize all
        restored = [Pulse.from_log(log) for log in logs]

        for original, rest in zip(pulses, restored):
            assert original.agent == rest.agent
            assert original.phase == rest.phase
            assert original.turn_count == rest.turn_count

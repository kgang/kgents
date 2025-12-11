"""
Tests for N-gent Phase 3: EchoChamber and LucidDreamer.

Tests:
- EchoMode: STRICT vs LUCID modes
- Echo: Simulation of past traces
- EchoChamber: Navigation and replay
- LucidDreamer: Counterfactuals and drift detection
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from ..echo_chamber import (
    CounterfactualResult,
    DriftReport,
    Echo,
    EchoChamber,
    EchoMode,
    LucidDreamer,
    SimpleDriftMeasurer,
    quick_drift_check,
)
from ..types import Determinism, SemanticTrace

# =============================================================================
# Fixtures
# =============================================================================


def make_trace(
    trace_id: str = "trace-1",
    agent_id: str = "TestAgent",
    action: str = "INVOKE",
    determinism: Determinism = Determinism.PROBABILISTIC,
    inputs: dict[str, Any] | None = None,
    outputs: dict[str, Any] | None = None,
    timestamp: datetime | None = None,
) -> SemanticTrace:
    """Create a test trace."""
    return SemanticTrace(
        trace_id=trace_id,
        parent_id=None,
        timestamp=timestamp or datetime.now(timezone.utc),
        agent_id=agent_id,
        agent_genus="T",
        action=action,
        inputs=inputs or {"prompt": "test"},
        outputs=outputs or {"result": "success"},
        input_hash="abc123",
        input_snapshot=b'{"prompt": "test"}',
        output_hash="def456",
        gas_consumed=100,
        duration_ms=50,
        determinism=determinism,
    )


def make_trace_sequence(count: int = 5) -> list[SemanticTrace]:
    """Create a sequence of traces."""
    base_time = datetime.now(timezone.utc)
    traces = []
    for i in range(count):
        traces.append(
            make_trace(
                trace_id=f"trace-{i}",
                agent_id=f"Agent{i % 2}",
                timestamp=base_time + timedelta(seconds=i),
            )
        )
    return traces


# =============================================================================
# EchoMode Tests
# =============================================================================


class TestEchoMode:
    """Tests for EchoMode enum."""

    def test_strict_mode_value(self):
        """Test STRICT mode value."""
        assert EchoMode.STRICT.value == "strict"

    def test_lucid_mode_value(self):
        """Test LUCID mode value."""
        assert EchoMode.LUCID.value == "lucid"


# =============================================================================
# Echo Tests
# =============================================================================


class TestEcho:
    """Tests for Echo dataclass."""

    def test_echo_creation(self):
        """Test creating an echo."""
        trace = make_trace()
        echo = Echo(
            original_trace=trace,
            echo_output={"result": "echoed"},
            mode=EchoMode.STRICT,
            drift=0.0,
        )

        assert echo.trace_id == trace.trace_id
        assert echo.echo_output == {"result": "echoed"}
        assert echo.mode == EchoMode.STRICT
        assert echo.drift == 0.0

    def test_echo_is_identical_true(self):
        """Test is_identical when outputs match."""
        trace = make_trace(outputs={"result": "success"})
        echo = Echo(
            original_trace=trace,
            echo_output={"result": "success"},
            mode=EchoMode.STRICT,
        )

        assert echo.is_identical is True

    def test_echo_is_identical_false(self):
        """Test is_identical when outputs differ."""
        trace = make_trace(outputs={"result": "success"})
        echo = Echo(
            original_trace=trace,
            echo_output={"result": "different"},
            mode=EchoMode.LUCID,
            drift=0.5,
        )

        assert echo.is_identical is False

    def test_echo_drifted_low(self):
        """Test drifted property with low drift."""
        trace = make_trace()
        echo = Echo(
            original_trace=trace,
            echo_output={},
            mode=EchoMode.LUCID,
            drift=0.05,
        )

        assert echo.drifted is False

    def test_echo_drifted_high(self):
        """Test drifted property with high drift."""
        trace = make_trace()
        echo = Echo(
            original_trace=trace,
            echo_output={},
            mode=EchoMode.LUCID,
            drift=0.5,
        )

        assert echo.drifted is True

    def test_echo_to_dict(self):
        """Test echo serialization."""
        trace = make_trace()
        echo = Echo(
            original_trace=trace,
            echo_output={"result": "echoed"},
            mode=EchoMode.STRICT,
            drift=0.1,
        )

        data = echo.to_dict()
        assert data["original_trace_id"] == trace.trace_id
        assert data["echo_output"] == {"result": "echoed"}
        assert data["mode"] == "strict"
        assert data["drift"] == 0.1


# =============================================================================
# EchoChamber Tests
# =============================================================================


class TestEchoChamber:
    """Tests for EchoChamber replay engine."""

    def test_chamber_creation(self):
        """Test creating an echo chamber."""
        traces = make_trace_sequence(5)
        chamber = EchoChamber(traces)

        assert len(chamber.traces) == 5
        assert chamber.position == 0
        assert chamber.echoes == []

    def test_chamber_current_trace(self):
        """Test getting current trace."""
        traces = make_trace_sequence(3)
        chamber = EchoChamber(traces)

        assert chamber.current_trace == traces[0]

    def test_chamber_step_forward(self):
        """Test stepping forward."""
        traces = make_trace_sequence(3)
        chamber = EchoChamber(traces)

        trace1 = chamber.step_forward()
        assert trace1 == traces[0]
        assert chamber.position == 1

        trace2 = chamber.step_forward()
        assert trace2 == traces[1]
        assert chamber.position == 2

    def test_chamber_step_backward(self):
        """Test stepping backward."""
        traces = make_trace_sequence(3)
        chamber = EchoChamber(traces)
        chamber.position = 2

        trace = chamber.step_backward()
        assert trace == traces[1]
        assert chamber.position == 1

    def test_chamber_step_backward_at_start(self):
        """Test stepping backward at start stays at 0."""
        traces = make_trace_sequence(3)
        chamber = EchoChamber(traces)

        trace = chamber.step_backward()
        assert trace == traces[0]
        assert chamber.position == 0

    def test_chamber_at_start(self):
        """Test at_start property."""
        traces = make_trace_sequence(3)
        chamber = EchoChamber(traces)

        assert chamber.at_start is True
        chamber.step_forward()
        assert chamber.at_start is False

    def test_chamber_at_end(self):
        """Test at_end property."""
        traces = make_trace_sequence(3)
        chamber = EchoChamber(traces)

        assert chamber.at_end is False
        chamber.position = 2
        assert chamber.at_end is True

    def test_chamber_progress(self):
        """Test progress property."""
        traces = make_trace_sequence(5)
        chamber = EchoChamber(traces)

        assert chamber.progress == 0.0
        chamber.position = 2
        assert chamber.progress == 0.4
        chamber.position = 5
        assert chamber.progress == 1.0

    def test_chamber_seek(self):
        """Test seek to position."""
        traces = make_trace_sequence(5)
        chamber = EchoChamber(traces)

        trace = chamber.seek(3)
        assert chamber.position == 3
        assert trace == traces[3]

    def test_chamber_seek_to_trace(self):
        """Test seek to specific trace by ID."""
        traces = make_trace_sequence(5)
        chamber = EchoChamber(traces)

        trace = chamber.seek_to_trace("trace-3")
        assert trace is not None
        assert trace.trace_id == "trace-3"
        assert chamber.position == 3

    def test_chamber_seek_to_trace_not_found(self):
        """Test seek to non-existent trace."""
        traces = make_trace_sequence(5)
        chamber = EchoChamber(traces)

        trace = chamber.seek_to_trace("nonexistent")
        assert trace is None
        assert chamber.position == 0  # Unchanged

    def test_chamber_reset(self):
        """Test reset."""
        traces = make_trace_sequence(5)
        chamber = EchoChamber(traces)
        chamber.position = 3
        chamber.echoes = [Echo(traces[0], {}, EchoMode.STRICT)]

        chamber.reset()
        assert chamber.position == 0
        assert chamber.echoes == []

    @pytest.mark.asyncio
    async def test_chamber_echo_strict(self):
        """Test strict echo returns stored output."""
        trace = make_trace(outputs={"result": "original"})
        chamber = EchoChamber([trace])

        echo = await chamber.echo_from(trace, EchoMode.STRICT)

        assert echo.mode == EchoMode.STRICT
        assert echo.echo_output == {"result": "original"}
        assert echo.drift == 0.0

    @pytest.mark.asyncio
    async def test_chamber_echo_lucid_deterministic(self):
        """Test lucid echo with deterministic trace."""
        trace = make_trace(
            determinism=Determinism.DETERMINISTIC,
            outputs={"result": "computed"},
        )
        chamber = EchoChamber([trace])

        echo = await chamber.echo_from(trace, EchoMode.LUCID)

        assert echo.mode == EchoMode.LUCID
        assert echo.drift == 0.0  # Deterministic = no drift

    @pytest.mark.asyncio
    async def test_chamber_echo_lucid_chaotic(self):
        """Test lucid echo with chaotic trace falls back to strict."""
        trace = make_trace(
            determinism=Determinism.CHAOTIC,
            outputs={"result": "external_api"},
        )
        chamber = EchoChamber([trace])

        echo = await chamber.echo_from(trace, EchoMode.LUCID)

        # Should fall back to STRICT for chaotic traces
        assert echo.mode == EchoMode.STRICT
        assert echo.drift is None

    @pytest.mark.asyncio
    async def test_chamber_replay_all(self):
        """Test replaying all traces."""
        traces = make_trace_sequence(3)
        chamber = EchoChamber(traces)

        echoes = await chamber.replay_all(EchoMode.STRICT)

        assert len(echoes) == 3
        assert all(e.mode == EchoMode.STRICT for e in echoes)


# =============================================================================
# SimpleDriftMeasurer Tests
# =============================================================================


class TestSimpleDriftMeasurer:
    """Tests for SimpleDriftMeasurer."""

    def test_identical_outputs(self):
        """Test drift is 0 for identical outputs."""
        measurer = SimpleDriftMeasurer()
        drift = measurer.measure({"a": 1}, {"a": 1})
        assert drift == 0.0

    def test_different_outputs(self):
        """Test drift is non-zero for different outputs."""
        measurer = SimpleDriftMeasurer()
        drift = measurer.measure({"a": 1}, {"b": 2})
        assert drift > 0.0

    def test_completely_different(self):
        """Test high drift for very different outputs."""
        measurer = SimpleDriftMeasurer()
        drift = measurer.measure(
            {"key1": "value1"},
            {"completely_different_key": "completely_different_value"},
        )
        assert drift > 0.5


# =============================================================================
# LucidDreamer Tests
# =============================================================================


class TestLucidDreamer:
    """Tests for LucidDreamer counterfactual exploration."""

    def test_dreamer_creation(self):
        """Test creating a lucid dreamer."""
        dreamer = LucidDreamer()
        assert dreamer.agent_registry is None
        assert dreamer.drift_measurer is not None

    @pytest.mark.asyncio
    async def test_dream_variant(self):
        """Test dreaming a variant."""
        trace = make_trace(
            inputs={"prompt": "original"},
            outputs={"result": "original_output"},
        )
        dreamer = LucidDreamer()

        result = await dreamer.dream_variant(
            trace,
            modified_input={"prompt": "modified"},
        )

        assert isinstance(result, CounterfactualResult)
        assert result.modified_input == {"prompt": "modified"}
        assert result.original_echo is not None
        assert result.variant_echo is not None

    @pytest.mark.asyncio
    async def test_detect_drift_over_time(self):
        """Test drift detection over time."""
        traces = make_trace_sequence(10)
        dreamer = LucidDreamer()

        reports = await dreamer.detect_drift_over_time(
            traces,
            interval=2,
            threshold=0.0,  # Report all
        )

        # Should sample every 2nd trace
        assert len(reports) <= 5

    @pytest.mark.asyncio
    async def test_sensitivity_analysis(self):
        """Test sensitivity analysis with multiple variations."""
        trace = make_trace()
        dreamer = LucidDreamer()

        variations = [
            {"prompt": "variation1"},
            {"prompt": "variation2"},
            {"prompt": "variation3"},
        ]

        results = await dreamer.sensitivity_analysis(trace, variations)

        assert len(results) == 3
        assert all(isinstance(r, CounterfactualResult) for r in results)


class TestCounterfactualResult:
    """Tests for CounterfactualResult."""

    def test_outcomes_similar(self):
        """Test outcomes_similar property."""
        trace = make_trace()
        original_echo = Echo(trace, {"result": "a"}, EchoMode.LUCID)
        variant_echo = Echo(trace, {"result": "a"}, EchoMode.LUCID)

        result = CounterfactualResult(
            original_echo=original_echo,
            variant_echo=variant_echo,
            modified_input={},
            divergence=0.05,
        )

        assert result.outcomes_similar is True
        assert result.outcomes_divergent is False

    def test_outcomes_divergent(self):
        """Test outcomes_divergent property."""
        trace = make_trace()
        original_echo = Echo(trace, {"result": "a"}, EchoMode.LUCID)
        variant_echo = Echo(trace, {"result": "completely_different"}, EchoMode.LUCID)

        result = CounterfactualResult(
            original_echo=original_echo,
            variant_echo=variant_echo,
            modified_input={},
            divergence=0.8,
        )

        assert result.outcomes_similar is False
        assert result.outcomes_divergent is True


class TestDriftReport:
    """Tests for DriftReport."""

    def test_significant_drift(self):
        """Test significant property."""
        trace = make_trace()
        report = DriftReport(
            trace=trace,
            drift=0.15,
            original_output={"a": 1},
            current_output={"b": 2},
        )

        assert report.significant is True
        assert report.critical is False

    def test_critical_drift(self):
        """Test critical property."""
        trace = make_trace()
        report = DriftReport(
            trace=trace,
            drift=0.6,
            original_output={"a": 1},
            current_output={"completely_different": "value"},
        )

        assert report.significant is True
        assert report.critical is True


# =============================================================================
# Quick Drift Check Tests
# =============================================================================


class TestQuickDriftCheck:
    """Tests for quick_drift_check utility."""

    @pytest.mark.asyncio
    async def test_quick_drift_check(self):
        """Test quick drift check utility."""
        traces = make_trace_sequence(5)

        total, drifted = await quick_drift_check(traces)

        assert total == 5
        assert drifted >= 0

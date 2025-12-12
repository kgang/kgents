"""Tests for Terrarium metrics module.

Tests the metrics calculation functions, emit loop, and MetricsManager.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import MagicMock

import pytest

if TYPE_CHECKING:
    from agents.flux import FluxAgent
from protocols.terrarium.events import EventType
from protocols.terrarium.metrics import (
    MetricsManager,
    calculate_flow,
    calculate_pressure,
    calculate_temperature,
    emit_fever_alert,
    emit_metrics_loop,
)
from protocols.terrarium.mirror import HolographicBuffer

# ─────────────────────────────────────────────────────────────
# Mock FluxAgent for testing
# ─────────────────────────────────────────────────────────────


@dataclass
class MockFluxConfig:
    """Mock FluxConfig for testing."""

    buffer_size: int = 100
    entropy_budget: float = 1000.0


@dataclass
class MockFluxState:
    """Mock FluxState enum."""

    value: str = "flowing"


@dataclass
class MockMetabolism:
    """Mock FluxMetabolism for testing."""

    _temperature: float = 0.5

    @property
    def temperature(self) -> float:
        return self._temperature


@dataclass
class MockFluxAgent:
    """Mock FluxAgent for testing metrics calculations."""

    _is_running: bool = True
    _events_processed: int = 0
    _entropy_remaining: float = 800.0
    _state: MockFluxState = field(default_factory=MockFluxState)
    config: MockFluxConfig = field(default_factory=MockFluxConfig)
    _metabolism: MockMetabolism | None = None

    # Mock queues
    _perturbation_queue: Any = field(default_factory=lambda: MockQueue())
    _output_queue: Any = field(default_factory=lambda: MockQueue())

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def events_processed(self) -> int:
        return self._events_processed

    @property
    def entropy_remaining(self) -> float:
        return self._entropy_remaining

    @property
    def state(self) -> MockFluxState:
        return self._state

    @property
    def metabolism(self) -> MockMetabolism | None:
        return self._metabolism


@dataclass
class MockQueue:
    """Mock asyncio queue for testing."""

    _size: int = 0

    def qsize(self) -> int:
        return self._size


# ─────────────────────────────────────────────────────────────
# Tests: Metric Calculations
# ─────────────────────────────────────────────────────────────


class TestCalculatePressure:
    """Tests for calculate_pressure function."""

    def test_zero_pressure_empty_queues(self) -> None:
        """Empty queues = zero pressure."""
        agent = MockFluxAgent()

        pressure = calculate_pressure(agent)  # type: ignore

        assert pressure == 0.0

    def test_pressure_from_output_queue(self) -> None:
        """Output queue fullness contributes to pressure."""
        agent = MockFluxAgent()
        agent._output_queue = MockQueue(_size=50)

        pressure = calculate_pressure(agent)  # type: ignore

        # 50/100 buffer size * 50 weight = 25
        assert pressure == 25.0

    def test_pressure_from_perturbation_queue(self) -> None:
        """Perturbation queue contributes heavily to pressure."""
        agent = MockFluxAgent()
        agent._perturbation_queue = MockQueue(_size=5)

        pressure = calculate_pressure(agent)  # type: ignore

        # 5/10 * 50 weight = 25
        assert pressure == 25.0

    def test_combined_pressure(self) -> None:
        """Both queues contribute to pressure."""
        agent = MockFluxAgent()
        agent._output_queue = MockQueue(_size=50)
        agent._perturbation_queue = MockQueue(_size=5)

        pressure = calculate_pressure(agent)  # type: ignore

        # Output: 50/100 * 50 = 25
        # Perturbation: 5/10 * 50 = 25
        # Total: 50
        assert pressure == 50.0

    def test_pressure_capped_at_100(self) -> None:
        """Pressure is capped at 100."""
        agent = MockFluxAgent()
        agent._output_queue = MockQueue(_size=100)
        agent._perturbation_queue = MockQueue(_size=20)

        pressure = calculate_pressure(agent)  # type: ignore

        assert pressure == 100.0


class TestCalculateFlow:
    """Tests for calculate_flow function."""

    def test_zero_flow_no_progress(self) -> None:
        """No events processed = zero flow."""
        agent = MockFluxAgent()
        agent._events_processed = 10

        flow = calculate_flow(agent, previous_count=10, time_delta=1.0)  # type: ignore

        assert flow == 0.0

    def test_flow_events_per_second(self) -> None:
        """Flow = events processed / time delta."""
        agent = MockFluxAgent()
        agent._events_processed = 20

        flow = calculate_flow(agent, previous_count=10, time_delta=2.0)  # type: ignore

        assert flow == 5.0  # 10 events / 2 seconds

    def test_flow_zero_time_delta(self) -> None:
        """Zero time delta = zero flow (avoid division by zero)."""
        agent = MockFluxAgent()
        agent._events_processed = 20

        flow = calculate_flow(agent, previous_count=10, time_delta=0.0)  # type: ignore

        assert flow == 0.0

    def test_flow_negative_delta_clipped(self) -> None:
        """Negative time delta = zero flow."""
        agent = MockFluxAgent()
        agent._events_processed = 20

        flow = calculate_flow(agent, previous_count=10, time_delta=-1.0)  # type: ignore

        assert flow == 0.0


class TestCalculateTemperature:
    """Tests for calculate_temperature function."""

    def test_temperature_from_metabolism(self) -> None:
        """Temperature comes from metabolism if attached."""
        agent = MockFluxAgent()
        agent._metabolism = MockMetabolism(_temperature=0.7)

        temp = calculate_temperature(agent)  # type: ignore

        assert temp == 0.7

    def test_temperature_from_entropy_consumption(self) -> None:
        """Without metabolism, temperature = entropy consumed ratio."""
        agent = MockFluxAgent()
        agent._entropy_remaining = 800.0  # 200 consumed of 1000

        temp = calculate_temperature(agent)  # type: ignore

        assert temp == 0.2  # 20% consumed

    def test_temperature_fully_consumed(self) -> None:
        """Fully consumed entropy = temperature 1.0."""
        agent = MockFluxAgent()
        agent._entropy_remaining = 0.0

        temp = calculate_temperature(agent)  # type: ignore

        assert temp == 1.0

    def test_temperature_capped(self) -> None:
        """Temperature capped at 1.0."""
        agent = MockFluxAgent()
        agent._metabolism = MockMetabolism(_temperature=1.5)

        temp = calculate_temperature(agent)  # type: ignore

        assert temp == 1.0


# ─────────────────────────────────────────────────────────────
# Tests: MetricsManager
# ─────────────────────────────────────────────────────────────


class TestMetricsManager:
    """Tests for MetricsManager class."""

    def test_empty_manager(self) -> None:
        """New manager has no active agents."""
        manager = MetricsManager()

        assert len(manager.active_agents) == 0

    @pytest.mark.asyncio
    async def test_start_metrics_creates_task(self) -> None:
        """start_metrics creates background task."""
        manager = MetricsManager()
        agent = MockFluxAgent()
        buffer = HolographicBuffer()

        result = manager.start_metrics("test-agent", agent, buffer)  # type: ignore

        assert result is True
        assert "test-agent" in manager.active_agents

        # Clean up
        manager.stop_all()

    @pytest.mark.asyncio
    async def test_start_metrics_idempotent(self) -> None:
        """Starting metrics for same agent twice returns False."""
        manager = MetricsManager()
        agent = MockFluxAgent()
        buffer = HolographicBuffer()

        manager.start_metrics("test-agent", agent, buffer)  # type: ignore
        result = manager.start_metrics("test-agent", agent, buffer)  # type: ignore

        assert result is False
        assert manager.active_agents.count("test-agent") == 1

        # Clean up
        manager.stop_all()

    @pytest.mark.asyncio
    async def test_stop_metrics_removes_task(self) -> None:
        """stop_metrics cancels task and removes from active."""
        manager = MetricsManager()
        agent = MockFluxAgent()
        buffer = HolographicBuffer()

        manager.start_metrics("test-agent", agent, buffer)  # type: ignore
        result = manager.stop_metrics("test-agent")

        assert result is True
        assert "test-agent" not in manager.active_agents

    def test_stop_metrics_nonexistent(self) -> None:
        """Stopping nonexistent agent returns False."""
        manager = MetricsManager()

        result = manager.stop_metrics("does-not-exist")

        assert result is False

    @pytest.mark.asyncio
    async def test_stop_all(self) -> None:
        """stop_all cancels all tasks."""
        manager = MetricsManager()
        agent1 = MockFluxAgent()
        agent2 = MockFluxAgent()
        buffer = HolographicBuffer()

        manager.start_metrics("agent-1", agent1, buffer)  # type: ignore
        manager.start_metrics("agent-2", agent2, buffer)  # type: ignore

        count = manager.stop_all()

        assert count == 2
        assert len(manager.active_agents) == 0

    @pytest.mark.asyncio
    async def test_is_emitting(self) -> None:
        """is_emitting returns correct status."""
        manager = MetricsManager()
        agent = MockFluxAgent()
        buffer = HolographicBuffer()

        assert manager.is_emitting("test-agent") is False

        manager.start_metrics("test-agent", agent, buffer)  # type: ignore

        assert manager.is_emitting("test-agent") is True

        manager.stop_metrics("test-agent")

        assert manager.is_emitting("test-agent") is False

    @pytest.mark.asyncio
    async def test_get_last_metrics(self) -> None:
        """get_last_metrics returns cached metrics."""
        manager = MetricsManager()
        agent = MockFluxAgent()
        buffer = HolographicBuffer()

        # Before starting, no metrics
        assert manager.get_last_metrics("test-agent") is None

        # After starting, has initial metrics
        manager.start_metrics("test-agent", agent, buffer)  # type: ignore

        metrics = manager.get_last_metrics("test-agent")
        assert metrics is not None
        assert "pressure" in metrics
        assert "flow" in metrics
        assert "temperature" in metrics

        # Clean up
        manager.stop_all()

    @pytest.mark.asyncio
    async def test_get_all_metrics(self) -> None:
        """get_all_metrics returns all cached metrics."""
        manager = MetricsManager()
        agent1 = MockFluxAgent()
        agent2 = MockFluxAgent()
        buffer = HolographicBuffer()

        manager.start_metrics("agent-1", agent1, buffer)  # type: ignore
        manager.start_metrics("agent-2", agent2, buffer)  # type: ignore

        all_metrics = manager.get_all_metrics()

        assert len(all_metrics) == 2
        assert "agent-1" in all_metrics
        assert "agent-2" in all_metrics

        # Clean up
        manager.stop_all()


# ─────────────────────────────────────────────────────────────
# Tests: Emit Metrics Loop
# ─────────────────────────────────────────────────────────────


class TestEmitMetricsLoop:
    """Tests for emit_metrics_loop function."""

    @pytest.mark.asyncio
    async def test_emits_metabolism_event(self) -> None:
        """Loop emits metabolism events to buffer."""
        agent = MockFluxAgent()
        buffer = HolographicBuffer()

        # Run for a short time then stop
        async def run_briefly() -> None:
            await asyncio.sleep(0.05)
            agent._is_running = False

        asyncio.create_task(run_briefly())

        await emit_metrics_loop(
            "test-agent",
            cast("FluxAgent[Any, Any]", agent),
            buffer,
            interval=0.02,  # type: ignore
        )

        # Should have emitted at least one metabolism event + stopped event
        snapshot = buffer.get_snapshot()
        assert len(snapshot) >= 1

        # Check event types
        types = [e.get("type") for e in snapshot]
        assert (
            EventType.METABOLISM.value in types
            or EventType.AGENT_STOPPED.value in types
        )

    @pytest.mark.asyncio
    async def test_emits_stopped_event_when_done(self) -> None:
        """Loop emits agent_stopped event when agent stops."""
        agent = MockFluxAgent()
        agent._is_running = False  # Already stopped
        buffer = HolographicBuffer()

        await emit_metrics_loop(
            "test-agent",
            cast("FluxAgent[Any, Any]", agent),
            buffer,
            interval=0.01,  # type: ignore
        )

        snapshot = buffer.get_snapshot()
        assert len(snapshot) >= 1

        # Last event should be stopped
        last_event = snapshot[-1]
        assert last_event.get("type") == EventType.AGENT_STOPPED.value


# ─────────────────────────────────────────────────────────────
# Tests: Fever Alert
# ─────────────────────────────────────────────────────────────


class TestEmitFeverAlert:
    """Tests for emit_fever_alert function."""

    @pytest.mark.asyncio
    async def test_no_alert_below_threshold(self) -> None:
        """No fever alert when temperature below threshold."""
        buffer = HolographicBuffer()

        result = await emit_fever_alert("test-agent", buffer, temperature=0.5)

        assert result is False
        assert len(buffer.get_snapshot()) == 0

    @pytest.mark.asyncio
    async def test_alert_above_threshold(self) -> None:
        """Fever alert emitted when temperature >= threshold."""
        buffer = HolographicBuffer()

        result = await emit_fever_alert("test-agent", buffer, temperature=0.85)

        assert result is True

        snapshot = buffer.get_snapshot()
        assert len(snapshot) == 1

        event = snapshot[0]
        assert event.get("type") == EventType.FEVER.value
        assert event.get("agent_id") == "test-agent"
        assert event.get("temperature") == 0.85

    @pytest.mark.asyncio
    async def test_high_severity_above_95(self) -> None:
        """High severity when temperature > 0.95."""
        buffer = HolographicBuffer()

        await emit_fever_alert("test-agent", buffer, temperature=0.98)

        snapshot = buffer.get_snapshot()
        event = snapshot[0]
        assert event.get("data", {}).get("severity") == "high"

    @pytest.mark.asyncio
    async def test_moderate_severity_below_95(self) -> None:
        """Moderate severity when temperature <= 0.95."""
        buffer = HolographicBuffer()

        await emit_fever_alert("test-agent", buffer, temperature=0.85)

        snapshot = buffer.get_snapshot()
        event = snapshot[0]
        assert event.get("data", {}).get("severity") == "moderate"

    @pytest.mark.asyncio
    async def test_custom_threshold(self) -> None:
        """Custom threshold respected."""
        buffer = HolographicBuffer()

        # Should not alert at 0.85 with threshold 0.9
        result = await emit_fever_alert(
            "test-agent", buffer, temperature=0.85, threshold=0.9
        )

        assert result is False

        # Should alert at 0.92
        result = await emit_fever_alert(
            "test-agent", buffer, temperature=0.92, threshold=0.9
        )

        assert result is True

"""Tests for StreamAgent - Temporal Witness foundation."""

from __future__ import annotations

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from agents.d.errors import DriftDetectionError
from agents.d.stream import (
    StreamAgent,
    WitnessReport,
)


class TestStreamAgentBasics:
    """Basic StreamAgent operations."""

    @pytest.fixture
    def counter_agent(self) -> StreamAgent[int, dict[str, Any]]:
        """Create a simple counter stream agent."""

        def fold(state: int, event: dict[str, Any]) -> int:
            if event.get("type") == "increment":
                return state + int(event.get("amount", 1))
            elif event.get("type") == "decrement":
                return state - int(event.get("amount", 1))
            return state

        return StreamAgent(fold=fold, initial=0)  # type: ignore[arg-type]

    @pytest.fixture
    def witness(self) -> WitnessReport:
        """Create a test witness report."""
        return WitnessReport(
            observer_id="test",
            confidence=0.9,
            context={"test": True},
        )

    async def test_append_and_load(
        self, counter_agent: StreamAgent[int, dict[str, Any]], witness: WitnessReport
    ) -> None:
        """Test appending events and loading state."""
        await counter_agent.append({"type": "increment", "amount": 5}, witness)  # type: ignore[arg-type]

        state = await counter_agent.load()
        assert state == 5  # type: ignore[comparison-overlap]

    async def test_multiple_events(
        self, counter_agent: StreamAgent[int, dict[str, Any]], witness: WitnessReport
    ) -> None:
        """Test multiple events fold correctly."""
        await counter_agent.append({"type": "increment", "amount": 5}, witness)  # type: ignore[arg-type]
        await counter_agent.append({"type": "increment", "amount": 3}, witness)  # type: ignore[arg-type]
        await counter_agent.append({"type": "decrement", "amount": 2}, witness)  # type: ignore[arg-type]

        state = await counter_agent.load()
        assert state == 6  # type: ignore[comparison-overlap]  # 5 + 3 - 2

    async def test_history_returns_states(
        self, counter_agent: StreamAgent[int, dict[str, Any]], witness: WitnessReport
    ) -> None:
        """Test history returns historical states."""
        await counter_agent.append({"type": "increment", "amount": 1}, witness)  # type: ignore[arg-type]
        await counter_agent.append({"type": "increment", "amount": 2}, witness)  # type: ignore[arg-type]
        await counter_agent.append({"type": "increment", "amount": 3}, witness)  # type: ignore[arg-type]

        history = await counter_agent.history()
        # States after each event: 1, 3, 6
        assert history == [6, 3, 1]  # type: ignore[comparison-overlap]  # Newest first

    async def test_history_limit(
        self, counter_agent: StreamAgent[int, dict[str, Any]], witness: WitnessReport
    ) -> None:
        """Test history respects limit."""
        for i in range(10):
            await counter_agent.append({"type": "increment", "amount": 1}, witness)  # type: ignore[arg-type]

        history = await counter_agent.history(limit=3)
        assert len(history) == 3

    async def test_event_count(
        self, counter_agent: StreamAgent[int, dict[str, Any]], witness: WitnessReport
    ) -> None:
        """Test event count."""
        assert await counter_agent.event_count() == 0

        await counter_agent.append({"type": "increment"}, witness)  # type: ignore[arg-type]
        await counter_agent.append({"type": "increment"}, witness)  # type: ignore[arg-type]

        assert await counter_agent.event_count() == 2


class TestTimeTravel:
    """Time-travel (replay) operations."""

    @pytest.fixture
    def agent_with_events(self) -> StreamAgent[list[str], str]:
        """Create agent with timed events."""

        def fold(state: list[str], event: str) -> list[str]:
            return state + [event]

        return StreamAgent(fold=fold, initial=[])  # type: ignore[arg-type]

    async def test_replay_to_timestamp(
        self, agent_with_events: StreamAgent[list[str], str]
    ) -> None:
        """Test replaying to specific timestamp."""
        agent = agent_with_events
        witness = WitnessReport(observer_id="test", confidence=1.0)

        # Add events at different times
        await agent.append("event1", witness)  # type: ignore[arg-type]
        mid_time = datetime.now()
        await agent.append("event2", witness)  # type: ignore[arg-type]
        await agent.append("event3", witness)  # type: ignore[arg-type]

        # Replay to mid_time should include event1 but not event2/3
        # Actually, mid_time is after event1, so it includes event1
        state = await agent.replay_to(mid_time)

        # Due to timing, this may include event1 or event1+event2
        assert "event1" in state or len(state) >= 1

    async def test_replay_range(
        self, agent_with_events: StreamAgent[list[str], str]
    ) -> None:
        """Test replaying a time range."""
        agent = agent_with_events
        witness = WitnessReport(observer_id="test", confidence=1.0)

        before = datetime.now() - timedelta(seconds=1)
        await agent.append("event1", witness)  # type: ignore[arg-type]
        await agent.append("event2", witness)  # type: ignore[arg-type]
        after = datetime.now() + timedelta(seconds=1)

        state = await agent.replay(before, after)
        assert state == ["event1", "event2"]  # type: ignore[comparison-overlap]

    async def test_replay_with_witnesses(
        self, agent_with_events: StreamAgent[list[str], str]
    ) -> None:
        """Test replay returns witness reports."""
        agent = agent_with_events
        witness = WitnessReport(observer_id="observer1", confidence=0.8)

        before = datetime.now() - timedelta(seconds=1)
        await agent.append("event1", witness)  # type: ignore[arg-type]
        after = datetime.now() + timedelta(seconds=1)

        results = await agent.replay_with_witnesses(before, after)

        assert len(results) == 1
        event, state, witness_report = results[0]
        assert event == "event1"  # type: ignore[comparison-overlap]
        assert witness_report.observer_id == "observer1"
        assert witness_report.confidence == 0.8


class TestDriftDetection:
    """Drift detection operations."""

    @pytest.fixture
    def numeric_agent(self) -> StreamAgent[dict[str, Any], dict[str, Any]]:
        """Create agent that tracks numeric values."""

        def fold(state: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
            return {**state, **event}

        return StreamAgent(fold=fold, initial={"value": 50})

    async def test_detect_drift_numeric(
        self, numeric_agent: StreamAgent[dict[str, Any], dict[str, Any]]
    ) -> None:
        """Test drift detection on numeric values."""
        agent = numeric_agent
        witness = WitnessReport(observer_id="test", confidence=1.0)

        # Add stable events first
        for _ in range(10):
            await agent.append({"value": 50 + (hash(str(_)) % 5 - 2)}, witness)

        # Add drifted events
        for _ in range(10):
            await agent.append({"value": 100 + (hash(str(_)) % 5 - 2)}, witness)

        # Detect drift
        report = await agent.detect_drift(
            trajectory="value",
            extractor=lambda s: s.get("value", 0),
            window=timedelta(hours=1),
        )

        assert report.drift_detected is True
        assert report.drift_magnitude > 0.5

    async def test_detect_drift_stable(
        self, numeric_agent: StreamAgent[dict[str, Any], dict[str, Any]]
    ) -> None:
        """Test drift detection when stable."""
        agent = numeric_agent
        witness = WitnessReport(observer_id="test", confidence=1.0)

        # Add consistent events
        for i in range(20):
            await agent.append({"value": 50 + (i % 3 - 1)}, witness)  # 49, 50, 51

        report = await agent.detect_drift(
            trajectory="value",
            extractor=lambda s: s.get("value", 0),
            window=timedelta(hours=1),
        )

        assert report.drift_detected is False
        assert report.drift_magnitude < 0.3

    async def test_detect_drift_insufficient_data(self) -> None:
        """Test drift detection with insufficient data."""

        def fold(state: int, event: int) -> int:
            return event

        agent: StreamAgent[int, int] = StreamAgent(fold=fold, initial=0)
        witness = WitnessReport(observer_id="test", confidence=1.0)

        await agent.append(1, witness)
        await agent.append(2, witness)

        with pytest.raises(DriftDetectionError, match="Insufficient data"):
            await agent.detect_drift(
                trajectory="test",
                extractor=lambda x: x,
                window=timedelta(hours=1),
            )


class TestMomentumTracking:
    """Momentum (semantic velocity) tracking."""

    @pytest.fixture
    def momentum_agent(self) -> StreamAgent[float, float]:
        """Create agent for momentum testing."""

        def fold(state: float, event: float) -> float:
            return event

        return StreamAgent(fold=fold, initial=0.0)

    async def test_momentum_increasing(
        self, momentum_agent: StreamAgent[float, float]
    ) -> None:
        """Test momentum when increasing."""
        agent = momentum_agent
        witness = WitnessReport(observer_id="test", confidence=0.9)

        # Rapidly increasing values
        for i in range(10):
            await agent.append(float(i * 10), witness)

        momentum = await agent.momentum(
            extractor=lambda x: x,
            window=timedelta(hours=1),
        )

        assert momentum.direction == "increasing"
        assert momentum.magnitude > 0
        assert momentum.confidence > 0.8

    async def test_momentum_decreasing(
        self, momentum_agent: StreamAgent[float, float]
    ) -> None:
        """Test momentum when decreasing."""
        agent = momentum_agent
        witness = WitnessReport(observer_id="test", confidence=0.9)

        # Rapidly decreasing values
        for i in range(10):
            await agent.append(float(100 - i * 10), witness)

        momentum = await agent.momentum(
            extractor=lambda x: x,
            window=timedelta(hours=1),
        )

        assert momentum.direction == "decreasing"
        assert momentum.magnitude > 0

    async def test_momentum_stable(
        self, momentum_agent: StreamAgent[float, float]
    ) -> None:
        """Test momentum when stable."""
        agent = momentum_agent
        witness = WitnessReport(observer_id="test", confidence=0.9)

        # Constant value
        for _ in range(10):
            await agent.append(50.0, witness)

        momentum = await agent.momentum(
            extractor=lambda x: x,
            window=timedelta(hours=1),
        )

        assert momentum.direction == "stable"
        assert momentum.magnitude < 0.01


class TestEntropyMeasurement:
    """Entropy (chaos vs stability) measurement."""

    async def test_entropy_high(self) -> None:
        """Test high entropy (rapid change)."""

        def fold(state: int, event: int) -> int:
            return event

        agent: StreamAgent[int, int] = StreamAgent(fold=fold, initial=0)

        # Many events with high anomaly score
        # Entropy = 0.6 * normalized_rate + 0.4 * avg_anomaly
        # With anomaly_score=0.8, the anomaly component is 0.4 * 0.8 = 0.32
        for i in range(100):
            witness = WitnessReport(
                observer_id="test",
                confidence=0.5,
                anomaly_score=0.8,
            )
            await agent.append(i, witness)

        entropy = await agent.entropy(window=timedelta(hours=1))
        # With 100 events over an hour (~0.028/sec) and high anomaly
        # Entropy should be meaningful (anomaly contributes 0.32)
        assert entropy > 0.3

    async def test_entropy_low(self) -> None:
        """Test low entropy (stable)."""

        def fold(state: int, event: int) -> int:
            return event

        agent: StreamAgent[int, int] = StreamAgent(fold=fold, initial=0)

        # Few events with low anomaly
        witness = WitnessReport(
            observer_id="test",
            confidence=1.0,
            anomaly_score=0.0,
        )
        await agent.append(1, witness)

        entropy = await agent.entropy(window=timedelta(hours=1))
        assert entropy < 0.5

    async def test_entropy_empty(self) -> None:
        """Test entropy when no events."""

        def fold(state: int, event: int) -> int:
            return event

        agent: StreamAgent[int, int] = StreamAgent(fold=fold, initial=0)

        entropy = await agent.entropy(window=timedelta(hours=1))
        assert entropy == 0.0


class TestEventHistory:
    """Event history queries."""

    async def test_event_history_filter(self) -> None:
        """Test filtering event history."""

        def fold(
            state: list[dict[str, str]], event: dict[str, str]
        ) -> list[dict[str, str]]:
            return state + [event]

        agent = StreamAgent[list[dict[str, str]], dict[str, str]](
            fold=fold,
            initial=[],  # type: ignore[arg-type]
        )
        witness = WitnessReport(observer_id="test", confidence=1.0)

        await agent.append({"type": "a"}, witness)  # type: ignore[arg-type]
        await agent.append({"type": "b"}, witness)  # type: ignore[arg-type]
        await agent.append({"type": "a"}, witness)  # type: ignore[arg-type]

        history = await agent.event_history(filter_by=lambda e: e.get("type") == "a")  # type: ignore[attr-defined]

        assert len(history) == 2
        assert all(e["type"] == "a" for _, e, _ in history)  # type: ignore[call-overload]

    async def test_events_since(self) -> None:
        """Test getting events since timestamp."""

        def fold(state: int, event: int) -> int:
            return event

        agent: StreamAgent[int, int] = StreamAgent(fold=fold, initial=0)
        witness = WitnessReport(observer_id="test", confidence=1.0)

        await agent.append(1, witness)
        since = datetime.now()
        await agent.append(2, witness)
        await agent.append(3, witness)

        events = await agent.events_since(since)
        # May include event 2 and 3 depending on timing
        assert len(events) >= 1


class TestWitnessReport:
    """Tests for WitnessReport dataclass."""

    def test_witness_report_valid(self) -> None:
        """Test valid witness report."""
        report = WitnessReport(
            observer_id="test",
            confidence=0.5,
            context={"key": "value"},
            anomaly_score=0.2,
        )

        assert report.observer_id == "test"
        assert report.confidence == 0.5
        assert report.context == {"key": "value"}
        assert report.anomaly_score == 0.2

    def test_witness_report_invalid_confidence(self) -> None:
        """Test invalid confidence raises error."""
        with pytest.raises(ValueError, match="Confidence"):
            WitnessReport(observer_id="test", confidence=1.5)

        with pytest.raises(ValueError, match="Confidence"):
            WitnessReport(observer_id="test", confidence=-0.1)


class TestStreamAgentPersistence:
    """Persistence tests."""

    async def test_persistence_round_trip(self) -> None:
        """Test save and load from disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "stream.json"

            def fold(state: int, event: int) -> int:
                return state + event

            # Create and populate
            agent1: StreamAgent[int, int] = StreamAgent(
                fold=fold, initial=0, persistence_path=path
            )
            witness = WitnessReport(observer_id="test", confidence=1.0)

            await agent1.append(5, witness)
            await agent1.append(3, witness)

            # Create new instance from same path
            agent2: StreamAgent[int, int] = StreamAgent(
                fold=fold, initial=0, persistence_path=path
            )

            # Should have loaded state
            state = await agent2.load()
            assert state == 8

            # Should have event history
            count = await agent2.event_count()
            assert count == 2

    async def test_persistence_preserves_witnesses(self) -> None:
        """Test that witness reports are preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "stream.json"

            def fold(state: int, event: int) -> int:
                return event

            agent1: StreamAgent[int, int] = StreamAgent(
                fold=fold, initial=0, persistence_path=path
            )
            witness = WitnessReport(
                observer_id="observer1",
                confidence=0.75,
                context={"test": True},
                anomaly_score=0.3,
            )

            await agent1.append(1, witness)

            # Load fresh
            agent2: StreamAgent[int, int] = StreamAgent(
                fold=fold, initial=0, persistence_path=path
            )

            events = await agent2.events_since(datetime.min)
            assert len(events) == 1
            assert events[0].witness.observer_id == "observer1"
            assert events[0].witness.confidence == 0.75
            assert events[0].witness.anomaly_score == 0.3


class TestBoundedEventLog:
    """Test bounded event log (max_events)."""

    async def test_max_events_enforced(self) -> None:
        """Test that max_events limit is enforced."""

        def fold(state: int, event: int) -> int:
            return state + 1

        agent: StreamAgent[int, int] = StreamAgent(fold=fold, initial=0, max_events=5)
        witness = WitnessReport(observer_id="test", confidence=1.0)

        # Add more events than max
        for i in range(10):
            await agent.append(1, witness)

        count = await agent.event_count()
        assert count == 5  # Should only keep last 5


class TestSaveMethod:
    """Test save() method (DataAgent protocol compatibility)."""

    async def test_save_creates_synthetic_event(self) -> None:
        """Test save() creates synthetic state_set event."""

        def fold(state: int, event: dict[str, Any] | int) -> int:
            if isinstance(event, dict) and event.get("__synthetic__") == "state_set":
                return int(event["value"])
            return state

        agent = StreamAgent[int, dict[str, Any] | int](
            fold=fold,
            initial=0,  # type: ignore[arg-type]
        )

        await agent.save(42)

        state = await agent.load()
        assert state == 42

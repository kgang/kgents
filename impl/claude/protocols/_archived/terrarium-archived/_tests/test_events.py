"""Tests for Terrarium events."""

from protocols.terrarium.events import (
    EventType,
    SemaphoreEvent,
    TerriumEvent,
    make_error_event,
    make_metabolism_event,
    make_result_event,
)


class TestEventType:
    """EventType enum values."""

    def test_event_types_are_strings(self) -> None:
        """Event types are string enums."""
        assert EventType.RESULT.value == "result"
        assert EventType.ERROR.value == "error"
        assert EventType.SEMAPHORE_EJECTED.value == "semaphore_ejected"


class TestTerriumEvent:
    """TerriumEvent dataclass."""

    def test_basic_event(self) -> None:
        """Basic event creation."""
        event = TerriumEvent(
            event_type=EventType.RESULT,
            agent_id="test-agent",
            data={"value": 42},
        )

        assert event.event_type == EventType.RESULT
        assert event.agent_id == "test-agent"
        assert event.data == {"value": 42}

    def test_as_dict_basic(self) -> None:
        """as_dict produces JSON-serializable dict."""
        event = TerriumEvent(
            event_type=EventType.RESULT,
            agent_id="test-agent",
            data={"result": "hello"},
        )

        d = event.as_dict()

        assert d["type"] == "result"
        assert d["agent_id"] == "test-agent"
        assert d["data"]["result"] == "hello"

    def test_as_dict_omits_zero_metrics(self) -> None:
        """Zero metrics are omitted from dict."""
        event = TerriumEvent(
            event_type=EventType.METABOLISM,
            agent_id="test",
            pressure=0.0,
            flow=0.0,
            temperature=0.0,
        )

        d = event.as_dict()

        assert "pressure" not in d
        assert "flow" not in d
        assert "temperature" not in d

    def test_as_dict_includes_nonzero_metrics(self) -> None:
        """Non-zero metrics are included."""
        event = TerriumEvent(
            event_type=EventType.METABOLISM,
            agent_id="test",
            pressure=50.0,
            flow=10.5,
            temperature=0.8,
        )

        d = event.as_dict()

        assert d["pressure"] == 50.0
        assert d["flow"] == 10.5
        assert d["temperature"] == 0.8


class TestSemaphoreEvent:
    """SemaphoreEvent for Purgatory integration."""

    def test_semaphore_event_creation(self) -> None:
        """Create semaphore event."""
        event = SemaphoreEvent(
            token_id="sem-123",
            agent_id="flux-agent",
            prompt="Choose deployment target",
            options=["staging", "production"],
            severity="warning",
        )

        assert event.token_id == "sem-123"
        assert event.prompt == "Choose deployment target"
        assert len(event.options) == 2

    def test_as_terrium_event(self) -> None:
        """Convert to TerriumEvent."""
        sem = SemaphoreEvent(
            token_id="sem-456",
            agent_id="flux-agent",
            prompt="Confirm?",
            options=["yes", "no"],
        )

        event = sem.as_terrium_event()

        assert event.event_type == EventType.SEMAPHORE_EJECTED
        assert event.agent_id == "flux-agent"
        assert event.data["token_id"] == "sem-456"
        assert event.data["prompt"] == "Confirm?"


class TestEventFactories:
    """Factory functions for common events."""

    def test_make_result_event(self) -> None:
        """make_result_event creates result event."""
        event = make_result_event(
            agent_id="test",
            result="computed value",
            state="FLOWING",
            pressure=25.0,
        )

        assert event.event_type == EventType.RESULT
        assert event.data["result"] == "computed value"
        assert event.state == "FLOWING"
        assert event.pressure == 25.0

    def test_make_error_event(self) -> None:
        """make_error_event creates error event."""
        event = make_error_event(
            agent_id="test",
            error="Something went wrong",
            error_type="ValueError",
        )

        assert event.event_type == EventType.ERROR
        assert event.data["error"] == "Something went wrong"
        assert event.data["error_type"] == "ValueError"

    def test_make_metabolism_event(self) -> None:
        """make_metabolism_event creates metabolism event."""
        event = make_metabolism_event(
            agent_id="flux-1",
            pressure=75.0,
            flow=20.0,
            temperature=0.5,
            state="PERTURBED",
        )

        assert event.event_type == EventType.METABOLISM
        assert event.pressure == 75.0
        assert event.flow == 20.0
        assert event.temperature == 0.5
        assert event.state == "PERTURBED"

"""
Tests for synergy event bus.

Foundation 4 - Wave 0: Cross-jewel communication infrastructure.
"""

from typing import Any

import pytest

from protocols.synergy.bus import (
    SynergyEventBus,
    get_synergy_bus,
    reset_synergy_bus,
)
from protocols.synergy.events import (
    Jewel,
    SynergyEvent,
    SynergyEventType,
    SynergyResult,
)


class MockHandler:
    """Mock handler for testing."""

    def __init__(
        self,
        name: str = "MockHandler",
        result: SynergyResult | None = None,
        should_fail: bool = False,
    ) -> None:
        self._name = name
        self._result = result
        self._should_fail = should_fail
        self.handled_events: list[SynergyEvent] = []

    @property
    def name(self) -> str:
        return self._name

    async def handle(self, event: SynergyEvent) -> SynergyResult:
        if self._should_fail:
            raise RuntimeError("Handler intentionally failed")

        self.handled_events.append(event)

        if self._result:
            return self._result

        return SynergyResult(
            success=True,
            handler_name=self._name,
            message="Handled successfully",
        )


@pytest.fixture
def bus() -> SynergyEventBus:
    """Create a fresh bus for each test."""
    return SynergyEventBus()


@pytest.fixture
def sample_event() -> SynergyEvent:
    """Create a sample event for testing."""
    return SynergyEvent(
        source_jewel=Jewel.GESTALT,
        target_jewel=Jewel.BRAIN,
        event_type=SynergyEventType.ANALYSIS_COMPLETE,
        source_id="test-123",
        payload={"module_count": 50},
    )


class TestSynergyEventBus:
    """Tests for SynergyEventBus."""

    @pytest.mark.asyncio
    async def test_register_and_emit(
        self,
        bus: SynergyEventBus,
        sample_event: SynergyEvent,
    ) -> None:
        """Registered handlers receive emitted events."""
        handler = MockHandler()
        bus.register(SynergyEventType.ANALYSIS_COMPLETE, handler)

        await bus.emit_and_wait(sample_event)

        assert len(handler.handled_events) == 1
        assert handler.handled_events[0].source_id == "test-123"

    @pytest.mark.asyncio
    async def test_multiple_handlers(
        self,
        bus: SynergyEventBus,
        sample_event: SynergyEvent,
    ) -> None:
        """Multiple handlers can be registered for same event type."""
        handler1 = MockHandler("Handler1")
        handler2 = MockHandler("Handler2")

        bus.register(SynergyEventType.ANALYSIS_COMPLETE, handler1)
        bus.register(SynergyEventType.ANALYSIS_COMPLETE, handler2)

        await bus.emit_and_wait(sample_event)

        assert len(handler1.handled_events) == 1
        assert len(handler2.handled_events) == 1

    @pytest.mark.asyncio
    async def test_unsubscribe(
        self,
        bus: SynergyEventBus,
        sample_event: SynergyEvent,
    ) -> None:
        """Unsubscribed handlers don't receive events."""
        handler = MockHandler()
        unsubscribe = bus.register(SynergyEventType.ANALYSIS_COMPLETE, handler)

        # Unsubscribe before emitting
        unsubscribe()

        await bus.emit_and_wait(sample_event)

        assert len(handler.handled_events) == 0

    @pytest.mark.asyncio
    async def test_handler_filters_by_event_type(
        self,
        bus: SynergyEventBus,
    ) -> None:
        """Handlers only receive events they're registered for."""
        handler = MockHandler()
        bus.register(SynergyEventType.CRYSTAL_FORMED, handler)

        # Emit a different event type
        event = SynergyEvent(
            source_jewel=Jewel.GESTALT,
            target_jewel=Jewel.BRAIN,
            event_type=SynergyEventType.ANALYSIS_COMPLETE,
            source_id="test-123",
        )

        await bus.emit_and_wait(event)

        assert len(handler.handled_events) == 0

    @pytest.mark.asyncio
    async def test_handler_failure_doesnt_break_others(
        self,
        bus: SynergyEventBus,
        sample_event: SynergyEvent,
    ) -> None:
        """A failing handler doesn't prevent other handlers from running."""
        failing_handler = MockHandler("FailingHandler", should_fail=True)
        working_handler = MockHandler("WorkingHandler")

        bus.register(SynergyEventType.ANALYSIS_COMPLETE, failing_handler)
        bus.register(SynergyEventType.ANALYSIS_COMPLETE, working_handler)

        results = await bus.emit_and_wait(sample_event)

        # The working handler should still have handled the event
        assert len(working_handler.handled_events) == 1

        # We should have 2 results (one failure, one success)
        assert len(results) == 2
        assert any(not r.success for r in results)  # One failed
        assert any(r.success for r in results)  # One succeeded

    @pytest.mark.asyncio
    async def test_subscribe_results(
        self,
        bus: SynergyEventBus,
        sample_event: SynergyEvent,
    ) -> None:
        """Result subscribers are notified of handler results."""
        handler = MockHandler()
        bus.register(SynergyEventType.ANALYSIS_COMPLETE, handler)

        received_results: list[tuple[SynergyEvent, SynergyResult]] = []

        def on_result(event: SynergyEvent, result: SynergyResult) -> None:
            received_results.append((event, result))

        bus.subscribe_results(on_result)

        await bus.emit_and_wait(sample_event)

        assert len(received_results) == 1
        event, result = received_results[0]
        assert event.source_id == "test-123"
        assert result.success is True

    @pytest.mark.asyncio
    async def test_unsubscribe_results(
        self,
        bus: SynergyEventBus,
        sample_event: SynergyEvent,
    ) -> None:
        """Unsubscribed result listeners don't receive notifications."""
        handler = MockHandler()
        bus.register(SynergyEventType.ANALYSIS_COMPLETE, handler)

        received_results: list[Any] = []

        def on_result(event: SynergyEvent, result: SynergyResult) -> None:
            received_results.append(result)

        unsubscribe = bus.subscribe_results(on_result)
        unsubscribe()

        await bus.emit_and_wait(sample_event)

        assert len(received_results) == 0

    @pytest.mark.asyncio
    async def test_no_handlers_returns_empty_results(
        self,
        bus: SynergyEventBus,
        sample_event: SynergyEvent,
    ) -> None:
        """Emitting to no handlers returns empty results."""
        results = await bus.emit_and_wait(sample_event)
        assert results == []

    def test_clear_removes_all(
        self,
        bus: SynergyEventBus,
    ) -> None:
        """Clear removes all handlers and subscribers."""
        handler = MockHandler()
        bus.register(SynergyEventType.ANALYSIS_COMPLETE, handler)
        bus.subscribe_results(lambda e, r: None)

        bus.clear()

        # Internal state should be empty
        assert len(bus._handlers) == 0
        assert len(bus._result_subscribers) == 0


class TestSingleton:
    """Tests for singleton management."""

    def setup_method(self) -> None:
        """Reset singleton before each test."""
        reset_synergy_bus()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        reset_synergy_bus()

    def test_get_synergy_bus_returns_same_instance(self) -> None:
        """get_synergy_bus returns the same instance."""
        bus1 = get_synergy_bus()
        bus2 = get_synergy_bus()

        assert bus1 is bus2

    def test_reset_synergy_bus_clears_instance(self) -> None:
        """reset_synergy_bus clears the singleton."""
        bus1 = get_synergy_bus()
        reset_synergy_bus()
        bus2 = get_synergy_bus()

        assert bus1 is not bus2

    def test_default_handlers_registered(self) -> None:
        """Default handlers are registered on first access."""
        bus = get_synergy_bus()

        # GestaltToBrainHandler should be registered
        handlers = bus._handlers.get(SynergyEventType.ANALYSIS_COMPLETE, [])
        assert len(handlers) > 0
        assert any("GestaltToBrain" in h.name for h in handlers)

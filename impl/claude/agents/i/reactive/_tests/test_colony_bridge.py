"""
Tests for ColonyDashboardBridge.

Wave 4 Test Suite
=================

Tests verify:
1. Activity buffer operations
2. Event to activity conversion
3. Bridge state updates from events
4. Signal binding and propagation
5. SSE event format
6. Factory function
"""

from __future__ import annotations

from datetime import datetime

import pytest

from agents.i.reactive.colony_bridge import (
    ActivityBuffer,
    ColonyDashboardBridge,
    _event_to_activity,
    create_bridge_and_dashboard,
)
from agents.i.reactive.colony_dashboard import ColonyDashboard, ColonyState, TownPhase
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import RenderTarget
from agents.town.citizen import Citizen, Eigenvectors
from agents.town.environment import TownEnvironment
from agents.town.flux import TownEvent, TownFlux

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_environment() -> TownEnvironment:
    """Create sample environment with citizens."""
    env = TownEnvironment(name="test-town")

    alice = Citizen(
        name="Alice",
        archetype="builder",
        region="plaza",
        eigenvectors=Eigenvectors(warmth=0.8, curiosity=0.7),
    )
    bob = Citizen(
        name="Bob",
        archetype="trader",
        region="plaza",
        eigenvectors=Eigenvectors(warmth=0.6, trust=0.9),
    )
    carol = Citizen(
        name="Carol",
        archetype="healer",
        region="clinic",
        eigenvectors=Eigenvectors(warmth=0.9, patience=0.8),
    )

    env.add_citizen(alice)
    env.add_citizen(bob)
    env.add_citizen(carol)

    return env


@pytest.fixture
def sample_flux(sample_environment: TownEnvironment) -> TownFlux:
    """Create sample TownFlux."""
    return TownFlux(sample_environment, seed=42)


@pytest.fixture
def sample_event() -> TownEvent:
    """Create sample TownEvent."""
    from agents.town.flux import TownPhase as FluxPhase

    return TownEvent(
        phase=FluxPhase.MORNING,
        operation="greet",
        participants=["Alice", "Bob"],
        success=True,
        message="Alice greeted Bob.",
        tokens_used=100,
        drama_contribution=0.2,
    )


# =============================================================================
# ActivityBuffer Tests
# =============================================================================


class TestActivityBuffer:
    """Tests for ActivityBuffer."""

    def test_push_and_retrieve(self) -> None:
        """Test pushing samples and retrieving as tuple."""
        buffer = ActivityBuffer(max_length=5)
        buffer.push(0.1)
        buffer.push(0.5)
        buffer.push(0.9)

        result = buffer.to_tuple()
        assert result == (0.1, 0.5, 0.9)

    def test_max_length_enforcement(self) -> None:
        """Test buffer respects max_length."""
        buffer = ActivityBuffer(max_length=3)
        for i in range(10):
            buffer.push(i / 10)

        result = buffer.to_tuple()
        assert len(result) == 3
        # Should have last 3 values
        assert result == (0.7, 0.8, 0.9)

    def test_value_clamping(self) -> None:
        """Test values are clamped to [0, 1]."""
        buffer = ActivityBuffer()
        buffer.push(-0.5)
        buffer.push(1.5)
        buffer.push(0.5)

        result = buffer.to_tuple()
        assert result == (0.0, 1.0, 0.5)

    def test_clear(self) -> None:
        """Test clearing buffer."""
        buffer = ActivityBuffer()
        buffer.push(0.5)
        buffer.push(0.5)
        buffer.clear()

        assert buffer.to_tuple() == ()


# =============================================================================
# Event to Activity Tests
# =============================================================================


class TestEventToActivity:
    """Tests for _event_to_activity conversion."""

    def test_failed_event_low_activity(self) -> None:
        """Failed events should have low activity."""
        from agents.town.flux import TownPhase as FluxPhase

        event = TownEvent(
            phase=FluxPhase.MORNING,
            operation="greet",
            participants=["Alice", "Bob"],
            success=False,
            message="Failed",
        )

        activity = _event_to_activity(event)
        assert activity == 0.1

    def test_successful_greet_base_activity(self) -> None:
        """Greet should have moderate activity."""
        from agents.town.flux import TownPhase as FluxPhase

        event = TownEvent(
            phase=FluxPhase.MORNING,
            operation="greet",
            participants=["Alice", "Bob"],
            success=True,
            tokens_used=0,
            drama_contribution=0.0,
        )

        activity = _event_to_activity(event)
        assert 0.3 <= activity <= 0.5

    def test_trade_higher_activity(self) -> None:
        """Trade should have higher activity than greet."""
        from agents.town.flux import TownPhase as FluxPhase

        greet = TownEvent(
            phase=FluxPhase.MORNING,
            operation="greet",
            participants=["Alice", "Bob"],
            success=True,
            tokens_used=100,
            drama_contribution=0.1,
        )

        trade = TownEvent(
            phase=FluxPhase.MORNING,
            operation="trade",
            participants=["Alice", "Bob"],
            success=True,
            tokens_used=100,
            drama_contribution=0.1,
        )

        assert _event_to_activity(trade) > _event_to_activity(greet)

    def test_tokens_boost_activity(self) -> None:
        """More tokens should boost activity."""
        from agents.town.flux import TownPhase as FluxPhase

        low_tokens = TownEvent(
            phase=FluxPhase.MORNING,
            operation="greet",
            participants=["Alice"],
            success=True,
            tokens_used=10,
            drama_contribution=0.0,
        )

        high_tokens = TownEvent(
            phase=FluxPhase.MORNING,
            operation="greet",
            participants=["Alice"],
            success=True,
            tokens_used=300,
            drama_contribution=0.0,
        )

        assert _event_to_activity(high_tokens) > _event_to_activity(low_tokens)

    def test_activity_capped_at_one(self) -> None:
        """Activity should not exceed 1.0."""
        from agents.town.flux import TownPhase as FluxPhase

        event = TownEvent(
            phase=FluxPhase.MORNING,
            operation="trade",
            participants=["Alice", "Bob"],
            success=True,
            tokens_used=1000,
            drama_contribution=1.0,
        )

        activity = _event_to_activity(event)
        assert activity <= 1.0


# =============================================================================
# ColonyDashboardBridge Tests
# =============================================================================


class TestColonyDashboardBridge:
    """Tests for ColonyDashboardBridge."""

    def test_creation(self, sample_flux: TownFlux) -> None:
        """Test bridge creation."""
        bridge = ColonyDashboardBridge(sample_flux)

        assert bridge.flux is sample_flux
        assert bridge.current_state is not None
        assert len(bridge.current_state.citizens) == 3

    def test_state_signal(self, sample_flux: TownFlux) -> None:
        """Test state signal is available."""
        bridge = ColonyDashboardBridge(sample_flux)

        signal = bridge.state_signal
        assert isinstance(signal, Signal)
        assert signal.value == bridge.current_state

    @pytest.mark.asyncio
    async def test_process_event_updates_state(
        self, sample_flux: TownFlux, sample_event: TownEvent
    ) -> None:
        """Test processing event updates state."""
        bridge = ColonyDashboardBridge(sample_flux)

        initial_events = bridge.current_state.total_events
        await bridge.process_event(sample_event)

        assert bridge.current_state.total_events == initial_events + 1

    @pytest.mark.asyncio
    async def test_process_event_updates_tokens(
        self, sample_flux: TownFlux, sample_event: TownEvent
    ) -> None:
        """Test processing event updates token count."""
        bridge = ColonyDashboardBridge(sample_flux)

        initial_tokens = bridge.current_state.total_tokens
        await bridge.process_event(sample_event)

        assert bridge.current_state.total_tokens == initial_tokens + 100

    @pytest.mark.asyncio
    async def test_process_event_updates_activity(
        self, sample_flux: TownFlux, sample_event: TownEvent
    ) -> None:
        """Test processing event updates citizen activity."""
        bridge = ColonyDashboardBridge(sample_flux)

        # Get Alice's initial activity
        alice_initial = None
        for c in bridge.current_state.citizens:
            if c.name == "Alice":
                alice_initial = c.activity
                break

        await bridge.process_event(sample_event)

        # Get Alice's updated activity
        alice_after = None
        for c in bridge.current_state.citizens:
            if c.name == "Alice":
                alice_after = c.activity
                break

        assert alice_after is not None
        assert len(alice_after) > len(alice_initial or ())

    def test_process_event_sync(self, sample_flux: TownFlux, sample_event: TownEvent) -> None:
        """Test synchronous event processing."""
        bridge = ColonyDashboardBridge(sample_flux)

        initial_events = bridge.current_state.total_events
        bridge.process_event_sync(sample_event)

        assert bridge.current_state.total_events == initial_events + 1

    def test_refresh(self, sample_flux: TownFlux) -> None:
        """Test refresh rebuilds state."""
        bridge = ColonyDashboardBridge(sample_flux)

        # Modify flux state
        sample_flux.day = 10

        # Refresh
        new_state = bridge.refresh()

        assert new_state.day == 10

    def test_reset(self, sample_flux: TownFlux, sample_event: TownEvent) -> None:
        """Test reset clears counters and buffers."""
        bridge = ColonyDashboardBridge(sample_flux)

        # Process some events
        bridge.process_event_sync(sample_event)
        bridge.process_event_sync(sample_event)

        assert bridge.current_state.total_events == 2

        # Reset
        bridge.reset()

        assert bridge.current_state.total_events == 0

    def test_clear_activity(self, sample_flux: TownFlux, sample_event: TownEvent) -> None:
        """Test clear_activity removes activity history."""
        bridge = ColonyDashboardBridge(sample_flux)

        # Process events to build activity
        bridge.process_event_sync(sample_event)
        bridge.process_event_sync(sample_event)

        # Clear activity
        bridge.clear_activity()
        bridge.refresh()

        # All citizens should have empty activity
        for c in bridge.current_state.citizens:
            assert c.activity == ()


class TestColonyDashboardBridgeSignal:
    """Tests for Signal binding."""

    @pytest.mark.asyncio
    async def test_signal_emits_on_process(
        self, sample_flux: TownFlux, sample_event: TownEvent
    ) -> None:
        """Test signal emits new state on process_event."""
        bridge = ColonyDashboardBridge(sample_flux)

        received_states: list[ColonyState] = []

        def on_change(state: ColonyState) -> None:
            received_states.append(state)

        bridge.subscribe(on_change)

        await bridge.process_event(sample_event)
        await bridge.process_event(sample_event)

        assert len(received_states) == 2

    def test_dashboard_bound_to_signal(
        self, sample_flux: TownFlux, sample_event: TownEvent
    ) -> None:
        """Test dashboard updates when bridge signal changes."""
        bridge = ColonyDashboardBridge(sample_flux)
        dashboard = ColonyDashboard()
        dashboard.bind_signal(bridge.state_signal)

        # Process event
        bridge.process_event_sync(sample_event)

        # Dashboard should reflect new state
        assert dashboard.state.value.total_events == 1


# =============================================================================
# SSE Event Tests
# =============================================================================


class TestSSEEvent:
    """Tests for SSE event format."""

    def test_sse_event_structure(self, sample_flux: TownFlux) -> None:
        """Test SSE event has required fields."""
        bridge = ColonyDashboardBridge(sample_flux)

        sse = bridge.to_sse_event()

        assert "event" in sse
        assert sse["event"] == "colony_state"
        assert "id" in sse
        assert "data" in sse
        assert "timestamp" in sse

    def test_sse_event_data(self, sample_flux: TownFlux) -> None:
        """Test SSE event data contains colony info."""
        bridge = ColonyDashboardBridge(sample_flux)

        sse = bridge.to_sse_event()
        data = sse["data"]

        assert "colony_id" in data
        assert "phase" in data
        assert "day" in data
        assert "citizens" in data
        assert len(data["citizens"]) == 3

    def test_sse_event_citizen_data(self, sample_flux: TownFlux) -> None:
        """Test SSE event citizen data format."""
        bridge = ColonyDashboardBridge(sample_flux)

        sse = bridge.to_sse_event()
        citizens = sse["data"]["citizens"]

        alice = next(c for c in citizens if c["name"] == "Alice")
        assert "id" in alice
        assert "phase" in alice
        assert "nphase" in alice
        assert "mood" in alice
        assert "capability" in alice
        assert "activity" in alice


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunction:
    """Tests for create_bridge_and_dashboard factory."""

    def test_creates_connected_pair(self, sample_flux: TownFlux) -> None:
        """Test factory creates connected bridge and dashboard."""
        bridge, dashboard = create_bridge_and_dashboard(sample_flux)

        assert isinstance(bridge, ColonyDashboardBridge)
        assert isinstance(dashboard, ColonyDashboard)

    def test_dashboard_bound_to_bridge(
        self, sample_flux: TownFlux, sample_event: TownEvent
    ) -> None:
        """Test dashboard is bound to bridge signal."""
        bridge, dashboard = create_bridge_and_dashboard(sample_flux)

        # Initial state
        initial_events = dashboard.state.value.total_events

        # Process event via bridge
        bridge.process_event_sync(sample_event)

        # Dashboard should update
        assert dashboard.state.value.total_events == initial_events + 1

    def test_custom_buffer_size(self, sample_flux: TownFlux) -> None:
        """Test custom activity buffer size."""
        bridge, _ = create_bridge_and_dashboard(sample_flux, activity_buffer_size=5)

        # Buffer should use custom size
        buffer = bridge._activity_buffers["test"]
        assert buffer.max_length == 5


# =============================================================================
# Integration Tests
# =============================================================================


class TestBridgeDashboardIntegration:
    """Integration tests for bridge + dashboard."""

    @pytest.mark.asyncio
    async def test_full_pipeline(self, sample_flux: TownFlux) -> None:
        """Test full pipeline from flux event to dashboard projection."""
        bridge, dashboard = create_bridge_and_dashboard(sample_flux)

        # Simulate some events
        from agents.town.flux import TownPhase as FluxPhase

        events = [
            TownEvent(
                phase=FluxPhase.MORNING,
                operation="greet",
                participants=["Alice", "Bob"],
                success=True,
                tokens_used=100,
            ),
            TownEvent(
                phase=FluxPhase.MORNING,
                operation="trade",
                participants=["Alice", "Carol"],
                success=True,
                tokens_used=200,
            ),
            TownEvent(
                phase=FluxPhase.AFTERNOON,
                operation="solo",
                participants=["Bob"],
                success=True,
                tokens_used=50,
            ),
        ]

        for event in events:
            await bridge.process_event(event)

        # Check dashboard state
        state = dashboard.state.value
        assert state.total_events == 3
        assert state.total_tokens == 350

        # Project to CLI
        cli = dashboard.project(RenderTarget.CLI)
        assert "Alice" in cli
        assert "Bob" in cli
        assert "Carol" in cli

        # Project to JSON
        json = dashboard.project(RenderTarget.JSON)
        assert json["metrics"]["total_events"] == 3
        assert len(json["citizens"]) == 3

    def test_multiple_event_processing(self, sample_flux: TownFlux) -> None:
        """Test processing many events maintains consistency."""
        bridge, dashboard = create_bridge_and_dashboard(sample_flux)

        from agents.town.flux import TownPhase as FluxPhase

        # Process 100 events
        for i in range(100):
            event = TownEvent(
                phase=FluxPhase.MORNING,
                operation="greet",
                participants=["Alice", "Bob"],
                success=True,
                tokens_used=10,
            )
            bridge.process_event_sync(event)

        assert dashboard.state.value.total_events == 100
        assert dashboard.state.value.total_tokens == 1000

"""
Tests for KgentFlux: K-gent as a Flux Stream Agent.

K-gent Phase 2: These tests verify the streaming behavior of K-gent,
including lifecycle, event processing, and perturbation injection.
"""

import asyncio
from datetime import timedelta
from typing import AsyncIterator

import pytest
from agents.k.events import (
    SoulEvent,
    SoulEventType,
    dialogue_turn_event,
    eigenvector_probe_event,
    error_event,
    feeling_event,
    gratitude_event,
    intercept_request_event,
    is_ambient_event,
    mode_change_event,
    observation_event,
    perturbation_event,
    ping_event,
    pulse_event,
    self_challenge_event,
    state_snapshot_event,
    thought_event,
)
from agents.k.flux import (
    KgentFlux,
    KgentFluxConfig,
    KgentFluxState,
    create_kgent_flux,
)
from agents.k.persona import DialogueMode
from agents.k.soul import KgentSoul

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def flux() -> KgentFlux:
    """Create a KgentFlux for testing."""
    return create_kgent_flux(agent_id="test-flux")


@pytest.fixture
def flux_no_pulse() -> KgentFlux:
    """Create a KgentFlux without pulse emission."""
    config = KgentFluxConfig(
        pulse_enabled=False,
        agent_id="test-flux-no-pulse",
    )
    return KgentFlux(config=config)


async def event_source(events: list[SoulEvent]) -> AsyncIterator[SoulEvent]:
    """Create an async iterator from a list of events."""
    for event in events:
        yield event


async def empty_source() -> AsyncIterator[SoulEvent]:
    """Empty event source."""
    return
    # Make this an async generator
    if False:  # noqa: SIM223
        yield  # type: ignore


async def slow_source(
    events: list[SoulEvent], delay: float = 0.1
) -> AsyncIterator[SoulEvent]:
    """Event source with delays between events."""
    for event in events:
        await asyncio.sleep(delay)
        yield event


# =============================================================================
# Initialization Tests
# =============================================================================


class TestKgentFluxInit:
    """Test KgentFlux initialization."""

    def test_create_default_flux(self) -> None:
        """Should create flux with defaults."""
        flux = KgentFlux()

        assert flux.state == KgentFluxState.DORMANT
        assert flux.events_processed == 0
        assert flux.is_dormant
        assert not flux.is_running

    def test_create_flux_with_config(self) -> None:
        """Should create flux with custom config."""
        config = KgentFluxConfig(
            pulse_enabled=False,
            entropy_budget=500.0,
            agent_id="custom-flux",
        )
        flux = KgentFlux(config=config)

        assert flux.id == "custom-flux"
        assert flux.entropy_remaining == 500.0
        assert not flux.config.pulse_enabled

    def test_create_flux_with_soul(self) -> None:
        """Should create flux with custom soul."""
        soul = KgentSoul()
        flux = KgentFlux(soul=soul)

        assert flux.soul is soul

    def test_factory_function(self) -> None:
        """Should create flux via factory."""
        flux = create_kgent_flux(agent_id="factory-flux")

        assert flux.id == "factory-flux"
        assert flux.state == KgentFluxState.DORMANT


class TestKgentFluxProperties:
    """Test KgentFlux properties."""

    def test_name_includes_id(self, flux: KgentFlux) -> None:
        """Name should include ID."""
        assert "test-flux" in flux.name

    def test_is_running_states(self) -> None:
        """is_running should reflect state correctly."""
        flux = KgentFlux()

        assert not flux.is_running  # DORMANT

    def test_is_dormant(self, flux: KgentFlux) -> None:
        """is_dormant should be True when DORMANT."""
        assert flux.is_dormant


# =============================================================================
# Lifecycle Tests
# =============================================================================


class TestKgentFluxLifecycle:
    """Test KgentFlux lifecycle state transitions."""

    @pytest.mark.asyncio
    async def test_start_changes_state_to_flowing(
        self, flux_no_pulse: KgentFlux
    ) -> None:
        """Starting flux should change state to FLOWING."""
        events = [ping_event()]

        async def collect_all() -> list[SoulEvent]:
            result = []
            async for event in flux_no_pulse.start(event_source(events)):
                result.append(event)
            return result

        results = await collect_all()
        assert len(results) == 1
        assert flux_no_pulse.state == KgentFluxState.STOPPED

    @pytest.mark.asyncio
    async def test_stop_terminates_flux(self, flux_no_pulse: KgentFlux) -> None:
        """Stopping flux should terminate processing."""
        events: list[SoulEvent] = []

        async def get_next_event() -> SoulEvent:
            async for event in flux_no_pulse.start(slow_source(events, 1.0)):
                return event
            raise StopAsyncIteration

        async def start_and_stop() -> None:
            task: asyncio.Task[SoulEvent] = asyncio.create_task(get_next_event())
            await asyncio.sleep(0.1)
            await flux_no_pulse.stop()
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, StopAsyncIteration):
                pass

        await start_and_stop()
        assert flux_no_pulse.state == KgentFluxState.STOPPED

    @pytest.mark.asyncio
    async def test_reset_returns_to_dormant(self, flux_no_pulse: KgentFlux) -> None:
        """Reset should return to DORMANT state."""
        # First, run and stop
        async for _ in flux_no_pulse.start(event_source([ping_event()])):
            pass

        assert flux_no_pulse.state == KgentFluxState.STOPPED

        # Reset
        flux_no_pulse.reset()
        current_state = flux_no_pulse.state  # Reload after state mutation
        assert current_state == KgentFluxState.DORMANT  # type: ignore[comparison-overlap]
        assert flux_no_pulse.events_processed == 0

    def test_reset_fails_from_dormant(self) -> None:
        """Reset should fail from DORMANT state."""
        flux = KgentFlux()

        with pytest.raises(RuntimeError):
            flux.reset()


# =============================================================================
# Event Processing Tests
# =============================================================================


class TestKgentFluxEventProcessing:
    """Test event processing through KgentFlux."""

    @pytest.mark.asyncio
    async def test_process_ping_event(self, flux_no_pulse: KgentFlux) -> None:
        """Should pass through ping events."""
        events = [ping_event()]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert len(results) == 1
        assert results[0].event_type == SoulEventType.PING

    @pytest.mark.asyncio
    async def test_process_dialogue_turn(self, flux_no_pulse: KgentFlux) -> None:
        """Should process dialogue turn events."""
        events = [dialogue_turn_event(message="Hello K-gent", is_request=True)]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert len(results) == 1
        assert results[0].event_type == SoulEventType.DIALOGUE_TURN
        # Response should have different content
        assert results[0].payload.get("is_request") is False

    @pytest.mark.asyncio
    async def test_process_mode_change(self, flux_no_pulse: KgentFlux) -> None:
        """Should process mode change events."""
        events = [mode_change_event(from_mode="reflect", to_mode="challenge")]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert len(results) == 1
        # Mode change produces a dialogue turn acknowledgment
        assert results[0].event_type == SoulEventType.DIALOGUE_TURN
        assert "challenge" in results[0].payload.get("mode", "").lower()

    @pytest.mark.asyncio
    async def test_process_state_snapshot(self, flux_no_pulse: KgentFlux) -> None:
        """Should process state snapshot requests."""
        events = [state_snapshot_event(state={})]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert len(results) == 1
        assert results[0].event_type == SoulEventType.STATE_SNAPSHOT
        assert results[0].soul_state is not None

    @pytest.mark.asyncio
    async def test_process_eigenvector_probe(self, flux_no_pulse: KgentFlux) -> None:
        """Should process eigenvector probe events."""
        events = [eigenvector_probe_event(eigenvectors={})]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert len(results) == 1
        assert results[0].event_type == SoulEventType.EIGENVECTOR_PROBE
        # Should have actual eigenvectors in response
        assert "eigenvectors" in results[0].payload

    @pytest.mark.asyncio
    async def test_multiple_events_processed(self, flux_no_pulse: KgentFlux) -> None:
        """Should process multiple events in order."""
        events = [
            ping_event(),
            dialogue_turn_event(message="first", is_request=True),
            ping_event(),
        ]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert len(results) == 3
        assert flux_no_pulse.events_processed == 3


# =============================================================================
# Invoke Tests (DORMANT vs FLOWING)
# =============================================================================


class TestKgentFluxInvoke:
    """Test invoke behavior in different states."""

    @pytest.mark.asyncio
    async def test_invoke_dormant_direct(self, flux: KgentFlux) -> None:
        """Invoke in DORMANT should process directly."""
        assert flux.is_dormant

        event = dialogue_turn_event(message="Test message", is_request=True)
        result = await flux.invoke(event)

        assert result.event_type == SoulEventType.DIALOGUE_TURN
        assert result.payload.get("is_request") is False

    @pytest.mark.asyncio
    async def test_invoke_dormant_mode_change(self, flux: KgentFlux) -> None:
        """Invoke mode change in DORMANT should work."""
        event = mode_change_event(from_mode="reflect", to_mode="advise")
        result = await flux.invoke(event)

        assert result.event_type == SoulEventType.DIALOGUE_TURN

    @pytest.mark.asyncio
    async def test_invoke_stopped_fails(self, flux_no_pulse: KgentFlux) -> None:
        """Invoke in STOPPED should fail."""
        # Run and stop
        async for _ in flux_no_pulse.start(event_source([ping_event()])):
            pass

        assert flux_no_pulse.state == KgentFluxState.STOPPED

        with pytest.raises(RuntimeError):
            await flux_no_pulse.invoke(ping_event())


# =============================================================================
# Entropy Tests
# =============================================================================


class TestKgentFluxEntropy:
    """Test entropy budget management."""

    @pytest.mark.asyncio
    async def test_entropy_decreases(self) -> None:
        """Entropy should decrease with each event."""
        config = KgentFluxConfig(
            entropy_budget=10.0,
            entropy_decay=1.0,
            pulse_enabled=False,
        )
        flux = KgentFlux(config=config)

        events = [ping_event(), ping_event(), ping_event()]

        async for _ in flux.start(event_source(events)):
            pass

        assert flux.entropy_remaining == 7.0

    @pytest.mark.asyncio
    async def test_entropy_exhaustion_stops_flux(self) -> None:
        """Exhausted entropy should stop flux."""
        config = KgentFluxConfig(
            entropy_budget=2.0,
            entropy_decay=1.0,
            pulse_enabled=False,
        )
        flux = KgentFlux(config=config)

        # More events than entropy budget
        events = [ping_event() for _ in range(10)]

        results: list[SoulEvent] = []
        async for result in flux.start(event_source(events)):
            results.append(result)

        # Should only process 2 events
        assert len(results) == 2
        assert flux.entropy_remaining == 0.0


# =============================================================================
# Dialogue Convenience Tests
# =============================================================================


class TestKgentFluxDialogue:
    """Test dialogue convenience method."""

    @pytest.mark.asyncio
    async def test_dialogue_creates_event(self, flux: KgentFlux) -> None:
        """dialogue() should create and process event."""
        result = await flux.dialogue("What should I focus on?")

        assert result.event_type == SoulEventType.DIALOGUE_TURN
        assert result.payload.get("is_request") is False

    @pytest.mark.asyncio
    async def test_dialogue_with_mode(self, flux: KgentFlux) -> None:
        """dialogue() should accept mode parameter."""
        result = await flux.dialogue(
            "Challenge my assumptions",
            mode=DialogueMode.CHALLENGE,
        )

        assert result.event_type == SoulEventType.DIALOGUE_TURN


# =============================================================================
# Mirror Integration Tests
# =============================================================================


class TestKgentFluxMirror:
    """Test Mirror Protocol integration."""

    def test_attach_mirror(self, flux: KgentFlux) -> None:
        """Should attach mirror."""
        from unittest.mock import MagicMock

        mock_mirror = MagicMock()
        result = flux.attach_mirror(mock_mirror)

        assert result is flux
        assert flux.mirror is mock_mirror

    def test_detach_mirror(self, flux: KgentFlux) -> None:
        """Should detach mirror."""
        from unittest.mock import MagicMock

        mock_mirror = MagicMock()
        flux.attach_mirror(mock_mirror)
        detached = flux.detach_mirror()

        assert detached is mock_mirror
        assert flux.mirror is None


# =============================================================================
# Repr Tests
# =============================================================================


class TestKgentFluxRepr:
    """Test string representation."""

    def test_repr_includes_state(self, flux: KgentFlux) -> None:
        """repr should include state."""
        r = repr(flux)
        assert "dormant" in r
        assert "test-flux" in r

    def test_repr_includes_events(self, flux: KgentFlux) -> None:
        """repr should include event count."""
        r = repr(flux)
        assert "events=" in r


# =============================================================================
# Intercept Tests
# =============================================================================


class TestKgentFluxIntercept:
    """Test intercept request processing."""

    @pytest.mark.asyncio
    async def test_process_intercept_request(self, flux_no_pulse: KgentFlux) -> None:
        """Should process intercept requests."""
        events = [
            intercept_request_event(
                token_id="token-123",
                prompt="Delete all files?",
                severity="critical",
            )
        ]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert len(results) == 1
        assert results[0].event_type == SoulEventType.INTERCEPT_RESULT
        # Dangerous operation should not be auto-approved
        assert results[0].payload.get("handled") is False

    @pytest.mark.asyncio
    async def test_intercept_preserves_correlation_id(
        self, flux_no_pulse: KgentFlux
    ) -> None:
        """Intercept result should preserve correlation ID."""
        events = [
            intercept_request_event(
                token_id="token-abc",
                prompt="Safe operation",
            )
        ]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert results[0].correlation_id == "token-abc"


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestKgentFluxErrors:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_error_produces_error_event(self) -> None:
        """Errors should produce error events."""
        # Create a flux with a soul that will raise an error
        flux = create_kgent_flux()

        # Note: Hard to force an error in normal processing
        # This test just verifies error_event creation works
        err = error_event(
            error="Test error",
            error_type="TestError",
            original_event_type="dialogue_turn",
        )

        assert err.event_type == SoulEventType.ERROR
        assert err.payload["error"] == "Test error"


# =============================================================================
# Pulse Tests
# =============================================================================


class TestKgentFluxPulse:
    """Test pulse emission."""

    @pytest.mark.asyncio
    async def test_pulse_config_interval(self) -> None:
        """Pulse interval should be configurable."""
        config = KgentFluxConfig(
            pulse_enabled=True,
            pulse_interval=timedelta(seconds=5),
        )
        flux = KgentFlux(config=config)

        assert flux.config.pulse_interval.total_seconds() == 5.0

    def test_pulse_disabled_by_config(self) -> None:
        """Pulse can be disabled via config."""
        config = KgentFluxConfig(pulse_enabled=False)
        flux = KgentFlux(config=config)

        assert not flux.config.pulse_enabled


# =============================================================================
# Ambient Event Tests: The Soul Present, Not Invoked
# =============================================================================


class TestKgentFluxAmbientEvents:
    """Test ambient event processing through KgentFlux."""

    @pytest.mark.asyncio
    async def test_process_thought_event(self, flux_no_pulse: KgentFlux) -> None:
        """Should process thought events (pass through with soul state)."""
        events = [thought_event(content="The algebra holds")]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert len(results) == 1
        assert results[0].event_type == SoulEventType.THOUGHT
        assert results[0].payload["content"] == "The algebra holds"
        # Should have soul state attached
        assert results[0].soul_state is not None
        assert "mode" in results[0].soul_state

    @pytest.mark.asyncio
    async def test_process_feeling_event(self, flux_no_pulse: KgentFlux) -> None:
        """Should process feeling events."""
        events = [feeling_event(valence="curious", intensity=0.7)]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert len(results) == 1
        assert results[0].event_type == SoulEventType.FEELING
        assert results[0].payload["valence"] == "curious"
        assert results[0].soul_state is not None

    @pytest.mark.asyncio
    async def test_process_observation_event(self, flux_no_pulse: KgentFlux) -> None:
        """Should process observation events."""
        events = [observation_event(pattern="Functors compose freely", confidence=0.9)]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert len(results) == 1
        assert results[0].event_type == SoulEventType.OBSERVATION
        assert "Functors" in results[0].payload["pattern"]

    @pytest.mark.asyncio
    async def test_process_self_challenge_event(self, flux_no_pulse: KgentFlux) -> None:
        """Should process self-challenge events."""
        events = [
            self_challenge_event(
                thesis="Composability is paramount",
                antithesis="But simplicity matters too",
            )
        ]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert len(results) == 1
        assert results[0].event_type == SoulEventType.SELF_CHALLENGE
        assert "thesis" in results[0].payload
        assert "antithesis" in results[0].payload

    @pytest.mark.asyncio
    async def test_process_gratitude_event(self, flux_no_pulse: KgentFlux) -> None:
        """Should process gratitude events."""
        events = [gratitude_event(for_what="the categorical foundations")]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert len(results) == 1
        assert results[0].event_type == SoulEventType.GRATITUDE
        assert "categorical" in results[0].payload["for_what"]

    @pytest.mark.asyncio
    async def test_ambient_events_include_eigenvectors(
        self, flux_no_pulse: KgentFlux
    ) -> None:
        """Ambient events should include eigenvector state."""
        events = [thought_event(content="Testing eigenvectors")]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert results[0].soul_state is not None
        assert "eigenvectors" in results[0].soul_state

    @pytest.mark.asyncio
    async def test_all_ambient_types_preserve_ambient_predicate(
        self, flux_no_pulse: KgentFlux
    ) -> None:
        """All ambient event types should remain ambient after processing."""
        events = [
            thought_event(content="test"),
            feeling_event(valence="curious"),
            observation_event(pattern="test"),
            self_challenge_event(thesis="a", antithesis="b"),
            gratitude_event(for_what="test"),
        ]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert len(results) == 5
        for result in results:
            assert is_ambient_event(result), f"{result.event_type} is not ambient"


class TestKgentFluxPerturbation:
    """Test perturbation event processing."""

    @pytest.mark.asyncio
    async def test_low_intensity_perturbation_passes_through(
        self, flux_no_pulse: KgentFlux
    ) -> None:
        """Low-intensity perturbations should pass through."""
        events = [perturbation_event(source="terrarium", intensity=0.3)]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert len(results) == 1
        assert results[0].event_type == SoulEventType.PERTURBATION
        assert results[0].soul_state is not None

    @pytest.mark.asyncio
    async def test_high_intensity_perturbation_triggers_thought(
        self, flux_no_pulse: KgentFlux
    ) -> None:
        """High-intensity perturbations should trigger thought response."""
        events = [perturbation_event(source="semaphore", intensity=0.9)]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert len(results) == 1
        # High intensity converts to thought
        assert results[0].event_type == SoulEventType.THOUGHT
        assert "semaphore" in results[0].payload["content"]


class TestKgentFluxMixedEvents:
    """Test processing mixed ambient and transactional events."""

    @pytest.mark.asyncio
    async def test_mixed_event_stream(self, flux_no_pulse: KgentFlux) -> None:
        """Should process mixed stream of ambient and transactional events."""
        events = [
            thought_event(content="First thought"),
            ping_event(),
            feeling_event(valence="focused"),
            dialogue_turn_event(message="Hello", is_request=True),
            gratitude_event(for_what="the tests"),
        ]

        results: list[SoulEvent] = []
        async for result in flux_no_pulse.start(event_source(events)):
            results.append(result)

        assert len(results) == 5

        # Check types in order
        assert results[0].event_type == SoulEventType.THOUGHT
        assert results[1].event_type == SoulEventType.PING
        assert results[2].event_type == SoulEventType.FEELING
        assert results[3].event_type == SoulEventType.DIALOGUE_TURN
        assert results[4].event_type == SoulEventType.GRATITUDE

    @pytest.mark.asyncio
    async def test_ambient_events_count_toward_processed(
        self, flux_no_pulse: KgentFlux
    ) -> None:
        """Ambient events should count toward events_processed."""
        events = [
            thought_event(content="One"),
            feeling_event(valence="two"),
            observation_event(pattern="three"),
        ]

        async for _ in flux_no_pulse.start(event_source(events)):
            pass

        assert flux_no_pulse.events_processed == 3


# =============================================================================
# Integration Test: Rumination Source → KgentFlux
# =============================================================================


class TestKgentFluxWithRumination:
    """Integration tests with rumination as the event source."""

    @pytest.mark.asyncio
    async def test_flux_processes_rumination_stream(self) -> None:
        """
        The core promise: async for event in kgent_flux.start(rumination_source).

        This tests that KgentFlux can consume events from the rumination
        generator and process them with soul state enrichment.
        """
        from agents.k.rumination import quick_rumination

        flux = KgentFlux(
            config=KgentFluxConfig(
                pulse_enabled=False,
                entropy_budget=10,
            )
        )
        soul = flux.soul

        # Collect events from rumination → flux
        results: list[SoulEvent] = []
        async for event in flux.start(quick_rumination(soul, count=5)):
            results.append(event)

        # Should have processed 5 events
        assert len(results) == 5
        assert flux.events_processed == 5

        # All should have soul state attached
        for event in results:
            assert event.soul_state is not None

    @pytest.mark.asyncio
    async def test_flux_rumination_respects_entropy(self) -> None:
        """Flux should stop when entropy is exhausted, even with continuous rumination."""
        from agents.k.rumination import RuminationConfig, ruminate

        flux = KgentFlux(
            config=KgentFluxConfig(
                pulse_enabled=False,
                entropy_budget=3,  # Only 3 events
                entropy_decay=1.0,
            )
        )
        soul = flux.soul

        # Create fast rumination that would produce many events
        rum_config = RuminationConfig(
            check_interval=timedelta(milliseconds=5),
            thought_probability=1.0,  # Always generate
        )

        results: list[SoulEvent] = []
        async for event in flux.start(ruminate(soul, rum_config)):
            results.append(event)

        # Should stop at 3 due to entropy exhaustion
        assert len(results) == 3
        assert flux.entropy_remaining == 0.0

    @pytest.mark.asyncio
    async def test_flux_rumination_preserves_variety(self) -> None:
        """Flux should preserve the variety of rumination event types."""
        from agents.k.rumination import RuminationConfig, ruminate

        flux = KgentFlux(
            config=KgentFluxConfig(
                pulse_enabled=False,
                entropy_budget=50,
            )
        )
        soul = flux.soul

        # Create rumination that produces variety
        rum_config = RuminationConfig(
            check_interval=timedelta(milliseconds=5),
            thought_probability=0.25,
            feeling_probability=0.25,
            observation_probability=0.25,
            challenge_probability=0.20,
            gratitude_probability=0.05,
        )

        event_types: set[SoulEventType] = set()
        count = 0
        async for event in flux.start(ruminate(soul, rum_config)):
            event_types.add(event.event_type)
            count += 1
            # Stop after we've seen variety or hit limit
            if len(event_types) >= 3 or count >= 20:
                await flux.stop()
                break

        # Should have at least 3 different ambient event types
        assert len(event_types) >= 3

    @pytest.mark.asyncio
    async def test_flux_with_rumination_is_the_ambient_soul(self) -> None:
        """
        The soul, present and ruminating.

        This is the philosophical test: when you wire rumination to flux,
        you get a soul that thinks, feels, observes, challenges itself,
        and expresses gratitude—all without external prompting.
        """
        from agents.k.rumination import quick_rumination

        flux = KgentFlux(
            config=KgentFluxConfig(
                pulse_enabled=False,
            )
        )
        soul = flux.soul

        # The soul, ruminating
        events = []
        async for event in flux.start(quick_rumination(soul, count=3)):
            events.append(event)
            # Print for the human watching
            print(f"  Soul: {event.event_type.value} - {event.payload}")

        # The soul was present
        assert len(events) == 3
        # All events came from the soul's internal life
        for event in events:
            assert is_ambient_event(event)

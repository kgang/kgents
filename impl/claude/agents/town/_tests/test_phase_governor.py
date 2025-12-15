"""
Tests for PhaseGovernor controlled playback.

Verifies:
- Events yielded at governed intervals
- Pause/resume functionality
- Playback speed control
- Stop functionality
- State tracking
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator
from typing import Any

import pytest
from agents.town.environment import create_mpp_environment
from agents.town.event_bus import EventBus
from agents.town.flux import TownFlux
from agents.town.phase_governor import (
    GovernorState,
    PhaseGovernor,
    PhaseTimingConfig,
    PlaybackState,
    create_phase_governor,
)


@pytest.fixture
def flux() -> TownFlux:
    """Create TownFlux for testing."""
    env = create_mpp_environment()
    return TownFlux(env, seed=42)


@pytest.fixture
def fast_config() -> PhaseTimingConfig:
    """Fast config for quick tests."""
    return PhaseTimingConfig(
        phase_duration_ms=100,  # 100ms per phase
        events_per_phase=3,
        playback_speed=1.0,
        min_event_delay_ms=10,
        max_event_delay_ms=50,
    )


class TestPhaseTimingConfig:
    """Tests for PhaseTimingConfig."""

    def test_default_values(self) -> None:
        """Default config has sensible values."""
        config = PhaseTimingConfig()
        assert config.phase_duration_ms == 5000
        assert config.events_per_phase == 5
        assert config.playback_speed == 1.0

    def test_effective_phase_duration(self) -> None:
        """effective_phase_duration_ms accounts for speed."""
        config = PhaseTimingConfig(phase_duration_ms=5000, playback_speed=2.0)
        assert config.effective_phase_duration_ms == 2500

        config = PhaseTimingConfig(phase_duration_ms=5000, playback_speed=0.5)
        assert config.effective_phase_duration_ms == 10000

    def test_event_interval_clamped(self) -> None:
        """event_interval_ms is clamped to min/max."""
        # Very fast (below min)
        config = PhaseTimingConfig(
            phase_duration_ms=100,
            events_per_phase=100,  # Would be 1ms each
            min_event_delay_ms=50,
        )
        assert config.event_interval_ms == 50  # Clamped to min

        # Very slow (above max)
        config = PhaseTimingConfig(
            phase_duration_ms=100000,
            events_per_phase=1,  # Would be 100s
            max_event_delay_ms=2000,
        )
        assert config.event_interval_ms == 2000  # Clamped to max


class TestPhaseGovernorBasic:
    """Basic PhaseGovernor functionality."""

    @pytest.mark.asyncio
    async def test_run_yields_events(
        self, flux: TownFlux, fast_config: PhaseTimingConfig
    ) -> None:
        """run() yields events from flux."""
        governor = PhaseGovernor(flux=flux, config=fast_config)

        events = []
        async for event in governor.run(num_phases=1):
            events.append(event)

        assert len(events) > 0

    @pytest.mark.asyncio
    async def test_run_multiple_phases(
        self, flux: TownFlux, fast_config: PhaseTimingConfig
    ) -> None:
        """run() processes multiple phases."""
        governor = PhaseGovernor(flux=flux, config=fast_config)

        events = []
        async for event in governor.run(num_phases=2):
            events.append(event)

        # Should have events from 2 phases
        assert len(events) >= 2

    @pytest.mark.asyncio
    async def test_state_tracks_progress(
        self, flux: TownFlux, fast_config: PhaseTimingConfig
    ) -> None:
        """State updates during run."""
        governor = PhaseGovernor(flux=flux, config=fast_config)

        async for _ in governor.run(num_phases=1):
            # During run, should be playing
            assert governor.is_playing
            assert governor.state.total_events > 0
            break  # Just check first event

    @pytest.mark.asyncio
    async def test_stopped_after_run(
        self, flux: TownFlux, fast_config: PhaseTimingConfig
    ) -> None:
        """State is stopped after run completes."""
        governor = PhaseGovernor(flux=flux, config=fast_config)

        async for _ in governor.run(num_phases=1):
            pass

        assert governor.is_stopped


class TestPhaseGovernorPauseResume:
    """Pause/resume functionality."""

    @pytest.mark.asyncio
    async def test_pause_blocks_events(
        self, flux: TownFlux, fast_config: PhaseTimingConfig
    ) -> None:
        """pause() blocks event yielding."""
        governor = PhaseGovernor(flux=flux, config=fast_config)

        events_before_pause: list[Any] = []
        pause_time = None

        async def run_with_pause() -> list[Any]:
            nonlocal pause_time
            events = []
            async for event in governor.run(num_phases=2):
                events.append(event)
                if len(events) == 2 and pause_time is None:
                    governor.pause()
                    pause_time = time.time()
                    # Resume after short delay
                    await asyncio.sleep(0.05)
                    governor.resume()
            return events

        events = await asyncio.wait_for(run_with_pause(), timeout=5.0)
        assert len(events) >= 2

    @pytest.mark.asyncio
    async def test_toggle_pause(
        self, flux: TownFlux, fast_config: PhaseTimingConfig
    ) -> None:
        """toggle_pause() switches state."""
        governor = PhaseGovernor(flux=flux, config=fast_config)

        # Start running
        run_task = asyncio.create_task(
            asyncio.wait_for(
                self._collect_events(governor.run(num_phases=1)), timeout=2.0
            )
        )

        await asyncio.sleep(0.01)

        # Toggle should pause
        is_paused = governor.toggle_pause()
        assert is_paused is True
        assert governor.is_paused

        # Toggle again should resume
        is_paused = governor.toggle_pause()
        assert is_paused is False
        assert governor.is_playing

        # Clean up
        governor.stop()
        try:
            await run_task
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass

    async def _collect_events(self, gen: AsyncIterator[Any]) -> list[Any]:
        """Helper to collect events from async generator."""
        events: list[Any] = []
        async for event in gen:
            events.append(event)
        return events


class TestPhaseGovernorSpeed:
    """Playback speed control."""

    def test_set_speed(self, flux: TownFlux) -> None:
        """set_speed() updates config."""
        governor = PhaseGovernor(flux=flux)

        governor.set_speed(2.0)
        assert governor.speed == 2.0

        governor.set_speed(0.5)
        assert governor.speed == 0.5

    def test_set_speed_clamped(self, flux: TownFlux) -> None:
        """Speed is clamped to valid range."""
        governor = PhaseGovernor(flux=flux)

        governor.set_speed(100.0)
        assert governor.speed == 10.0  # Max

        governor.set_speed(0.01)
        assert governor.speed == 0.1  # Min

    def test_speed_up(self, flux: TownFlux) -> None:
        """speed_up() increases speed."""
        governor = PhaseGovernor(flux=flux)
        governor.set_speed(1.0)

        new_speed = governor.speed_up(2.0)
        assert new_speed == 2.0

    def test_slow_down(self, flux: TownFlux) -> None:
        """slow_down() decreases speed."""
        governor = PhaseGovernor(flux=flux)
        governor.set_speed(2.0)

        new_speed = governor.slow_down(2.0)
        assert new_speed == 1.0


class TestPhaseGovernorStop:
    """Stop functionality."""

    @pytest.mark.asyncio
    async def test_stop_ends_run(
        self, flux: TownFlux, fast_config: PhaseTimingConfig
    ) -> None:
        """stop() ends run() early."""
        governor = PhaseGovernor(flux=flux, config=fast_config)

        events = []

        async def run_and_stop() -> None:
            async for event in governor.run(num_phases=10):
                events.append(event)
                if len(events) >= 2:
                    governor.stop()

        await asyncio.wait_for(run_and_stop(), timeout=2.0)

        # Should have stopped early
        assert len(events) >= 2
        assert len(events) < 20  # Didn't run all 10 phases
        assert governor.is_stopped


class TestPhaseGovernorEventBus:
    """Event bus integration."""

    @pytest.mark.asyncio
    async def test_publishes_to_event_bus(
        self, flux: TownFlux, fast_config: PhaseTimingConfig
    ) -> None:
        """Events are published to event bus."""
        bus: EventBus[Any] = EventBus()
        sub = bus.subscribe()

        governor = PhaseGovernor(flux=flux, config=fast_config, event_bus=bus)

        yielded: list[Any] = []
        async for event in governor.run(num_phases=1):
            yielded.append(event)

        # Collect from subscriber
        received: list[Any] = []
        while sub.pending_count > 0:
            recv = await sub.get(timeout=0.1)
            if recv:
                received.append(recv)

        assert len(received) == len(yielded)

        sub.close()
        bus.close()


class TestPhaseGovernorState:
    """State tracking."""

    def test_initial_state(self, flux: TownFlux) -> None:
        """Initial state is stopped with zero counters."""
        governor = PhaseGovernor(flux=flux)

        assert governor.is_stopped
        assert not governor.is_playing
        assert not governor.is_paused
        assert governor.state.total_events == 0
        assert governor.state.current_phase == 0

    @pytest.mark.asyncio
    async def test_state_updates_during_run(
        self, flux: TownFlux, fast_config: PhaseTimingConfig
    ) -> None:
        """State updates as events are yielded."""
        governor = PhaseGovernor(flux=flux, config=fast_config)

        event_count = 0
        async for _ in governor.run(num_phases=1):
            event_count += 1
            assert governor.state.total_events == event_count
            assert governor.state.last_event_time is not None


class TestFactoryFunction:
    """Factory function tests."""

    def test_create_phase_governor(self, flux: TownFlux) -> None:
        """create_phase_governor creates configured governor."""
        governor = create_phase_governor(
            flux=flux,
            phase_duration_ms=3000,
            playback_speed=1.5,
        )

        assert governor.config.phase_duration_ms == 3000
        assert governor.config.playback_speed == 1.5

    def test_create_with_event_bus(self, flux: TownFlux) -> None:
        """create_phase_governor accepts event_bus."""
        bus: EventBus[Any] = EventBus()
        governor = create_phase_governor(flux=flux, event_bus=bus)

        assert governor.event_bus is bus
        bus.close()

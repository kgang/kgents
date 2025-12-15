"""
Tests for FactoryBridge (Micro-Experience Factory).

Phase: IMPLEMENT
Crown Jewel: plans/micro-experience-factory.md

Test Categories:
1. Bridge initialization and environment-to-scatter conversion
2. Flux event streaming to isometric updates
3. Perturbation pad handling
4. Replay bar rendering
"""

from __future__ import annotations

import pytest
from agents.town.environment import create_mpp_environment, create_phase2_environment
from agents.town.factory_bridge import (
    FactoryBridge,
    FactoryBridgeConfig,
    render_replay_bar,
)
from agents.town.flux import TownFlux
from agents.town.isometric import IsometricState
from agents.town.trace_bridge import ReplayState, TownTrace

# =============================================================================
# FactoryBridge Initialization Tests
# =============================================================================


class TestFactoryBridgeInit:
    """Tests for FactoryBridge initialization."""

    def test_creates_with_flux(self) -> None:
        """Bridge initializes from flux."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        assert bridge.flux is flux
        assert bridge.widget is not None
        assert bridge.config is not None

    def test_uses_custom_config(self) -> None:
        """Bridge accepts custom config."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        config = FactoryBridgeConfig(grid_width=10, grid_height=10)
        bridge = FactoryBridge(flux, config)

        assert bridge.config.grid_width == 10
        assert bridge.config.grid_height == 10

    def test_initial_state_has_citizens(self) -> None:
        """Initial state contains citizens from environment."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        state = bridge.get_state()
        # MPP environment has 3 citizens
        assert len(state.cells) == 3

    def test_phase2_environment(self) -> None:
        """Bridge works with Phase 2 environment (7 citizens)."""
        env = create_phase2_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        state = bridge.get_state()
        # Phase 2 has 7 citizens
        assert len(state.cells) == 7


# =============================================================================
# Environment to Scatter Conversion Tests
# =============================================================================


class TestEnvironmentToScatter:
    """Tests for environment-to-scatter conversion."""

    def test_citizens_become_points(self) -> None:
        """Each citizen becomes a scatter point."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        # Access internal method for testing
        scatter = bridge._environment_to_scatter(env)

        assert len(scatter.points) == len(env.citizens)

    def test_eigenvectors_preserved(self) -> None:
        """Eigenvector values are preserved in scatter points."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        scatter = bridge._environment_to_scatter(env)

        for point in scatter.points:
            citizen = env.citizens.get(point.citizen_id)
            assert citizen is not None
            assert point.warmth == citizen.eigenvectors.warmth
            assert point.trust == citizen.eigenvectors.trust

    def test_archetype_colors(self) -> None:
        """Archetypes get assigned colors."""
        env = create_phase2_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        # Test known archetype color
        scholar_color = bridge._archetype_color("Scholar")
        assert scholar_color == "#3b82f6"

        # Unknown archetypes get default color
        unknown_color = bridge._archetype_color("UnknownType")
        assert unknown_color == "#64748b"


# =============================================================================
# Flux Event Streaming Tests
# =============================================================================


class TestFluxStreaming:
    """Tests for flux event streaming."""

    @pytest.mark.asyncio
    async def test_run_yields_frames(self) -> None:
        """run() yields ASCII frames."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        frames: list[str] = []
        async for frame in bridge.run(num_phases=1):
            frames.append(frame)

        # Should have at least initial frame + events
        assert len(frames) >= 1
        # Frames contain ASCII art
        assert "ISOMETRIC FACTORY" in frames[0]

    @pytest.mark.asyncio
    async def test_run_updates_tick(self) -> None:
        """run() advances the tick counter."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        initial_tick = bridge.get_state().current_tick

        # Run one phase
        async for _ in bridge.run(num_phases=1):
            pass

        final_tick = bridge.get_state().current_tick
        assert final_tick > initial_tick

    @pytest.mark.asyncio
    async def test_run_records_trace(self) -> None:
        """run() records events in trace."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        # Run one phase
        async for _ in bridge.run(num_phases=1):
            pass

        # Trace should have events
        assert len(flux.trace.events) > 0


# =============================================================================
# Perturbation Pad Tests
# =============================================================================


class TestPerturbation:
    """Tests for perturbation pad handling."""

    @pytest.mark.asyncio
    async def test_perturb_greet(self) -> None:
        """Perturbing with 'greet' triggers greet operation."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        event = await bridge.perturb("greet")

        assert event is not None
        assert event.operation == "greet"
        assert event.metadata.get("perturbation") is True

    @pytest.mark.asyncio
    async def test_perturb_gossip(self) -> None:
        """Perturbing with 'gossip' triggers gossip operation."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        event = await bridge.perturb("gossip")

        assert event is not None
        assert event.operation in ("gossip", "solo")  # May fallback if no third party

    @pytest.mark.asyncio
    async def test_perturb_invalid_pad(self) -> None:
        """Invalid pad ID returns None."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        event = await bridge.perturb("invalid_pad")

        assert event is None

    @pytest.mark.asyncio
    async def test_perturb_cooldown(self) -> None:
        """Perturbation respects cooldown."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        config = FactoryBridgeConfig(perturbation_cooldown_ms=10000)  # 10s cooldown
        bridge = FactoryBridge(flux, config)

        # First perturb succeeds
        event1 = await bridge.perturb("greet")
        assert event1 is not None

        # Immediate second perturb should fail (cooldown)
        event2 = await bridge.perturb("greet")
        assert event2 is None


# =============================================================================
# Frame and State Access Tests
# =============================================================================


class TestStateAccess:
    """Tests for state access methods."""

    def test_get_frame(self) -> None:
        """get_frame() returns ASCII string."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        frame = bridge.get_frame()

        assert isinstance(frame, str)
        assert "ISOMETRIC FACTORY" in frame

    def test_get_state(self) -> None:
        """get_state() returns IsometricState."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        state = bridge.get_state()

        assert isinstance(state, IsometricState)

    def test_get_replay_state(self) -> None:
        """get_replay_state() returns ReplayState."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        replay = bridge.get_replay_state()

        assert isinstance(replay, ReplayState)
        assert replay.current_tick == 0

    def test_toggle_bloom(self) -> None:
        """toggle_bloom() toggles slop bloom mode."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        assert bridge.get_state().slop_bloom_active is False

        bridge.toggle_bloom()
        assert bridge.get_state().slop_bloom_active is True

        bridge.toggle_bloom()
        assert bridge.get_state().slop_bloom_active is False


# =============================================================================
# Replay Bar Rendering Tests
# =============================================================================


class TestReplayBar:
    """Tests for replay bar rendering."""

    def test_empty_trace(self) -> None:
        """Empty trace renders correctly."""
        trace = TownTrace()
        replay = trace.create_replay_state()

        bar = render_replay_bar(trace, replay)

        assert "●" in bar
        assert "[0/0]" in bar

    def test_mid_replay(self) -> None:
        """Mid-replay position renders correctly."""
        trace = TownTrace()
        # Create replay at tick 5 of 10
        replay = ReplayState(current_tick=5, max_tick=10)

        bar = render_replay_bar(trace, replay)

        assert "●" in bar
        assert "[5/10]" in bar
        # Position indicator should be roughly in the middle
        assert "◀" in bar
        assert "▶" in bar

    def test_end_of_trace(self) -> None:
        """End-of-trace renders correctly."""
        trace = TownTrace()
        replay = ReplayState(current_tick=10, max_tick=10)

        bar = render_replay_bar(trace, replay)

        assert "[10/10]" in bar


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for the full demo flow."""

    @pytest.mark.asyncio
    async def test_full_day_simulation(self) -> None:
        """Simulate a full day (4 phases)."""
        env = create_phase2_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        frame_count = 0
        async for frame in bridge.run(num_phases=4):
            frame_count += 1
            # Verify frame is valid ASCII
            assert isinstance(frame, str)
            assert len(frame) > 0

        # Should have multiple frames (initial + events from 4 phases)
        assert frame_count >= 4

        # Verify state advanced
        state = bridge.get_state()
        assert state.current_tick > 0

    @pytest.mark.asyncio
    async def test_perturb_during_simulation(self) -> None:
        """Perturbation during simulation updates state."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        bridge = FactoryBridge(flux)

        # Get initial tick
        initial_tick = bridge.get_state().current_tick

        # Perturb
        event = await bridge.perturb("greet")
        assert event is not None

        # State should have advanced
        assert bridge.get_state().current_tick > initial_tick

        # Frame should reflect change
        frame = bridge.get_frame()
        assert "ISOMETRIC FACTORY" in frame

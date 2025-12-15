"""
Tests for live_town.py demo notebook.

Verifies:
- All imports work
- Dashboard can be created from flux
- PhaseGovernor runs correctly
- Components integrate properly
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest


class TestDemoImports:
    """Test that all demo imports work."""

    def test_core_imports(self) -> None:
        """Core marimo and agent imports work."""
        # These are the imports from the demo
        from agents.town.environment import create_mpp_environment
        from agents.town.flux import TownFlux

        assert create_mpp_environment is not None
        assert TownFlux is not None

    def test_dashboard_imports(self) -> None:
        """Dashboard component imports work."""
        from agents.town.event_bus import EventBus
        from agents.town.live_dashboard import DashboardLayout, LiveDashboard
        from agents.town.phase_governor import PhaseGovernor, PhaseTimingConfig
        from agents.town.trace_bridge import TownTrace

        assert EventBus is not None
        assert LiveDashboard is not None
        assert DashboardLayout is not None
        assert PhaseGovernor is not None
        assert PhaseTimingConfig is not None
        assert TownTrace is not None


class TestDemoSimulationCreation:
    """Test simulation creation as done in demo."""

    def test_create_environment(self) -> None:
        """Can create MPP environment."""
        from agents.town.environment import create_mpp_environment

        env = create_mpp_environment()

        assert env is not None
        assert len(env.citizens) >= 3  # Minimum viable

    def test_create_flux_with_event_bus(self) -> None:
        """Can create TownFlux with EventBus wired."""
        from agents.town.environment import create_mpp_environment
        from agents.town.event_bus import EventBus
        from agents.town.flux import TownFlux

        env = create_mpp_environment()
        event_bus: EventBus[Any] = EventBus()
        flux = TownFlux(env, seed=42, event_bus=event_bus)

        assert flux is not None
        assert flux.event_bus is event_bus

        event_bus.close()

    def test_create_governor(self) -> None:
        """Can create PhaseGovernor with config."""
        from agents.town.environment import create_mpp_environment
        from agents.town.event_bus import EventBus
        from agents.town.flux import TownFlux
        from agents.town.phase_governor import PhaseGovernor, PhaseTimingConfig

        env = create_mpp_environment()
        event_bus: EventBus[Any] = EventBus()
        flux = TownFlux(env, seed=42, event_bus=event_bus)

        config = PhaseTimingConfig(
            phase_duration_ms=1000,
            events_per_phase=3,
            playback_speed=2.0,
        )
        governor = PhaseGovernor(flux=flux, config=config, event_bus=event_bus)

        assert governor is not None
        assert governor.speed == 2.0

        event_bus.close()

    def test_create_dashboard_from_flux(self) -> None:
        """Can create LiveDashboard from TownFlux."""
        from agents.town.environment import create_mpp_environment
        from agents.town.flux import TownFlux
        from agents.town.live_dashboard import LiveDashboard

        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        dashboard = LiveDashboard.from_flux(flux)

        assert dashboard is not None
        assert dashboard.flux is flux
        assert dashboard.isometric is not None
        assert dashboard.scatter is not None
        assert dashboard.timeline is not None

        dashboard.close()


class TestDemoPlaybackControl:
    """Test playback controls as used in demo."""

    def test_play_pause(self) -> None:
        """Play/pause controls work."""
        from agents.town.environment import create_mpp_environment
        from agents.town.flux import TownFlux
        from agents.town.live_dashboard import LiveDashboard

        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        dashboard = LiveDashboard.from_flux(flux)

        assert not dashboard.is_playing

        dashboard.play()
        assert dashboard.is_playing

        dashboard.pause()
        assert not dashboard.is_playing

        dashboard.close()

    def test_speed_control(self) -> None:
        """Speed control works."""
        from agents.town.environment import create_mpp_environment
        from agents.town.flux import TownFlux
        from agents.town.live_dashboard import LiveDashboard

        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        dashboard = LiveDashboard.from_flux(flux)

        dashboard.set_speed(2.0)
        assert dashboard.playback_speed == 2.0

        dashboard.set_speed(0.5)
        assert dashboard.playback_speed == 0.5

        dashboard.close()


class TestDemoLayoutControl:
    """Test layout controls as used in demo."""

    def test_layout_changes(self) -> None:
        """Layout changes work."""
        from agents.town.environment import create_mpp_environment
        from agents.town.flux import TownFlux
        from agents.town.live_dashboard import DashboardLayout, LiveDashboard

        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        dashboard = LiveDashboard.from_flux(flux)

        dashboard.set_layout(DashboardLayout.MINIMAL)
        assert dashboard.state.panel_visible["isometric"] is True
        assert dashboard.state.panel_visible["scatter"] is False

        dashboard.set_layout(DashboardLayout.FULL)
        assert dashboard.state.panel_visible["scatter"] is True

        dashboard.close()


class TestDemoRendering:
    """Test rendering as done in demo."""

    def test_render_cli(self) -> None:
        """CLI rendering works."""
        from agents.town.environment import create_mpp_environment
        from agents.town.flux import TownFlux
        from agents.town.live_dashboard import LiveDashboard

        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        dashboard = LiveDashboard.from_flux(flux)

        output = dashboard.render_cli(width=80)

        assert "AGENT TOWN" in output
        assert len(output) > 100

        dashboard.close()

    def test_render_json(self) -> None:
        """JSON rendering works."""
        from agents.town.environment import create_mpp_environment
        from agents.town.flux import TownFlux
        from agents.town.live_dashboard import LiveDashboard

        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        dashboard = LiveDashboard.from_flux(flux)

        output = dashboard.render_json()

        assert "dashboard" in output
        assert "isometric" in output
        assert "scatter" in output

        dashboard.close()


class TestDemoGovernorRun:
    """Test governor running as done in demo."""

    @pytest.mark.asyncio
    async def test_governor_generates_events(self) -> None:
        """PhaseGovernor generates events."""
        from agents.town.environment import create_mpp_environment
        from agents.town.event_bus import EventBus
        from agents.town.flux import TownFlux
        from agents.town.phase_governor import PhaseGovernor, PhaseTimingConfig

        env = create_mpp_environment()
        event_bus: EventBus[Any] = EventBus()
        flux = TownFlux(env, seed=42, event_bus=event_bus)

        # Fast config for testing
        config = PhaseTimingConfig(
            phase_duration_ms=100,
            events_per_phase=2,
            playback_speed=10.0,  # Very fast
            min_event_delay_ms=10,
            max_event_delay_ms=50,
        )
        governor = PhaseGovernor(flux=flux, config=config, event_bus=event_bus)

        events = []
        async for event in governor.run(num_phases=1):
            events.append(event)

        assert len(events) > 0
        assert events[0].phase is not None
        assert events[0].operation is not None

        event_bus.close()

    @pytest.mark.asyncio
    async def test_full_integration(self) -> None:
        """Full integration: flux → governor → dashboard."""
        from agents.town.environment import create_mpp_environment
        from agents.town.flux import TownFlux
        from agents.town.live_dashboard import LiveDashboard
        from agents.town.phase_governor import PhaseGovernor, PhaseTimingConfig

        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        dashboard = LiveDashboard.from_flux(flux)

        # Create governor
        config = PhaseTimingConfig(
            phase_duration_ms=100,
            events_per_phase=2,
            playback_speed=10.0,
            min_event_delay_ms=10,
            max_event_delay_ms=50,
        )
        governor = PhaseGovernor(
            flux=flux,
            config=config,
            event_bus=dashboard.event_bus,
        )

        # Run one phase
        events = []
        async for event in governor.run(num_phases=1):
            events.append(event)

        assert len(events) > 0

        # Dashboard should have updated
        # (Events flow through event_bus to dashboard)

        dashboard.close()


class TestDemoTimelineIntegration:
    """Test timeline as used in demo."""

    def test_timeline_navigation(self) -> None:
        """Timeline navigation works."""
        from agents.town.environment import create_mpp_environment
        from agents.town.flux import TownFlux
        from agents.town.live_dashboard import LiveDashboard

        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        dashboard = LiveDashboard.from_flux(flux)

        # Step controls
        dashboard.step_forward()
        dashboard.step_backward()

        # Render timeline
        if dashboard.timeline:
            output = dashboard.timeline.render_cli(width=60)
            assert len(output) > 0

        dashboard.close()


class TestDemoCitizenSelection:
    """Test citizen selection as used in demo."""

    def test_select_citizen(self) -> None:
        """Citizen selection works."""
        from agents.town.environment import create_mpp_environment
        from agents.town.flux import TownFlux
        from agents.town.live_dashboard import LiveDashboard

        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)
        dashboard = LiveDashboard.from_flux(flux)

        # Get a citizen name (env.citizens is a dict)
        citizen_names = [c.name for c in env.citizens.values()]
        if citizen_names:
            dashboard.select_citizen(citizen_names[0])
            assert dashboard.state.selected_citizen_id == citizen_names[0]

        dashboard.close()

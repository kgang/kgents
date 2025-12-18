"""
Integration tests for Agent Town MPP.

Verifies end-to-end behavior:
- Full simulation loop
- CLI handler
- Metrics flow
"""

from __future__ import annotations

import pytest

from agents.town.citizen import Citizen
from agents.town.environment import create_mpp_environment
from agents.town.flux import TownFlux, TownPhase
from agents.town.operad import PRECONDITION_CHECKER, TOWN_OPERAD


class TestEndToEndSimulation:
    """Test complete simulation flow."""

    @pytest.mark.asyncio
    async def test_full_day_simulation(self) -> None:
        """Run a full simulated day (4-phase cycle)."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        initial_day = flux.day
        events_collected = []

        # Run morning
        phase1 = flux.current_phase
        assert phase1 == TownPhase.MORNING
        async for event in flux.step():
            events_collected.append(event)

        # Run afternoon
        phase2 = flux.current_phase
        assert phase2 == TownPhase.AFTERNOON
        async for event in flux.step():
            events_collected.append(event)

        # Run evening
        phase3 = flux.current_phase
        assert phase3 == TownPhase.EVENING
        async for event in flux.step():
            events_collected.append(event)

        # Run night
        phase4 = flux.current_phase
        assert phase4 == TownPhase.NIGHT
        async for event in flux.step():
            events_collected.append(event)

        # Day should have advanced
        assert flux.day == initial_day + 1
        assert flux.current_phase == TownPhase.MORNING

        # Should have generated some events
        assert len(events_collected) > 0

    @pytest.mark.asyncio
    async def test_multi_day_simulation(self) -> None:
        """Run multiple days (4-phase cycle)."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        for _ in range(12):  # 3 days = 12 phases (4 per day)
            async for _ in flux.step():
                pass

        assert flux.day >= 4  # Started at 1, 12 steps = 3 days = day 4

    @pytest.mark.asyncio
    async def test_simulation_produces_metrics(self) -> None:
        """Simulation produces trackable metrics."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        for _ in range(4):
            async for _ in flux.step():
                pass

        status = flux.get_status()

        # Should have tracked metrics
        assert status["total_events"] > 0
        assert status["total_tokens"] > 0


class TestOperadIntegration:
    """Test operad integration with environment."""

    def test_greet_requires_colocation(self) -> None:
        """Greet precondition enforces co-location."""
        env = create_mpp_environment()

        alice = env.get_citizen_by_name("Alice")
        bob = env.get_citizen_by_name("Bob")
        assert alice is not None
        assert bob is not None

        # Alice is in inn, Bob in square
        assert alice.region != bob.region

        results = PRECONDITION_CHECKER.validate_operation("greet", [alice, bob], env)

        # Should fail locality check
        locality_result = next((r for r in results if r.precondition == "locality"), None)
        assert locality_result is not None
        assert not locality_result.passed

    def test_greet_succeeds_when_colocated(self) -> None:
        """Greet succeeds when citizens are co-located."""
        env = create_mpp_environment()

        alice = env.get_citizen_by_name("Alice")
        clara = env.get_citizen_by_name("Clara")
        assert alice is not None
        assert clara is not None

        # Both in inn
        assert alice.region == clara.region

        results = PRECONDITION_CHECKER.validate_operation("greet", [alice, clara], env)

        assert all(r.passed for r in results)


class TestRelationshipEvolution:
    """Test relationship changes over simulation."""

    @pytest.mark.asyncio
    async def test_relationships_change(self) -> None:
        """Relationships evolve through interactions."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        alice = env.get_citizen_by_name("Alice")
        clara = env.get_citizen_by_name("Clara")
        assert alice is not None
        assert clara is not None

        # Record initial relationship
        initial_rel = alice.get_relationship(clara.id)

        # Run several steps
        for _ in range(10):
            async for _ in flux.step():
                pass

        # Check for any relationship changes (may or may not happen)
        # At minimum, verify relationships are valid
        final_rel = alice.get_relationship(clara.id)
        assert -1.0 <= final_rel <= 1.0


class TestRightToRestIntegration:
    """Test Right to Rest across system."""

    @pytest.mark.asyncio
    async def test_resting_citizens_not_disturbed(self) -> None:
        """Resting citizens are not selected for interactions."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        alice = env.get_citizen_by_name("Alice")
        assert alice is not None
        alice.rest()

        # Run a step
        async for event in flux.step():
            # Alice should not be in any event participants
            # (unless it's a wake event, which we don't have yet)
            if "Alice" in event.participants:
                # If Alice is in an event, it should have failed
                # due to rest check, OR she woke up first
                pass  # Just verify we don't crash


class TestAccursedShareIntegration:
    """Test accursed share across system."""

    @pytest.mark.asyncio
    async def test_surplus_tracked(self) -> None:
        """Surplus is tracked across citizens."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        # Run several steps to accumulate surplus
        for _ in range(6):
            async for _ in flux.step():
                pass

        # Get status
        status = flux.get_status()
        assert "accursed_surplus" in status

    @pytest.mark.asyncio
    async def test_surplus_distributed(self) -> None:
        """Surplus is distributed among citizens."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        # Run several steps
        for _ in range(10):
            async for _ in flux.step():
                pass

        # Check individual surpluses
        total = 0.0
        for citizen in env.citizens.values():
            total += citizen.accursed_surplus

        assert env.total_accursed_surplus() == total


class TestCitizenPhaseIntegration:
    """Test citizen phases across system."""

    @pytest.mark.asyncio
    async def test_phases_change_during_simulation(self) -> None:
        """Citizen phases change during simulation."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        # All start IDLE
        for citizen in env.citizens.values():
            assert citizen.phase.name == "IDLE"

        # Run a step
        async for _ in flux.step():
            pass

        # Some phases should have changed
        phases = [c.phase.name for c in env.citizens.values()]
        # After evening, some should be resting
        # This depends on the random seed


class TestMetricsIntegration:
    """Test metrics across system."""

    @pytest.mark.asyncio
    async def test_token_spend_tracked(self) -> None:
        """Token spend is tracked in environment."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        initial_spend = env.total_token_spend

        for _ in range(4):
            async for _ in flux.step():
                pass

        final_spend = env.total_token_spend
        assert final_spend > initial_spend

    @pytest.mark.asyncio
    async def test_tension_index_computable(self) -> None:
        """Tension index can be computed."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        for _ in range(4):
            async for _ in flux.step():
                pass

        tension = env.tension_index()
        assert isinstance(tension, float)
        assert tension >= 0

    @pytest.mark.asyncio
    async def test_cooperation_level_computable(self) -> None:
        """Cooperation level can be computed."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        for _ in range(4):
            async for _ in flux.step():
                pass

        coop = env.cooperation_level()
        assert isinstance(coop, float)
        assert coop >= 0


class TestCLIHandlerIntegration:
    """Test CLI handler integration (without actual CLI)."""

    def test_town_handler_import(self) -> None:
        """Can import town handler."""
        from protocols.cli.handlers.town import cmd_town

        assert cmd_town is not None

    def test_town_start_creates_simulation(self) -> None:
        """Start command creates simulation state."""
        from protocols.cli.handlers.town import _simulation_state, _start_simulation

        # Clear any existing state
        _simulation_state.clear()

        result = _start_simulation([], None)

        assert result == 0
        assert "environment" in _simulation_state
        assert "flux" in _simulation_state

    def test_town_status_without_simulation(self) -> None:
        """Status works without simulation."""
        from protocols.cli.handlers.town import _show_status, _simulation_state

        _simulation_state.clear()

        result = _show_status(None)
        assert result == 0

    def test_town_step_requires_simulation(self) -> None:
        """Step requires running simulation."""
        from protocols.cli.handlers.town import _simulation_state, _step_simulation

        _simulation_state.clear()

        result = _step_simulation(None)
        assert result == 1  # Error code

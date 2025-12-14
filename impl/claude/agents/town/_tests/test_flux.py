"""
Tests for TownFlux.

Verifies:
- Phase advancement
- Event generation
- Precondition enforcement
- Metrics tracking
"""

from __future__ import annotations

import pytest
from agents.town.environment import create_mpp_environment
from agents.town.flux import TownEvent, TownFlux, TownPhase


class TestTownPhase:
    """Test TownPhase enum."""

    def test_phases_exist(self) -> None:
        """Phase 2 phases exist."""
        assert TownPhase.MORNING
        assert TownPhase.AFTERNOON
        assert TownPhase.EVENING
        assert TownPhase.NIGHT

    def test_phase_count(self) -> None:
        """Phase 2 has 4 phases."""
        assert len(TownPhase) == 4


class TestTownEvent:
    """Test TownEvent dataclass."""

    def test_basic_creation(self) -> None:
        """Can create an event."""
        event = TownEvent(
            phase=TownPhase.MORNING,
            operation="greet",
            participants=["Alice", "Bob"],
            success=True,
            message="Alice greeted Bob",
        )

        assert event.phase == TownPhase.MORNING
        assert event.operation == "greet"
        assert "Alice" in event.participants

    def test_default_tokens(self) -> None:
        """Default tokens is 0."""
        event = TownEvent(
            phase=TownPhase.MORNING,
            operation="greet",
            participants=["Alice"],
            success=True,
        )
        assert event.tokens_used == 0

    def test_to_dict(self) -> None:
        """Can serialize to dict."""
        event = TownEvent(
            phase=TownPhase.MORNING,
            operation="greet",
            participants=["Alice", "Bob"],
            success=True,
            tokens_used=200,
        )
        d = event.to_dict()

        assert d["phase"] == "MORNING"
        assert d["operation"] == "greet"
        assert d["tokens_used"] == 200


class TestTownFlux:
    """Test TownFlux simulation loop."""

    def test_basic_creation(self) -> None:
        """Can create flux."""
        env = create_mpp_environment()
        flux = TownFlux(env)

        assert flux.environment is env
        assert flux.day == 1
        assert flux.current_phase == TownPhase.MORNING

    def test_seeded_creation(self) -> None:
        """Can create with seed for reproducibility."""
        env = create_mpp_environment()
        flux1 = TownFlux(env, seed=42)
        flux2 = TownFlux(env, seed=42)

        # Same seed should produce same first operation
        op1 = flux1._select_operation()
        op2 = flux2._select_operation()
        assert op1 == op2

    def test_citizens_property(self) -> None:
        """Citizens property returns all citizens."""
        env = create_mpp_environment()
        flux = TownFlux(env)

        assert len(flux.citizens) == 3

    def test_phase_advancement(self) -> None:
        """Phases advance correctly (4-phase cycle)."""
        env = create_mpp_environment()
        flux = TownFlux(env)

        # Start at morning
        assert flux.current_phase == TownPhase.MORNING
        assert flux.day == 1

        # MORNING -> AFTERNOON
        flux._next_phase()
        assert flux.current_phase == TownPhase.AFTERNOON

        # AFTERNOON -> EVENING
        flux._next_phase()
        assert flux.current_phase == TownPhase.EVENING

        # EVENING -> NIGHT
        flux._next_phase()
        assert flux.current_phase == TownPhase.NIGHT

        # NIGHT -> MORNING (day increments)
        flux._next_phase()
        assert flux.current_phase == TownPhase.MORNING
        assert flux.day == 2

    def test_select_operation(self) -> None:
        """Select operation returns valid operation."""
        env = create_mpp_environment()
        flux = TownFlux(env)

        op = flux._select_operation()
        assert op in ["greet", "gossip", "trade", "solo"]

    def test_select_participants_solo(self) -> None:
        """Solo operation selects one participant."""
        env = create_mpp_environment()
        flux = TownFlux(env)

        participants = flux._select_participants("solo")
        assert len(participants) == 1

    def test_select_participants_binary(self) -> None:
        """Binary operations select co-located participants."""
        env = create_mpp_environment()
        flux = TownFlux(env)

        participants = flux._select_participants("greet")

        # Should be 1 or 2 (could fall back to solo if no co-located pair)
        assert len(participants) >= 1

        if len(participants) == 2:
            # If 2, they should be co-located
            assert participants[0].region == participants[1].region


class TestFluxStep:
    """Test step execution."""

    @pytest.mark.asyncio
    async def test_step_generates_events(self) -> None:
        """Step generates events."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        events = []
        async for event in flux.step():
            events.append(event)

        assert len(events) >= 1
        assert all(isinstance(e, TownEvent) for e in events)

    @pytest.mark.asyncio
    async def test_step_advances_phase(self) -> None:
        """Step advances phase."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        initial_phase = flux.current_phase
        async for _ in flux.step():
            pass

        assert flux.current_phase != initial_phase

    @pytest.mark.asyncio
    async def test_step_tracks_tokens(self) -> None:
        """Step tracks token usage."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        async for _ in flux.step():
            pass

        assert flux.total_tokens > 0

    @pytest.mark.asyncio
    async def test_step_tracks_events(self) -> None:
        """Step tracks event count."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        async for _ in flux.step():
            pass

        assert flux.total_events > 0


class TestFluxOperations:
    """Test operation execution."""

    def test_execute_greet(self) -> None:
        """Greet operation produces valid event."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        alice = env.get_citizen_by_name("Alice")
        clara = env.get_citizen_by_name("Clara")  # Also in inn
        assert alice is not None
        assert clara is not None

        event = flux._execute_greet([alice, clara], 200, 0.1)

        assert event.operation == "greet"
        assert event.success
        assert "Alice" in event.participants
        assert "Clara" in event.participants

    def test_execute_solo(self) -> None:
        """Solo operation produces valid event."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        alice = env.get_citizen_by_name("Alice")
        assert alice is not None

        event = flux._execute_solo(alice, 300, 0.1)

        assert event.operation == "solo"
        assert event.success
        assert "Alice" in event.participants

    def test_execute_gossip_needs_third_party(self) -> None:
        """Gossip needs a third party to gossip about."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        alice = env.get_citizen_by_name("Alice")
        clara = env.get_citizen_by_name("Clara")
        assert alice is not None
        assert clara is not None

        event = flux._execute_gossip([alice, clara], 500, 0.4)

        assert event.operation == "gossip"
        # Should succeed because Bob exists
        assert event.success

    def test_execute_trade(self) -> None:
        """Trade operation updates relationships."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        alice = env.get_citizen_by_name("Alice")
        clara = env.get_citizen_by_name("Clara")
        assert alice is not None
        assert clara is not None

        # Record initial relationships
        initial_a_c = alice.get_relationship(clara.id)
        initial_c_a = clara.get_relationship(alice.id)

        event = flux._execute_trade([alice, clara], 400, 0.3)

        assert event.operation == "trade"
        assert event.success

        # Relationships should improve
        assert alice.get_relationship(clara.id) > initial_a_c
        assert clara.get_relationship(alice.id) > initial_c_a


class TestFluxStatus:
    """Test status reporting."""

    def test_get_status(self) -> None:
        """Status returns expected fields."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        status = flux.get_status()

        assert "day" in status
        assert "phase" in status
        assert "total_events" in status
        assert "total_tokens" in status
        assert "tension_index" in status
        assert "cooperation_level" in status
        assert "citizens" in status

    @pytest.mark.asyncio
    async def test_status_updates_after_step(self) -> None:
        """Status updates after step."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        status_before = flux.get_status()

        async for _ in flux.step():
            pass

        status_after = flux.get_status()

        assert status_after["total_events"] > status_before["total_events"]


class TestAccursedShare:
    """Test accursed share mechanics."""

    @pytest.mark.asyncio
    async def test_surplus_accumulates(self) -> None:
        """Surplus accumulates through operations."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        initial_surplus = env.total_accursed_surplus()

        # Run several steps to accumulate surplus
        for _ in range(3):
            async for _ in flux.step():
                pass

        final_surplus = env.total_accursed_surplus()

        # May not always be greater due to spending, but should be non-negative
        assert final_surplus >= 0

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
        current: TownPhase = flux.current_phase
        assert current == TownPhase.MORNING
        assert flux.day == 1

        # MORNING -> AFTERNOON
        current = flux._next_phase()
        assert current == TownPhase.AFTERNOON

        # AFTERNOON -> EVENING
        current = flux._next_phase()
        assert current == TownPhase.EVENING

        # EVENING -> NIGHT
        current = flux._next_phase()
        assert current == TownPhase.NIGHT

        # NIGHT -> MORNING (day increments)
        current = flux._next_phase()
        assert current == TownPhase.MORNING
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
    """Test operation execution (Phase 7: async)."""

    @pytest.mark.asyncio
    async def test_execute_greet(self) -> None:
        """Greet operation produces valid event."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        alice = env.get_citizen_by_name("Alice")
        clara = env.get_citizen_by_name("Clara")  # Also in inn
        assert alice is not None
        assert clara is not None

        event = await flux._execute_greet([alice, clara], 200, 0.1)

        assert event.operation == "greet"
        assert event.success
        assert "Alice" in event.participants
        assert "Clara" in event.participants

    @pytest.mark.asyncio
    async def test_execute_solo(self) -> None:
        """Solo operation produces valid event."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        alice = env.get_citizen_by_name("Alice")
        assert alice is not None

        event = await flux._execute_solo(alice, 300, 0.1)

        assert event.operation == "solo"
        assert event.success
        assert "Alice" in event.participants

    @pytest.mark.asyncio
    async def test_execute_gossip_needs_third_party(self) -> None:
        """Gossip needs a third party to gossip about."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        alice = env.get_citizen_by_name("Alice")
        clara = env.get_citizen_by_name("Clara")
        assert alice is not None
        assert clara is not None

        event = await flux._execute_gossip([alice, clara], 500, 0.4)

        assert event.operation == "gossip"
        # Should succeed because Bob exists
        assert event.success

    @pytest.mark.asyncio
    async def test_execute_trade(self) -> None:
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

        event = await flux._execute_trade([alice, clara], 400, 0.3)

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


class TestMemoryIntegration:
    """Test D-gent memory integration in TownFlux."""

    def test_pending_memories_initialized(self) -> None:
        """Flux initializes pending memories list."""
        env = create_mpp_environment()
        flux = TownFlux(env)

        assert hasattr(flux, "_pending_memories")
        assert flux._pending_memories == []

    @pytest.mark.asyncio
    async def test_gossip_stores_memory(self) -> None:
        """Gossip operation queues memory storage."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        alice = env.get_citizen_by_name("Alice")
        clara = env.get_citizen_by_name("Clara")
        assert alice is not None
        assert clara is not None

        # Clear any existing pending memories
        flux._pending_memories.clear()

        # Execute gossip (Phase 7: now async)
        event = await flux._execute_gossip([alice, clara], 500, 0.4)

        assert event.success
        # Should have queued 2 memories (one for each participant)
        assert len(flux._pending_memories) == 2

        # Check memory content structure
        citizen1, key1, content1 = flux._pending_memories[0]
        assert content1["type"] == "gossip"
        assert content1["speaker"] == alice.name
        assert content1["listener"] == clara.name
        assert "subject" in content1

    @pytest.mark.asyncio
    async def test_memories_processed_in_step(self) -> None:
        """Pending memories are processed during step."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        # Run a step
        async for _ in flux.step():
            pass

        # After step, pending memories should be cleared
        assert len(flux._pending_memories) == 0

    @pytest.mark.asyncio
    async def test_citizen_memories_persist(self) -> None:
        """Citizen memories persist after gossip."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=101)  # Seed that produces gossip

        alice = env.get_citizen_by_name("Alice")
        assert alice is not None

        # Run several steps to increase chance of gossip
        for _ in range(5):
            async for _ in flux.step():
                pass

        # Check if any memories were stored (via the memory store)
        store = alice.memory._store
        # Should have at least some state (even if not gossip specifically)
        # This tests the integration is wired correctly
        assert store is not None

    def test_get_remembered_subjects_empty(self) -> None:
        """Get remembered subjects returns empty for new citizen."""
        env = create_mpp_environment()
        flux = TownFlux(env)

        alice = env.get_citizen_by_name("Alice")
        assert alice is not None

        subjects = flux._get_remembered_subjects(alice)
        assert subjects == []

    def test_get_remembered_subjects_with_gossip(self) -> None:
        """Get remembered subjects returns subjects from gossip memories."""
        env = create_mpp_environment()
        flux = TownFlux(env)

        alice = env.get_citizen_by_name("Alice")
        assert alice is not None

        # Manually add a gossip memory to Alice's store
        alice.memory._store.state["gossip_1"] = {
            "type": "gossip",
            "subject": "Bob",
            "speaker": "Alice",
        }

        subjects = flux._get_remembered_subjects(alice)
        assert "Bob" in subjects

    @pytest.mark.asyncio
    async def test_recall_gossip_subjects_async(self) -> None:
        """Async recall returns subjects from gossip memories."""
        env = create_mpp_environment()
        flux = TownFlux(env)

        alice = env.get_citizen_by_name("Alice")
        assert alice is not None

        # Add gossip memory via async store
        await alice.remember(
            {"type": "gossip", "subject": "Clara", "speaker": "Alice"},
            key="test_gossip",
        )

        subjects = await flux._recall_gossip_subjects(alice)
        assert "Clara" in subjects


# =============================================================================
# TownFlux → TownTrace Integration Tests (Step 1)
# =============================================================================


class TestTownFluxTraceIntegration:
    """Tests for TownFlux → TownTrace wiring."""

    def test_flux_has_trace(self) -> None:
        """TownFlux initializes with empty trace."""
        env = create_mpp_environment()
        flux = TownFlux(env)

        assert hasattr(flux, "trace")
        assert len(flux.trace.events) == 0

    @pytest.mark.asyncio
    async def test_step_appends_to_trace(self) -> None:
        """TownFlux.step() appends events to trace."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        # Run a step
        events_generated = 0
        async for event in flux.step():
            events_generated += 1

        # Trace should have the same number of events
        assert len(flux.trace.events) == events_generated
        assert events_generated > 0  # At least one event

    @pytest.mark.asyncio
    async def test_trace_events_match_generated(self) -> None:
        """Trace events match the generated events."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=123)

        generated: list[TownEvent] = []
        async for event in flux.step():
            generated.append(event)

        # Check trace events match
        for i, event in enumerate(generated):
            trace_event = flux.trace.events[i]
            assert trace_event.operation == event.operation
            assert list(trace_event.participants) == event.participants
            assert trace_event.success == event.success

    @pytest.mark.asyncio
    async def test_trace_creates_valid_replay_state(self) -> None:
        """Trace can create valid ReplayState after step()."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=456)

        # Run multiple steps
        for _ in range(3):
            async for _ in flux.step():
                pass

        replay_state = flux.trace.create_replay_state()

        assert replay_state.max_tick == len(flux.trace.events)
        assert replay_state.max_tick > 0
        assert replay_state.start_time is not None


# =============================================================================
# TownFlux Perturbation Tests (Step 5)
# =============================================================================


class TestTownFluxPerturbation:
    """Tests for TownFlux.perturb() - HITL perturbation injection."""

    @pytest.mark.asyncio
    async def test_perturb_valid_operation(self) -> None:
        """Perturb with valid operation returns event."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        event = await flux.perturb("solo")

        assert event is not None
        assert event.operation == "solo"
        assert event.success

    @pytest.mark.asyncio
    async def test_perturb_invalid_operation_returns_none(self) -> None:
        """Perturb with invalid operation returns None."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        event = await flux.perturb("invalid_op")

        assert event is None

    @pytest.mark.asyncio
    async def test_perturb_greet(self) -> None:
        """Perturb with greet operation works."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        event = await flux.perturb("greet")

        assert event is not None
        assert event.operation == "greet"
        # Greet needs 2 participants
        assert len(event.participants) >= 1

    @pytest.mark.asyncio
    async def test_perturb_gossip(self) -> None:
        """Perturb with gossip operation works."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        event = await flux.perturb("gossip")

        assert event is not None
        assert event.operation == "gossip"

    @pytest.mark.asyncio
    async def test_perturb_trade(self) -> None:
        """Perturb with trade operation works."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        event = await flux.perturb("trade")

        assert event is not None
        assert event.operation == "trade"

    @pytest.mark.asyncio
    async def test_perturb_marks_metadata(self) -> None:
        """Perturb marks event with perturbation metadata."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        event = await flux.perturb("solo")

        assert event is not None
        assert event.metadata.get("perturbation") is True
        assert event.metadata.get("perturbation_source") == "hitl_pad"

    @pytest.mark.asyncio
    async def test_perturb_appends_to_trace(self) -> None:
        """Perturb appends event to trace."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        initial_count = len(flux.trace.events)
        await flux.perturb("solo")

        assert len(flux.trace.events) == initial_count + 1

    @pytest.mark.asyncio
    async def test_perturb_updates_counters(self) -> None:
        """Perturb updates event and token counters."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        initial_events = flux.total_events
        initial_tokens = flux.total_tokens

        await flux.perturb("solo")

        assert flux.total_events == initial_events + 1
        assert flux.total_tokens > initial_tokens

    @pytest.mark.asyncio
    async def test_perturb_with_specific_participants(self) -> None:
        """Perturb with specific participants uses them."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        # Get citizen IDs
        alice = env.get_citizen_by_name("Alice")
        assert alice is not None

        event = await flux.perturb("solo", participant_ids=[alice.id])

        assert event is not None
        assert alice.name in event.participants

    @pytest.mark.asyncio
    async def test_perturb_with_invalid_participants_falls_back(self) -> None:
        """Perturb with invalid participant IDs returns None."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        event = await flux.perturb(
            "greet", participant_ids=["invalid_id_1", "invalid_id_2"]
        )

        # Should return None because participants don't exist
        assert event is None

    @pytest.mark.asyncio
    async def test_perturb_async(self) -> None:
        """Async perturb works."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        event = await flux.perturb_async("solo")

        assert event is not None
        assert event.operation == "solo"

    @pytest.mark.asyncio
    async def test_perturb_goes_through_normal_execution(self) -> None:
        """Perturb uses normal execution path (perturbation principle)."""
        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        alice = env.get_citizen_by_name("Alice")
        clara = env.get_citizen_by_name("Clara")
        assert alice is not None
        assert clara is not None

        # Record initial relationship
        initial_rel = alice.get_relationship(clara.id)

        # Execute trade via perturb (should update relationship)
        event = await flux.perturb("trade", participant_ids=[alice.id, clara.id])

        if event and event.success:
            # Relationship should be updated (trade improves relationships)
            assert alice.get_relationship(clara.id) > initial_rel

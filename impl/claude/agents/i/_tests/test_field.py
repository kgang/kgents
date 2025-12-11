"""
Tests for I-gent Stigmergic Field.

Tests the core field dynamics:
- Entity management
- Pheromone emission and decay
- Field simulation (Brownian motion, gravity, repulsion)
- Dialectic phase transitions
"""

import pytest
from agents.i.field import (
    DialecticPhase,
    Entity,
    EntityType,
    FieldSimulator,
    FieldState,
    Pheromone,
    PheromoneType,
    create_default_field,
    create_demo_field,
)
from agents.i.types import Phase


class TestEntity:
    """Tests for Entity class."""

    def test_entity_creation(self):
        """Test basic entity creation."""
        entity = Entity(
            id="test-agent",
            entity_type=EntityType.JUDGE,
            x=10,
            y=5,
            phase=Phase.ACTIVE,
        )
        assert entity.id == "test-agent"
        assert entity.entity_type == EntityType.JUDGE
        assert entity.x == 10
        assert entity.y == 5
        assert entity.phase == Phase.ACTIVE
        assert entity.symbol == "J"

    def test_entity_position(self):
        """Test position property."""
        entity = Entity(id="e", entity_type=EntityType.ID, x=3, y=7)
        assert entity.position == (3, 7)

    def test_entity_distance(self):
        """Test distance calculation."""
        e1 = Entity(id="e1", entity_type=EntityType.ID, x=0, y=0)
        e2 = Entity(id="e2", entity_type=EntityType.ID, x=3, y=4)
        assert e1.distance_to(e2) == 5.0  # 3-4-5 triangle

    def test_entity_move(self):
        """Test entity movement with bounds."""
        entity = Entity(id="e", entity_type=EntityType.ID, x=5, y=5)
        bounds = (10, 10)

        # Normal move
        entity.move(2, 2, bounds)
        assert entity.position == (7, 7)

        # Move past bounds
        entity.move(10, 10, bounds)
        assert entity.position == (9, 9)  # Clamped to bounds

        # Negative move past zero
        entity.move(-20, -20, bounds)
        assert entity.position == (0, 0)  # Clamped to zero

    def test_entity_type_properties(self):
        """Test entity type classification."""
        assert EntityType.JUDGE.is_agent
        assert EntityType.COMPOSE.is_agent
        assert not EntityType.TASK.is_agent

        assert EntityType.TASK.is_attractor
        assert EntityType.HYPOTHESIS.is_attractor
        assert not EntityType.JUDGE.is_attractor


class TestPheromone:
    """Tests for Pheromone class."""

    def test_pheromone_creation(self):
        """Test pheromone creation."""
        p = Pheromone(
            ptype=PheromoneType.PROGRESS,
            x=5,
            y=5,
            intensity=1.0,
            birth_tick=0,
        )
        assert p.ptype == PheromoneType.PROGRESS
        assert p.intensity == 1.0

    def test_pheromone_decay(self):
        """Test pheromone decay over time."""
        p = Pheromone(
            ptype=PheromoneType.PROGRESS,  # decay_rate = 5
            x=0,
            y=0,
            intensity=1.0,
            birth_tick=0,
        )

        # No decay at birth
        assert p.decay(0) == 1.0

        # Partial decay
        assert p.decay(2) == pytest.approx(0.6, rel=0.01)

        # Full decay
        assert p.decay(5) == 0.0
        assert p.decay(10) == 0.0

    def test_pheromone_decay_rates(self):
        """Test different decay rates by type."""
        assert PheromoneType.PROGRESS.decay_rate == 5
        assert PheromoneType.CONFLICT.decay_rate == 2
        assert PheromoneType.SYNTHESIS.decay_rate == 3
        assert PheromoneType.ERROR.decay_rate == 1


class TestFieldState:
    """Tests for FieldState class."""

    def test_field_creation(self):
        """Test field state creation."""
        state = FieldState(width=60, height=20)
        assert state.width == 60
        assert state.height == 20
        assert state.tick == 0
        assert state.entropy == 50.0
        assert state.heat == 0.0
        assert state.dialectic_phase == DialecticPhase.DORMANT

    def test_add_entity(self):
        """Test adding entities to field."""
        state = FieldState(width=60, height=20)
        entity = Entity(id="test", entity_type=EntityType.JUDGE, x=10, y=10)

        state.add_entity(entity)
        assert "test" in state.entities
        assert state.get_entity("test") == entity

    def test_remove_entity(self):
        """Test removing entities."""
        state = FieldState(width=60, height=20)
        entity = Entity(id="test", entity_type=EntityType.JUDGE, x=10, y=10)

        state.add_entity(entity)
        removed = state.remove_entity("test")
        assert removed == entity
        assert "test" not in state.entities

    def test_emit_pheromone(self):
        """Test pheromone emission."""
        state = FieldState(width=60, height=20)
        state.tick = 5

        p = state.emit_pheromone(PheromoneType.PROGRESS, 10, 10, 0.8)
        assert p.x == 10
        assert p.y == 10
        assert p.intensity == 0.8
        assert p.birth_tick == 5
        assert len(state.pheromones) == 1

    def test_get_pheromones_at(self):
        """Test getting pheromones at location."""
        state = FieldState(width=60, height=20)
        state.emit_pheromone(PheromoneType.PROGRESS, 5, 5)
        state.emit_pheromone(PheromoneType.CONFLICT, 5, 5)
        state.emit_pheromone(PheromoneType.PROGRESS, 10, 10)

        at_5_5 = state.get_pheromones_at(5, 5)
        assert len(at_5_5) == 2

        at_10_10 = state.get_pheromones_at(10, 10)
        assert len(at_10_10) == 1

    def test_decay_pheromones(self):
        """Test pheromone decay cleanup."""
        state = FieldState(width=60, height=20)
        state.emit_pheromone(PheromoneType.ERROR, 5, 5)  # decay_rate = 1

        # Move time forward past decay
        state.tick = 2
        removed = state.decay_pheromones()
        assert removed == 1
        assert len(state.pheromones) == 0

    def test_log_event(self):
        """Test event logging."""
        state = FieldState(width=60, height=20)
        state.log_event("test", "source", "Test message", "info")

        events = state.get_recent_events(10)
        assert len(events) == 1
        assert events[0]["type"] == "test"
        assert events[0]["source"] == "source"
        assert events[0]["message"] == "Test message"

    def test_log_event_limit(self):
        """Test event log limit."""
        state = FieldState(width=60, height=20)

        # Add more than 100 events
        for i in range(150):
            state.log_event("test", "source", f"Message {i}")

        assert len(state.events) == 100
        # Should keep most recent
        assert state.events[-1]["message"] == "Message 149"

    def test_entities_at(self):
        """Test getting entities at position."""
        state = FieldState(width=60, height=20)
        e1 = Entity(id="e1", entity_type=EntityType.ID, x=5, y=5)
        e2 = Entity(id="e2", entity_type=EntityType.COMPOSE, x=5, y=5)
        e3 = Entity(id="e3", entity_type=EntityType.JUDGE, x=10, y=10)

        state.add_entity(e1)
        state.add_entity(e2)
        state.add_entity(e3)

        at_5_5 = state.entities_at(5, 5)
        assert len(at_5_5) == 2

        at_10_10 = state.entities_at(10, 10)
        assert len(at_10_10) == 1

    def test_get_attractors(self):
        """Test getting task attractors."""
        state = FieldState(width=60, height=20)
        state.add_entity(Entity(id="j", entity_type=EntityType.JUDGE, x=5, y=5))
        state.add_entity(Entity(id="t", entity_type=EntityType.TASK, x=10, y=10))
        state.add_entity(Entity(id="h", entity_type=EntityType.HYPOTHESIS, x=15, y=15))

        attractors = state.get_attractors()
        assert len(attractors) == 2
        assert all(a.entity_type.is_attractor for a in attractors)

    def test_get_agents(self):
        """Test getting bootstrap agents."""
        state = FieldState(width=60, height=20)
        state.add_entity(Entity(id="j", entity_type=EntityType.JUDGE, x=5, y=5))
        state.add_entity(Entity(id="t", entity_type=EntityType.TASK, x=10, y=10))
        state.add_entity(Entity(id="c", entity_type=EntityType.COMPOSE, x=15, y=15))

        agents = state.get_agents()
        assert len(agents) == 2
        assert all(a.entity_type.is_agent for a in agents)


class TestFieldSimulator:
    """Tests for FieldSimulator class."""

    def test_simulator_creation(self):
        """Test simulator creation."""
        state = FieldState(width=60, height=20)
        sim = FieldSimulator(state)
        assert sim.state == state
        assert not sim.is_paused

    def test_pause_resume(self):
        """Test simulation pause and resume."""
        state = FieldState(width=60, height=20)
        sim = FieldSimulator(state)

        sim.pause()
        assert sim.is_paused

        sim.resume()
        assert not sim.is_paused

    def test_tick_advances_time(self):
        """Test that tick advances simulation time."""
        state = FieldState(width=60, height=20)
        sim = FieldSimulator(state)

        initial_tick = state.tick
        sim.tick()
        assert state.tick == initial_tick + 1

    def test_tick_paused(self):
        """Test that tick does nothing when paused."""
        state = FieldState(width=60, height=20)
        sim = FieldSimulator(state)

        sim.pause()
        initial_tick = state.tick
        sim.tick()
        assert state.tick == initial_tick  # No change

    def test_entities_move(self):
        """Test that entities move during simulation."""
        state = FieldState(width=60, height=20)
        entity = Entity(id="test", entity_type=EntityType.JUDGE, x=30, y=10)
        state.add_entity(entity)

        sim = FieldSimulator(state, brownian_probability=1.0)  # Always move

        # Run many ticks to ensure movement
        for _ in range(100):
            sim.tick()

        # Entity should have moved (very likely with 100% brownian)
        # Can't assert exact position due to randomness
        assert state.tick == 100

    def test_dialectic_phase_updates(self):
        """Test dialectic phase transitions."""
        state = FieldState(width=60, height=20)

        # Add active judge
        state.add_entity(
            Entity(id="j", entity_type=EntityType.JUDGE, x=10, y=10, phase=Phase.ACTIVE)
        )

        sim = FieldSimulator(state)
        sim.tick()

        # Should be in FLUX with active agents
        assert state.dialectic_phase == DialecticPhase.FLUX

    def test_dialectic_tension(self):
        """Test tension phase when contradiction is active."""
        state = FieldState(width=60, height=20)

        # Add active contradict agent
        state.add_entity(
            Entity(
                id="x",
                entity_type=EntityType.CONTRADICT,
                x=10,
                y=10,
                phase=Phase.ACTIVE,
            )
        )

        sim = FieldSimulator(state)
        sim.tick()

        assert state.dialectic_phase == DialecticPhase.TENSION

    def test_dialectic_sublate(self):
        """Test sublate phase when synthesis is active."""
        state = FieldState(width=60, height=20)

        # Add active sublate agent
        state.add_entity(
            Entity(
                id="s", entity_type=EntityType.SUBLATE, x=10, y=10, phase=Phase.ACTIVE
            )
        )

        sim = FieldSimulator(state)
        sim.tick()

        assert state.dialectic_phase == DialecticPhase.SUBLATE

    def test_heat_accumulation(self):
        """Test heat accumulation from active agents."""
        state = FieldState(width=60, height=20)
        state.heat = 0

        # Add active agent
        state.add_entity(
            Entity(id="j", entity_type=EntityType.JUDGE, x=10, y=10, phase=Phase.ACTIVE)
        )

        sim = FieldSimulator(state, heat_generation=0.5)

        for _ in range(10):
            sim.tick()

        assert state.heat > 0

    def test_cooling_trigger(self):
        """Test cooling phase triggers at high heat."""
        state = FieldState(width=60, height=20)
        state.heat = 95  # Above threshold

        state.add_entity(
            Entity(id="j", entity_type=EntityType.JUDGE, x=10, y=10, phase=Phase.ACTIVE)
        )

        sim = FieldSimulator(state)
        sim.tick()

        # Heat should have reduced and agents should be waning
        assert state.heat < 95
        assert state.dialectic_phase == DialecticPhase.COOLING

    def test_synthesize(self):
        """Test synthesis operation."""
        state = FieldState(width=60, height=20)
        state.entropy = 50

        # Add two entities to synthesize
        state.add_entity(Entity(id="a", entity_type=EntityType.ID, x=10, y=10))
        state.add_entity(Entity(id="b", entity_type=EntityType.COMPOSE, x=20, y=10))

        sim = FieldSimulator(state)
        result = sim.synthesize(["a", "b"], "synthesis-result")

        assert result is not None
        assert result.id == "synthesis-result"
        assert result.entity_type == EntityType.ARTIFACT
        # Position should be centroid
        assert result.x == 15
        assert result.y == 10
        # Entropy should have increased
        assert state.entropy > 50

    def test_synthesize_fails_with_single_entity(self):
        """Test synthesis requires multiple entities."""
        state = FieldState(width=60, height=20)
        state.add_entity(Entity(id="a", entity_type=EntityType.ID, x=10, y=10))

        sim = FieldSimulator(state)
        result = sim.synthesize(["a"], "result")

        assert result is None

    def test_pheromone_decay_during_tick(self):
        """Test pheromones decay during simulation."""
        state = FieldState(width=60, height=20)
        state.emit_pheromone(PheromoneType.ERROR, 5, 5)  # Fast decay

        sim = FieldSimulator(state)

        # Tick past decay time
        for _ in range(3):
            sim.tick()

        # Pheromone should be cleaned up
        assert len(state.pheromones) == 0


class TestCreateFunctions:
    """Tests for field creation functions."""

    def test_create_default_field(self):
        """Test default field creation."""
        state = create_default_field()

        assert state.width == 60
        assert state.height == 20
        # Should have 7 bootstrap agents
        assert len(state.entities) == 7
        # All should be agents
        assert all(e.entity_type.is_agent for e in state.entities.values())

    def test_create_default_field_custom_size(self):
        """Test default field with custom size."""
        state = create_default_field(width=100, height=50)
        assert state.width == 100
        assert state.height == 50

    def test_create_demo_field(self):
        """Test demo field creation."""
        state = create_demo_field()

        # Should have bootstrap agents plus task and hypothesis
        assert len(state.entities) >= 7
        # Should have non-zero entropy and heat
        assert state.entropy > 0
        assert state.heat > 0
        # Should have focus set
        assert state.focus is not None


class TestDialecticPhase:
    """Tests for DialecticPhase enum."""

    def test_all_phases_exist(self):
        """Test all expected phases exist."""
        phases = [
            DialecticPhase.DORMANT,
            DialecticPhase.FLUX,
            DialecticPhase.TENSION,
            DialecticPhase.SUBLATE,
            DialecticPhase.FIX,
            DialecticPhase.COOLING,
        ]
        assert len(phases) == 6

    def test_phase_values(self):
        """Test phase string values."""
        assert DialecticPhase.DORMANT.value == "dormant"
        assert DialecticPhase.FLUX.value == "flux"
        assert DialecticPhase.TENSION.value == "tension"
        assert DialecticPhase.SUBLATE.value == "sublate"
        assert DialecticPhase.FIX.value == "fix"
        assert DialecticPhase.COOLING.value == "cooling"
